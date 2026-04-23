"""
Temporary module for SMI calculation

Created by: Samuel
Created on: April 18, 2026

"""
import SimpleITK as sitk
import numpy as np
import vtk

from SimpleITK.utilities import sitk2vtk


def compute_bv(bone_mask: np.ndarray):
    """
    Calculate bone volume. 

    Parameters:
    ----------
    bone_mask: np.ndarray
        Numpy array representing a binary mask of bone.
    
    """
    bone_mask_np = sitk.GetArrayFromImage(bone_mask)
    bone_mask_np = bone_mask_np != 0

    spacing = bone_mask.GetSpacing()

    voxel_volume = spacing[0] * spacing[1] * spacing[2]
    return bone_mask_np.sum() * voxel_volume


def compute_bs(trab_seg, spacing):
    # convert to vtk compatible object for mesh creation
    vtk_trab_seg = sitk2vtk(trab_seg)


    # Use Marching Cubes (Flying Edges) to produce a surface mesh
    flying_edges = vtk.vtkFlyingEdges3D()
    flying_edges.SetInputData(vtk_trab_seg)
    flying_edges.SetValue(0, 0.5) 
    flying_edges.ComputeNormalsOn()
    flying_edges.Update()




def structure_model_index(trab_seg):
    """
    Approximate implementation of the SMI calculation discussed in 
    https://www.tandfonline.com/doi/abs/10.1080/01495739708936692

    
    Parameters
    ----------
    trab_seg : SimpleITK.Image
        Binary image representing trabecular segmentation.
    peri_mask : SimpleITK.Image
        Binary image representing periosteal mask.

    Returns
    -------
    float
        Structure Model Index (SMI)
    """
    bone_volume = compute_bv(trab_seg)
    
    # use initial and dilated bone surfaces to estimate the derivative bs/bv
    initial_bone_surface = compute_bs_vtk(trab_seg)

    # dilated_bone_surface 

    

    







