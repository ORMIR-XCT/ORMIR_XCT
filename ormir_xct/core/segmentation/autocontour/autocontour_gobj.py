"""
Use this script instead of the autocontour.py script if the bones are
too close to distinguish between distal and proximal. You will need to
provide the distal and proximal GOBJ masks (as NIFTI or similar) to mask
out the bone of interest.
"""

import SimpleITK as sitk

from ormir_xct.core.util.file_reader import verify_image
from ormir_xct.core.util.hrpqct_rescale import convert_hu_to_bmd
from ormir_xct.core.segmentation.autocontour.AutocontourKnee import AutocontourKnee


def autocontour_gobj(img, dst_gobj, prx_gobj):
    """Script for calculating periosteal masks using distal and proximal GOBJ masks.
    A variant of autocontour for when bones are too close to distinguish between distal and proximal.

    Parameters
    ----------
    - img : str or sitk.Image
        str path or sitk image of bones

    - dst_gobj: str or sitk.Image
        str path or sitk image of distal mask

    - prx_gobj: satr or sitk.Image
        str path or sitk image of proximal mask

    Returns
    ----------
    - return_values : tuple
        contains sitk images of dst_mask, prx_mask, mask
    """

    # Read in images as floats to increase precision
    img = verify_image(img, sitk.sitkFloat32)
    dst_gobj = verify_image(dst_gobj)
    prx_gobj = verify_image(prx_gobj)

    # Mu_Water, Rescale_Slope, and Rescale_Intercept are hard coded
    # To-Do: get directly from the image, if possible, or from the user
    image_bmd = convert_hu_to_bmd(img, 0.2409, 1603.51904, -391.209015)

    dst_gobj = sitk.Resample(dst_gobj, image_bmd, interpolator=sitk.sitkNearestNeighbor)
    prx_gobj = sitk.Resample(prx_gobj, image_bmd, interpolator=sitk.sitkNearestNeighbor)

    dst_masked_image = sitk.Mask(image_bmd, dst_gobj)
    prx_masked_image = sitk.Mask(image_bmd, prx_gobj)

    # Run the autocontour method for each bone
    auto_contour = AutocontourKnee()
    prx_mask = auto_contour.get_periosteal_mask(dst_masked_image, 1)
    dst_mask = auto_contour.get_periosteal_mask(prx_masked_image, 1)

    # If the masks overlap, subtract one from the other to remove the overlap
    # The choice of which mask is subtracted from which is arbitrary
    combined = prx_mask & dst_mask
    combined_array = sitk.GetArrayFromImage(combined)

    if combined_array.nonzero()[0].size != 0:
        dst_mask = (dst_mask - prx_mask) & dst_mask

    # Create a mask for the entire joint
    mask = prx_mask + dst_mask

    return dst_mask, prx_mask, mask
