# Manuel A. Morales (moralesq@mit.edu)
# Harvard-MIT Department of Health Sciences & Technology
# Athinoula A. Martinos Center for Biomedical Imaging
# -------------------------------------------------------
# Adam L. Johnson, M.D. (aljohnson@mgh.harvard.edu)
# Cardiovascular Research Center, Division of Cardiology
# Massachusetts General Hospital

from re import S
from matplotlib.pyplot import axis, colorbar
import numpy as np
import nibabel as nib
import matplotlib
import matplotlib.pylab as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Ellipse
from matplotlib.gridspec import GridSpec
from scipy.ndimage.measurements import label
from utils import geometry
from matplotlib import animation, cm


def PlotContours(ax: plt.Axes,
                 mask: np.ndarray,
                 tissue_labels=[1],
                 contour_colors=['lime'],
                 contour_labels=['PA'],
                 tolerance=0.1,
                 alpha=1,
                 linewidth=2,
                 legend=False):

    contours = geometry.labels_to_contours(mask, tissue_labels=tissue_labels)

    for tissue in contours:
        t_contour = contours[tissue]
        t_idx = tissue_labels.index(tissue)
        ax.plot(t_contour[:, 1], t_contour[:, 0],
                alpha=alpha,
                linewidth=linewidth,
                color=contour_colors[t_idx],
                label=contour_labels[t_idx])
    if legend:
        ax.legend(fontsize=26)
    return ax


def PlotMask(ax: plt.Axes,
             label_nifti: np.ndarray,
             tissue_label=1,
             alpha=0.15) -> plt.Axes:
    """
    Plot a binary mask on a subplot object

    Parameters
    ----------
    ax : plt.Axes
        matplotlib subplot object
    label_nifti : np.ndarray
        Segmentation/label nifti
    tissue_label : int, optional
        Tissue label to select from the segmentation nifti, by default 1
    alpha : float, optional
        Mask image transparency, by default 0.15

    Returns
    -------
    plt.Axes
        matplotlib subplot object
    """

    mask = (label_nifti == tissue_label)
    colors = [(0, 0, 1, c) for c in np.linspace(0, 1, 100)]
    cmapblue = mcolors.LinearSegmentedColormap.from_list('mycmap', colors, N=5)
    ax.imshow(mask, cmap=cmapblue, alpha=alpha, interpolation='none')
    return ax


def PlotEllipse(ax: plt.Axes,
                label_nifti: np.ndarray,
                tissue_label=1,
                alpha=0.15,
                ellipseColor='red',
                axesColor='white') -> plt.Axes:
    """
    Fit an ellipse to a given segmentation, and plot in on the subplot (ax) object

    Parameters
    ----------
    ax : plt.Axes
        matplotlib subplot object
    label_nifti : np.ndarray
        Segmented (labeled) nifti image (2-dimensional)
    tissue_label : int, optional
        Tissue label to select from segmentation, by default 1
    alpha : float, optional
        Image transparency for the ellipse, by default 0.15
    ellipseColor : str, optional
        Ellipse color, by default 'red'
    axesColor : str, optional
        Color of major and minor axes lines, by default 'white'

    Returns
    -------
    ax : plt.Axes
        matplotlib subplot object
    """

    center, (minor_ax, major_ax), theta = geometry.fit_ellipse_px(
        label_nifti, tissue_label=tissue_label)

    # switch center from row/column to x/y
    center_xy = center[::-1]

    # plot ellipse
    plt_ellipse = Ellipse(center_xy,
                          height=2*minor_ax,
                          width=2*major_ax,
                          angle=theta,
                          alpha=alpha,
                          color=ellipseColor)
    ax.add_patch(plt_ellipse)

    # plot principle axes
    rot_mat = geometry.rotation_mat_2d(theta * np.pi / 180)
    maj_vec = rot_mat @ [major_ax, 0]
    min_vec = rot_mat @ [0, minor_ax]
    maj_ax = np.array([center_xy - maj_vec, center_xy + maj_vec])
    min_ax = np.array([center_xy - min_vec, center_xy + min_vec])

    ax.plot(maj_ax[:, 0], maj_ax[:, 1], axesColor,
            linewidth=4, linestyle='dashed')
    ax.plot(min_ax[:, 0], min_ax[:, 1], axesColor,
            linewidth=4, linestyle='dashed')
    return ax


