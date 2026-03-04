import argparse
import sys

import SimpleITK as sitk
from ormir_xct.segmentation.gauss_seg import threshold_dict, gauss_seg


# Entry method for running this as a primary script
# Taken from ormir.segmentation.gauss_seg

def gauss_seg_workflow():
    parser = argparse.ArgumentParser(
        prog="gauss_seg",
        description="""
        Binarize an input image following the standard segmentation protocol 
        performed in IPL (Scanco). This is roughly equivalent to the IPL 
        command '/seg_gauss' with sigma = 0.5.

        The binarization is done using the same thresholds set in IPL, but  
        we need to know the image units prior to binarization 
        (default is set to BMD units).
        """,
    )

    parser.add_argument("input_image", type=str, help="The input image")
    parser.add_argument("output_image", type=str, help="The output image")
    parser.add_argument(
        "--image_units",
        type=str,
        nargs="?",
        default="BMD",
        help="Image voxel units (options: BMD, SCANCO, ATTENUATION, HU, PER1000)",
    )
    args = parser.parse_args()

    input_image_path = args.input_image
    output_image_path = args.output_image
    image_units = (args.image_units).lower()

    if image_units not in threshold_dict.keys():
        print(
            "ERROR: Invalid image units provided. Only BMD, SCANCO, ATTENUATION, HU, or PER1000 are accepted."
        )
        sys.exit(1)
    else:
        lower_threshold, upper_threshold = threshold_dict[image_units]
        

    # Read in image as a 32-bit float so that we can rescale correctly if needed
    input_image = sitk.ReadImage(input_image_path, sitk.sitkFloat32)
    seg = gauss_seg(input_image, lower_threshold, upper_threshold)

    print(f"Writing segementation to {output_image_path}")
    sitk.WriteImage(seg, output_image_path)


# Entry point for running this as a primary script
if __name__ == "__main__":
    gauss_seg_workflow()
