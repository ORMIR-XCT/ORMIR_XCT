import argparse
import SimpleITK as sitk

from ormir_xct.segmentation.local_adaptive_threshold import adaptive_local_thresholding

def local_adaptive_threshold_workflow():

    parser = argparse.ArgumentParser(
        description="""
        Perform adaptive local thresholding on an image to segment bone. You provide an input image 
        and lower and upper thresholds and a bone segmentation will be created. Optionally you can 
        specify the size and shape of the structuring element used for identifying the local thresholds, 
        as well as the minimum structure size to keep in the segmentation. Finally, you can also specify 
        whether to base the local thresholds on the mean of local voxels, the average of the min and max 
        of local voxels, or the minimum of each of these methods. This method is based on the following 
        article: https://doi.org/10.1016/j.bone.2021.116225.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", type=str, help="Input image filename to be segmented.")
    parser.add_argument("output", type=str, help="Output image filename.")
    parser.add_argument(
        "--lower-threshold",
        "-lt",
        type=float,
        default=190,
        help="Lower threshold for bone segmentation.",
    )
    parser.add_argument(
        "--upper-threshold",
        "-ut",
        type=float,
        default=450,
        help="Upper threshold for bone segmentation.",
    )
    parser.add_argument(
        "--structuring-element-size",
        "-sz",
        type=int,
        default=6,
        help="""Size of the structuring element used for identifying local thresholds.
        If the footprint shape is a ball, this is the radius. If the footprint shape is a cube, 
        this is the width.""",
    )
    parser.add_argument(
        "--structuring-element-shape",
        "-sh",
        type=str,
        default="ball",
        choices=["ball", "cube"],
        help="Shape of the structuring element used for identifying local thresholds.",
    )
    parser.add_argument(
        "--sigma",
        "-sg",
        type=float,
        default=None,
        help="Sigma for the gaussian filter.",
    )
    parser.add_argument(
        "--minimum-structure-size",
        "-ms",
        type=int,
        default=64,
        help="Minimum size of structures to keep in the segmentation.",
    )
    parser.add_argument(
        "--local-threshold-method",
        "-ltm",
        type=str,
        default="mean",
        choices=["mean", "minmax", "both"],
        help="""Method for determining local thresholds. `mean` uses the mean of local voxels. `minmax` uses the 
        average of the min and max of local voxels. `both` uses the minimum of both methods.""",
    )

    args = parser.parse_args()

    input_img = sitk.ReadImage(args.input, sitk.sitkFloat32)

    output_img = adaptive_local_thresholding(
        input_img,
        args.structuring_element_shape,
        args.structuring_element_size,
        args.lower_threshold,
        args.supper_threshold,
        args.local_threshold_method,
        args.sigma,
        args.minimum_structure_size,
    )

    print(f"Writing thresholded image to {args.output_path}.")
    sitk.WriteImage(output_img, args.output_path)

    return output_img


if __name__ == "__main__":
    local_adaptive_threshold_workflow()