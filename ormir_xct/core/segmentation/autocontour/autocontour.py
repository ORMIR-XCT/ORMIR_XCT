import SimpleITK as sitk

from ormir_xct.core.util.file_reader import verify_image
from ormir_xct.core.util.hrpqct_rescale import convert_hu_to_bmd
from ormir_xct.core.segmentation.autocontour.AutocontourKnee import AutocontourKnee


def autocontour(
    img, mu_water=0.2409, rescale_slope=1603.51904, rescale_intercept=-391.209015
):
    """Script for calculating periosteal masks using the autocontour workflow

    Parameters
    ----------
    - img : str
        str path or sitk image of bones

    Returns
    ----------
    - return_values  : tuple
        sitk images of dst_mask, prx_mask, mask
    """

    img = verify_image(img, sitk.sitkFloat32)

    # Mu_Water, Rescale_Slope, and Rescale_Intercept are hard coded
    # To-Do: get directly from the image, if possible, or from the user
    img = convert_hu_to_bmd(img, mu_water, rescale_slope, rescale_intercept)

    auto_contour = AutocontourKnee()
    prx_mask = auto_contour.get_periosteal_mask(img, 1)
    dst_mask = auto_contour.get_periosteal_mask(img, 2)

    # Create a mask for the entire joint
    mask = prx_mask + dst_mask

    return dst_mask, prx_mask, mask
