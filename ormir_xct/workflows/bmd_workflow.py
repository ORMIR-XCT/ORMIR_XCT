import argparse
import SimpleITK as sitk

# file_reader?
from ormir_xct.microarchitecture.bone_mineral_density.bmd import bmd
from ormir_xct.util.file_reader import verify_image

def bmd_workflow():
    # Parse input arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("image", type=str, help="The input image (path + filename)")
    parser.add_argument(
        "--image_units",
        type=str,
        nargs="?",
        default="BMD",
        help="The image voxel units (options: BMD, SCANCO, ATTENUATION, HU)",
    )
    parser.add_argument(
        "--mu_scaling",
        type=int,
        nargs="?",
        default=8192,
        help="The Scanco defined scaling value (usually 8192 or 4096)",
    )
    parser.add_argument(
        "--mu_water",
        type=float,
        nargs="?",
        default=0.25,
        help="Linear attenuation of water",
    )
    parser.add_argument(
        "--rescale_slope",
        type=float,
        nargs="?",
        default=1600.0,
        help="Slope to scale to BMD",
    )
    parser.add_argument(
        "--rescale_intercept",
        type=float,
        nargs="?",
        default=-390.0,
        help="Intercept to scale to BMD",
    )

    args = parser.parse_args()

    image = verify_image(args.image)

    # Get the image stats
    mean, std = bmd(
        image, args.image_units, args.mu_scaling, args.mu_water, args.rescale_slope, args.rescale_intercept
    )

    print("BMD Statistics:")
    print(f"mean: {mean}")
    print(f"std: {std}")


if __name__ == "__main__":
    bmd_workflow()
