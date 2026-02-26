import argparse
import SimpleITK as sitk

from ormir_xct.segmentation.fft_laplace import fft_laplace_hamming, segmentation_laplace_hamming

from ormir_xct.util.file_reader import verify_image



def fft_laplace_workflow():
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

    # The segmentation_laplace_hamming method writes the segmented image to provided path
    if args.upper and args.lower:
        segmented_image_np = segmentation_laplace_hamming(image, args.output_path, lower_threshold=args.lower, upper_threshold=args.upper)
    else:
        segmented_image_np = segmentation_laplace_hamming(image, args.output_path)
    
    print(f"Writing segmentation to {args.output_path}")
    return segmented_image_np


if __name__ == "__main__":
    fft_laplace_workflow()

