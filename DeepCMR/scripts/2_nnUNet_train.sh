#!/bin/bash
# Adam L. Johnson, M.D. (aljohnson@mgh.harvard.edu)
# Cardiovascular Research Center, Division of Cardiology
# Massachusetts General Hospital

# Load environment
source ~/.bashrc > /dev/null 2>&1
conda init > /dev/null 2>&1
conda deactivate > /dev/null 2>&1
conda activate DL_cuda11 > /dev/null 2>&1

# Check if project root is set
[ -z "$NNUNET_PROJ_ROOT" ] && echo '$NNUNET_PROJ_ROOT must be set. See DeepCMR/README.md.' && exit 1
echo -e "Project root: $NNUNET_PROJ_ROOT\n"

# ----------------- DO NOT CHANGE THESE -----------------
export nnUNet_raw_data_base=$NNUNET_PROJ_ROOT/nnUNet_raw_data_base
export nnUNet_preprocessed=$NNUNET_PROJ_ROOT/nnUNet_preprocessed
export RESULTS_FOLDER=$NNUNET_PROJ_ROOT/nnUNet_trained_models
# -------------------------------------------------------

echo -e "Running command: nnUNet_train 2d nnUNetTrainerV2 $2 $3 --npz\n"
nvidia-smi
srun --unbuffered nnUNet_train 2d nnUNetTrainerV2 $2 $3 --npz

# FYI: for some reason, nnUNet_train only works when run with srun --unbuffered.
# I'm not sure why it needs srun, but the --unbuffered part is needed for nnUNet
# stdout to work (not sure why). It fails completely without srun on my setup.
# I figured this out because everything works when run in interactive mode
# (i.e. srun --pty bash), because --pty implicitly calls --unbuffered.

unset nnUNet_raw_data_base
unset nnUNet_preprocessed
unset RESULTS_FOLDER
