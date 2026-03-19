import argparse

from ormir_xct.core.segmentation.fft_laplace_hamming import fft_laplace_hamming_seg
from ormir_xct.core.util.file_reader import verify_image


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fft-laplace",
        description="Binarize an input image using a Laplace-Hamming filter and fixed threshold.",
    )
    parser.add_argument("input_image", type=str, help="Path to the input image")
    parser.add_argument("output_path", type=str, help="Path to the output image")
    parser.add_argument("--eps", type=float, default=0.45, help="Laplace epsilon")
    parser.add_argument(
        "--cutoff", type=float, default=0.3, help="Low-pass cutoff frequency"
    )
    parser.add_argument("--amp", type=float, default=1.0, help="Hamming amplitude")
    parser.add_argument("--lower", type=int, default=475, help="Lower threshold")
    parser.add_argument("--upper", type=int, default=10000, help="Upper threshold")
    return parser


def run(
    input_image: str,
    output_path: str,
    eps: float = 0.45,
    cutoff: float = 0.3,
    amp: float = 1.0,
    lower: int = 475,
    upper: int = 10000,
):
    image = verify_image(input_image)

    segmented_image_np = fft_laplace_hamming_seg(
        image,
        output_path,
        eps,
        cutoff,
        amp,
        lower_threshold=lower,
        upper_threshold=upper,
    )

    print(f"Writing segmentation to {output_path}")
    return segmented_image_np


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    run(
        input_image=args.input_image,
        output_path=args.output_path,
        eps=args.eps,
        cutoff=args.cutoff,
        amp=args.amp,
        lower=args.lower,
        upper=args.upper,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
