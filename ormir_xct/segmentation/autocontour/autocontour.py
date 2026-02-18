import os
import argparse
import SimpleITK as sitk

from ormir_xct.segmentation.autocontour.AutocontourKnee import AutocontourKnee
from ormir_xct.util.scanco_rescale import convert_hu_to_bmd


def autocontour(
    img, mu_water=0.2409, rescale_slope=1603.51904, rescale_intercept=-391.209015
):
    # Mu_Water, Rescale_Slope, and Rescale_Intercept are hard coded
    # To-Do: get directly from the image, if possible, or from the user
    img = convert_hu_to_bmd(img, mu_water, rescale_slope, rescale_intercept)

    auto_contour = AutocontourKnee()
    prx_mask = auto_contour.get_periosteal_mask(img, 1)
    dst_mask = auto_contour.get_periosteal_mask(img, 2)

    # Create a mask for the entire joint
    mask = prx_mask + dst_mask

    return dst_mask, prx_mask, mask

