import os
import argparse
import SimpleITK as sitk

from ormir_xct.core.segmentation.autocontour import autocontour


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autocontour",
        description="Generate proximal, distal, and combined masks using the autocontour workflow.",
    )
    parser.add_argument("image_path", type=str, help="Path to the input image")
    parser.add_argument(
        "--mu-water",
        type=float,
        default=0.2409,
        help="Linear attenuation of water (default: 0.2409)",
    )
    parser.add_argument(
        "--rescale-slope",
        type=float,
        default=1603.51904,
        help="Slope used to rescale to BMD (default: 1603.51904)",
    )
    parser.add_argument(
        "--rescale-intercept",
        type=float,
        default=-391.209015,
        help="Intercept used to rescale to BMD (default: -391.209015)",
    )
    return parser


def run(
    image_path: str,
    mu_water: float = 0.2409,
    rescale_slope: float = 1603.51904,
    rescale_intercept: float = -391.209015,
) -> int:
    image_dir = os.path.dirname(image_path)
    basename = os.path.splitext(os.path.basename(image_path))[0]

    prx_mask_path = os.path.join(image_dir, f"{basename}_PRX_MASK.nii")
    dst_mask_path = os.path.join(image_dir, f"{basename}_DST_MASK.nii")
    mask_path = os.path.join(image_dir, f"{basename}_MASK.nii")

    image = sitk.ReadImage(image_path, sitk.sitkFloat32)

    dst_mask, prx_mask, mask = autocontour(
        image,
        mu_water,
        rescale_slope,
        rescale_intercept,
    )

    print(f"Writing mask to {mask_path}")
    sitk.WriteImage(mask, mask_path)

    print(f"Writing proximal mask to {prx_mask_path}")
    sitk.WriteImage(prx_mask, prx_mask_path)

    print(f"Writing distal mask to {dst_mask_path}")
    sitk.WriteImage(dst_mask, dst_mask_path)

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return run(
            image_path=args.image_path,
            mu_water=args.mu_water,
            rescale_slope=args.rescale_slope,
            rescale_intercept=args.rescale_intercept,
        )
    except Exception as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
