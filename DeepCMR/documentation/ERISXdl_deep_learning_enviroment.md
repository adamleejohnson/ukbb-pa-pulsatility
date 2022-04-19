### Virtual Environment

Run the following commands to create and activate a deep learning environment that uses python version 3.6 and GPU CUDA version 11 (only for ERISXdl cluster).

```bash
conda create --name DL_cuda11 python=3.6
```

```bash
conda activate DL_cuda11
```

### Jupyter Kernels

Run the following commands to install the Jupyter notebooks

```bash
pip install ipykernel
```

```bash
pip install ipywidgets --user
```

```bash
python -m ipykernel install --user --name DL_cuda11 --display-name "Python (DL_cuda11)"
```

- We need to edit the document located at `.local/share/jupyter/kernels/dl_cuda11/kernel.json` by adding some information. This step enables you to use the Jupyter notebooks online using your user name. Make sure to replace the user name. For example, you can edit the document using vim:

```bash
vim .local/share/jupyter/kernels/dl_cuda11/kernel.json
```

- The final document should look like this:

```json
{
  "argv": [
    "~/.conda/envs/DL_cuda11/bin/python",
    "-m",
    "ipykernel_launcher",
    "-f",
    "{connection_file}"
  ],

  "env": {
    "PYTHONPATH": "~/.conda/envs/DL_cuda11/lib/python3.6/site-packages/",
    "LD_LIBRARY_PATH": "~/.conda/envs/DL_cuda11/lib"
  },

  "display_name": "Python (DL_cuda11)",
  "language": "python"
}
```

- Don't forget to change the username!

### Cuda and PyTorch

Install the cuda toolkit and pytorch (preferably v1.8.1) with this command. See [pytorch installation command generator](https://pytorch.org/get-started/locally/).

```bash
conda install -c nvidia cuDNN
conda install pytorch torchvision torchaudio cudatoolkit=11.1 -c pytorch-lts -c nvidia
```

### Extras

These packages allow nnUNet to create plots of the network architecture.

```bash
conda install graphviz python-graphviz
pip3 install hiddenlayer
```

### nnUNet

```bash
pip3 install nnunet
```

### Environment variables

Finally, modify the `LD_LIBRARY_PATH` environment variable with the conda helper.

Switch to the base environment (this ensures `$CONDA_PREFIX` is defined correctly in the next step):

```bash
conda deactivate; conda activate
```

Run the conda command to set an environment variable specific to the DL_cuda11 virtual environment:

```bash
conda env config vars set LD_LIBRARY_PATH=$CONDA_PREFIX/pkgs/cudnn-8.0.4-cuda11.1_0/lib:$CONDA_PREFIX/pkgs/cudatoolkit-11.1.1-h6406543_8/lib:$LD_LIBRARY_PATH -n DL_cuda11
```

Set nnUNet_n_proc_DA environment variable [see instructions here](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/expected_epoch_times.md#results).

```bash
conda env config vars set nnUNet_n_proc_DA=20 -n DL_cuda11
```

---

All commands in one block (silent install):

```bash
conda create -y --name DL_cuda11 python=3.6; conda deactivate; conda activate DL_cuda11; yes | pip install ipykernel; yes | pip install ipywidgets --user; python -m ipykernel install --user --name DL_cuda11 --display-name "Python (DL_cuda11)"; echo '{
  "argv": [
    "~/.conda/envs/DL_cuda11/bin/python",
    "-m",
    "ipykernel_launcher",
    "-f",
    "{connection_file}"
  ],

  "env": {
    "PYTHONPATH": "~/.conda/envs/DL_cuda11/lib/python3.6/site-packages/",
    "LD_LIBRARY_PATH": "~/.conda/envs/DL_cuda11/lib"
  },

  "display_name": "Python (DL_cuda11)",
  "language": "python"
}' > ~/.local/share/jupyter/kernels/dl_cuda11/kernel.json; conda install -y -c nvidia cuDNN; conda install -y pytorch torchvision torchaudio cudatoolkit=11.1 -c pytorch-lts -c nvidia; conda install -y graphviz python-graphviz; yes | pip3 install hiddenlayer; yes | pip3 install nnunet; conda deactivate; conda activate; conda env config vars set LD_LIBRARY_PATH=$CONDA_PREFIX/pkgs/cudnn-8.0.4-cuda11.1_0/lib:$CONDA_PREFIX/pkgs/cudatoolkit-11.1.1-h6406543_8/lib:$LD_LIBRARY_PATH -n DL_cuda11; conda env config vars set nnUNet_n_proc_DA=20 -n DL_cuda11
```

```bash
conda env config vars set NNUNET_PROJ_ROOT={deepcmr_data_root}/nnUNET -n DL_cuda11
```
