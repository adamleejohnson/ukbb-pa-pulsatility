Pulmonary Artery Pulsatility (CMR + Deep neural network + UK Biobank)
=====

![R](https://img.shields.io/badge/R-276DC3?style=plastic&logo=r&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54)

### Table of Contents
- [Pulmonary Artery Pulsatility (CMR + Deep neural network + UK Biobank)](#pulmonary-artery-pulsatility-cmr--deep-neural-network--uk-biobank)
    - [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [Note on R dependencies](#note-on-r-dependencies)
- [Project Layout](#project-layout)
- [Deep learning neural network (DeepCMR)](#deep-learning-neural-network-deepcmr)
- [UK Biobank phenotype data](#uk-biobank-phenotype-data)
- [Contact](#contact)


*April 2022*&nbsp;&nbsp;|&nbsp;&nbsp;*Adam L. Johnson, MD*&nbsp;&nbsp;[✉️](mailto:aljohnson@mgh.harvard.edu)

# Introduction

This repository contains the code and project structure used in the analysis of pulmonary artery pulsatility by cardiac MRI in the UK Biobank. It is intended to accompany unpublished work currently submitted for peer-review. This repository does **not** contain any raw datasets that were either used by or produced during the analyses – these data files are large, and, in many cases, are restricted by material transfer agreements. Nor does this repository contain any result tables or figures (please refer to the manuscript and supplemental materials for these). The included code is meant to provide implementation details of our methodology, and to encourage reproducibility of our results. The majority of the code is written in either Python or R.

# Note on R dependencies

The R code used throughout this project utilizes two custom-built R packages hosted on GitHub:

1. adamleejohnson/R-ajtools (https://github.com/adamleejohnson/R-ajtools)
2. adamleejohnson/R-ukbiobank (https://github.com/adamleejohnson/R-ukbiobank)

The first, _ajtools_, is a collection of functions, utilities, infix operators, and customized ggplots and patchworks. Documentation is available throughout the package.

The second package, _ukbiobank_, was specifically constructed to facilitate the extraction of relevant phenotypes from raw UK Biobank phenotype data. It is used extensively in the epidemiologic analyses in this project. Please refer to the package for detailed documentation.

Finally, [`notebooks/setup.R`](notebooks/setup.R) performs several initialization tasks common to the `.Rmd` notebooks, such as loading required packages. It also sets the working directory by searching for a parent folder named `ukbb-pulmonary-artery/`.

# Project Layout

```py
ukbb-pulmonary-artery/
├── README.md
│
├── DeepCMR/               # CMR image processing and DNN (see below)
│   ├── README.md
│   ├── data/              # data management interfaces for Deep CMR
│   ├── documentation/     # additional DeepCMR documentation
│   ├── horos/             # extract ROIs from Horos
│   ├── models/            # image segmentation models
│   ├── notebooks
│   │   ├── analysis                                            ─┐
│   │   │   ├── 1_inter-subject-repeatability.ipynb              │
│   │   │   ├── 2_nnUNet_test_analysis.ipynb                     │
│   │   │   ├── 3_nnUNet_predict_analysis.ipynb                  │
│   │   │   └── 5_outlier_analysis.ipynb                         │
│   │   ├── data                                                 │
│   │   │   ├── 1_convert_dicoms_to_nifti.ipynb                  ├─ # Jupyter notebooks
│   │   │   ├── 2_inspect_converted_nifti.ipynb                  │
│   │   │   ├── 3_convert_dicoms_to_nifti_for_all_subjects.ipynb │
│   │   │   ├── 4_export_nifti_for_training_with_nnUNet.ipynb    │
│   │   │   └── 5_export_nifti_for_predicting_with_nnUNet .ipynb │
│   │   └── results                                              │
│   │       └── 1_nnUNet_results.ipynb                          ─┘
│   │
│   ├── options            # global python options
│   ├── results            # results storage
│   ├── scripts            # training scripts
│   └── utils              # misc python utils
│
├── scripts/               # miscellaneous helper scripts
├── data/                  # input data for the analyses in 'notebooks/'
├── notebooks/        
│   ├── 01_training_validation.Rmd          ─┐
│   ├── 02_outlier_removal.Rmd               │
│   ├── 03_merge_data.Rmd                    │
│   ├── 04_principal_component_review.Rmd    │
│   ├── 05_export_data_for_gwas.Rmd          │
│   ├── 06_baseline_characteristics.Rmd      │
│   ├── 07_analyze_epidemiology.Rmd          │
│   ├── 08_analyze_gwas_results.Rmd          ├─ # R markdown notebooks for analyses
│   ├── 09_analyze_gtex_coloc.Rmd            │
│   ├── 10_analyze_eMAGMA.Rmd                │
│   ├── 11_analyze_ABC.Rmd                   │
│   ├── 12_analyze_all_secondary.Rmd         │
│   ├── 13_analyze_single_cell.Rmd           │
│   └── setup.R                             ─┘
│
├── analyses/              # output of analysis results
└── figures/               # output figures and tables
```

The general workflow is as follows:

    data → notebooks → analyses/results → figures

# Deep learning neural network (DeepCMR)

The [`DeepCMR/`](DeepCMR/) folder contains Python code and shell scripts for processing DICOM image files with their accompanying manual annotations, performing neural network training and inference, and processing the neural network-generated annotations to calculate segmentation geometries and quality control metrics.

Refer to [`DeepCMR/README.md`](DeepCMR/README.md) for additional documentation about the cardiac MRI and deep learning workflows.

# UK Biobank phenotype data

UK Biobank phenotype data was obtained under an approved UK Biobank application. Selected fields were extracted from the raw datafile using `ukbconv`. Data was loaded into R and saved as a .rds file. See https://biobank.ctsu.ox.ac.uk/crystal/exinfo.cgi?src=accessing_data_guide for additional details.

# Contact

Please contact Adam L. Johnson (aljohnson@mgh.harvard.edu) with any questions pertaining to this project.