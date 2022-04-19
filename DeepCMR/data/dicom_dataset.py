# Manuel A. Morales (moralesq@mit.edu)
# Harvard-MIT Department of Health Sciences & Technology  
# Athinoula A. Martinos Center for Biomedical Imaging

import os
import h5py
import glob
import pydicom
import warnings
import numpy as np
import pandas as pd
import nibabel as nib

from data.base_dataset import BaseDataset
from data.image_folder import make_dataset
from horos.ROI import decode_NS

class DICOMDataset(BaseDataset):

    def __init__(self, opt, load_labels_from_OsiriX=False):
        BaseDataset.__init__(self, opt)
        self.filenames = sorted(make_dataset(opt.dataroot, 
                                             opt.max_dataset_size, 
                                             opt.username, 
                                             'DICOM', 
                                             glob_search=opt.glob_search,
                                             dicom_folder_start=opt.dicom_folder_start))
        
        self.read_metadata()
        self.load_labels_from_OsiriX = load_labels_from_OsiriX
        
    def __len__(self):
        return len(self.acquisitions)
                
    def __getitem__(self, idx): 
        pid = '_'.join(self.acquisitions[idx].split('_')[:-1]) #PatientName
        uid = self.acquisitions[idx].split('_')[-1] #AcquisitionInstanceUID
        df  = self.metadata[(self.metadata.PatientName==pid)&(self.metadata.AcquisitionInstanceUID==uid)]
        
        # second bool might yield errors once we expand to other datasets
        BOOL1 = self.metadata_OsiriX.PatientName==pid
        BOOL2 = self.metadata_OsiriX.StudyInstanceUID==df.StudyInstanceUID.unique()[0]
        df_OsiriX = self.metadata_OsiriX[BOOL1&BOOL2]

        return self.load_acquisition(df, df_OsiriX)
        
    def read_metadata(self):       
        
        metadata = {'FileName':[],
                    'PatientName':[], 
                    'SeriesInstanceUID':[], 
                    'StudyInstanceUID':[],
                    'SOPInstanceUID':[],
                    'SeriesDescription':[],
                    'ProtocolName':[], 
                    'SeriesTime':[], 
                    'TriggerTime':[], 
                    'InstanceNumber':[], 
                    'ImageOrientationPatient':[],  
                    'ImagePositionPatient':[],
                    'SliceLocation':[], 
                    'PixelSpacing':[], 
                    'SliceThickness':[], 
                    'AcquisitionInstanceUID':[], 
                    'SliceInstanceUID':[]}
        
        for filename in self.filenames:
            dicom = pydicom.read_file(filename)
            
            # Metadata common to all datasets
            metadata['FileName']                += [filename]
            metadata['PatientName']             += [str(dicom[0x0010, 0x0010].value)]
            metadata['SeriesInstanceUID']       += [dicom.SeriesInstanceUID]
            metadata['StudyInstanceUID']        += [dicom.StudyInstanceUID]
            metadata['SeriesDescription']       += [dicom.SeriesDescription]
            metadata['InstanceNumber']          += [dicom.InstanceNumber]
            metadata['AcquisitionInstanceUID']  += [dicom.SeriesInstanceUID.split('.')[9]]
            metadata['SliceInstanceUID']        += [dicom.SeriesInstanceUID.split('.')[10]]

            if dicom.SeriesDescription != 'OsiriX ROI SR':


                metadata['SOPInstanceUID']          += [dicom.SOPInstanceUID]
                metadata['ProtocolName']            += [dicom.ProtocolName]
                metadata['SeriesTime']              += [dicom.SeriesTime]
                metadata['TriggerTime']             += [dicom.TriggerTime]
                metadata['ImageOrientationPatient'] += [dicom.ImageOrientationPatient]
                metadata['ImagePositionPatient']    += [dicom.ImagePositionPatient]
                metadata['SliceLocation']           += [dicom.SliceLocation]
                metadata['PixelSpacing']            += [dicom.PixelSpacing]
                metadata['SliceThickness']          += [dicom.SliceThickness]
            else:
                metadata['SOPInstanceUID']          += [dicom[0x0040, 0xa730][0][0x0008, 0x1199][0][0x0008, 0x1155].value]
                metadata['ProtocolName']            += [np.nan]
                metadata['SeriesTime']              += [np.nan]
                metadata['TriggerTime']             += [np.nan]
                metadata['ImageOrientationPatient'] += [np.nan]
                metadata['ImagePositionPatient']    += [np.nan]
                metadata['SliceLocation']           += [np.nan]
                metadata['PixelSpacing']            += [np.nan]
                metadata['SliceThickness']          += [np.nan]

        metadata = pd.DataFrame(metadata)
        metadata_OsiriX = metadata[metadata.SeriesDescription=='OsiriX ROI SR']
        metadata = metadata[metadata.SeriesDescription!='OsiriX ROI SR']
        
        acquisitions = []
        print('Found %d patient(s):'%(len(metadata.PatientName.unique())))
        for patient in metadata.PatientName.unique():
            acqs = metadata[metadata.PatientName==patient].AcquisitionInstanceUID.unique().tolist()
            print(patient, ': with', len(acqs), 'acquisitions:')
            for acq in sorted(acqs):
                acquisitions += [patient+'_'+acq]
                print('  ', acquisitions[-1])
            
        print('Found %d patient(s) with labels:'%(len(metadata_OsiriX.PatientName.unique())))
        for patient in metadata_OsiriX.PatientName.unique():
            print(patient)

        self.metadata        = metadata
        self.metadata_OsiriX = metadata_OsiriX
        self.acquisitions    = acquisitions


    def load_acquisition(self, df, df_OsiriX, apply_spline=True):
        

        slices = df.SeriesInstanceUID.unique().tolist()
        phases = df.SeriesInstanceUID.value_counts().unique()
        assert len(phases)==1, 'Number of phases does not match!'
        number_of_slices = len(slices) 
        number_of_phases = int(phases)
        pixel_array = pydicom.read_file(df.iloc[0].FileName).pixel_array
        
        
        
        acq_4D = np.zeros((pixel_array.shape +(number_of_slices, number_of_phases)), dtype=pixel_array.dtype)
        acq_4D_OsiriX = {}
        areas_cm2 = {}
        for z_slice, series in enumerate(slices):
            for phase in range(number_of_phases):
                filename = df[df.SeriesInstanceUID==series].sort_values('InstanceNumber').iloc[phase].FileName
                dicom = pydicom.read_file(filename)
                acq_4D[:,:,z_slice,phase] += dicom.pixel_array
                
                if self.load_labels_from_OsiriX:
                    SOPInstanceUID  = df[df.SeriesInstanceUID==series].sort_values('InstanceNumber').iloc[phase].SOPInstanceUID
                    filename_OsiriX = df_OsiriX[df_OsiriX.SOPInstanceUID==SOPInstanceUID].FileName
                    
                    if len(filename_OsiriX) != 1:
                        # this is a problem unique to the server. 
                        # let's assume for now content time refers to when the ROI was edited
                        filename_OsiriX = list(filename_OsiriX)
                        ContentTimes = [pydicom.read_file(filename).ContentTime for filename in filename_OsiriX]
                        j = np.argmax(ContentTimes)
                        print('Warning: found %d ROIs with the same SOPInstanceUID'%(len(filename_OsiriX)))

                        NS = str(pydicom.read_file(filename_OsiriX[j]).EncapsulatedDocument)
                    else:
                        
                        NS = str(pydicom.read_file(filename_OsiriX.item()).EncapsulatedDocument)
                    coords, area_cm2 = decode_NS(NS=NS, apply_spline=apply_spline)
                    acq_4D_OsiriX['%s_%s'%(z_slice,phase)] = coords
                    areas_cm2['%s_%s'%(z_slice,phase)] = area_cm2
                    
        affine = read_affine(df.iloc[df.SliceLocation.argmin()])

        return nib.Nifti1Image(acq_4D, affine), acq_4D_OsiriX, areas_cm2
    
def extract_cosines(ImageOrientationPatient):
    row_cosine    = np.array(ImageOrientationPatient[:3])
    column_cosine = np.array(ImageOrientationPatient[3:])
    slice_cosine  = np.cross(row_cosine, column_cosine)
    return np.stack((row_cosine, column_cosine, slice_cosine))

def read_affine(df, viewer='slicer'):
    Zooms = np.array(list(df.PixelSpacing)+[df.SliceThickness], dtype=float)
    ImageOrientationPatient = np.array(df.ImageOrientationPatient, dtype=float)
    ImagePositionPatient    = np.array(df.ImagePositionPatient, dtype=float)
    
    ijk2ras = extract_cosines(ImageOrientationPatient)
    if viewer == "slicer":
        ijk2ras = (ijk2ras*np.array([-1,-1,1])).T
        ImagePositionPatient = ImagePositionPatient*np.array([-1,-1,1])

    affine  = np.stack((ijk2ras[:,0]*Zooms[0],
                        ijk2ras[:,1]*Zooms[1],
                        ijk2ras[:,2]*Zooms[2],
                        ImagePositionPatient), axis=1)
    
    return np.vstack((affine,[[0,0,0,1]]))   

