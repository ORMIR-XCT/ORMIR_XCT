
import os
import sys 
import shutil
import tempfile
import unittest

import vtk
import vtkbone

from ormir_xct.util.vtkbone_file_converter import file_read, aim_reader, aim_writer, nifti_reader, nifti_writer
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk


class TestFileConverter(unittest.TestCase):
    def setup(self):
        self.filenames = [
            "test_aim",
            "test_nii"
        ]

        self.path = os.getcwd()
        self.parent = os.path.dirname(self.path)
        self.filepath = os.path.join(self.parent, "data")

        # Create a temp directory
        self.test_dir = tempfile.mkdtemp()

        # Paths for test files
        # Input images
        self.test_aim = os.path.join(self.filepath, self.filenames[0] + ".AIM")
        self.test_nii = os.path.join(self.filepath, self.filenames[1] + ".nii")

        # Output images
        # AIM conversion
        self.test_aim_temp = os.path.join(self.test_dir, self.filenames[0] + ".AIM")
        self.test_aim_to_nii_temp = os.path.join(
            self.test_dir, self.filenames[0] + ".nii"
        )

        # NIFTI conversion
        self.test_nii_temp = os.path.join(self.test_dir, self.filenames[2] + ".nii")
        self.test_nii_to_aim_temp = os.path.join(
            self.test_dir, self.filenames[1] + ".AIM"
        )
        
        # Copy test data to temp directory
        shutil.copy(self.test_aim, self.test_aim_temp)
        shutil.copy(self.test_nii, self.test_nii_temp)

        self.assertTrue(os.path.isfile(self.test_aim_temp))
        self.assertTrue(os.path.isfile(self.test_nii_temp))

    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def spacing_check(self, input_image, output_image):
        input_spacing = input_image.GetSpacing()
        output_spacing = output_image.GetSpacing()

        self.assertAlmostEqual(input_spacing[0], output_spacing[0], 4)
        self.assertAlmostEqual(input_spacing[1], output_spacing[1], 4)
        self.assertAlmostEqual(input_spacing[2], output_spacing[2], 4)
    
    def position_check(self, input_image, output_image):
        input_origin = input_image.GetOrigin()
        output_origin = output_image.GetOrigin()

        self.assertAlmostEqual(input_origin[0], output_origin[0], 4)
        self.assertAlmostEqual(input_origin[1], output_origin[1], 4)
        self.assertAlmostEqual(input_origin[2], output_origin[2], 4)
    
    def test_aim_to_nii(self):
        """
        Test the conversion of Scanco AIM to NIFTI using vtkbone and vtk.
        """
        extension = os.path.splitext(self.test_aim_to_nii_temp)[1]
        self.assertTrue(extension.lower() == ".nii")

        file_read(self.test_aim_temp, self.test_aim_to_nii_temp)

        
        

    def test_nii_to_aim(self):
        """
        Test the conversion of Scanco NIFTI to AIM using vtkbone and vtk.
        """
        extension = os.path.splitext(self.test_nii_to_aim_temp)[1]
        self.assertTrue(extension.lower() == ".AIM")

        file_read(self.test_nii_temp, self.test_nii_to_aim_temp)

    
    def test_aim_read(self):
        """
        Test the reading of a Scanco AIM file.
        """
        
    
    def test_aim_write(self):
        """
        Test the writing of a Scanco AIM file.
        """
        
    
    def test_nii_read(self):
        """
        Test the reading of a Scanco NIFTI file.
        """
        
    
    def test_nii_write(self):
        """
        Test the writing of a Scanco NIFTI file.
        """
        
    
    def test_wrong_input_type(self):
        """
        Test the handel of incorrect input type files.
        """
        
    
    def test_wrong_output_type(self):
        """
        Test the handel of incorrect output type files.
        """
        
    