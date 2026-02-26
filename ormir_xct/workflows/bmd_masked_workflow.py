import argparse
import SimpleITK as sitk

from ormir_xct.microarchitecture.bone_mineral_density.bmd_masked import bmd_masked
from ormir_xct.util.file_reader import verify_image


def bmd_masked_workflow():
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
        default=8192,
        help="The Scanco defined scaling value (usually 8192 or 4096)",
    )
    parser.add_argument(
        "mu_water",
        type=float,
        nargs="?",
        default=0.25,
        help="Linear attenuation of water (default = 0.25)",
    )
    parser.add_argument(
        "rescale_slope",
        type=float,
        nargs="?",
        default=1600.0,
        help="Slope to scale to BMD (default = 1600.0)",
    )
    parser.add_argument(
        "rescale_intercept",
        type=float,
        nargs="?",
        default=-390.0,
        help="Intercept to scale to BMD (default = -390.0)",
    )
    args = parser.parse_args()

    image = verify_image(args.image)
    mask = sitk.ReadImage(args.image_seg)

    mean, std = bmd_masked(
        image,
        mask,
        args.image_units.lower(),
        args.mu_scaling,
        args.mu_water,
        args.rescale_slope,
        args.rescale_intercept,
    )

    print("BMD Statistics:")
    print(f"mean: {mean}")
    print(f"std: {std}")


if __name__ == "__main__":
    bmd_masked_workflow()


