import argparse
import numpy as np
import SimpleITK as sitk

from scipy import ndimage
from skimage.filters import gaussian
from skimage.morphology import ball, cube, remove_small_objects
from concurrent.futures import ThreadPoolExecutor


def compute_minmax_threshold_image(
    density: np.ndarray, footprint: np.ndarray
) -> np.ndarray:
    """
    Calculate the minmax threshold image.

    Parameters
    ----------
    density : np.ndarray
        The density image to be thresholded.

    footprint : np.ndarray
        The footprint to use for identifying local thresholds.

    Returns
    -------
    np.ndarray
        The minmax threshold image.
    """
    print("Calculating max image...")
    max_image = ndimage.maximum_filter(density, footprint=footprint)
    print("Calculating min image...")
    min_image = ndimage.minimum_filter(density, footprint=footprint)
    print("Calculating minmax threshold image...")
    return (min_image + max_image) / 2


def compute_mean_threshold_image(
    density: np.ndarray, footprint: np.ndarray
) -> np.ndarray:
    """
    Calculate the mean threshold image.

    Parameters
    ----------
    density : np.ndarray
        The density image to be thresholded.

    footprint : np.ndarray
        The footprint to use for identifying local thresholds.

    silent : bool
        Whether to suppress terminal output.

    Returns
    -------
    np.ndarray
        The mean threshold image.
    """
    print("Calculating mean image...")
    return ndimage.convolve(density, footprint / footprint.sum())


def compute_adaptive_local_threshold_segmentation(
    density: np.ndarray,
    low_threshold: float,
    high_threshold: float,
    footprint: np.ndarray,
    mode: str,
    sigma: float,
    min_size: int,
) -> np.ndarray:
    """
    Perform local adaptive thresholding on a density image.

    Parameters
    ----------
    density : np.ndarray
        The density image to be thresholded.

    low_threshold : float
        The lower threshold for the density image.

    high_threshold : float
        The upper threshold for the density image.

    footprint : np.ndarray
        The footprint to use for identifying local thresholds.

    mode : str
        The mode to use for identifying local thresholds. Can be `mean`, `minmax`, or `both`.

    sigma : float
        The sigma to use for the gaussian filter.

    min_size : int
        The minimum size of structures to keep in the segmentation.

    Returns
    -------
    np.ndarray
        The thresholded image.
    """
    print(f"Calculating threshold image using mode: {mode}")
    if mode == "mean":
        threshold_image = compute_mean_threshold_image(density, footprint)
    elif mode == "minmax":
        threshold_image = compute_minmax_threshold_image(density, footprint)
    elif mode == "both":
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_mean = executor.submit(
                compute_mean_threshold_image, density, footprint
            )
            future_minmax = executor.submit(
                compute_minmax_threshold_image, density, footprint
            )
            threshold_image = np.minimum(future_mean.result(), future_minmax.result())
    else:
        raise ValueError(
            f"`mode` must be one of `mean`, `minmax`, or `both`, received {mode}."
        )

    if sigma != None:
        density = gaussian(density, sigma=sigma)

    return remove_small_objects(
        ((density > low_threshold) & (density > threshold_image))
        | (density > high_threshold),
        min_size=min_size,
    )


def adaptive_local_thresholding(
    image_sitk,
    structuring_element_shape,
    structuring_element_size,
    lower_threshold,
    upper_threshold,
    local_threshold_method,
    sigma,
    minimum_structure_size,
):
    image = sitk.GetArrayFromImage(image_sitk)

    if structuring_element_shape == "ball":
        footprint = ball(structuring_element_size)
    elif structuring_element_shape == "cube":
        footprint = cube(structuring_element_size)
    else:
        raise ValueError("Invalid structuring element shape.")
    segmentation = compute_adaptive_local_threshold_segmentation(
        image,
        lower_threshold,
        upper_threshold,
        footprint,
        local_threshold_method,
        sigma,
        minimum_structure_size,
    )
    segmentation_sitk = sitk.GetImageFromArray(segmentation.astype(int))
    segmentation_sitk.CopyInformation(image_sitk)

    return segmentation_sitk


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perform adaptive local thresholding on an image to segment bone. You provide an input image "
        "and lower and upper thresholds and a bone segmentation will be created. Optionally you can "
        "specify the size and shape of the structuring element used for identifying the local thresholds, "
        "as well as the minimum structure size to keep in the segmentation. Finally, you can also specify "
        "whether to base the local thresholds on the mean of local voxels, the average of the min and max "
        "of local voxels, or the minimum of each of these methods. This method is based on the following "
        "article: https://doi.org/10.1016/j.bone.2021.116225. ",
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
        help="Size of the structuring element used for identifying local thresholds."
        "If the footprint shape is a ball, this is the radius. If the footprint shape is a cube, "
        "this is the width.",
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
        help="Method for determining local thresholds. `mean` uses the mean of local voxels. `minmax` uses the "
        "average of the min and max of local voxels. `both` uses the minimum of both methods.",
    )

    args = parser.parse_args()
    input_path = args.input
    output_path = args.output
    structuring_element_shape = args.structuring_element_shape
    structuring_element_size = args.structuring_element_size
    lower_threshold = args.lower_threshold
    upper_threshold = args.upper_threshold
    local_threshold_method = args.local_threshold_method
    sigma = args.sigma
    minimum_structure_size = args.minimum_structure_size

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

    sitk.WriteImage(output_img, output_path)