#!/usr/bin/python
import os
import re
from pydicom import dcmread
import pandas as pd
import argparse

parser = argparse.ArgumentParser(
    description='''Search through a directory containing unzipped UK Biobank
        cardiac MRI studies, and create a table associating the UK Biobank
        patient ID with the patient ID/name stored in DICOM tags'''
)
parser.add_argument("SearchDir", type=str,
                    help="Directory to search through")
parser.add_argument("OutputFile", type=str, help="Output xlsx file")
args = parser.parse_args()

if not args.OutputFile.endswith('.xlsx'):
    args.OutputFile += '.xlsx'

assert os.path.isdir(
    args.SearchDir), "Search directory must be a valid path"

id_dicts = []
succ_count = 0
fail_count = 0
# get all subdirectories of the root directory
for path in os.scandir(args.SearchDir):
    if path.is_dir:

        # check if directory name is in correct (UKB CMR) format &
        # extract participant ID from directory name
        m = re.search(r"^(\d+)_(\d+)_(\d)_\d$", path.name)
        if m:
            ukb_id = m.group(1)
            ukb_field = m.group(2)
            ukb_instance = m.group(3)

            # go into the directory and find a dicom file
            found_dcm = False
            for file in os.scandir(path):
                if file.is_file and file.name.endswith('.dcm'):

                  # Read the dicom and extract info
                    with dcmread(file) as dcm1:

                        id_dicts.append({
                            "UKB_ID": ukb_id,
                            "UKB_field": ukb_field,
                            "UKB_Instance": ukb_instance,
                            "Directory": path.name,
                            "PatientID": dcm1.PatientID,
                            "PatientName": dcm1.PatientName
                        })

                        succ_count += 1

                    # don't iterate through other dicoms, assume that since
                    # they're all in the same folder, they have the same patient
                    # identifiers
                    found_dcm = True
                    break

            if not found_dcm:
                print("ERROR: Could not find DICOM in %s" & path.name)
                fail_count += 1

        else:
            print("ERROR: Directory %s doesn't match UKB pattern" & path.name)
            fail_count += 1

    print("Success: %d, Error: %d | Processed path %s" %
          (succ_count, fail_count, path.name), end='\r')

print()
print("Finished processing %d files (%d errors)." %
      (succ_count + fail_count, fail_count))

# save dictionary as data_frame
id_dicts = pd.DataFrame(id_dicts)

# write file to disk
id_dicts.to_excel(args.OutputFile, index=False)
