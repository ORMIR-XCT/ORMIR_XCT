import unittest
import numpy as np
import SimpleITK as sitk
import os
import shutil
import tempfile

from ormir_xct.bone_parameters.bone_parameters import (
    calculate_bone_parameter,
    trab_peri_array,
    bone_volume_fraction,
    trabecular_thickness,
    trabecular_separation,
    trabecular_number,
    total_bone_area,
    bone_mineral_density,
    bone_mineral_density_mask
)

class TestBoneParameters(unittest.TestCase):
    def setUp(self):
        self.filenames = "test_nii"
        self.path = os.getcwd()
        self.parent = os.path.dirname(self.path)
        self.filepath = os.path.join(self.parent, "ORMIR_XCT/tests/data")

        self.test_dir = tempfile.mkdtemp()

        self.test_nii = os.path.join(self.filepath, self.filenames + ".nii")
        self.test_nii_temp = os.path.join(self.test_dir, self.filenames + ".nii")

        shutil.copy(self.test_nii, self.test_nii_temp)

        self.image = sitk.ReadImage(self.test_nii_temp, sitk.sitkFloat32)
        self.mask = sitk.GetImageFromArray((sitk.GetArrayFromImage(self.image) > 0).astype(np.uint8))
        self.mask.CopyInformation(self.image)
        self.spacing = self.image.GetSpacing()
        
        self.mu_scaling = 8192
        self.mu_water = 0.24090
        self.rescale_slope = 1603.51904
        self.rescale_intercept = -391.209015
        
        self.trab_seg, self.peri_mask, self.trab_seg_np, self.peri_mask_np = trab_peri_array(
            self.image, self.spacing, self.mu_water, self.rescale_slope, self.rescale_intercept
        )
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_trab_peri_array(self):
        trab_seg, peri_mask, trab_seg_np, peri_mask_np = trab_peri_array(
            self.image, self.spacing, self.mu_water, self.rescale_slope, self.rescale_intercept
        )

        self.assertIsInstance(trab_seg, sitk.Image, "SimpleITK object type wasn't created.")
        self.assertIsInstance(peri_mask, sitk.Image, "SimpleITK object type wasn't created.")
        self.assertIsInstance(trab_seg_np, np.ndarray, "Numpy array object type wasn't created.")
        self.assertIsInstance(peri_mask_np, np.ndarray, "Numpy array object type wasn't created.")

        # Ensure dimensions match original image
        original_shape = sitk.GetArrayFromImage(self.image).shape
        self.assertEqual(trab_seg_np.shape, original_shape, "Origianl shape of image doesn't match.")
        self.assertEqual(peri_mask_np.shape, original_shape, "Origianl shape of image doesn't match.")

    
    def test_calculate_bone_parameter_bmd(self):
        mean, std = calculate_bone_parameter(
            self.test_nii_temp, "bmd", self.mu_scaling, self.mu_water,
            self.rescale_slope, self.rescale_intercept, image_units="scanco"
        )

        self.assertIsNotNone(mean, "No value was returned.")
        self.assertIsNotNone(std, "No value was returned.")

    def test_calculate_bone_parameter_bv(self):
        bvtv = calculate_bone_parameter(
            self.test_nii_temp, "bv", self.mu_scaling, self.mu_water,
            self.rescale_slope, self.rescale_intercept
        )
        
        self.assertIsNotNone(bvtv, "No value was returned.")

    def test_bone_volume_fraction(self):
        result = bone_volume_fraction(self.trab_seg_np, self.peri_mask_np)
        self.assertIsNotNone(result, "No value was returned.")

    def test_trabecular_thickness(self):
        img, stats = trabecular_thickness(self.trab_seg_np, self.spacing, self.image)
        self.assertIsInstance(img, sitk.Image, "SimpleITK object type wasn't created.")
        self.assertIsNotNone(stats, "No value was returned.")

    def test_trabecular_separation(self):
        img, stats = trabecular_separation(self.trab_seg, self.peri_mask, self.spacing, self.image)
        self.assertIsInstance(img, sitk.Image, "SimpleITK object type wasn't created.")
        self.assertIsNotNone(stats, "No value was returned.")

    def test_trabecular_number(self):
        with self.assertRaises(SystemExit):
            img, stats = trabecular_number(self.trab_seg_np, self.spacing, self.image)

    def test_total_bone_area(self):
        result = total_bone_area(self.peri_mask_np, self.spacing)
        self.assertIsNotNone(result, "No value was returned.")

    def test_bone_mineral_density(self):
        mean, std = bone_mineral_density(
            self.image, "scanco", self.mu_scaling, self.mu_water, 
            self.rescale_slope, self.rescale_intercept
        )

        self.assertIsNotNone(mean)
        self.assertIsNotNone(std)

    def test_bone_mineral_density_mask(self):
        mean, std = bone_mineral_density_mask(
            self.image, self.mask, "scanco", self.mu_scaling, 
            self.mu_water, self.rescale_slope, self.rescale_intercept
        )

        self.assertIsNotNone(mean, "No value was returned.")
        self.assertIsNotNone(std, "No value was returned.")

    def test_calculate_bone_parameter_invalid(self):
        with self.assertRaises(SystemExit, msg="Didn't catch invalid parameter."):
            calculate_bone_parameter(
                self.test_nii_temp, "invalid_param", self.mu_scaling, self.mu_water,
                self.rescale_slope, self.rescale_intercept, image_units="scanco"
            )
