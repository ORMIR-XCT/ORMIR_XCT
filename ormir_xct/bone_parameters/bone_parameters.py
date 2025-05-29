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

def idk(image_path, para, mu_scaling, mu_water, rescale_slope, rescale_intercept, image_units, mask):
    # Figure out what mask??? 

    if not image_path:
        print("Error: No image path was provided.")
        sys.exit(1)

    image = sitk.ReadImage(image_path, sitk.sitkFloat32)
    image_np = sitk.GetArrayFromImage(image)
    spacing = image.GetSpacing()

    # Use standard threshold values in HU
    trab_seg = ipl_seg(image, 
                        1170, 10000, 
                        value_in_range=1,
                        voxel_size=spacing[0]
                        )

    # Generate the periosteal and endosteal segmentations
    _, _, peri_mask = autocontour(image, mu_water, rescale_slope, rescale_intercept)


    if para == 'bone volume fraction':
        bone_volume_fraction(trab_seg, peri_mask)
    elif para == 'trabecular thickness':
        trabecular_thickness(trab_seg, spacing, image)
    elif para == 'trabecular separation':
        trabecular_separation(trab_seg, peri_mask, spacing, image)
    elif para == 'trabecular number':
        trabecular_number(trab_seg, spacing, image)
    elif para == 'total bone area':
        total_bone_area(peri_mask, spacing)
    elif para == 'bone mineral density':
        bone_mineral_density(image_np, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept)
    elif para == 'bone mineral desnity mask':
        bone_mineral_density_mask(image,mask,image_units,mu_scaling,mu_water,rescale_slope,rescale_intercept)
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

def trabecular_number(trab_seg, spacing, image):
    trab_seg_np = sitk.GetArrayFromImage(trab_seg)

    # Skeletonize the trabecular bone segmentation 
    thickness_stats = calc_structure_thickness_statistics(
        trab_seg_np, tuple(spacing), 0, oversample=False, skeletonize=True
    )

    # Mean spacing between the midlines of the trabeculae
    mean_spacing = thickness_stats[0] 
    # The inverse of the mean of the distance transform
    tb_n = 1 / mean_spacing

    print(f"Trabecular Number (Tb.N) = {tb_n}")
    print(f"Mean spacing between ridges = {mean_spacing}")
    print()

    dt = sitk.GetImageFromArray(thickness_stats[4])
    dt.SetOrigin(image.GetOrigin())
    dt.SetSpacing(image.GetSpacing())
    dt.SetDirection(image.GetDirection())

    return dt

def total_bone_area(peri_mask, spacing):
    peri_mask_np = sitk.GetArrayFromImage(peri_mask)
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
        image_statistics_filter.Execute(image_array)
    elif image_units == "scanco":
        # Convert from Scanco native units to linear attenuation
        # Then convert to BMD
        image_array = convert_scanco_to_bmd(
            image_array, mu_scaling, rescale_slope, rescale_intercept
        )
        image_statistics_filter.Execute(image_array)
    elif image_units == "attenuation":
        # Convert to BMD
        image_array = convert_linear_attenuation_to_bmd(
            image_array, rescale_slope, rescale_intercept
        )
        image_statistics_filter.Execute(image_array)
    elif image_units == "hu":
        # Convert from HU to linear attenuation
        # Then convert to BMD
        image_array = convert_hu_to_bmd(
            image_array, mu_water, rescale_slope, rescale_intercept
        )
        image_statistics_filter.Execute(image_array)
    else:
        print(
            "ERROR: Invalid image units provided. Only BMD, SCANCO, ATTENUATION, or HU are accepted."
        )
        sys.exit(1)

    mean = image_statistics_filter.GetMean()
    std = image_statistics_filter.GetSigma()
    return mean, std

# Might combine with bone mineral density
def bone_mineral_density_mask(image,mask,image_units,mu_scaling,mu_water,rescale_slope,rescale_intercept):
    mean, std = 0, 0

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
    mean = numpy_image[mask > 0].mean()
    std = numpy_image[mask > 0].std()

    return mean, std