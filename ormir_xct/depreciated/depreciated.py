"""
Temporary file to hold depreciated methods while restructuring
"""


# removed from laplace_hamming_filter.py
def image_read(input_image, segmentation=False, write_path=None, low_threshold = 1170, up_threshold = 10000):
    """
    Reads an input image and calls respective filter and segmentation functions.

    Parameters
    ----------
    input_image : string
        Path to the input image
    
    segmentation : boolean
        Checks if user wants segmentation of image
    
    write_path: string
        Path to the segmented image
    
    Returns
    -------
    filtered_image_np : array
        The result of applying the FFT Laplace Hamming filter.

    """

    # Extract directory, filename, basename, and extensions from the input image
    _, input_filename = os.path.split(input_image)
    _, input_extension = os.path.splitext(input_filename)

    # Calls file reader function
    if not (os.path.isfile(input_image) and (".nii" in input_extension.lower())):
        print()
        print("Error: input file extension must be nii.")
        sys.exit(1)
    
    image = sitk.ReadImage(input_image)
    image_np= sitk.GetArrayFromImage(image)
    
    filtered_image_np = fft_laplace_hamming(image_np)

    # Runs segmentation of image if true
    if segmentation:
        if write_path:
            segmentation_laplace_hamming(image, filtered_image_np, write_path, low_threshold, up_threshold)
        else:
            print("Error: No output path was provided.")
            sys.exit(1)
    
    return filtered_image_np


