"""
Use this script instead of the autocontour.py script if the bones are
too close to distinguish between distal and proximal. You will need to 
provide the distal and proximal GOBJ masks (as NIFTI or similar) to mask
out the bone of interest.
"""

import os
import argparse
import SimpleITK as sitk

from ormir_xct.segmentation.autocontour.AutocontourKnee import AutocontourKnee
from ormir_xct.util.scanco_rescale import convert_hu_to_bmd


# We may wish to move this to a shared module within the autocontour package so autocontour.py can access it
def _ensure_image(img, precision=None):
    """
    Helper function to ensure string paths are converted to sitk.Image before processing
    
    :param img: Either a string path to an sitk readable image or an sitk.Image
    :param precision: Provide read type for added precision
    """

    if isinstance(img, str):
        return sitk.ReadImage(img, precision) if precision else sitk.ReadImage(img)
    else:
        return sitk.Cast(img, precision) if precision else img

def autocontour_gobj(img, dst_gobj, prx_gobj):
    """
    Script for calculating periosteal masks using distal and proximal GOBJ masks. 
    A variant of autocontour for when bones are too close to distinguish between distal and proximal.
    
    :param img: str path to or image of bones
    :param dst_gobj: str path to or image of distal mask
    :param prx_gobj: str path to or image of proximal mask
    """
    
    # Read in images as floats to increase precision
    img = _ensure_image(img, sitk.sitkFloat32)
    dst_gobj = _ensure_image(dst_gobj)
    prx_gobj = _ensure_image(prx_gobj)

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



def main():
    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", type=str, help="Image (path + filename)")
    parser.add_argument(
        "dst_gobj_path",
        type=str,
        help="Distal contour from UCT_EVALUATION (path + filename)",
    )
    parser.add_argument(
        "prx_gobj_path",
        type=str,
        help="Proximal contour from UCT_EVALUATION (path + filename)",
    )
    args = parser.parse_args()

    image_path = args.image_path
    dst_gobj_path = args.dst_gobj_path
    prx_gobj_path = args.prx_gobj_path

    # Create a new folder to hold the output images
    image_dir = os.path.dirname(image_path)
    basename = os.path.splitext(os.path.basename(image_path))[0]

    prx_mask_path = os.path.join(image_dir, basename + "_PRX_MASK.nii")
    dst_mask_path = os.path.join(image_dir, basename + "_DST_MASK.nii")
    mask_path = os.path.join(image_dir, basename + "_MASK.nii")

    dst_mask, prx_mask, mask = autocontour_gobj(image_path, dst_gobj_path, prx_gobj_path)
    
    sitk.WriteImage(dst_mask, dst_mask_path)
    sitk.WriteImage(prx_mask, prx_mask_path)
    sitk.WriteImage(mask, mask_path)
    


if __name__ == "__main__":
    main()
