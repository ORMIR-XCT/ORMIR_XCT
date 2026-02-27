"""
test_ipl_segmentation.py

Created by:   Michael Kuczynski
Created on:   June 29, 2022

Description: Test IPL standard segmentation.
"""

import os
import unittest
import numpy as np
import SimpleITK as sitk
import tempfile

from ormir_xct.segmentation.gauss_seg import gauss_seg


def create_sphere_mask(shape, voxel_width, radius):
    """
    Creates a binary NumPy sphere with given radius and voxel size.
    """
    center = (
        voxel_width[0] * (shape[0] // 2),
        voxel_width[1] * (shape[1] // 2),
        voxel_width[2] * (shape[2] // 2),
    )
    x, y, z = np.meshgrid(
        *[voxel_width[i] * np.arange(0, shape[i]) for i in range(3)], indexing="ij"
    )
    mask = np.zeros(shape, dtype=bool)
    mask[
        (x - center[0]) ** 2 + (y - center[1]) ** 2 + (z - center[2]) ** 2 < radius**2
    ] = 1
    return mask


class TestIPLSegmentation(unittest.TestCase):
    def create_test_image_np(self):
        voxel_width = (1, 1, 1)
        shape = (10, 10, 10)
        radius = 4
        sphere = create_sphere_mask(shape, voxel_width, radius).astype(float)


        return sphere
    
    def test_gauss_segmentation(self):
        """Tests gauss_seg with image input"""
        sphere_array = self.create_test_image_np()
        sphere = sitk.GetImageFromArray(sphere_array)

        result_image = gauss_seg(sphere, 1, 2, 1, 1, 0.01)
        result_array = sitk.GetArrayFromImage(result_image).astype(float)

        np.testing.assert_array_equal(sphere_array, result_array)

    def test_gauss_segmentation_path_handling(self):
        """Tests gauss_seg with path input"""
        # Create a temp directory
        self.test_dir = tempfile.mkdtemp()

        # Paths for test files
        # input image path
        self.test_input_nii = os.path.join(self.test_dir, "gauss_test_input.nii")
        self.test_output_nii = os.path.join(self.test_dir, "gauss_test_output.nii")


        sphere_array = self.create_test_image_np()
        sitk.WriteImage(sitk.GetImageFromArray(sphere_array), self.test_input_nii)

        result_image = gauss_seg(self.test_input_nii, 1, 2, 1, 1, 0.01)
        result_array = sitk.GetArrayFromImage(result_image).astype(float)

        np.testing.assert_array_equal(sphere_array, result_array)






