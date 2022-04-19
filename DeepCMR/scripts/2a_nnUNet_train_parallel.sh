#!/bin/bash
# Adam L. Johnson, M.D. (aljohnson@mgh.harvard.edu)
# Cardiovascular Research Center, Division of Cardiology
# Massachusetts General Hospital

# Load environment
source ~/.bashrc > /dev/null 2>&1
conda init > /dev/null 2>&1
conda deactivate > /dev/null 2>&1
conda activate DL_cuda11 > /dev/null 2>&1

# ------------------------- DO NOT CHANGE THESE -------------------------
[ -z "$NNUNET_PROJ_ROOT" ] && echo '$NNUNET_PROJ_ROOT must be set. See DeepCMR/README.md.' && exit 1
export nnUNet_raw_data_base=$NNUNET_PROJ_ROOT/nnUNet_raw_data_base
export nnUNet_preprocessed=$NNUNET_PROJ_ROOT/nnUNet_preprocessed
export RESULTS_FOLDER=$NNUNET_PROJ_ROOT/nnUNet_trained_models
# -----------------------------------------------------------------------


# Define commands to be run in parallel:
commands='

echo -e "Running command: nnUNet_train 2d nnUNetTrainerV2 '$2' {1} --npz\n"
nvidia-smi
srun --unbuffered nnUNet_train 2d nnUNetTrainerV2 '$2' {1} --npz

'
# The entire block is enclosed in single quotes. Bash variables
# will need to be placed outside of the single quotes. Use {n}
# wherever we need to include the iteration index.


# Define log file stub:
logfile_stub="~/logs/nnUNet_train_parallel_$SLURM_JOB_ID"
# for each iteration index n, ".n.log" will be appended to the logfile
# stub and will be used as the stdout/stderr for that iteration.


# Define srun arguments:
srun="srun -n1 -N1 --exclusive --unbuffered"
# --exclusive     ensures srun uses distinct CPUs for each job step
# -N1 -n1         allocates a single node to each task

# Define parallel arguments:
parallel="parallel -N 1 --delay .2 -j $SLURM_NTASKS"
# -N 1              is number of arguments to pass to each job
# --delay .2        prevents overloading the controlling node on short jobs
# -j $SLURM_NTASKS  is the number of concurrent tasks parallel runs, so number of CPUs allocated

# Print some information
start_time=$(date +%s)
printf "%s: Execution start\n" $(date +%m/%d/%Y-%H:%M:%S)
printf "Running 5 instances across $SLURM_NTASKS parallel tasks, with $SLURM_GPUS_PER_TASK gpu(s) & $SLURM_CPUS_PER_TASK cpu(s) per task, spread across the cluster. See separate logfiles for output of each instance.\n"

# Run the tasks:
$parallel "$srun bash -c '$commands'>$logfile_stub.{1}.log 2>&1" ::: $(seq 0 4)
# in this case, we are running a script named runtask, and passing it a single argument
# {1} is the first argument
# parallel uses ::: to separate options. Here {1..64} is a shell expansion defining the values for
#    the first argument, but could be any shell command
#
# so parallel will run the runtask script for the numbers 1 through 64, with a max of 40 running 
#    at any one time
#
# as an example, the first job will be run like this:
#    srun -N1 -n1 --exclusive ./runtask arg1:1


unset nnUNet_raw_data_base
unset nnUNet_preprocessed
unset RESULTS_FOLDER

# Print some information
end_time=$(date +%s)
printf "%s: Execution end\n\n" $(date +%m/%d/%Y-%H:%M:%S)
duration=$((end_time - start_time))
printf 'Total duration (hh:mm:ss): %.2d:%.2d:%.2d\n' $((duration/3600)) $((duration%3600/60)) $((duration%60))
