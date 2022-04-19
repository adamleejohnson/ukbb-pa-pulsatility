# Manuel A. Morales (moralesq@mit.edu)
# Harvard-MIT Department of Health Sciences & Technology
# Athinoula A. Martinos Center for Biomedical Imaging

import numpy as np
import pandas as pd
import nibabel as nib
from matplotlib import path
from medpy.metric.binary import hd, dc


def contour_to_mask(contour, shape):

    mask = np.zeros(shape, dtype='uint8')
    shape = mask.shape[:2]

    if len(mask.shape) == 4:
        for key in contour:
            z_slice, phase = np.array(key.split('_'), dtype=int)
            closed_path = path.Path(contour[key][:, ::-1])
            m = closed_path.contains_points(
                list(np.ndindex(shape))).reshape(shape)
            mask[:, :, z_slice, phase] += m.astype('uint8')

    return mask


def contour_to_nifti(contour, shape, affine):
    mask = contour_to_mask(contour=contour, shape=shape)
    return nib.Nifti1Image(mask, affine=affine)


def get_geometric_metrics(M_gt, M_pred, voxelspacing,
                          tissue_labels=[1, 2, 3], tissue_label_names=['RV', 'LVM', 'LV'], phase=0):
    """Calculate the Dice Similarity Coefficient and Hausdorff distance. 
    """

    Dice = []
    Hausdorff = []
    TissueClass = []
    for label in tissue_labels:
        TissueClass += [tissue_label_names[label-1]]

        gt_label = np.copy(M_gt)
        gt_label[gt_label != label] = 0

        pred_label = np.copy(M_pred)
        pred_label[pred_label != label] = 0

        gt_label = np.clip(gt_label, 0, 1)
        pred_label = np.clip(pred_label, 0, 1)

        dice = dc(gt_label, pred_label)
        hausdorff = hd(gt_label, pred_label, voxelspacing=voxelspacing)

        Dice.append(dice)
        Hausdorff.append(hausdorff)

    output = {'DSC': Dice, 'HD': Hausdorff,
              'TissueClass': TissueClass, 'Phase': [phase]*len(tissue_labels)}
    return pd.DataFrame(output)


def get_area_cm2(M, pixel_spacing_mm, tissue_label=1):
    pixel_area_cm2 = np.prod(pixel_spacing_mm) / 100
    area_cm2 = (M == tissue_label).sum()*pixel_area_cm2
    return area_cm2