def makefig_overview(original_nii_path: str,
                     label_nii_path: str,
                     patient_name: str,
                     margin=5,
                     frame_interval=5,
                     intensity_min=0,
                     intensity_max=384,
                     interpolation='bilinear',
                     cmap='gray',
                     plt_show=True,
                     ellipse_show=False
                     ) -> matplotlib.figure:
    """
    Create a visual overview of the segmentation.

    Parameters
    ----------
    original_nii_path : str
        Path to original nifti file to display raw image data
    label_nii_path : str
        Path to segmentation (prediction) nifti file
    patient_name : str
        Patient name (for labeling)
    margin : int, optional
        Number of pixels to pad around the segmentation, by default 5
    frame_interval : int, optional
        Show every N frames, by default 5
    intensity_min : int, optional
        Minimum pixel intensity value (mapped to 0), by default 0
    intensity_max : int, optional
        Maximum pixel intensity value (mapped to 1), by default 384
    interpolation : str, optional
        Raw image interpolation, by default 'nearest'
    cmap : str, optional
        Color map to use for raw image, by default 'gray'
    """

    original_nifti = nib.load(original_nii_path).get_fdata()
    label_nifti = nib.load(label_nii_path).get_fdata()

    num_frames = original_nifti.shape[3]
    num_plots = int((num_frames - 1) / frame_interval) + 1

    # get common bounding box
    rb, cb = geometry.common_bounding_box(label_nifti, margin=margin)

    I = original_nifti.squeeze()
    L = label_nifti.squeeze()

    nrows = 2 if ellipse_show else 1
    fig, ax = plt.subplots(nrows=nrows,
                           ncols=num_plots,
                           dpi=72,
                           figsize=(5*num_plots, 5*nrows),
                           gridspec_kw={'wspace': 0, 'hspace': 0})
    fig.patch.set_facecolor('black')

    for i, t in enumerate(range(0, num_frames-1, frame_interval)):
        if ellipse_show:
            # set limits
            for j in (0, 1):
                ax[j][i].set_xlim(cb)
                ax[j][i].set_ylim(rb)
                ax[j][i].invert_yaxis()
                ax[j][i].axis('off')
                ax[j][i].set_xticklabels([])
                ax[j][i].set_yticklabels([])

            # show original mri image
            ax[0][i].imshow(I[:, :, t], cmap=cmap,
                            interpolation=interpolation, vmin=intensity_min, vmax=intensity_max)
            ax[1][i].imshow(I[:, :, t], cmap=cmap, interpolation=interpolation,
                            vmin=intensity_min, vmax=intensity_max)

            # plot linear contour
            try:
                PlotContours(ax[0][i], L[:, :, t])
            except:
                pass

            # plot mask
            try:
                PlotMask(ax[0][i], L[:, :, t])
            except:
                pass

            # plot ellipse
            try:
                PlotEllipse(ax[1][i], L[:, :, t])
            except:
                pass

            ax[0][i].set_title(patient_name if i == 0 else t,
                               fontsize=30, color='white')
            if i == 0:
                ax[1][i].set_title('Ellipse Fit', fontsize=30, color='white')

        else:
            # set limits
            ax[i].set_xlim(cb)
            ax[i].set_ylim(rb)
            ax[i].invert_yaxis()
            ax[i].axis('off')
            ax[i].set_xticklabels([])
            ax[i].set_yticklabels([])

            # show original mri image
            ax[i].imshow(I[:, :, t], cmap=cmap,
                         interpolation=interpolation, vmin=intensity_min, vmax=intensity_max)

            # plot linear contour
            try:
                PlotContours(ax[i], L[:, :, t])
            except:
                pass

            # plot mask
            try:
                PlotMask(ax[i], L[:, :, t])
            except:
                pass

            ax[i].set_title(patient_name if i == 0 else t,
                            fontsize=30, color='white')

    if plt_show:
        plt.show()

    return fig


