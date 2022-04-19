#!/bin/bash
# Adam L. Johnson, M.D. (aljohnson@mgh.harvard.edu)
# Cardiovascular Research Center, Division of Cardiology
# Massachusetts General Hospital

# print info about current host
hostname=$(hostname)
hostname=${hostname%%.*}
lscpu
lshosts -l $hostname

# move to output folder
outdir="~/ukbb-pulmonary-artery/pca/4_flashpca_results"
mkdir -p $outdir
cd $outdir


flashpca --version

flashpca \
   --bfile ../3_filtered_geno_files/ukb_cmr_pca_10_2021 \
   --suffix _ukb_cmr_10.2021.txt \
   --numthreads 8 \
   --memory 8192 \
   --verbose
