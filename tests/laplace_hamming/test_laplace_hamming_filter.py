import scipy
import SimpleITK as sitk
import numpy as np
import os
import sys
import shutil
import tempfile
import unittest

from scipy.fft import fftshift
from scipy.fft import fftn, ifftn
from ormir_xct.laplace_hamming.laplace_hamming_filter import image_read, segmentation_laplace_hamming

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

        # Output images
        # segmented imaze??????
        self.test_nii_temp = os.path.join(self.test_dir, self.filenames + ".nii")
        self.test_nii_to_filter_temp = os.path.join(
            self.test_dir, self.filenames[2] + ".nii"
        )

        # Copy test data to temp directory
        shutil.copy(self.test_nii, self.test_nii_temp)

        self.assertTrue(os.path.isfile(self.test_nii_temp))

    def tearDown(self):
        shutil.rmtree(self.test_dir)


    def test_image_read(self):
        """
        
        """
        frequency_domain = image_read(self.test_nii)
        self.assertIsNotNone(frequency_domain, "The file wasn't filtered")
    
    def test_segmention_image(self):
        """
        
        """
        frequency_domain = image_read(self.test_nii)
        self.assertIsNotNone(frequency_domain, "The file wasn't filtered")

    def test_output_file_empty(self):
        """
        
        """
        with self.assertRaises(SystemExit) as cm:
            image_read(self.test_nii_temp, True)

        self.assertEqual(cm.exception.code, 1, "No output file path was not catched")


    def test_wrong_input_type(self):
        """
        
        """
        with self.assertRaises(SystemExit) as cm:
            image_read(os.path.join(self.test_dir, "invalid.txt"))

        self.assertEqual(cm.exception.code, 1, "Invalid file input was not catched")

    