"""
trabecular_microarchitecture.py

Created by:   Sarah Elmahdy & Michael Kuczynski
Created on:   June 2025
Updated:      March 10, 2026

Description: Calculates trabecular microarchitecture parameters, including:
                - Trabecular Thickness (Tb.Th)
                - Trabecular Separation (Tb.Sp)
                - Trabecular Bone Volume Fraction (Tb.BV/TV)
             The user can compute all parameters, or select which to compute.
"""

import SimpleITK as sitk
import numpy as np
from skimage.morphology import skeletonize
from ormir_xct.core.util.hildebrand_thickness import calc_structure_thickness_statistics


def trabecular_bone_volume_fraction(trab_seg, peri_mask):
    """
    Compute trabecular bone volume fraction (Tb.BV/TV).

    Parameters
    ----------
    trab_seg : SimpleITK.Image
        Binary image representing trabecular segmentation.
    peri_mask : SimpleITK.Image
        Binary image representing periosteal mask.

    Returns
    -------
    float
        Bone volume fraction value.
    """
    trab_seg_np = sitk.GetArrayFromImage(trab_seg)
    peri_mask_np = sitk.GetArrayFromImage(peri_mask)

    bvtv = (trab_seg_np > 0).sum() / (peri_mask_np > 0).sum()
    return bvtv


def trabecular_thickness(trab_seg):
    """
    Compute trabecular thickness.

    Parameters
    ----------
    trab_seg : SimpleITK.Image
        Binary segmentation of trabecular bone.

    Returns
    -------
    tuple
        Thickness statistics (mean, std, min, max, thickness_map).
    """
    trab_seg_np = sitk.GetArrayFromImage(trab_seg)
    spacing = trab_seg.GetSpacing()

    # Returns [mean Tb.Th, st. dev. Tb.Th, min Tb.Th, max Tb.Th, DT image]
    thickness_stats = list(
        calc_structure_thickness_statistics(
            trab_seg_np, tuple(spacing), 0, oversample=False, skeletonize=False
        )
    )

    # Replace the NumPy DT array with a DT image (SimpleITK)
    dt = sitk.GetImageFromArray(thickness_stats[4])
    dt.CopyInformation(trab_seg)

    thickness_stats[4] = dt

    return thickness_stats


def trabecular_separation(trab_seg, peri_mask):
    """
    Compute trabecular separation statistics.

    Parameters
    ----------
    trab_seg : SimpleITK.Image
        Binary image of trabecular segmentation.
    peri_mask : SimpleITK.Image
        Binary image of periosteal mask.

    Returns
    -------
    tuple
        Separation statistics (mean, std, min, max, thickness_map).
    """
    trab_seg_np = sitk.GetArrayFromImage(trab_seg)
    peri_mask_np = sitk.GetArrayFromImage(peri_mask)

    # Ensure masks have a value of 1
    trab_seg_np = trab_seg_np != 0
    peri_mask_np = peri_mask_np != 0

    # Invert the trabecular mask
    trab_seg_inv = 1 - trab_seg_np

    # Only compute separation within the periosteal mask
    masked_np = trab_seg_inv * peri_mask_np

    spacing = trab_seg.GetSpacing()

    # Returns [mean Tb.Sp, st. dev. Tb.Sp, min Tb.Sp, max Tb.Sp, DT image]
    thickness_stats = list(
        calc_structure_thickness_statistics(
            masked_np, tuple(spacing), 0, oversample=False, skeletonize=False
        )
    )

    # Replace the NumPy DT array with a DT image (SimpleITK)
    dt = sitk.GetImageFromArray(thickness_stats[4])
    dt.CopyInformation(trab_seg)

    thickness_stats[4] = dt

    return thickness_stats


def trabecular_number_derived(bvtv, tbth):
    if tbth <= 0:
        raise ValueError("Tb.Th must be positive.")
    
    return bvtv/tbth

def trabecular_number(trab_seg, bone_mask):
    """
    Finding the thickness of the background between thinned ridge centers to estimate 
    inverse trabecular number. Makes use of the existing structure thickness calculation method.

    Method is as described here: https://www.sciencedirect.com/science/article/pii/S0895611198000718

    Parameters:
    trab_seg: SimpleITK.Image
        Binary image of trabecular segmentation.

    bone_mask: SimpleITK.Image
        Binary image of periosteal mask.
    
    Returns:
    float
        Calculated trabecular number.
    """
    spacing = trab_seg.GetSpacing()

    trab_seg_np = sitk.GetArrayFromImage(trab_seg) 
    bone_mask_np = sitk.GetArrayFromImage(bone_mask)

    # ensure values of 1 (like above)
    trab_seg_np = trab_seg_np != 0
    bone_mask_np = bone_mask_np != 0

    # check shape
    if trab_seg_np.shape != bone_mask_np.shape:
        raise ValueError("trab_seg and bone_mask must have the same dimensions.")

    # produce a skeleton for ridge extraction (not necessary if we use skeleton in calc_structure_thickness_statistics)

    # skeleton_np = skeletonize(trab_seg_np, method = 'lee')
    # sitk.WriteImage(sitk.GetImageFromArray(skeleton_np.astype(np.uint8)), 'test2.nii')

    # skeleton_np = skeleton_np != 0
    # ridge_background = (bone_mask_np & (~skeleton_np)).astype(np.uint8)


    ridge_background = (bone_mask_np & (~trab_seg_np)).astype(np.uint8)

    # ridge_background = ridge_background.astype(np.uint8)

    ridge_background_img = sitk.GetImageFromArray(ridge_background)
    # sitk.WriteImage(ridge_background_img, 'test3.nii')

    thickness_stats = calc_structure_thickness_statistics(
        ridge_background,
        spacing,
        0,
        oversample=False,
        skeletonize=True, 
    )

    mean_ridge_spacing = thickness_stats[0]

    if mean_ridge_spacing is None or mean_ridge_spacing <= 0:
        raise ValueError("Mean ridge spacing must be positive to compute Tb.N.")

    # Tb.N. is taken as the inverse of the mean spacing between ridges
    return 1/mean_ridge_spacing


def trabecular_microarchitecture(trab_seg, peri_mask):
    """
    Compute trabecular microarchitecture parameters.

    Parameters
    ----------
    trab_seg : SimpleITK.Image
        Binary image of trabecular segmentation.
    peri_mask : SimpleITK.Image
        Binary image of periosteal mask.

    Returns
    -------
    tuple
        Trabecular microarchitecture parameters dictionary and DT images.
    """
    bvtv_results = trabecular_bone_volume_fraction(trab_seg, peri_mask)
    tbth_results = trabecular_thickness(trab_seg)
    tbsp_results = trabecular_separation(trab_seg, peri_mask)
    tbn_results = trabecular_number(trab_seg, peri_mask)
    tbn_derived = trabecular_number_derived(bvtv_results, tbth_results[0])

    tb_microarch = {
        "Tb.BV/TV": bvtv_results,
        "Mean Tb.Th": tbth_results[0],
        "StDev Tb.Th": tbth_results[1],
        "Min Tb.Th": tbth_results[2],
        "Max Tb.Th": tbth_results[3],
        "Mean Tb.Sp": tbsp_results[0],
        "StDev Tb.Sp": tbsp_results[1],
        "Min Tb.Sp": tbsp_results[2],
        "Max Tb.Sp": tbsp_results[3],
        "Derived Tb.N": tbn_derived,
        "Tb.N": tbn_results,
    }

    return (tb_microarch, tbth_results[4], tbsp_results[4])



