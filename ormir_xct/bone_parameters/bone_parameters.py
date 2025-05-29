import os
import sys
import numpy as np
import SimpleITK as sitk

from matplotlib import pyplot as plt

from ormir_xct.bone_parameters import bmd
from ormir_xct.segmentation.ipl_seg import ipl_seg
from ormir_xct.autocontour.autocontour import autocontour
from ormir_xct.util.hildebrand_thickness import calc_structure_thickness_statistics

from ormir_xct.util.scanco_rescale import (
    convert_scanco_to_bmd,
    convert_linear_attenuation_to_bmd,
    convert_hu_to_bmd,
)

def trab_peri_array(image, spacing, mu_water, rescale_slope, rescale_intercept):
    # Use standard threshold values in HU
    trab_seg = ipl_seg(image, 
                        1170, 10000, 
                        value_in_range=1,
                        voxel_size=spacing[0]
                        )

    # Generate the periosteal and endosteal segmentations
    dst_mask, prx_mask, peri_mask = autocontour(image, mu_water, rescale_slope, rescale_intercept)

    trab_seg_np = sitk.GetArrayFromImage(trab_seg)
    peri_mask_np = sitk.GetArrayFromImage(peri_mask)

    return trab_seg, peri_mask, trab_seg_np, peri_mask_np

def idk(image_path, para, mu_scaling, mu_water, rescale_slope, rescale_intercept, image_units = None, mask = None):
    # Figure out what mask??? 

    if not image_path:
        print("Error: No image path was provided.")
        sys.exit(1)

    image = sitk.ReadImage(image_path, sitk.sitkFloat32)
    image_np = sitk.GetArrayFromImage(image)
    spacing = image.GetSpacing()

    # Use standard threshold values in HU
    trab_seg, peri_mask, trab_seg_np, peri_mask_np = trab_peri_array(image, spacing, mu_water, rescale_slope, rescale_intercept)

    tb = None
    if para == 'bv':
        dt = bone_volume_fraction(trab_seg_np, peri_mask_np)
    elif para == 'tb.th':
        dt, tb = trabecular_thickness(trab_seg_np, spacing, image)
    elif para == 'tb.sp':
        dt, tb = trabecular_separation(trab_seg, peri_mask, spacing, image)
    elif para == 'tb.n':
        dt, tb = trabecular_number(trab_seg_np, spacing, image)
    elif para == 'tba':
        dt = total_bone_area(peri_mask_np, spacing)
    elif para == 'bmd':
        dt, tb = bone_mineral_density(image_np, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept)
    elif para == 'bmdmask':
        dt, tb = bone_mineral_density_mask(image, mask, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept)
    else:
        print("Error: Not a valid parameter.")
        sys.exit(1)

    if tb:
        return dt, tb
    else:
        return dt

def bone_volume_fraction(trab_seg_np, peri_mask_np):
    bvtv = (trab_seg_np > 0).sum() / (peri_mask_np > 0).sum()
    print(f"BV/TV = {bvtv}")

    return bvtv

def trabecular_thickness(trab_seg_np, spacing, image):
    thickness_stats = calc_structure_thickness_statistics(
        trab_seg_np, tuple(spacing), 0, oversample=False, skeletonize=False
    )

    print(f"mean thickness is {thickness_stats[0]} +/- {thickness_stats[1]}")
    print(f"max thickness is {thickness_stats[3]}")

    dt = sitk.GetImageFromArray(thickness_stats[4])

    dt.SetOrigin(image.GetOrigin())
    dt.SetSpacing(image.GetSpacing())
    dt.SetDirection(image.GetDirection())

    return dt, thickness_stats

def trabecular_separation(trab_seg, peri_mask, spacing, image):
    trab_seg_inv = 1 - trab_seg

    masked = sitk.Mask(trab_seg_inv, peri_mask)
    masked_np = sitk.GetArrayFromImage(masked)

    thickness_stats = calc_structure_thickness_statistics(
        masked_np, tuple(spacing), 0, oversample=False, skeletonize=False
    )

    print(f"mean separation is {thickness_stats[0]} +/- {thickness_stats[1]}")
    print(f"max separation is {thickness_stats[3]}")

    dt = sitk.GetImageFromArray(thickness_stats[4])
    dt.SetOrigin(image.GetOrigin())
    dt.SetSpacing(image.GetSpacing())
    dt.SetDirection(image.GetDirection())

    return dt, thickness_stats

