#!/usr/bin/python
import os
from pathlib import Path
from pydicom import dcmread
import pandas as pd

import argparse

parser = argparse.ArgumentParser(
    description='''Read from an Excel file that defines the training set for the list of studies
                (a value of TRUE in the column labeled TrainingSet), and read the from the Reader
                column to determine the assigned reader. Then edit the DICOM files for that study
                so that the ReferringPhysician field is set to the name of the reader.''')
parser.add_argument(
    "dictionary",
    type=str,
    help="Excel spreadsheet file containing a list of studies, whether those studies are in the TrainingSet, and who the readers are")
parser.add_argument(
    "srcdir",
    type=str,
    help="Input directory containing the unzipped UKB studies")
parser.add_argument(
    "destdir",
    type=str,
    help="Output directory where modified DICOMs will be saved")
parser.add_argument(
    "reader_col",
    type=str,
    help="Name of the column containing reader names")
args = parser.parse_args()

# params
dictionary = args.dictionary
src_dir = args.srcdir
dest_dir = args.destdir
reader_col = args.reader_col

# load dictionary
ids = pd.read_excel(dictionary, engine='openpyxl', dtype={
    'UKB_ID': 'str',
    'UKB_Field': 'str',
    'UKB_Instance': 'str',
    'Directory': 'str',
    'PatientID': 'str',
    'PatientName': 'str',
    'TrainingSet': 'bool',
    'ValidationSet': 'bool',
    'TestSet': 'bool',
    reader_col: 'str'
})
print("Loaded dictionary from %s." % dictionary)

if not reader_col in ids.columns:
    raise Exception(reader_col + " column not found")

succ_count = 0
fail_count = 0
# loop through all training set rows
ts = ids.loc[ids['TrainingSet'] & ~pd.isna(ids[reader_col])]

for i, row in ts.iterrows():
    thisDir = row['Directory']
    thisUKBID = row['UKB_ID']
    thisPtID = row['PatientID']
    thisPtName = row['PatientName']
    thisReader = row[reader_col]

    thisSrcPath = os.path.join(src_dir, thisDir)

    # for each study, rename the Referring Physician to the assigned reader
    # and save a copy in the destination folder

    # make destination directory for this reader and this patient
    thisDestPath = os.path.join(dest_dir, thisDir)
    Path(thisDestPath).mkdir(parents=True, exist_ok=True)

    num_dcm = 0
    if os.path.isdir(thisSrcPath):

        # go into the source directory and find the dicom files
        found_dcm = False
        for file in os.scandir(thisSrcPath):
            if file.is_file and file.name.endswith('.dcm'):

                # Edit and store the dicom in destination directory
                with dcmread(file) as dcm:

                    # Referring Physician's Name
                    # dcm[0x0008, 0x0090]
                    dcm.ReferringPhysicianName = thisReader

                    # print("Saving %s" % os.path.join(this_dest_dir, file.name))
                    # input("Press Enter to continue...")
                    dcm.save_as(os.path.join(thisDestPath, file.name))
                    num_dcm += 1

                found_dcm = True

        if found_dcm:
            succ_count += 1
        else:
            print("ERROR: Could not find DICOMs in %s" % thisSrcPath)
            fail_count += 1

    else:
        print("ERROR: Directory %s does not exist" % thisSrcPath)
        fail_count += 1

    print("Success: %d, Error: %d | Processed path %s with %d DICOMs" % (succ_count, fail_count, thisSrcPath, num_dcm))

print()
print("Finished processing %d studies (%d errors)." % (succ_count + fail_count, fail_count))

# Change permissions
print("Fixing permissions...")
os.chmod(dest_dir, 0o555)
for root, dirs, files in os.walk(dest_dir):
    for d in dirs:
        os.chmod(os.path.join(root, d), 0o555)
    for f in files:
        os.chmod(os.path.join(root, f), 0o444)
print("Done")