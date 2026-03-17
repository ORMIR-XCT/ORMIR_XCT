import argparse
import SimpleITK as sitk

from ormir_xct.core.microarchitecture.trabecular_microarchitecture import (
    trabecular_bone_volume_fraction,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trab-bvtv",
        description="Compute trabecular bone volume fraction (Tb.BV/TV).",
    )
    parser.add_argument(
        "input_image",
        type=str,
        help="Path to the trabecular segmentation image",
    )
    parser.add_argument(
        "peri_mask",
        type=str,
        help="Path to the periosteal mask image",
    )

    return parser


def run(
    input_image: str,
    peri_mask: str,
) -> int:

    trab_seg = sitk.ReadImage(input_image, sitk.sitkUInt8)
    peri_mask_img = sitk.ReadImage(peri_mask, sitk.sitkUInt8)

    bvtv = trabecular_bone_volume_fraction(trab_seg, peri_mask_img)

    print(f"Tb.BV/TV: {bvtv:.4f}")

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return run(
            input_image=args.input_image,
            peri_mask=args.peri_mask,
        )
    except Exception as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
