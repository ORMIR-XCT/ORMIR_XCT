import os
import sys

import vtk
import vtkbone
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

def file_read(input_image, output_image):
    """
    Reads an input and output and calls respective file function reader/writer.

    Parameters
    ----------
    input_image : string
        Path to the input image

    output_image : string
        Path to the output image

    Returns
    -------
    """

    # Extract directory, filename, basename, and extensions from the input image
    input_dir, input_filename = os.path.split(input_image)
    input_basename, input_extension = os.path.splitext(input_filename)

    # Calls file reader function
    if os.path.isfile(input_image) and (".nii" in input_extension.lower()):
        array, reader_output = nifti_reader(input_image)
    elif ".aim" in input_extension.lower():
        array, reader_output = aim_reader(input_image)
    else:
        print()
        print("Error: input file extension must be AIM or NII.")
        sys.exit(1)
    
    # Extract directory, filename, basename, and extensions from the output image
    output_dir, output_filename = os.path.split(output_image)
    output_basename, output_extension = os.path.splitext(output_filename)

    # Calls file output functions
    if output_extension.lower() == ".nii" or output_extension.lower() == ".nii.gz":
        output_image_filename = os.path.join(output_dir, output_basename + ".nii")
        nifti_writer(output_image_filename, array, reader_output)
    elif output_extension.lower() == ".aim":
        output_image_filename = os.path.join(output_dir, output_basename + ".aim")
        aim_writer(output_image_filename, array, reader_output)
    else:
        print()
        print("Error: output file extension must be AIM or NII.")
        sys.exit(1)


def aim_reader(input_image):
    """
    Reads an AIM file and sets up the needed variables to be used to write an image.

    Parameters
    ----------
    input_image : string
        Path to the input image

    Returns
    -------
    array: array
        Numpy array

    reader_output: vtkboneFiniteElementModel
        AIM reader output data object
    """
    aim_reader = vtkbone.vtkboneAIMReader()
    aim_reader.SetFileName(input_image)
    aim_reader.DataOnCellsOff()
    aim_reader.Update()
    aim = aim_reader.GetOutput()
    
    aim_scalars = aim.GetPointData().GetScalars()
    array = vtk_to_numpy(aim_scalars)
    
    dims = aim.GetDimensions()
    array = array.reshape(dims, order='F')
    return array, aim

def aim_writer(output_image, array, reader_output):
    """
    Writes an AIM image.

    Parameters
    ----------
    output_image : string
        Path to the output image
    
    array: array
        Numpy array

    reader_output: vtkboneFiniteElementModel
        Output data object

    Returns
    -------
    """

    # Convert NumPy array back to VTK image 
    temp = np.ascontiguousarray(np.atleast_3d(array))
    vtk_image = vtk.vtkImageData()
    vtkArray = numpy_to_vtk(
        temp.ravel(order='F'),
        deep=True, array_type=vtk.VTK_SHORT
    )

    dims = reader_output.GetDimensions()
    vtk_image.SetDimensions(dims)
    vtk_image.SetSpacing(reader_output.GetSpacing())
    vtk_image.SetOrigin(reader_output.GetOrigin())
    vtk_image.GetPointData().SetScalars(vtkArray)


    aim_writer = vtkbone.vtkboneAIMWriter()
    aim_writer.SetInputData(vtk_image)
    aim_writer.SetFileName(output_image)
    aim_writer.Write()



def nifti_reader(input_image):
    """
    Reads an NIFTI file and sets up the needed variables to be used to write an image.

    Parameters
    ----------
    input_image : string
        Path to the input image

    Returns
    -------
    array: array
        Numpy array

    reader_output: vtkboneFiniteElementModel
        NIFTI reader output data object
    """
    nifti_reader = vtk.vtkNIFTIImageReader()
    nifti_reader.SetFileName(input_image)
    nifti_reader.Update()
    nifti = nifti_reader.GetOutput()
    nifti_scalars = nifti.GetPointData().GetScalars()

    array = vtk_to_numpy(nifti_scalars)

    dims = nifti.GetDimensions()

    # Need to use Fortran-like index ordering for OpenVMS
    array = array.reshape(dims, order='F')
    return array, nifti
    


def nifti_writer(output_image, array, reader_output):
    """
    Writes an NIFTI image.

    Parameters
    ----------
    output_image : string
        Path to the output image
    
    array: array
        Numpy array

    reader_output: vtkboneFiniteElementModel
        Output data object

    Returns
    -------
    """

    # Convert NumPy array back to VTK image 
    temp = np.ascontiguousarray(np.atleast_3d(array))
    vtk_image = vtk.vtkImageData()
    vtkArray = numpy_to_vtk(
        temp.ravel(order='F'),
        deep=True, array_type=vtk.VTK_SHORT
    )
    vtk_image.SetDimensions(array.shape)
    vtk_image.SetSpacing(reader_output.GetSpacing())
    vtk_image.SetOrigin(reader_output.GetOrigin())
    vtk_image.GetPointData().SetScalars(vtkArray)

    nifti_writer = vtk.vtkNIFTIImageWriter()
    nifti_writer.SetInputData(vtk_image)
    nifti_writer.SetFileName(output_image)
    nifti_writer.Write()