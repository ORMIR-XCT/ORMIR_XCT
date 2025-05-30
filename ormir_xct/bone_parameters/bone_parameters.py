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
    """
    Segment trabecular bone and generate periosteal mask using autocontour.

    Parameters
    ----------
    image : SimpleITK.Image
        Input CT image.
    spacing : tuple
        Voxel spacing of the image.
    mu_water : float
        Linear attenuation of water.
    rescale_slope : float
        Slope used in rescaling image intensities.
    rescale_intercept : float
        Intercept used in rescaling image intensities.

    Returns
    -------
    trab_seg : SimpleITK.Image
        Segmented trabecular region.
    peri_mask : SimpleITK.Image
        Mask of periosteal boundary.
    trab_seg_np : numpy.ndarray
        Numpy array of trabecular segmentation.
    peri_mask_np : numpy.ndarray
        Numpy array of periosteal mask.
    """
    
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

# Figure out what mask??? 
def calculate_bone_parameter(image_path, para, mu_scaling, mu_water, rescale_slope, rescale_intercept, image_units = None, mask = None):
    """
    Dispatch function to compute selected bone parameter based on identifier.

    Parameters
    ----------
    image_path : str
        Path to image file.
    para : str
        Bone parameter to compute.
    mu_scaling : int
        Scaling factor for converting units.
    mu_water : float
        Linear attenuation of water.
    rescale_slope : float
        Intensity rescale slope.
    rescale_intercept : float
        Intensity rescale intercept.
    image_units : str, optional
        Units of the input image (e.g., 'hu', 'scanco').
    mask : SimpleITK.Image, optional
        Binary mask for use in BMD calculations.

    Returns
    -------
    result : float or tuple
        Computed parameter or result image and statistics.
    """

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
        # dt, tb = bone_mineral_density(image_np, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept)
        dt, tb = bone_mineral_density(image, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept)
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
    """
    Compute bone volume fraction (BV/TV).

    Parameters
    ----------
    trab_seg_np : numpy.ndarray
        Binary array representing trabecular segmentation.
    peri_mask_np : numpy.ndarray
        Binary array representing periosteal mask.

    Returns
    -------
    float
        Bone volume fraction value.
    """
    
    bvtv = (trab_seg_np > 0).sum() / (peri_mask_np > 0).sum()
    print(f"BV/TV = {bvtv}")

    return bvtv

def trabecular_thickness(trab_seg_np, spacing, image):
    """
    Compute trabecular thickness statistics.

    Parameters
    ----------
    trab_seg_np : numpy.ndarray
        Binary segmentation of trabecular bone.
    spacing : tuple
        Image spacing.
    image : SimpleITK.Image
        Original input image (for metadata).

    Returns
    -------
    SimpleITK.Image
        Image of local thickness.
    tuple
        Thickness statistics (mean, std, min, max, thickness_map).
    """
    
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
    """
    Compute trabecular separation statistics.

    Parameters
    ----------
    trab_seg : SimpleITK.Image
        Binary image of trabecular segmentation.
    peri_mask : SimpleITK.Image
        Binary image of periosteal mask.
    spacing : tuple
        Image spacing.
    image : SimpleITK.Image
        Original input image (for metadata).

    Returns
    -------
    SimpleITK.Image
        Image of local separation.
    tuple
        Separation statistics.
    """
    
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
    """
    Estimate trabecular number from skeletonized thickness statistics.

    Parameters
    ----------
    trab_seg_np : numpy.ndarray
        Binary trabecular mask.
    spacing : tuple
        Image spacing.
    image : SimpleITK.Image
        Original input image (for metadata).

    Returns
    -------
    SimpleITK.Image
        Image of local spacing used to compute Tb.N.
    tuple
        Skeleton-based thickness statistics.
    """
    
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
    """
    Compute the total bone cross-sectional area.

    Parameters
    ----------
    peri_mask_np : numpy.ndarray
        Binary array of periosteal segmentation.
    spacing : tuple
        Pixel spacing in mm.

    Returns
    -------
    float
        Total bone area in mm^2.
    """
    
    pixel_area = spacing[0] * spacing[1]
    
    total_area = (peri_mask_np > 0).sum() * pixel_area
    print(f"Total Bone Area = {total_area} mm^2")
    return total_area

def bone_mineral_density(image, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept):
    """
    Compute bone mineral density (BMD) from the intensity information of the
    provided image. The image units need to be provided to convert voxels to
    BMD units (mg HA/ccm) before calculating BMD.

    Parameters
    ----------
    image_array : numpy array

    image_units : string

    mu_scaling : int

    mu_water : float

    rescale_slope : float

    rescale_intercept : float

    Returns
    -------
    image_statistics_filter : SimpleITK.StatisticsImageFilter
    """
    
    mean, std = 0, 0
    # Now convert to BMD units if needed
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
    mean = numpy_image.mean()
    std = numpy_image.std()
    print(f"mean bone mineral density is {mean} +/- {std}")

    return mean, std

