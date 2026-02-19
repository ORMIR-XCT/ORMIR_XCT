import argparse
import os

import SimpleITK as sitk

from ormir_xct.segmentation.autocontour import autocontour


def main():
    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", type=str, help="Image (path + filename)")
    parser.add_argument(
        "mu_water",
        type=float,
        nargs="?",
        default="0.2409",
        help="Linear attenuation of water (default = 0.2409)",
    )
    parser.add_argument(
        "rescale_slope",
        type=float,
        nargs="?",
        default="1603.51904",
        help="Slope to scale to BMD (default = 1603.51904)",
    )
    parser.add_argument(
        "rescale_intercept",
        type=float,
        nargs="?",
        default="-391.209015",
        help="Intercept to scale to BMD (default = -391.209015)",
    )
    args = parser.parse_args()

    image_path = args.image_path
    mu_water = args.mu_water
    rescale_slope = args.rescale_slope
    rescale_intercept = args.rescale_intercept

    # Create a new folder to hold the output images
    image_dir = os.path.dirname(image_path)
    basename = os.path.splitext(os.path.basename(image_path))[0]

    prx_mask_path = os.path.join(image_dir, basename + "_PRX_MASK.nii")
    dst_mask_path = os.path.join(image_dir, basename + "_DST_MASK.nii")
    mask_path = os.path.join(image_dir, basename + "_MASK.nii")

    # Read in images as floats to increase precision
    image = sitk.ReadImage(image_path, sitk.sitkFloat32)

    # Run the autocontour method for each bone
    dst_mask, prx_mask, mask = autocontour(image, 
                                           mu_water,
                                           rescale_slope,
                                           rescale_intercept
                                           )

    print(f"Writing mask to {mask_path}")
    sitk.WriteImage(mask, mask_path)

    print(f"Writing proximal mask to {prx_mask_path}")
    sitk.WriteImage(prx_mask, prx_mask_path)

    print(f"Writing distal mask to {dst_mask_path}")
    sitk.WriteImage(dst_mask, dst_mask_path)


if __name__ == "__main__":
    main()
