import vtk
import vtkbone
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

#-------------#
# AIM Reading
#-------------#
nifti_read_path = "example/test.nii"
aim_write_path = "test/test2.AIM"

nifti_reader = vtk.vtkNIFTIImageReader()
nifti_reader.SetFileName(nifti_read_path)
nifti_reader.Update()
nifti = nifti_reader.GetOutput()
nifti_scalars = nifti.GetPointData().GetScalars()

array = vtk_to_numpy(nifti_scalars)

dims = nifti.GetDimensions()

# Need to use Fortran-like index ordering for OpenVMS
array = array.reshape(dims, order='F')


#-------------#
# AIM Writing
#-------------#
# Convert NumPy array back to VTK image 
temp = np.ascontiguousarray(np.atleast_3d(array))
vtk_image = vtk.vtkImageData()
vtkArray = numpy_to_vtk(
    temp.ravel(order='F'),
    deep=True, array_type=vtk.VTK_SHORT
)
vtk_image.SetDimensions(dims)
vtk_image.SetSpacing(nifti.GetSpacing())
vtk_image.SetOrigin(nifti.GetOrigin())
vtk_image.GetPointData().SetScalars(vtkArray)


aim_writer = vtkbone.vtkboneAIMWriter()
aim_writer.SetInputData(vtk_image)
aim_writer.SetFileName(aim_write_path)
aim_writer.Write()

