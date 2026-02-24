import argparse
import SimpleITK as sitk

from ormir_xct.segmentation.fft_laplace import fft_laplace_hamming, segmentation_laplace_hamming

from ormir_xct.util.file_reader import verify_image



def main():
    parser = argparse.ArgumentParser(
        prog="gauss_seg",
        description="""
        Binarize an input image using the laplace hamming approach
        """,
    )
    parser.add_argument("input_image", type=str, help="The input image path")
    parser.add_argument("output_path", type=str, help="The output image")
    parser.add_argument("upper", type=int, help="Upper threshold", required=False)
    parser.add_argument("lower", type=int, help="Lower threshold", required=False)

    args = parser.parse_args()

    image = verify_image(args.input_image)
    image_np= sitk.GetArrayFromImage(image)

    filtered_image_np = fft_laplace_hamming(image_np)

    # The segmentation_laplace_hamming method writes the segmented image to provided path
    if args.upper and args.lower:
        segmented_image_np = segmentation_laplace_hamming(image, filtered_image_np, args.output_path, args.lower, args.upper)
    else:
        segmented_image_np = segmentation_laplace_hamming(image, filtered_image_np, args.output_path)
    
    print(f"Writing segmentation to {args.output_path}")
    return segmented_image_np


if __name__ == "__main__":
    main()

