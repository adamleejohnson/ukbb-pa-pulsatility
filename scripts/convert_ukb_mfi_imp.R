# File to convert UK Biobank imputation information files to parquet format
# -- mfi files are downloaded from https://biobank.ndph.ox.ac.uk/ukb/refer.cgi?id=1967
# -- parquet files are compressed and save to disk

files <- list.files(path = "../../Archives.nosync/ukb_imp_mfi", pattern = "*.txt", full.names = T)
for (f in files) {
  i <- vroom::vroom(f, show_col_types = F, col_names = c(
    "Alternate_id",
    "rsid",
    "Position",
    "Allele1",
    "Allele2",
    "MAF",
    "Minor_Allele",
    "INFO"
  ))
  ajtools::write_parquet_zstd(i, xfun::sans_ext(f), 19)
}
