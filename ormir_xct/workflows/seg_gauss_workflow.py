import argparse
import SimpleITK as sitk

from ormir_xct.core.segmentation.seg_gauss import seg_gauss, threshold_dict


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gauss-seg",
        description=(
            "Binarize an input image using Gaussian smoothing followed by "
            "thresholding. Thresholds can be selected automatically based "
            "on image units or manually specified."
        ),
    )
    parser.add_argument("input_image", type=str, help="Path to the input image")
    parser.add_argument("output_image", type=str, help="Path to the output image")
    parser.add_argument(
        "--image-units",
        type=str,
        default="BMD",
        help="Image voxel units: BMD, SCANCO, ATTENUATION, HU, or PER1000",
    )
    parser.add_argument(
        "--lower",
        type=float,
        help="Lower threshold (overrides image-units preset)",
    )
    parser.add_argument(
        "--upper",
        type=float,
        help="Upper threshold (overrides image-units preset)",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=0.5,
        help="Gaussian sigma",
    )
    parser.add_argument(
        "--support",
        type=int,
        default=1,
        help="Gaussian kernel support in voxels",
    )
    parser.add_argument(
        "--inside-value",
        type=int,
        default=127,
        help="Output value for voxels inside the threshold range",
    )
    parser.add_argument(
        "--outside-value",
        type=int,
        default=0,
        help="Output value for voxels outside the threshold range",
    )
    parser.add_argument(
        "--use-image-spacing",
        action="store_true",
        help="Interpret sigma in physical units using image spacing",
    )

    return parser


def run(
    input_image: str,
    output_image: str,
    image_units: str = "BMD",
    lower: float | None = None,
    upper: float | None = None,
    sigma: float = 0.5,
    support: int = 1,
    inside_value: int = 127,
    outside_value: int = 0,
    use_image_spacing: bool = False,
) -> int:

    # Determine thresholds
    if lower is not None or upper is not None:

        if lower is None or upper is None:
            raise ValueError("Both --lower and --upper must be provided together.")

        lower_threshold = lower
        upper_threshold = upper

    else:
        image_units = image_units.lower()

        if image_units not in threshold_dict:
            valid_units = ", ".join(sorted(threshold_dict.keys()))
            raise ValueError(
                f"Invalid image units '{image_units}'. Valid options are: {valid_units}."
            )

        lower_threshold, upper_threshold = threshold_dict[image_units]

    input_img = sitk.ReadImage(input_image, sitk.sitkFloat32)

    seg = seg_gauss(
        input_image=input_img,
        lower_threshold=lower_threshold,
        upper_threshold=upper_threshold,
        value_in_range=inside_value,
        value_outside_range=outside_value,
        sigma=sigma,
        support=support,
        use_image_spacing=use_image_spacing,
    )

    print(f"Writing segmentation to {output_image}")
    sitk.WriteImage(seg, output_image)

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return run(
            input_image=args.input_image,
            output_image=args.output_image,
            image_units=args.image_units,
            lower=args.lower,
            upper=args.upper,
            sigma=args.sigma,
            support=args.support,
            inside_value=args.inside_value,
            outside_value=args.outside_value,
            use_image_spacing=args.use_image_spacing,
        )
    except Exception as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
