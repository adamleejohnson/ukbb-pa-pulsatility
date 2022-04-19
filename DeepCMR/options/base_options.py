import os
import argparse
import tensorflow

class JupyterOptions():
    
    def __init__(self, dataroot, username=None, max_dataset_size=float("inf"), 
                       glob_search=False, dicom_folder_start=0):
        """This class defines options used during jupyter sessions.
        """
        self.dataroot = dataroot
        self.username = username
        self.max_dataset_size = max_dataset_size
        self.glob_search = glob_search
        self.dicom_folder_start = dicom_folder_start