# Might combine with bone mineral density
def bone_mineral_density_mask(image, mask, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept):
    """
    Calculates Bone Mineral Density (BMD) of an image in mgHA/ccm after masking
    with the input segmentation mask. The user must specify what the input
    image's units are (e.g., HU, Scanco native, linear attenuation).

    Parameters
    ----------
    image : SimpleITK.Image

    mask  : SimpleITK.Image

    image_units : string

    mu_scaling : int

    mu_water : float

    rescale_slope : float

    rescale_intercept : float

    Returns
    -------
    list
        A list containing the mean and std BMD
    """
    
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

    print(f"mean bone mineral density mask is {mean} +/- {std}")
    
    return mean, std


# Currently bmd uses simpleITK and bmd mask uses numpy 
# Create a way to ensure they both use the same method
# Might just call external file?
# def bone_mineral_density(image_array, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept):
    # """
    #     Compute bone mineral density (BMD) from the intensity information of the
    #     provided image. The image units need to be provided to convert voxels to
    #     BMD units (mg HA/ccm) before calculating BMD.

    #     Parameters
    #     ----------
    #     image_array : numpy array

    #     image_units : string

    #     mu_scaling : int

    #     mu_water : float

    #     rescale_slope : float

    #     rescale_intercept : float

    #     Returns
    #     -------
    #     image_statistics_filter : SimpleITK.StatisticsImageFilter
    #     """
#     image_statistics_filter = sitk.StatisticsImageFilter()

#     # Now convert to BMD units if needed
#     if image_units == "bmd":
#         # No conversion needed
#         image = sitk.GetImageFromArray(image_array)
#         image_statistics_filter.Execute(image)
#     elif image_units == "scanco":
#         # Convert from Scanco native units to linear attenuation
#         # Then convert to BMD
#         image_array = convert_scanco_to_bmd(
#             image_array, mu_scaling, rescale_slope, rescale_intercept
#         )
#         image = sitk.GetImageFromArray(image_array)
#         image_statistics_filter.Execute(image)
#     elif image_units == "attenuation":
#         # Convert to BMD
#         image_array = convert_linear_attenuation_to_bmd(
#             image_array, rescale_slope, rescale_intercept
#         )
#         image = sitk.GetImageFromArray(image_array)
#         image_statistics_filter.Execute(image)
#     elif image_units == "hu":
#         # Convert from HU to linear attenuation
#         # Then convert to BMD
#         image_array = convert_hu_to_bmd(
#             image_array, mu_water, rescale_slope, rescale_intercept
#         )
#         image = sitk.GetImageFromArray(image_array)
#         image_statistics_filter.Execute(image)
#     else:
#         print(
#             "ERROR: Invalid image units provided. Only BMD, SCANCO, ATTENUATION, or HU are accepted."
#         )
#         sys.exit(1)

#     mean = image_statistics_filter.GetMean()
#     std = image_statistics_filter.GetSigma()
#     print(f"mean bone mineral density is {mean} +/- {std}")

#     return mean, std

# Might combine with bone mineral density
# def bone_mineral_density_mask(image, mask, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept):
    # """
    # Calculates Bone Mineral Density (BMD) of an image in mgHA/ccm after masking
    # with the input segmentation mask. The user must specify what the input
    # image's units are (e.g., HU, Scanco native, linear attenuation).

    # Parameters
    # ----------
    # image : SimpleITK.Image

    # mask  : SimpleITK.Image

    # image_units : string

    # mu_scaling : int

    # mu_water : float

    # rescale_slope : float

    # rescale_intercept : float

    # Returns
    # -------
    # list
    #     A list containing the mean and std BMD
    # """
#     mean, std = 0, 0
#     image_statistics_filter = sitk.StatisticsImageFilter()
    
#     # No conversion needed if we already have BMD units
#     if image_units == "scanco":
#         # Convert from Scanco native units to linear attenuation. Then convert to BMD.
#         # Convert both the image and background value.
#         image = convert_scanco_to_bmd(
#             image, mu_scaling, rescale_slope, rescale_intercept
#         )
#         image_statistics_filter.Execute(image)
#     elif image_units == "attenuation":
#         # Convert to BMD.
#         # Convert both the image and background value.
#         image = convert_linear_attenuation_to_bmd(
#             image, rescale_slope, rescale_intercept
#         )
#         image_statistics_filter.Execute(image)
#     elif image_units == "hu":
#         # Convert from HU to linear attenuation. Then convert to BMD.
#         # Convert both the image and background value.
#         image = convert_hu_to_bmd(image, mu_water, rescale_slope, rescale_intercept)
#         image_statistics_filter.Execute(image)
#     elif image_units != "bmd":
#         print(
#             "ERROR: Invalid image units provided. Only BMD, SCANCO, ATTENUATION, or HU are accepted."
#         )
#         sys.exit(1)

#     mean = image_statistics_filter.GetMean()
#     std = image_statistics_filter.GetSigma()

#     print(f"mean bone mineral density mask is {mean} +/- {std}")
    
#     return mean, std