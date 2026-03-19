import argparse

from ormir_xct.core.microarchitecture.bmd import bmd
from ormir_xct.core.util.file_reader import verify_image


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bmd",
        description="Compute bone mineral density statistics from an input image.",
    )
    parser.add_argument("image", type=str, help="Path to the input image")
    parser.add_argument(
        "--image-units",
        type=str,
        default="BMD",
        help="Image voxel units: BMD, SCANCO, ATTENUATION, or HU",
    )
    parser.add_argument(
        "--mu-scaling",
        type=int,
        default=8192,
        help="Scanco scaling value (usually 8192 or 4096)",
    )
    parser.add_argument(
        "--mu-water",
        type=float,
        default=0.25,
        help="Linear attenuation of water (default: 0.25)",
    )
    parser.add_argument(
        "--rescale-slope",
        type=float,
        default=1600.0,
        help="Slope used to rescale to BMD (default: 1600.0)",
    )
    parser.add_argument(
        "--rescale-intercept",
        type=float,
        default=-390.0,
        help="Intercept used to rescale to BMD (default: -390.0)",
    )
    return parser


def run(
    image: str,
    image_units: str = "BMD",
    mu_scaling: int = 8192,
    mu_water: float = 0.25,
    rescale_slope: float = 1600.0,
    rescale_intercept: float = -390.0,
) -> int:
    input_image = verify_image(image)

    mean, std = bmd(
        input_image,
        image_units.lower(),
        mu_scaling,
        mu_water,
        rescale_slope,
        rescale_intercept,
    )

    print("BMD Statistics:")
    print(f"mean: {mean}")
    print(f"std: {std}")

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return run(
            image=args.image,
            image_units=args.image_units,
            mu_scaling=args.mu_scaling,
            mu_water=args.mu_water,
            rescale_slope=args.rescale_slope,
            rescale_intercept=args.rescale_intercept,
        )
    except Exception as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
