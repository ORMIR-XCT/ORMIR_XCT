"""
fft_laplace_hamming.py

Created by:   Michael Kuczynski
Created on:   2024

Description: Implementation of the IPL fft_laplace_hamming function.
             Smoothing + edge enhancement is performed with a Laplace-Hamming
             filter, and segmentation is performed with a global threshold.
"""

import numpy as np
import SimpleITK as sitk

from ormir_xct.core.util.file_reader import verify_image


def compute_laplacian_filter(shape):
    """
    Compute the Laplacian filter in the frequency domain for edge enhancement.

    Parameters
    ----------
    shape : np.ndarray
        Numpy array of frequency domain shape

    Returns
    -------
    laplacian_filter : np.ndarray
        Laplacian filter in the frequency domain
    """

    # Produce the discrete Fourier transform of frequency domain
    kx = np.fft.fftfreq(shape[0])[:, None, None]
    ky = np.fft.fftfreq(shape[1])[None, :, None]
    kz = np.fft.fftfreq(shape[2])[None, None, :]
    laplacian_filter = -(kx**2 + ky**2 + kz**2)
    return laplacian_filter


def apply_hamming_window(frequency_domain, cutoff_ratio, amplitude):
    """Apply a 3D Hamming window in the frequency domain with specified cutoff and amplitude.

    Parameters
    ----------
    - frequency_domain : np.ndarray
        Frequency domain

    - cutoff_ratio : float
        Low-pass cutoff frequency of the Hamming filter.

    - amplitude : float
        Amplitude of the Hamming filter.

    Returns
    ----------
    - frequency_domain  : np.ndarray
        Frequency domain

    """

    # Get the shape of the frequency domain
    shape = frequency_domain.shape
    shape_x = shape[0]
    shape_y = shape[1]
    shape_z = shape[2]

    # Get the hamming window
    hamming_x = np.hamming(shape_x) * amplitude
    hamming_y = np.hamming(shape_y) * amplitude
    hamming_z = np.hamming(shape_z) * amplitude

    # Create a 3D Hamming filter by broadcasting
    hamming_3d = (
        hamming_x[:, None, None] * hamming_y[None, :, None] * hamming_z[None, None, :]
    )

    # Compute normalized distance and apply cutoff ratio in-place
    center_x, center_y, center_z = shape_x // 2, shape_y // 2, shape_z // 2
    max_distance = np.sqrt(center_x**2 + center_y**2 + center_z**2)
    for x in range(shape_x):
        for y in range(shape_y):
            for z in range(shape_z):
                distance = np.sqrt(
                    (x - center_x) ** 2 + (y - center_y) ** 2 + (z - center_z) ** 2
                )
                if distance / max_distance > cutoff_ratio:
                    hamming_3d[x, y, z] = 0

    # Apply the Hamming window to the frequency domain in-place
    frequency_domain *= hamming_3d
    return frequency_domain


def fft_laplace_hamming(
    image_np, laplace_epsilon=0.45, lp_cut_off_freq=0.3, hamming_amp=1.0
):
    """
    Apply FFT Laplace Hamming filter on given image array in preparation for segmentation based on zero crossing of second derivative.
    Default input parameters are selected based on the paper by Sadoughi, et al. JBMR. 2023: https://doi.org/10.1002%2Fjbmr.4819

    Parameters
    ----------
    - image_np : np.ndarray
        The numpy array of input image

    - laplace_epsilon : float
        Weight of the curvature image; higher values result in more edge-enhancement.

    - lp_cut_off_freq : float
        Low-pass cutoff frequency of the Hamming filter.

    - hamming_amp : float
        Amplitude of the Hamming filter.

    Returns
    ----------
    - filtered_image_np : np.ndarray
        The result of applying the FFT Laplace Hamming filter.
    """

    # Step 2: Perform a 3D Fourier transform and shift to center zero frequency
    frequency_domain = np.fft.fftn(image_np)
    frequency_domain_shifted = np.fft.fftshift(frequency_domain)

    # Step 3: Apply the Hamming window in the frequency domain
    frequency_domain_shifted = apply_hamming_window(
        frequency_domain_shifted, lp_cut_off_freq, hamming_amp
    )

    # Step 4: Apply Laplacian filter in the frequency domain for edge enhancement
    laplacian_filter = compute_laplacian_filter(frequency_domain_shifted.shape)
    frequency_domain_laplace = (
        frequency_domain_shifted * laplacian_filter * laplace_epsilon
    )
    frequency_domain_combined = frequency_domain_shifted + frequency_domain_laplace

    # Step 5: Reconstruct the final filtered image by adding weighted original image
    frequency_domain_unshifted = np.fft.ifftshift(frequency_domain_combined)
    curvature_image_np = np.abs(np.fft.ifftn(frequency_domain_unshifted))

    # Combine curvature image with original image with variable weight
    final_image_np = (1 - laplace_epsilon) * image_np + curvature_image_np

    return final_image_np


def fft_laplace_hamming_seg(
    image,
    write_path=None,
    laplace_epsilon=0.45,
    lp_cut_off_freq=0.3,
    hamming_amp=1.0,
    lower_threshold=475,
    upper_threshold=10000,
):
    """
    Provides the segmentation of the image and write down the segmented image if write_path is provided.
    Default input parameters are selected based on the paper by Sadoughi, et al. JBMR. 2023: https://doi.org/10.1002%2Fjbmr.4819
    It is assumed that the input image is in units of per mille by default.

    Parameters
    ----------
    image : sitk.Image or str
        sitk image object of input or string path to input image

    write_path: str or None, default: None
        Path to write the segmented image. Will not write output if no path is given.

    lower_threshold: int, default: 475
        Lower threshold for segmentation

    upper_threshold: int, default: 10000
        Upper threshold for segmentation

    Returns
    -------
    seg : sitk.Image
        Segmented image

    """
    # Handles string paths to input image
    image = verify_image(image)

    # Obtain filtered image
    filtered_image_np = fft_laplace_hamming(
        sitk.GetArrayFromImage(image), laplace_epsilon, lp_cut_off_freq, hamming_amp
    )

    # Setup image object
    im = sitk.GetImageFromArray(filtered_image_np)
    im.SetOrigin(image.GetOrigin())
    im.SetDirection(image.GetDirection())
    im.SetSpacing(image.GetSpacing())

    # Binary thresholding
    seg = sitk.BinaryThreshold(im, lower_threshold, upper_threshold, 1, 0)

    # Write the segmented image if path provided
    if write_path:
        sitk.WriteImage(seg, write_path)

    return seg
