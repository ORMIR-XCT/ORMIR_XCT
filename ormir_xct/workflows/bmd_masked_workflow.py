import argparse
import SimpleITK as sitk

from ormir_xct.microarchitecture.bone_mineral_density.bmd_masked import bmd_masked
from ormir_xct.util.file_reader import file_reader


def main():
    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=str, help="The input image (path + filename)")
    parser.add_argument(
        "image_seg", type=str, help="The input image mask (path + filename)"
    )
    parser.add_argument(
        "image_units",
        type=str,
        nargs="?",
        default="BMD",
        help="The image voxel units (options: BMD, SCANCO, ATTENUATION, HU)",
    )
    parser.add_argument(
        "mu_scaling",
        type=int,
        nargs="?",
        default="8192",
        help="The Scanco defined scaling value (usually 8192 or 4096)",
    )
    parser.add_argument(
        "mu_water",
        type=float,
        nargs="?",
        default="0.25",
        help="Linear attenuation of water (default = 0.25)",
    )
    parser.add_argument(
        "rescale_slope",
        type=float,
        nargs="?",
        default="1600.0",
        help="Slope to scale to BMD (default = 1600.0)",
    )
    parser.add_argument(
        "rescale_intercept",
        type=float,
        nargs="?",
        default="-390.0",
        help="Intercept to scale to BMD (default = -390.0)",
    )
    args = parser.parse_args()

    image_path = args.image
    image_mask_path = args.image_seg
    image_units = (args.image_units).lower()
    mu_scaling = args.mu_scaling
    mu_water = args.mu_water
    rescale_slope = args.rescale_slope
    rescale_intercept = args.rescale_intercept

    image = file_reader(image_path)
    mask = sitk.ReadImage(image_mask_path)

    mean, std = bmd_masked(
        image,
        mask,
        image_units,
        mu_scaling,
        mu_water,
        rescale_slope,
        rescale_intercept,
    )
    print(mean)
    print(std)


if __name__ == "__main__":
    main()


