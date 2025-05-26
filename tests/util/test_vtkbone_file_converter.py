
import os
import sys 
import shutil
import tempfile
import unittest

import vtk
import vtkbone

from ormir_xct.util.vtkbone_file_converter import file_read, aim_reader, aim_writer, nifti_reader, nifti_writer
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk


class TestVTKboneFileConverter(unittest.TestCase):
    def setUp(self):
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
        self.test_nii_temp = os.path.join(self.test_dir, self.filenames[1] + ".nii")
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

        self.assertAlmostEqual(input_spacing[0], output_spacing[0], 4, "x spacinging doesn't match.")
        self.assertAlmostEqual(input_spacing[1], output_spacing[1], 4, "y spacinging doesn't match.")
        self.assertAlmostEqual(input_spacing[2], output_spacing[2], 4, "z spacinging doesn't match.")
    
    def position_check(self, input_image, output_image):
        input_origin = input_image.GetOrigin()
        output_origin = output_image.GetOrigin()

        self.assertAlmostEqual(input_origin[0], output_origin[0], 4, "x position doesn't match")
        self.assertAlmostEqual(input_origin[1], output_origin[1], 4, "y position doesn't match")
        self.assertAlmostEqual(input_origin[2], output_origin[2], 4, "z position doesn't match")
    
    def test_aim_to_nii(self):
        """
        Test the conversion of Scanco AIM to NIFTI using vtkbone and vtk.
        """
        extension = os.path.splitext(self.test_aim_to_nii_temp)[1]
        self.assertEqual(extension.lower(), ".nii", "Extension doesn't match")

        file_read(self.test_aim_temp, self.test_aim_to_nii_temp)

        _, input_reader, _ = aim_reader(self.test_aim_temp)
        _, output_reader = nifti_reader(self.test_aim_to_nii_temp)
        output_reader.SetOrigin(input_reader.GetOrigin())

        self.spacing_check(input_reader, output_reader)
        self.position_check(input_reader, output_reader)

    def test_nii_to_aim(self):
        """
        Test the conversion of Scanco NIFTI to AIM using vtkbone and vtk.
        """
        extension = os.path.splitext(self.test_nii_to_aim_temp)[1]
        self.assertEqual(extension.lower(), ".aim", "Extension doesn't match")

        file_read(self.test_nii_temp, self.test_nii_to_aim_temp)

        _, input_reader = nifti_reader(self.test_nii_temp)
        _, output_reader, _ = aim_reader(self.test_nii_to_aim_temp)
        output_reader.SetOrigin(input_reader.GetOrigin())

        self.spacing_check(input_reader, output_reader)
        self.position_check(input_reader, output_reader)
    
    def test_aim_read(self):
        """
        Test the reading of a Scanco AIM file.
        """
        array, reader_output, _ = aim_reader(self.test_aim_temp)
        self.assertIsNotNone(array)
        self.assertEqual(reader_output.GetDataObjectType(), vtk.VTK_IMAGE_DATA)

    def test_aim_write(self):
        """
        Test the writing of a Scanco AIM file.
        """
        array, reader_output, _ = aim_reader(self.test_aim_temp)
        aim_writer(self.test_aim_to_nii_temp.replace(".nii", ".AIM"), array, reader_output)
        self.assertTrue(os.path.exists(self.test_aim_to_nii_temp.replace(".nii", ".AIM")))

    def test_nii_read(self):
        """
        Test the reading of a Scanco NIFTI file.
        """
        array, reader_output = nifti_reader(self.test_nii_temp)
        self.assertIsNotNone(array)
        self.assertEqual(reader_output.GetDataObjectType(), vtk.VTK_IMAGE_DATA)

    def test_nii_write(self):
        """
        Test the writing of a Scanco NIFTI file.
        """
        array, reader_output = nifti_reader(self.test_nii_temp)
        nifti_writer(self.test_nii_to_aim_temp.replace(".AIM", ".nii"), array, reader_output)
        self.assertTrue(os.path.exists(self.test_nii_to_aim_temp.replace(".AIM", ".nii")))

    def test_wrong_input_type(self):
        """
        Test handling of incorrect input type files.
        """
        dummy_input = os.path.join(self.test_dir, "invalid.txt")
        with open(dummy_input, "w") as f:
            f.write("Invalid content")

        with self.assertRaises(SystemExit) as cm:
            file_read(dummy_input, self.test_nii_to_aim_temp)

        self.assertEqual(cm.exception.code, 1, "Invalid file input was not catched")

    def test_wrong_output_type(self):
        """
        Test handling of incorrect output type files.
        """
        with self.assertRaises(SystemExit) as cm:
            file_read(self.test_nii_temp, os.path.join(self.test_dir, "invalid.txt"))

        self.assertEqual(cm.exception.code, 1, "Invalid file output was not catched")

        
    