"""
seg_gauss.py

Created by:   Michael Kuczynski
Created on:   June 29, 2022

Description: Binarize an input image following the standard
              segmentation protocol performed in IPL. 

Notes:
  1. Gaussian smoothing is done in IPL with sigma = 0.5
      and support = 1 (for example). In ITK, this translates 
      to using the SmoothingRecursiveGaussian filter with
      sigma = 0.5 * voxel size = 0.5 * 0.0606964.
  2. The output of the Guassian filter will be a float
      image so we may need to cast to a different type
      depending on what image you want to write to.
  3. The binarization is done using the same thresholds
      set in IPL, but we need to know the image units
      prior to binarization (default is set to BMD units).
"""

import SimpleITK as sitk

from ormir_xct.core.util.file_reader import verify_image

# Default threshold values used in IPL
thresholds = {
    "HU_Lower": 1170.0,
    "HU_Upper": 10000.0,
    "BMD_Lower": 446.8,
    "BMD_Upper": 3000.0,
    "Native_Lower": 4259.0,
    "Native_Upper": 32767.0,
    "LinAtt_Lower": 0.52,
    "LinAtt_Upper": 4.00,
    "Per1000_Lower": 130.0,
    "Per1000_Upper": 1000.0,
}

threshold_dict = { 
    "bmd": (thresholds["BMD_Lower"], thresholds["BMD_Upper"]),
    "scanco": (thresholds["Native_Lower"], thresholds["Native_Upper"]),
    "attenuation": (thresholds["LinAtt_Lower"], thresholds["LinAtt_Upper"]),
    "hu": (thresholds["HU_Lower"], thresholds["HU_Upper"]),
    "per1000": (thresholds["Per1000_Lower"], thresholds["Per1000_Upper"])
}


def seg_gauss(
    input_image,
    lower_threshold,
    upper_threshold,
    value_in_range=127,
    value_outside_range=0,
    sigma=0.5,
    support=1,
    use_image_spacing=False
):
    """
    Perform Gaussian smoothing with an explicit kernel support and then
    binary threshold the smoothed image.

    Parameters
    ----------
    input_image : SimpleITK.Image or str
        Input image or path to input image.

    lower_threshold : float
        Lower threshold for binarization.

    upper_threshold : float
        Upper threshold for binarization.

    value_in_range : int, optional
        Output value assigned to voxels inside the threshold range.

    value_outside_range : int, optional
        Output value assigned to voxels outside the threshold range.

    sigma : float, optional
        Gaussian sigma. If use_image_spacing=False, interpreted in voxels.
        If use_image_spacing=True, interpreted in physical units.

    support : int, optional
        Half-width of the Gaussian kernel in voxels. The total kernel width
        used by SimpleITK is 2 * support + 1.

    use_image_spacing : bool, optional
        Whether sigma is interpreted in physical units using the image spacing.

    Returns
    -------
    seg : SimpleITK.Image
        Thresholded segmentation image.
    """

    # Handle string paths
    input_image = verify_image(input_image)

    if sigma <= 0:
        raise ValueError("sigma must be > 0")

    if support < 0:
        raise ValueError("support must be >= 0")

    maximum_kernel_width = 2 * int(support) + 1

    variance = float(sigma) ** 2

    smooth = sitk.DiscreteGaussian(
        input_image,
        variance=variance,
        maximumKernelWidth=maximum_kernel_width,
        useImageSpacing=use_image_spacing,
    )

    seg = sitk.BinaryThreshold(
        smooth,
        lowerThreshold=lower_threshold,
        upperThreshold=upper_threshold,
        insideValue=value_in_range,
        outsideValue=value_outside_range,
    )
    return seg


