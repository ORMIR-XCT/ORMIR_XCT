import vtk
import vtkbone
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

#-------------#
# AIM Reading
#-------------#
nifti_reader = vtk.vtkNIFTIImageReader()
nifti_reader.SetFileName("/Users/sarahelmahdy/Desktop/ORMIR_XCT/startup/test.nii")
nifti = nifti_reader.GetOutput()

# array = vtk_to_numpy(nifti.GetPointData().GetScalars())

# Need to use Fortran-like index ordering for OpenVMS
# array = array.reshape(nifti.GetFileDimensionality(), order='F')

#-------------#
# AIM Writing
#-------------#
# Convert NumPy array back to VTK image 
# temp = np.ascontiguousarray(np.atleast_3d(array))
vtk_image = vtk.vtkImageData()
# vtkArray = numpy_to_vtk(
#     temp.ravel(order='F'),
#     deep=True, array_type=vtk.VTK_SHORT
# )
vtk_image.SetDimensions(nifti.GetDimensions())
vtk_image.SetSpacing(nifti.GetSpacing())
vtk_image.SetOrigin(nifti.GetOrigin())

aim_writer = vtkbone.vtkboneAIMWriter()
aim_writer.SetInputData(vtk_image)
aim_writer.NewProcessingLogOff()
# aim_writer.SetProcessingLog(proc_log)
aim_writer.SetFileName("/Users/sarahelmahdy/Desktop/ORMIR_XCT/startup/test.AIM")
aim_writer.Write()

# Read in processing log as string
with open("/Users/sarahelmahdy/Desktop/ORMIR_XCT/startup/proc_log.txt", "r") as file:
    proc_log = file.read()

