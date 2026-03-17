import argparse
import csv
import SimpleITK as sitk

from ormir_xct.core.microarchitecture.trabecular_microarchitecture import (
    trabecular_microarchitecture,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trab-microarch",
        description="Compute trabecular microarchitecture parameters.",
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
        "output_csv",
        type=str,
        help="Path to the output CSV file",
    )
    parser.add_argument(
        "output_tbth",
        type=str,
        help="Path to the output Tb.Th image",
    )
    parser.add_argument(
        "output_tbsp",
        type=str,
        help="Path to the output Tb.Sp image",
    )

    return parser


def run(
    input_image: str,
    peri_mask: str,
    output_csv: str,
    output_tbth: str,
    output_tbsp: str,
) -> int:

    trab_seg = sitk.ReadImage(input_image, sitk.sitkUInt8)
    peri_mask_img = sitk.ReadImage(peri_mask, sitk.sitkUInt8)

    tb_microarch, tbth_map, tbsp_map = trabecular_microarchitecture(
        trab_seg, peri_mask_img
    )

    print("Trabecular microarchitecture parameters:")

    for key, value in tb_microarch.items():
        print(f"{key}: {value:.6f}")

    print(f"Writing metrics to {output_csv}")

    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Parameter", "Value"])

        for key, value in tb_microarch.items():
            writer.writerow([key, value])

    print(f"Writing Tb.Th map to {output_tbth}")
    sitk.WriteImage(tbth_map, output_tbth)

    print(f"Writing Tb.Sp map to {output_tbsp}")
    sitk.WriteImage(tbsp_map, output_tbsp)

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return run(
            input_image=args.input_image,
            peri_mask=args.peri_mask,
            output_csv=args.output_csv,
            output_tbth=args.output_tbth,
            output_tbsp=args.output_tbsp,
        )
    except Exception as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
