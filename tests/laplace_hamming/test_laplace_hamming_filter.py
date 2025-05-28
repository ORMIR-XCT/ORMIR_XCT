import SimpleITK as sitk
import numpy as np
import os
import shutil
import tempfile
import unittest

from ormir_xct.laplace_hamming.laplace_hamming_filter import image_read, fft_laplace_hamming, segmentation_laplace_hamming

class TestLaplaceHammingFilter(unittest.TestCase):

    def setUp(self):
        self.filenames = "test_nii"

        self.path = os.getcwd()
        self.parent = os.path.dirname(self.path)
        self.filepath = os.path.join(self.parent, "data")

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


    def test_image_read(self):
        """
        Test image_read returns filtered image for valid input.
        """
        filtered_image_np = image_read(self.test_nii_temp)
        self.assertIsNotNone(filtered_image_np, "The file wasn't filtered.")
        self.assertIsInstance(filtered_image_np, np.ndarray, "The output isn't an array.")
    
    def test_segmention_image(self):
        """
        Test if segmentation is generated and saved successfully.
        """
        filtered_image_np = image_read(self.test_nii_temp , segmentation=True, write_path=self.test_nii_filtered_temp)
        self.assertTrue(os.path.isfile(self.test_nii_filtered_temp))

    def test_output_file_empty(self):
        """
        Test image_read exits when segmentation is requested without write path.
        """
        with self.assertRaises(SystemExit) as cm:
            image_read(self.test_nii_temp, True)

        self.assertEqual(cm.exception.code, 1, "No output file path was not catched.")


    def test_wrong_input_type(self):
        """
        Test image_read exits for invalid file types.
        """
        with self.assertRaises(SystemExit) as cm:
            image_read(os.path.join(self.test_dir, "invalid.txt"))

        self.assertEqual(cm.exception.code, 1, "Invalid file input was not catched.")
    
    def test_fft_laplace_hamming_preserves_shape(self):
        """
        Test that the filter preserves the original image shape.
        """
        image = sitk.ReadImage(self.test_nii_temp)
        image_np = sitk.GetArrayFromImage(image)
        filtered_image_np = fft_laplace_hamming(image_np)
        self.assertEqual(image_np.shape, filtered_image_np.shape,"Filter array doesn't have same size as original image.")

    def test_fft_laplace_hamming_segmentation(self):
        """
        Test that the segmentation filter works.
        """
        image = sitk.ReadImage(self.test_nii_temp)
        image_np = sitk.GetArrayFromImage(image)
        filtered_image_np = fft_laplace_hamming(image_np)
        segmented_image_np = segmentation_laplace_hamming(image, filtered_image_np, self.test_nii_filtered_temp)
        self.assertIsNotNone(segmented_image_np, "The file wasn't segmented.")
        self.assertIsInstance(segmented_image_np, np.ndarray, "The output isn't an array.")

    def test_fft_laplace_hamming_segmentation_preserves_shape(self):
        """
        Test that the segmentation filter works.
        """
        image = sitk.ReadImage(self.test_nii_temp)
        image_np = sitk.GetArrayFromImage(image)
        filtered_image_np = fft_laplace_hamming(image_np)
        segmented_image_np = segmentation_laplace_hamming(image, filtered_image_np, self.test_nii_filtered_temp)
        self.assertIsNotNone(segmented_image_np, "The file wasn't segmented.")
        self.assertIsInstance(segmented_image_np, np.ndarray, "The output isn't an array.")
        self.assertEqual(image_np.shape, segmented_image_np.shape,"Segmentation array doesn't have same size as original image.")