def make_mask_animation(original_nii_path: str,
                        label_nii_path: str,
                        patient_name: str,
                        output_path: str,
                        ffmpeg='/usr/bin/ffmpeg',
                        margin=20,
                        intensity_min=0,
                        intensity_max=384,
                        interpolation='bilinear',
                        cmap='gray',
                        contour_show=True,
                        ellipse_show=False,
                        area_plot=False,
                        show_name=False
                        ) -> animation.Animation:

    original_nifti = nib.load(original_nii_path)
    pixel_spacing_2d = original_nifti.header.get_zooms()[:2]
    original_nifti = original_nifti.get_fdata()
    label_nifti = nib.load(label_nii_path).get_fdata()

    num_frames = original_nifti.shape[3]

    # get common bounding box
    rbounds, cbounds = geometry.common_bounding_box(label_nifti, margin=margin, square=True)

    I = original_nifti.squeeze()
    L = label_nifti.squeeze()

    # # create animation
    # # https://eli.thegreenplace.net/2016/drawing-animated-gifs-with-matplotlib/
    # fig, _ = plt.subplots(nrows=2 if area_plot else 1, dpi=72, figsize=(5, 10 if area_plot else 5))
    fig = plt.figure(figsize=(5, 6 if area_plot else 5))
    if area_plot:
        gs = GridSpec(nrows=2, ncols=1, height_ratios=[7, 1])
        fig.add_subplot(gs[0, 0])
        fig.add_subplot(gs[1, 0])
    else:
        fig.add_subplot()
    fig.patch.set_facecolor('black')
    ax = fig.axes

    # get areas
    if area_plot:
        areas = []
        for i in range(num_frames):
            areas += [geometry.get_area_cm2(L[:, :, i], pixel_spacing_2d)]

    def reset_plot():
        ax[0].clear()
        ax[0].set_xlim(cbounds)
        ax[0].set_ylim(rbounds)
        ax[0].invert_yaxis()
        # ax.axis('off')
        ax[0].set_xticklabels([])
        ax[0].set_yticklabels([])

        if area_plot:
            ax[1].clear()
            ax[1].set_ylabel("Area $(\mathrm{cm}^2)$", color='white', fontsize=10)
            ax[1].tick_params(axis='y', colors='white', which='both', labelsize=10)
            ax[1].spines['left'].set_color('white')
            ax[1].set_facecolor('black')

    def animate(i):
        reset_plot()

        image_i = I[:, :, i]
        label_i = L[:, :, i]

        im = ax[0].imshow(image_i, cmap=cmap,
                          interpolation=interpolation, vmin=intensity_min, vmax=intensity_max)
        if contour_show:
            PlotContours(ax[0], label_i)
            PlotMask(ax[0], label_i)

        ax[0].set_title(patient_name if show_name else "", fontsize=15, color='white')
        ax[0].set_xlabel('Frame %02d / %02d' % (i+1, num_frames), fontsize=10, color='white', loc='right')

        if area_plot:
            ax[1].plot(list(range(1, num_frames+1)), areas)
            ax[1].plot([i+1], areas[i], marker="o", color="white")

        return im,

    # plt.tight_layout()
    r = animation.FuncAnimation(fig, func=animate, frames=range(num_frames),
                                interval=100, blit=True, repeat=True)
    plt.rcParams['animation.ffmpeg_path'] = ffmpeg
    Writer = animation.FFMpegWriter(fps=20)
    r.save(output_path, writer=Writer)
    plt.close()

    return r
