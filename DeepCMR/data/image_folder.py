# Manuel A. Morales (moralesq@mit.edu)
# Harvard-MIT Department of Health Sciences & Technology
# Athinoula A. Martinos Center for Biomedical Imaging

import os
import glob
import pydicom

EXTENSIONS = {}
EXTENSIONS['NIFTI'] = ['.nii.gz', '.nii']
EXTENSIONS['DICOM'] = ['CINE_segmented_LVOT','OsiriX ROI SR']
#EXTENSIONS['DICOM'] = ['CINE_segmented_SAX']
EXTENSIONS['H5PY']  = ['.h5']


def is_data_file(filename, dformat="NIFTI"):
    return any(filename.endswith(extension) for extension in EXTENSIONS[dformat])

def is_valid_dicom(filename, ReferringPhysicianName=None):
    is_valid = False
    try:
        # DICOM files often do have the .dcm extension, thus we need to test all files in folder.
        # can we load it?
        dicom = pydicom.read_file(filename)

        # does it have the correct Referring Physician?
        if ReferringPhysicianName is not None:
            if dicom.ReferringPhysicianName != ReferringPhysicianName: return is_valid
        
        # does it define a protocol/series?
        if 'ProtocolName' in dicom:
            protocol_name = dicom.ProtocolName
        elif 'SeriesDescription' in dicom:
            # This approach could potentially lead to errors.
            protocol_name = dicom.SeriesDescription
        else:
            return is_valid
            
        # is the protocol/series supported?
        if not any(protocol in protocol_name for protocol in EXTENSIONS['DICOM']): return is_valid
        
        # this is the siemens segmentation output, i think. 
        if 'InlineVF' in dicom.SeriesDescription: return is_valid
        # ADDITIONAL TECHNICAL CHECKS
        # check images come primary data (i.e., MR or CT scanners)
        if 'Secondary' in dicom.file_meta[0x0002, 0x0002].repval: return is_valid
        
        is_valid = True
        
    except:
        is_valid = False
                    
    return is_valid

def make_dataset(dir, max_dataset_size=float("inf"), ReferringPhysicianName=None, dformat="NIFTI", 
                 glob_search=False, dicom_folder_start=0):
    
    filenames = []
    assert os.path.isdir(dir), '%s is not a valid directory' % dir
    
    if glob_search:
        dicom_folders = sorted(glob.glob(os.path.join(dir, '*')))
        for root in dicom_folders[dicom_folder_start:max_dataset_size]:
            for filename in glob.glob(os.path.join(root, '*')):
                if is_valid_dicom(filename, ReferringPhysicianName=ReferringPhysicianName):
                    filenames.append(filename)
    else:

        for root, _, fnames in sorted(os.walk(dir)):
            for fname in fnames:

                if dformat == 'DICOM':
                    if is_valid_dicom(os.path.join(root, fname), ReferringPhysicianName=ReferringPhysicianName):
                        filenames.append(os.path.join(root, fname))
                elif is_data_file(fname, dformat=dformat):
                    path = os.path.join(root, fname)
                    filenames.append(path)

                if len(filenames) == max_dataset_size: return filenames

    return filenames