def trabecular_number(trab_seg_np, spacing, image):
    # Skeletonize the trabecular bone segmentation 
    thickness_stats = calc_structure_thickness_statistics(
        trab_seg_np, tuple(spacing), 0, oversample=False, skeletonize=True
    )

    # Mean spacing between the midlines of the trabeculae
    mean_spacing = thickness_stats[0] 
    # The inverse of the mean of the distance transform
    tb_n = 1 / mean_spacing

    print(f"Trabecular Number (Tb.N) = {tb_n}")

    dt = sitk.GetImageFromArray(thickness_stats[4])
    dt.SetOrigin(image.GetOrigin())
    dt.SetSpacing(image.GetSpacing())
    dt.SetDirection(image.GetDirection())

    return dt, thickness_stats

def total_bone_area(peri_mask_np, spacing):
    pixel_area = spacing[0] * spacing[1]
    
    total_area = (peri_mask_np > 0).sum() * pixel_area
    print(f"Total Bone Area = {total_area} mm^2")
    return total_area

# Currently bmd uses simpleITK and bmd mask uses numpy 
# Create a way to ensure they both use the same method
# Might just call external file?
def bone_mineral_density(image_array, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept):
    image_statistics_filter = sitk.StatisticsImageFilter()

    # Now convert to BMD units if needed
    if image_units == "bmd":
        # No conversion needed
        image = sitk.GetImageFromArray(image_array)
        image_statistics_filter.Execute(image)
    elif image_units == "scanco":
        # Convert from Scanco native units to linear attenuation
        # Then convert to BMD
        image_array = convert_scanco_to_bmd(
            image_array, mu_scaling, rescale_slope, rescale_intercept
        )
        image = sitk.GetImageFromArray(image_array)
        image_statistics_filter.Execute(image)
    elif image_units == "attenuation":
        # Convert to BMD
        image_array = convert_linear_attenuation_to_bmd(
            image_array, rescale_slope, rescale_intercept
        )
        image = sitk.GetImageFromArray(image_array)
        image_statistics_filter.Execute(image)
    elif image_units == "hu":
        # Convert from HU to linear attenuation
        # Then convert to BMD
        image_array = convert_hu_to_bmd(
            image_array, mu_water, rescale_slope, rescale_intercept
        )
        image = sitk.GetImageFromArray(image_array)
        image_statistics_filter.Execute(image)
    else:
        print(
            "ERROR: Invalid image units provided. Only BMD, SCANCO, ATTENUATION, or HU are accepted."
        )
        sys.exit(1)

    mean = image_statistics_filter.GetMean()
    std = image_statistics_filter.GetSigma()
    print(f"mean bone mineral density is {mean} +/- {std}")

    return mean, std

# Might combine with bone mineral density
def bone_mineral_density_mask(image, mask, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept):
    mean, std = 0, 0
    image_statistics_filter = sitk.StatisticsImageFilter()
    # No conversion needed if we already have BMD units
    if image_units == "scanco":
        # Convert from Scanco native units to linear attenuation. Then convert to BMD.
        # Convert both the image and background value.
        image = convert_scanco_to_bmd(
            image, mu_scaling, rescale_slope, rescale_intercept
        )
    elif image_units == "attenuation":
        # Convert to BMD.
        # Convert both the image and background value.
        image = convert_linear_attenuation_to_bmd(
            image, rescale_slope, rescale_intercept
        )
    elif image_units == "hu":
        # Convert from HU to linear attenuation. Then convert to BMD.
        # Convert both the image and background value.
        image = convert_hu_to_bmd(image, mu_water, rescale_slope, rescale_intercept)
    elif image_units != "bmd":
        print(
            "ERROR: Invalid image units provided. Only BMD, SCANCO, ATTENUATION, or HU are accepted."
        )
        sys.exit(1)

    numpy_image = sitk.GetArrayFromImage(image)
    mask = sitk.GetArrayFromImage(mask)
    mean = numpy_image.GetMean()
    std = numpy_image.GetSigma()

    print(f"mean bone mineral density mask is {mean} +/- {std}")
    
    return mean, std