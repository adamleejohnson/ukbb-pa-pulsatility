#!/usr/bin/python
# pip3 install openpyxl
import pandas as pd
import os
import math
import random
import argparse

parser = argparse.ArgumentParser(
    description='''Randomly select a number of studies and create a TrainingSet
    column set to TRUE/FALSE'''
)
parser.add_argument("input",
                    type=str,
                    help='''Excel spreadsheet file containing a list of studies''')
parser.add_argument("output",
                    type=str,
                    help='''Output Excel spreadsheet containing new columns denoting whether
                    each study is part of the training set''')
parser.add_argument("size",
                    type=int,
                    help="Size of training set",
                    metavar="size")
args = parser.parse_args()

if not args.output.endswith('.xlsx'):
    args.output += '.xlsx'

# define params
output_file = args.output
num_training = args.size

# read dictionary as dataframe
dictionary = args.dictionary
ids = pd.read_excel(dictionary, engine='openpyxl', dtype={
    'UKB_ID': 'str',
    'UKB_Field': 'str',
    'UKB_Instance': 'str',
    'Directory': 'str',
    'PatientID': 'str',
    'PatientName': 'str',
    'TrainingSet': 'bool'
})

# make a "TrainingSet" column
try:
    ids.insert(len(ids.columns), 'TrainingSet', pd.NA)
except Exception:
    pass
ids['TrainingSet'] = False

# choose N random entires
ts = ids.sample(num_training)

# update the dictionary
ts['TrainingSet'] = True
ids.update(ts)

# write file to disk
ids.to_excel(output_file, index=False)
