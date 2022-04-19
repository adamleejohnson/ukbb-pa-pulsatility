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
   --indep-pairwise 1000 80 0.1 \
   --bfile 0_merged_bed_filtered_samples/ukb_cmr_pca_10_2021_merge \
   --extract 1_filtered_snps_freq/ukb_cmr_pca_10_2021.snplist \
   --out 2_filtered_snps_LD/ukb_cmr_pca_10_2021 \
   --threads 4 \
   --memory 8000
