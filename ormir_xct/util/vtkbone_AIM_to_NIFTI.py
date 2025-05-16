import vtk
import vtkbone
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

#---------------#
# AIM Reading
#---------------#
aim_read_path = "example/DYNACT2_214_TMC_MID.AIM"
nifti_write_path = "test/test.nii"

aim_reader = vtkbone.vtkboneAIMReader()
aim_reader.SetFileName(aim_read_path)
aim_reader.DataOnCellsOff()
aim_reader.Update()
aim = aim_reader.GetOutput()
aim_scalars = aim.GetPointData().GetScalars()
array = vtk_to_numpy(aim_scalars)
dims = aim.GetDimensions()
# Need to use Fortran-like index ordering for OpenVMS
array = array.reshape(dims, order='F')

#---------------#
# NIFTI Writing
#---------------#
# Convert NumPy array back to VTK image 
temp = np.ascontiguousarray(np.atleast_3d(array))
vtk_image = vtk.vtkImageData()
vtkArray = numpy_to_vtk(
    temp.ravel(order='F'),
    deep=True, array_type=vtk.VTK_SHORT
)
vtk_image.SetDimensions(array.shape)
vtk_image.SetSpacing(aim.GetSpacing())
vtk_image.SetOrigin(aim.GetOrigin())
vtk_image.GetPointData().SetScalars(vtkArray)

nifti_writer = vtk.vtkNIFTIImageWriter()
nifti_writer.SetInputData(vtk_image)
nifti_writer.SetFileName("nifti_write_path")
nifti_writer.Write()