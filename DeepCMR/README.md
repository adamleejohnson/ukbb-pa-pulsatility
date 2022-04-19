# DeepCMR

Deep Learning Application for Cardiac Magnetic Resonance Imaging

### Table of Contents

  - [Summary of Workflow](#summary-of-workflow)
    - [Training](#training)
    - [Predicting](#predicting)
  - [Summary of Jupyter Notebooks](#summary-of-jupyter-notebooks)
  - [Details](#details)
    - [Setting up the Deep Learning environment](#setting-up-the-deep-learning-environment)
    - [Importing and converting DICOMs to NIFTI](#importing-and-converting-dicoms-to-nifti)
    - [Preparing training and testing folders](#preparing-training-and-testing-folders)
    - [Train and Test nnUNet](#train-and-test-nnunet)
    - [Analyzing the testing results](#analyzing-the-testing-results)
      - [Repeatability](#repeatability)
      - [nnUNet](#nnunet)
    - [Predicting and analyzing the whole UK Biobank dataset](#predicting-and-analyzing-the-whole-uk-biobank-dataset)


## Summary of Workflow

### Training

Project root (for data): `{deepcmr_data_root}/` Repository root (for scripts & notebooks): `~/DeepCMR/`

1.  **DICOM-to-Nifti conversion**
    -   `notebooks/data/1_convert_dicoms_to_nifti.ipynb`
    -   Input:
        -   `OrthancDicomStorage/` (Training)
        -   `OrthancDicomStorage-Practice/` (Testing)
    -   Output:
        -   `OrthancDicomStorageNiftis/` (Training)
        -   `OrthancDicomStorage-PracticeNiftis/` (Testing)
2.  **Export Niftis to individual files for nnUNet**
    -   `notebooks/data/4_export_nifti_for_training_with_nnUNet.ipynb`
    -   Input:
        -   `OrthancDicomStorageNiftis/` (Training)
        -   `OrthancDicomStorage-PracticeNiftis/` (Testing)
    -   Output:  `nnUNET/nnUNet_raw_data_base/nnUNet_raw_data/Task618_UKBBPulmonaryArtery/`
3.  **Pre-process files for nnUNet training**
    -   `scripts/1_nnUNet_preprocess.sh 618`
    -   Input:  `nnUNET/nnUNet_raw_data_base/nnUNet_raw_data/Task618_UKBBPulmonaryArtery/`
    -   Output:  `nnUNET/nnUNet_preprocessed/Task618_UKBBPulmonaryArtery/`
4.  **Train nnUNet**
    -   `scripts/2_nnUNet_train.sh 618 Task618_UKBBPulmonaryArtery {0,1,2,3,4}`
    -   `scripts/3_nnUNet_postprocess.sh 618`
    -   Input:  `nnUNET/nnUNet_preprocessed/Task618_UKBBPulmonaryArtery/`
    -   Output:  `nUNET/nnUNet_trained_models/nnUNet/2d/Task618_UKBBPulmonaryArtery/`
5.  **Run network on the test (i.e. repeatability) set**
    -   `scripts/4_nnUNet_test.sh 618 Task618_UKBBPulmonaryArtery/`
    -   Input:  `nnUNET/nnUNet_raw_data_base/nnUNet_raw_data/Task618_UKBBPulmonaryArtery/`
    -   Output:  `nnUNET/results/test/618/`
6.  **Recompile the predictions made on the test set**
    -   `notebooks/results/1_nnUNet_results.ipynb`
    -   Input:  `nnUNET/results/test/618/`
    -   Output:  `predicted_niftis_nnUNet/Task618_UKBBPulmonaryArtery/test/`
7.  **Analyze the predictions made on the test set**
    -   `notebooks/analysis/2_nnUNet_test_analysis.ipynb`
    -   Input:  `predicted_niftis_nnUNet/Task618_UKBBPulmonaryArtery/test/`
    -   Output:  `[repo]/results/nnUNet/repeatability_Task618`

### Predicting

Project root (for data): `{deepcmr_data_root}/` Repository root (for scripts & notebooks): `~/DeepCMR/`

1.  **DICOM-to-Nifti conversion for whole UKBB dataset**
    -   `notebooks/data/3_convert_dicoms_to_nifti_for_all_subjects.ipynb`
    -   Input:  `cmr_lvot_20212_unzipped/`
    -   Output:  `cmr_lvot_20212_niftis/`
2.  **Export Niftis to individual files for nnUNet**
    -   `notebooks/data/5_export_nifti_for_predicting_with_nnUNet.ipynb`
    -   Input:  `cmr_lvot_20212_niftis/`
    -   Output:  `nnUNET/exported_nifts_for_predicting/cmr_lvot_20212_niftis/batch_XXX/` where XXX $\in$ {0, ...,}
3.  **Run network on the whole UKBB dataset**
    -   `scripts/5_nnUNet_predict.sh Task618_UKBBPulmonaryArtery exported_nifts_for_predicting/cmr_lvot_20212_niftis/batch_XXX/ cmr_lvot_20212/batch_XXX`
    -   Multi: `sbatch scripts/5a_nnUNet_predict_batch64.sh Task618_UKBBPulmonaryArtery exported_nifts_for_predicting/cmr_lvot_20212_niftis cmr_lvot_20212`
    -   Input:  `nnUNET/exported_nifts_for_predicting/cmr_lvot_20212_niftis/`
    -   Output:  `nnUNET/nnUNet_predictions/Task618_UKBBPulmonaryArtery/cmr_lvot_20212/`
4.  **Recompile the predictions**
    -   `notebooks/results/1_nnUNet_results.ipynb`
    -   Input:  `nnUNET/nnUNet_predictions/Task618_UKBBPulmonaryArtery/cmr_lvot_20212/`
    -   Output:  `predicted_niftis_nnUNet/Task618_UKBBPulmonaryArtery/cmr_lvot_20212/`
5.  **Analyze the predictions**
    -   `notebooks/analysis/3_nnUNet_predict_analysis.ipynb`
    -   Input:  `predicted_niftis_nnUNet/Task618_UKBBPulmonaryArtery/cmr_lvot_20212/`
    -   Output:  `[repo]/results/nnUNet/618/`

## Summary of Jupyter Notebooks
- **Data Preprocessing:**
  - [Convert Training Dicoms to Nifti](notebooks/data/1_convert_dicoms_to_nifti.ipynb)
  - [Inspect Converted Dicoms](notebooks/data/2_inspect_converted_nifti.ipynb)
  - [Convert All Dicoms to Nifti](notebooks/data/3_convert_dicoms_to_nifti_for_all_subjects.ipynb)
  - [Export for nnUNet](notebooks/data/4_export_nifti_for_training_with_nnUNet.ipynb)
- **Training Results:**
  - [nnUNet](notebooks/results/1_nnUNet_results.ipynb)
- **Analyses:**
  - [Repeatability](notebooks/analysis/1_inter-subject-repeatability.ipynb)
  - [nnUNet_analysis](notebooks/analysis/2_nnUNet_test_analysis.ipynb)

## Details

### Setting up the Deep Learning environment

We need to set up a virtual environment in the ERISXdl server to run all the deep learning packages and to use the Jupyter notebook; follow these [instructions](documentation/ERISXdl_deep_learning_enviroment.md). The [nnUNet](https://github.com/MIC-DKFZ/nnUNet) package and dependencies must also be installed as well if you want to use it.

Some of the Jupyter notebooks use these packages:
- `numpy pandas nibabel opencv-python matplotlib seaborn tqdm scikit-image tqdm joblib medpy`


### Importing and converting DICOMs to NIFTI

Images and manual labels for training and testing are imported as DICOMs from the `OrthancDicomStorage/` and `OrthancDicomStorageNiftis-Practice` folders, accordingly. These DICOMs are converted to NIFTI and saved in a new folder.

- Notebook: [Convert Training Dicoms to Nifti](notebooks/data/1_convert_dicoms_to_nifti.ipynb)

The training and testing images and labels can be inspected in the notebook:
- Notebook: [Inspect Converted Dicoms](notebooks/data/2_inspect_converted_nifti.ipynb)

### Preparing training and testing folders

The NIFTI data needs to be in a specific format for each of the training models. The [nnUNet](https://github.com/MIC-DKFZ/nnUNet) package requires the definition of a "task". In this case all training data has been saved as task 618: `Task618_UKBBPulmonaryArtery/`. Furthermore, each frame needs to be saved as a separate 3D NIFTI. The package also requires a .json file describing the training dataset.

- Notebook: [Export for nnUNet](notebooks/data/4_export_nifti_for_training_with_nnUNet.ipynb)

### Train and Test nnUNet

The nn-UNet scripts use environment variables to identify input and output folders. Since we're using a conda virtual environment, we can tell conda to set the variable. In my case:

```bash
conda env config vars set NNUNET_PROJ_ROOT={deepcmr_data_root}/nnUNET -n DL_cuda11
```

First, pre-process the data:

```bash
sbatch scripts/1_nnUNet_preprocess.sh 618
```

The nnUNet runds 5-fold crosstesting, therefore 5 different models need to be trained. In the ERISXdl server, we can then run all 5 training experiments at once, simply run this command for fold = {0,1,2,3,4}.

```bash
sbatch scripts/2_nnUNet_train.sh 618 Task618_UKBBPulmonaryArtery <fold>
```

Once all the folds have been trained, we then run post-processing:

```bash
sbatch scripts/3_nnUNet_postproceess.sh 618
```

Then we can test on the testing images as follows:

```bash
sbatch scripts/4_nnUNet_test.sh 618 Task618_UKBBPulmonaryArtery
```

nnUNet will save the results (3D, per frame) in `$nnUNet_PROJ_ROOT/results/outputFolder/task` (for nnUNet_test.sh, outputFolder = 'test'). Then, using the using the notebook [nnUNet_results](notebooks/results/1_nnUNet_results.ipynb), these are combined into 4D NIFTIs for each subject and saved in the `{deepcmr_data_root}/OrthancDicomStorage-PracticeNiftis_Output_nnUNet` folder.

### Analyzing the testing results

#### Repeatability

The inter-subject repeatability (reader 1 vs reader 2) is calculated in notebook
- Notebook: [Repeatability](notebooks/analysis/1_inter-subject-repeatability.ipynb)

#### nnUNet

Geometric metrics (i.e., DSC, HD) as well as vessel area and distensibility are calculated. Other metrics such as sphericity could also be implemented.

- Notebook: [nnUNet_analysis](notebooks/analysis/2_nnUNet_test_analysis.ipynb)

### Predicting and analyzing the whole UK Biobank dataset

We can predict on a new set of images as follows:

```bash
sbatch scripts/5_nnUNet_predict.sh 618 inputPath outputLabel
```

However, this will not work if we have a large number of files that have been split into separate batch_XXX folders by `notebooks/data/5_export_nifti_for_predicting_with_nnUNet.ipynb`. Instead, use the following script, which will run N separate intances of the prediction command in paralell (the script is setup to perform 8 tasks in parallel, with each task requiring 1 GPU + 24 CPUs + 48G memory). Each N corresponds to a batch_XXX folder. For example, if there are 64 batch folders (batch_000 ... batch_63), run the command:

```bash
sbatch scripts/5a_nnUNet_predict_batches.sh 64 Task618_UKBBPulmonaryArtery exported_nifts_for_predicting/cmr_lvot_20212_niftis/ cmr_lvot_20212/
```
