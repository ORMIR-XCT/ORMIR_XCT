import argparse
import SimpleITK as sitk

from ormir_xct.core.microarchitecture.trabecular_microarchitecture import (
    trabecular_separation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trab-tbsp",
        description="Compute trabecular separation (Tb.Sp).",
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
    parser.add_argument(
        "output_image",
        type=str,
        help="Path to the output Tb.Sp image",
    )

    return parser


def run(
    input_image: str,
    peri_mask: str,
    output_image: str,
) -> int:

    trab_seg = sitk.ReadImage(input_image, sitk.sitkUInt8)
    peri_mask_img = sitk.ReadImage(peri_mask, sitk.sitkUInt8)

    tbsp_results = trabecular_separation(trab_seg, peri_mask_img)
    tbsp_map = tbsp_results[4]

    print(f"Mean Tb.Sp: {tbsp_results[0]:.6f}")
    print(f"StDev Tb.Sp: {tbsp_results[1]:.6f}")
    print(f"Min Tb.Sp: {tbsp_results[2]:.6f}")
    print(f"Max Tb.Sp: {tbsp_results[3]:.6f}")

    print(f"Writing Tb.Sp map to {output_image}")
    sitk.WriteImage(tbsp_map, output_image)

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return run(
            input_image=args.input_image,
            peri_mask=args.peri_mask,
            output_image=args.output_image,
        )
    except Exception as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
