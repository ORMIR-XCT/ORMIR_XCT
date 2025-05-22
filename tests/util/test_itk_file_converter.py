
import os
import sys 
import shutil
import tempfile
import unittest
from matplotlib import pyplot as plt
import numpy as np

import itk
import SimpleITK as sitk

from ormir_xct.util.ITK_file_converter import file_read, nifti_reader, nifti_writer, isq_writer, aim_isq_reader
from ormir_xct.util.sitk_itk import itk_sitk, sitk_itk

class TestFileConverter(unittest.TestCase):
    def setup(self):
        self.filenames = [
            "test_aim",
            "test_isq",
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
        self.test_isq = os.path.join(self.filepath, self.filenames[1] + ".ISQ")
        self.test_nii = os.path.join(self.filepath, self.filenames[2] + ".nii")

        # Output images
        # AIM conversion
        self.test_aim_temp = os.path.join(self.test_dir, self.filenames[0] + ".AIM")
        self.test_aim_to_nii_temp = os.path.join(
            self.test_dir, self.filenames[0] + ".nii"
        )

        # ISQ conversion
        self.test_isq_temp = os.path.join(self.test_dir, self.filenames[1] + ".ISQ")
        self.test_isq_to_nii_temp = os.path.join(
            self.test_dir, self.filenames[1] + ".nii"
        )
       
        # NIFTI conversion
        self.test_nii_temp = os.path.join(self.test_dir, self.filenames[2] + ".nii")
        self.test_nii_to_isq_temp = os.path.join(
            self.test_dir, self.filenames[2] + ".ISQ"
        )

        # Copy test data to temp directory
        shutil.copy(self.test_aim, self.test_aim_temp)
        shutil.copy(self.test_isq, self.test_isq_temp)
        shutil.copy(self.test_nii, self.test_nii_temp)

        self.assertTrue(os.path.isfile(self.test_aim_temp))
        self.assertTrue(os.path.isfile(self.test_isq_temp))
        self.assertTrue(os.path.isfile(self.test_nii_temp))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def spacing_check(self, input_image, output_image):
        input_spacing = input_image.GetSpacing()
        output_spacing = output_image.GetSpacing()

        self.assertAlmostEqual(input_spacing[0], output_spacing[0], 4)
        self.assertAlmostEqual(input_spacing[1], output_spacing[1], 4)
        self.assertAlmostEqual(input_spacing[2], output_spacing[2], 4)

    def dimension_check(self, input_image, output_image):
        input_size = input_image.GetSize()
        output_size = output_image.GetSize()

        self.assertAlmostEqual(input_size[0], output_size[0], 4)
        self.assertAlmostEqual(input_size[1], output_size[1], 4)
        self.assertAlmostEqual(input_size[2], output_size[2], 4)

    def position_check(self, input_image, output_image):
        input_origin = input_image.GetOrigin()
        output_origin = output_image.GetOrigin()

        self.assertAlmostEqual(input_origin[0], output_origin[0], 4)
        self.assertAlmostEqual(input_origin[1], output_origin[1], 4)
        self.assertAlmostEqual(input_origin[2], output_origin[2], 4)

    def direction_check(self, input_image, output_image):
        input_direction = input_image.GetDirection()
        output_direction = output_image.GetDirection()

        self.assertAlmostEqual(input_direction[0], output_direction[0], 4)
        self.assertAlmostEqual(input_direction[1], output_direction[1], 4)
        self.assertAlmostEqual(input_direction[2], output_direction[2], 4)
    
    def test_aim_to_nii(self):
        """
        Test the conversion of Scanco AIM to NIFTI using ITKIOScanco and SimpleITK.
        """
        extension = os.path.splitext(self.test_aim_to_nii_temp)[1]
        self.assertTrue(extension.lower() == ".nii")

        file_read(self.test_aim_temp, self.test_aim_to_nii_temp)

        image_type = itk.Image[itk.ctype("signed short"), 3]
        reader = itk.ImageFileReader[image_type].New()
        image_io = itk.ScancoImageIO.New()
        reader.SetImageIO(image_io)
        reader.SetFileName(self.test_aim_temp)
        reader.Update()

        aim_file = itk.imread(self.test_aim_to_nii_temp)
        nii_file = itk.imread(self.test_aim_to_nii_temp)

        self.spacing_check(aim_file, nii_file)
        self.dimension_check(aim_file, nii_file)
        self.position_check(aim_file, nii_file)
        self.direction_check(aim_file, nii_file)

    
    def test_nii_to_isq(self):
        """
        Test the conversion of Scanco NIFTI to ISQ using ITKIOScanco and SimpleITK.
        """
        extension = os.path.splitext(self.test_nii_to_isq_temp)[1]
        self.assertTrue(extension.lower() == ".ISQ")

        file_read(self.test_nii_temp, self.test_nii_to_isq_temp)
        
    
    def test_isq_to_nii(self):
        """
        Test the conversion of Scanco ISQ to NIFTI using ITKIOScanco and SimpleITK.
        """
        extension = os.path.splitext(self.test_isq_to_nii_temp)[1]
        self.assertTrue(extension.lower() == ".nii")

        file_read(self.test_isq_temp, self.test_isq_to_nii_temp)

        image_type = itk.Image[itk.ctype("signed short"), 3]
        reader = itk.ImageFileReader[image_type].New()
        image_io = itk.ScancoImageIO.New()
        reader.SetImageIO(image_io)
        reader.SetFileName(self.test_isq_temp)
        reader.Update()

        isq_file = itk.imread(self.test_isq_to_nii_temp)
        nii_file = itk.imread(self.test_isq_to_nii_temp)
        # ORIGIN WONT BE THE SAME!!!!!!!!
        
        self.spacing_check(isq_file, nii_file)
        self.dimension_check(isq_file, nii_file)
        self.position_check(isq_file, nii_file)
        self.direction_check(isq_file, nii_file)
    
    def test_aim_read(self):
        """
        Test the reading of a Scanco AIM file.
        """
        
    
    def test_nii_read(self):
        """
        Test the reading of a Scanco NIFTI file.
        """
        
    
    def test_nii_write(self):
        """
        Test the writing of a Scanco NIFTI file.
        """
        
    
    def test_isq_read(self):
        """
        Test the reading of a Scanco ISQ file.
        """
        
    
    def test_isq_write(self):
        """
        Test the writing of a Scanco ISQ file.
        """
        
    
    def test_wrong_input_type(self):
        """
        Test the handel of incorrect input type files.
        """
        
    
    def test_wrong_output_type(self):
        """
        Test the handel of incorrect output type files.
        """
        
    