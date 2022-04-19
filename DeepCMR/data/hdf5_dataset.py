import h5py
import numpy as np
import pandas as pd
import torch

class HDF5Dataset(torch.utils.data.Dataset):
    
    def __init__(self, h5_file):
        self.h5_file = h5_file
        self.info_df = self.__getinfo__()
         
    def __len__(self):
        return len(self.info_df)
    
    def __getitem__(self, index):
        return self.__getgroup__(index)
        
    def __getinfo__(self):
        info_dic = {}
        with h5py.File(self.h5_file, 'r') as h5_file:
            for group_name, group in h5_file.items():
                info_dic[group_name] = []
                for data_name, data in group.items():
                    info_dic[group_name].append(data_name)
         
        info_df = pd.DataFrame.from_dict(info_dic, orient='index')
        info_df.sort_index(inplace=True)
        return info_df
    
    def __getgroup__(self, index):
        raise NotImplementedError
        
class SegmentationDataset(HDF5Dataset):
    
    def __init__(self, h5_file, x_name='x', y_name='y', transform=None):
        super().__init__(h5_file)
        self.transform = transform
        
    def __getgroup__(self, index):
        with h5py.File(self.h5_file, 'r') as h5_file:
            x  = h5_file[self.info_df.index[index]]['x'][:]
            y  = h5_file[self.info_df.index[index]]['y'][:]
            if self.transform is not None:
                x, y = self.transform(x, y)
            return x.astype('float32'), y.astype('int')
        
    def __inspect__(self):
        """Verify h5 file meets `SimpleDataset` assumptions."""
        # need to make sure all samples have the same dimensions
        raise NotImplementedError
        
        
import cv2
from scipy.ndimage import rotate
from skimage.measure import find_contours

class Transform():
    
    def __init__(self, augmentation=False, crop=False, video=False):
        
        self.augmentation = augmentation
        self.crop = crop
        self.video = video

    def joint_transform(self, x, y, **kwargs):

        if self.augmentation:

            angle_max    = kwargs.pop('angle_degree',360);
            pixel_max    = kwargs.pop('translate_pixels',25)
            often_affine = kwargs.pop('translate_percent',0.5)
            often_blur = kwargs.pop('often_blur',0.5)
            
            xaxes = range(len(x.shape))[-2:]
            yaxes = range(len(y.shape))[-2:]
            
            if np.random.rand() < often_blur:
                x, y = self.gaussian_blur(x, y)
            
            # Random rotations
            if np.random.rand() < often_affine:
                angle = np.random.randint(1, angle_max+1)
                x = rotate(x, angle=angle, axes=xaxes, reshape=False, order=1, mode='constant', cval=0)
                y = rotate(y, angle=angle, axes=yaxes, reshape=False, order=0, mode='constant', cval=0)

            # Random translations and inversions
            
            for xaxis, yaxis in zip(xaxes, yaxes):
                
                if np.random.rand() < often_affine:
                    x = np.flip(x, axis=xaxis)
                    y = np.flip(y, axis=yaxis)

                if np.random.rand() < often_affine:
                    shift = np.random.randint(-pixel_max,pixel_max)

                    x = np.roll(x, shift=shift, axis=xaxis)
                    y = np.roll(y, shift=shift, axis=yaxis)
                    
            if self.video:
                if np.random.rand() < often_affine:
                    x = np.flip(x, axis=0)
                    y = np.flip(y, axis=0)
                    
                if np.random.rand() < often_affine:
                    nt = x.shape[0]//2
                    temporal_shift = np.random.randint(-nt,nt)

                    x = np.roll(x, shift=temporal_shift, axis=0)
                    y = np.roll(y, shift=temporal_shift, axis=0)

        if self.crop:
            xaxes = range(len(x.shape))[-2:]
            yaxes = range(len(y.shape))[-2:]

            for xaxis, yaxis in zip(xaxes, yaxes):                
                x = x.take(indices=range(32, 64+32), axis=xaxis)
                y = y.take(indices=range(32, 64+32), axis=yaxis)

        return x, y
    
    def gaussian_blur(self, x, y, nt_min=5, rmin=15, rmax=60, ksize=(9,9)):

        if len(x.shape) == 3:
            assert len(y.shape) == 2

            c = find_contours(y, level=0.9)[0]
            c = c[np.random.randint(len(c))]
            Y, X = np.meshgrid(range(y.shape[-2]),range(y.shape[-1]))
            a = np.random.randint(1,3)
            b = np.random.randint(1,3)
            r = np.random.randint(rmin,rmax)
            mask = ((X-c[0])/a)**2 + ((Y-c[1])/b)**2 < r

            blurred_img = cv2.GaussianBlur(x[0], ksize, 0)
            x[0][mask==1] = blurred_img[mask==1]

        elif len(x.shape) == 4:
            assert len(y.shape) == 3
            assert len(x) >= nt_min
            # use first mask as reference 
            c = find_contours(y[0], level=0.9)[0]
            c = c[np.random.randint(len(c))]
            Y, X = np.meshgrid(range(y.shape[-2]),range(y.shape[-1]))
            a = np.random.randint(1,3)
            b = np.random.randint(1,3)
            r = np.random.randint(rmin,rmax)
            mask = ((X-c[0])/a)**2 + ((Y-c[1])/b)**2 < r

            # apply to nt_min frames
            start = np.random.randint(0, len(x)-5)
            stop = start + nt_min
            for t in range(start, stop):
            #for t in range(len(x)):
                blurred_img = cv2.GaussianBlur(x[t,0], ksize, 0)
                x[t,0][mask==1] = blurred_img[mask==1]

        return x, y