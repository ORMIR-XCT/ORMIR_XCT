import argparse
import SimpleITK as sitk

from ormir_xct.core.microarchitecture.trabecular_microarchitecture import (
    trabecular_thickness,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trab-tbth",
        description="Compute trabecular thickness (Tb.Th).",
    )
    parser.add_argument(
        "input_image",
        type=str,
        help="Path to the trabecular segmentation image",
    )
    parser.add_argument(
        "output_image",
        type=str,
        help="Path to the output Tb.Th image",
    )

    return parser


def run(
    input_image: str,
    output_image: str,
) -> int:

    trab_seg = sitk.ReadImage(input_image, sitk.sitkUInt8)

    tbth_results = trabecular_thickness(trab_seg)
    tbth_map = tbth_results[4]

    print(f"Mean Tb.Th: {tbth_results[0]:.6f}")
    print(f"StDev Tb.Th: {tbth_results[1]:.6f}")
    print(f"Min Tb.Th: {tbth_results[2]:.6f}")
    print(f"Max Tb.Th: {tbth_results[3]:.6f}")

    print(f"Writing Tb.Th map to {output_image}")
    sitk.WriteImage(tbth_map, output_image)

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return run(
            input_image=args.input_image,
            output_image=args.output_image,
        )
    except Exception as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
