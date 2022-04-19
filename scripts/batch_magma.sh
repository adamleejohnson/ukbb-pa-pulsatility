#!/bin/bash

Nsamples=40496

tissues=(
	Artery_Coronary
	Artery_Aorta
	Artery_Tibial
	Cells_Cultured_fibroblasts
	Heart_Atrial_Appendage
	Heart_Left_Ventricle
	Lung
)

magma_cmd="
mkdir -p results/{1}

./magma \
	--bfile g1000_eur/g1000_eur \
	--gene-annot emagma_gtex_annot/{1}.genes.annot \
	--pval pulsatility_gwas.txt N=${Nsamples} \
	--gene-model snp-wise=multi \
	--genes-only \
	--out results/{1}/{1}_eMAGMA_multi
"

parallel -j 4 --delay 1 "$magma_cmd" ::: ${tissues[@]}
