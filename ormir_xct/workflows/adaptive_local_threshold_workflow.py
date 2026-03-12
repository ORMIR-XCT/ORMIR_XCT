import argparse
import SimpleITK as sitk

from ormir_xct.core.segmentation.adaptive_local_threshold import (
    adaptive_local_thresholding,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="local-adaptive-threshold",
        description=(
            "Perform adaptive local thresholding on an image to segment bone. "
            "Provide an input image and lower and upper thresholds to create a "
            "bone segmentation. Optionally specify the size and shape of the "
            "structuring element used for identifying local thresholds, the "
            "minimum structure size to keep in the segmentation, and the method "
            "used to compute local thresholds."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", type=str, help="Input image filename to segment")
    parser.add_argument("output", type=str, help="Output image filename")
    parser.add_argument(
        "--lower-threshold",
        "-lt",
        type=float,
        default=190,
        help="Lower threshold for bone segmentation",
    )
    parser.add_argument(
        "--upper-threshold",
        "-ut",
        type=float,
        default=450,
        help="Upper threshold for bone segmentation",
    )
    parser.add_argument(
        "--structuring-element-size",
        "-sz",
        type=int,
        default=6,
        help=(
            "Size of the structuring element used for identifying local "
            "thresholds. If the shape is 'ball', this is the radius. "
            "If the shape is 'cube', this is the width."
        ),
    )
    parser.add_argument(
        "--structuring-element-shape",
        "-sh",
        type=str,
        default="ball",
        choices=["ball", "cube"],
        help="Shape of the structuring element used for identifying local thresholds",
    )
    parser.add_argument(
        "--sigma",
        "-sg",
        type=float,
        default=None,
        help="Sigma for the Gaussian filter",
    )
    parser.add_argument(
        "--minimum-structure-size",
        "-ms",
        type=int,
        default=64,
        help="Minimum size of structures to keep in the segmentation",
    )
    parser.add_argument(
        "--local-threshold-method",
        "-ltm",
        type=str,
        default="mean",
        choices=["mean", "minmax", "both"],
        help=(
            "Method for determining local thresholds. 'mean' uses the mean of "
            "local voxels. 'minmax' uses the average of the min and max of local "
            "voxels. 'both' uses the minimum of both methods."
        ),
    )
    return parser


def run(
    input_path: str,
    output_path: str,
    lower_threshold: float = 190,
    upper_threshold: float = 450,
    structuring_element_size: int = 6,
    structuring_element_shape: str = "ball",
    sigma: float | None = None,
    minimum_structure_size: int = 64,
    local_threshold_method: str = "mean",
) -> int:
    input_img = sitk.ReadImage(input_path, sitk.sitkFloat32)

    output_img = adaptive_local_thresholding(
        input_img,
        structuring_element_shape,
        structuring_element_size,
        lower_threshold,
        upper_threshold,
        local_threshold_method,
        sigma,
        minimum_structure_size,
    )

    print(f"Writing thresholded image to {output_path}.")
    sitk.WriteImage(output_img, output_path)

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return run(
            input_path=args.input,
            output_path=args.output,
            lower_threshold=args.lower_threshold,
            upper_threshold=args.upper_threshold,
            structuring_element_size=args.structuring_element_size,
            structuring_element_shape=args.structuring_element_shape,
            sigma=args.sigma,
            minimum_structure_size=args.minimum_structure_size,
            local_threshold_method=args.local_threshold_method,
        )
    except Exception as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
