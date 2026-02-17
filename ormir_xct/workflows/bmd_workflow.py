import argparse
import SimpleITK as sitk

# file_reader?
from ormir_xct.microarchitecture.bone_mineral_density.bmd import bmd, file_reader

def main():
    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=str, help="The input imagek (path + filename)")
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
        help="Linear attenuation of water",
    )
    parser.add_argument(
        "rescale_slope",
        type=float,
        nargs="?",
        default="1600.0",
        help="Slope to scale to BMD",
    )
    parser.add_argument(
        "rescale_intercept",
        type=float,
        nargs="?",
        default="-390.0",
        help="Intercept to scale to BMD",
    )
    args = parser.parse_args()

    image_path = args.image
    image_units = (args.image_units).lower()
    mu_scaling = args.mu_scaling
    mu_water = args.mu_water
    rescale_slope = args.rescale_slope
    rescale_intercept = args.rescale_intercept

    image = file_reader(image_path)

    # Get the image stats
    stats = bmd(
        image, image_units, mu_scaling, mu_water, rescale_slope, rescale_intercept
    )
    print(stats)


if __name__ == "__main__":
    main()
