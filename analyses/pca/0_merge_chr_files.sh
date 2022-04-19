#!/bin/bash
# Adam L. Johnson, M.D. (aljohnson@mgh.harvard.edu)
# Cardiovascular Research Center, Division of Cardiology
# Massachusetts General Hospital

# ==================================================================================
# working directory
working_dir="~/ukbb-pulmonary-artery/pca"
# ==================================================================================

cd $working_dir

# print info about current host
hostname=$(hostname)
hostname=${hostname%%.*}
lscpu
lshosts -l $hostname

plink2 --version

plink2 \
   --make-bed \
   --pmerge-list ukb_geno_files.txt bfile \
   --pmerge-list-dir original_geno_files \
   --keep ukb_cmr_sample_IDs_10_2021.txt \
   --out 0_merged_bed_filtered_samples/ukb_cmr_pca_10_2021_merge \
   --threads 4 \
   --memory 8000
