import SimpleITK as sitk
import numpy as np
import os
import shutil
import tempfile
import unittest

from ormir_xct.core.segmentation.fft_laplace_hamming import fft_laplace_hamming, fft_laplace_hamming_seg

class TestLaplaceHammingFilter(unittest.TestCase):

    def setUp(self):
        self.filenames = "test_nii"

        self.path = os.getcwd()
        self.parent = os.path.dirname(self.path)
        self.filepath = os.path.join(self.parent, "ORMIR_XCT/tests/data")

        # Create a temp directory
        self.test_dir = tempfile.mkdtemp()

        # Paths for test files
        # Input images
        self.test_nii = os.path.join(self.filepath, self.filenames + ".nii")
        self.test_nii_filtered_temp = os.path.join(self.test_dir, self.filenames + "_filtered.nii")
        # Output images
        self.test_nii_temp = os.path.join(self.test_dir, self.filenames + ".nii")
        self.test_nii_to_filter_temp = os.path.join(
            self.test_dir, self.filenames + ".nii"
        )

        # Copy test data to temp directory
        shutil.copy(self.test_nii, self.test_nii_temp)

        self.assertTrue(os.path.isfile(self.test_nii_temp))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    
    def test_segmention_image(self):
        """
        Test if segmentation is generated and saved successfully.
        """

        # Remove output if it exists
        if os.path.exists(self.test_nii_temp):
            os.remove(self.test_nii_temp)


        fft_laplace_hamming_seg(self.test_nii, write_path=self.test_nii_temp)

        self.assertTrue(
            os.path.isfile(self.test_nii_filtered_temp),
            "Output file was not generated."
        )

    def test_output_file_not_generated(self):
        """
        Test fft_laplace_hamming_seg does not write output when segmentation is requested without write path.
        """

        output_path = "temp_output.nii"

        # Make sure it doesn't exist beforehand
        if os.path.exists(output_path):
            os.remove(output_path)

        fft_laplace_hamming_seg(self.test_nii_temp)

        self.assertFalse(
            os.path.exists(output_path),
            "Output file was generated when it should not have been."
        )
        
    
    def test_fft_laplace_hamming_preserves_shape(self):
        """
        Test that the filter preserves the original image shape.
        """
        image = sitk.ReadImage(self.test_nii_temp)
        image_np = sitk.GetArrayFromImage(image)
        filtered_image_np = fft_laplace_hamming(image_np)
        self.assertEqual(image_np.shape, filtered_image_np.shape, "Filter array doesn't have same size as original image.")

    def test_fft_laplace_hamming_segmentation(self):
        """
        Test that the segmentation works with image input.
        """
        image = sitk.ReadImage(self.test_nii_temp)
        segmented_image = fft_laplace_hamming_seg(image, self.test_nii_filtered_temp)
        self.assertIsNotNone(segmented_image, "The file wasn't segmented.")
        self.assertIsInstance(segmented_image, sitk.Image, "The output isn't an image.")

    def test_fft_laplace_hamming_segmentation_preserves_shape(self):
        """
        Test that the segmentation works and preserves shape.
        """
        image = sitk.ReadImage(self.test_nii_temp)
        image_np = sitk.GetArrayFromImage(image)
        segmented_image = fft_laplace_hamming_seg(image, self.test_nii_filtered_temp)
        segmented_image_np = sitk.GetArrayFromImage(segmented_image)
        self.assertIsNotNone(segmented_image, "The file wasn't segmented.")

        self.assertIsInstance(segmented_image_np, np.ndarray, "The output isn't an array.")
        self.assertEqual(image_np.shape, segmented_image.shape,"Segmentation array doesn't have same size as original image.")