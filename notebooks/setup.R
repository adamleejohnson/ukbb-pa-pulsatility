# custom packages hosted on github (tools, helpers, etc)
# devtools::install_github("adamleejohnson/R-ajtools")
# devtools::install_github("adamleejohnson/R-ukbiobank")

# libraries: core
library(tidyverse)
library(ajtools)
library(arrow, include.only = c("read_parquet", "write_parquet"))
library(vroom, include.only = "vroom")
library(magrittr, include.only = "%<>%")
loadNamespace("ukbiobank") # custom package hosted on github
loadNamespace("reticulate")
loadNamespace("readxl")

# libraries: statistics
loadNamespace("survival")
loadNamespace("survminer")
loadNamespace("Rfast")
loadNamespace("coloc")
loadNamespace("susieR")
loadNamespace("psych")
loadNamespace("irr")

# libraries: plotting
library(ggplot2)
library(patchwork)
loadNamespace("ggforce")
loadNamespace("ggsignif")
loadNamespace("locuscomparer")

# libraries: tables
library(flextable, mask.ok = "compose")
library(DiagrammeR)
loadNamespace("tableone")
loadNamespace("DiagrammeRsvg")
loadNamespace("gridExtra")
loadNamespace("kableExtra")
loadNamespace("rsvg")
loadNamespace("gtsummary")

# Find the working directory:
# recursively travel up until we find the specified folder
PROJ_ROOT <- getwd()
while (basename(PROJ_ROOT %<>% dirname()) != "ukbb-pulmonary-artery") {}
knitr::opts_knit$set(root.dir = PROJ_ROOT)

# ggplot2 theme options
theme_set(
  theme_classic(
    base_size = 7,
    base_family = "Arial"
  ) +
    theme(
      plot.margin = margin(1, 1, 1, 1),
      plot.title = element_text(size = rel(1), hjust = 0.5),
      plot.background = element_blank(),
      panel.background = element_blank(),
      legend.background = element_rect(fill = "transparent"),
      axis.text = element_text(color = "black"),
      axis.ticks = element_line()
    )
)

# gt & gtsummary options
purrr::quietly(gtsummary::theme_gtsummary_journal)()

# flextable options
flextable::set_flextable_defaults(
  font.family = "Arial",
  font.size = 8,
  text.align = NULL,
  cs.family = "Arial",
  border.color = "black"
)

# python options
# set up a conda environment so we can use modules in the DeepCMR sub-folder!
Sys.unsetenv("RETICULATE_PYTHON") # don't let reticulate look at this environment variable for python
options(reticulate.conda_binary = "~/.conda/bin/conda")
reticulate::use_condaenv(condaenv = "rstudio", required = T)
reticulate::py_discover_config() # make sure reticulate is looking in the right spot
reticulate::py_run_string('
import sys
from pathlib import Path

repo_path = Path(r.PROJ_ROOT).joinpath("DeepCMR")
assert repo_path.is_dir(), "The repo_path must be set to the DeepCMR root in order to find custom modules"
if not str(repo_path.resolve()) in sys.path: sys.path.append(str(repo_path.resolve()))

import numpy as np
import pandas as pd
import nibabel as nib
from pathlib import Path
')
