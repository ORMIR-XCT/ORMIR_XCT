import os
import sys
import numpy as np
import SimpleITK as sitk

from matplotlib import pyplot as plt

from ormir_xct.bone_parameters import bmd
from ormir_xct.segmentation.ipl_seg import ipl_seg
from ormir_xct.autocontour.autocontour import autocontour
from ormir_xct.util.hildebrand_thickness import calc_structure_thickness_statistics

def idk(image_path, para):
    if not image_path:
        print("Error: No image path was provided.")
        sys.exit(1)

    image = sitk.ReadImage(image_path, sitk.sitkFloat32)
    spacing = image.GetSpacing()

    # Use standard threshold values in HU
    trab_seg = ipl_seg(image, 
                        1170, 10000, 
                        value_in_range=1,
                        voxel_size=spacing[0]
                        )

    # Define header information (pulled from original AIM image)
    # Need to automate getting these data from AIM file
    mu_scaling = 8192
    mu_water = 0.24090
    rescale_slope = 1603.51904
    rescale_intercept = -391.209015

    # Generate the periosteal and endosteal segmentations
    _, _, peri_mask = autocontour(image, mu_water, rescale_slope, rescale_intercept)


    if para == 'bone volume fraction':
        bone_volume_fraction(trab_seg, peri_mask)
    elif para == 'trabecular thickness':
        trabecular_thickness(trab_seg, spacing, image)
    elif para == 'trabecular separation':
        trabecular_separation(trab_seg, peri_mask, spacing, image)
    elif para == 'trabecular number':
        trabecular_number()
    elif para == 'total bone area':
        total_bone_area()
    elif para == 'bone mineral density':
        bone_mineral_density()
    else:
        print("Error: Not a valid parameter.")
        sys.exit(1)

def bone_volume_fraction(trab_seg, peri_mask):
    trab_seg_np = sitk.GetArrayFromImage(trab_seg)
    peri_mask_np = sitk.GetArrayFromImage(peri_mask)

    bvtv = (trab_seg_np > 0).sum() / (peri_mask_np > 0).sum()
    print(f"BV/TV = {bvtv}")
    print()

    return bvtv


def trabecular_thickness(trab_seg, spacing, image):
    trab_seg_np = sitk.GetArrayFromImage(trab_seg)

    thickness_stats = calc_structure_thickness_statistics(
        trab_seg_np, tuple(spacing), 0, oversample=False, skeletonize=False
    )

    print(f"mean thickness is {thickness_stats[0]} +/- {thickness_stats[1]}")
    print(f"max thickness is {thickness_stats[3]}")

    dt = sitk.GetImageFromArray(thickness_stats[4])

    dt.SetOrigin(image.GetOrigin())
    dt.SetSpacing(image.GetSpacing())
    dt.SetDirection(image.GetDirection())

    return dt

def trabecular_separation(trab_seg, peri_mask, spacing, image):
    trab_seg_inv = 1 - trab_seg

    masked = sitk.Mask(trab_seg_inv, peri_mask)
    masked_np = sitk.GetArrayFromImage(masked)

    thickness_stats = calc_structure_thickness_statistics(
        masked_np, tuple(spacing), 0, oversample=False, skeletonize=False
    )

    print(f"mean separation is {thickness_stats[0]} +/- {thickness_stats[1]}")
    print(f"max separation is {thickness_stats[3]}")
    print()

    dt = sitk.GetImageFromArray(thickness_stats[4])
    dt.SetOrigin(image.GetOrigin())
    dt.SetSpacing(image.GetSpacing())
    dt.SetDirection(image.GetDirection())

    return dt

def trabecular_number():
    ''

def total_bone_area():
    ''

def bone_mineral_density():
    ''