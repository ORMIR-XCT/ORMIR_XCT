import os
import sys

import itk
import SimpleITK as sitk
from ormir_xct.util.sitk_itk import itk_sitk, sitk_itk


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
        reader = nifti_reader(input_image)
    elif ".aim" in input_extension.lower():
        reader = aim_isq_reader(input_image)
    elif ".isq" in input_extension.lower():
        reader = aim_isq_reader(input_image)
    else:
        print()
        print("Error: input file extension must be AIM, NII, ISQ.")
        sys.exit(1)
    
    # Extract directory, filename, basename, and extensions from the output image
    output_dir, output_filename = os.path.split(output_image)
    output_basename, output_extension = os.path.splitext(output_filename)

    # Calls file output functions
    if output_extension.lower() == ".nii" or output_extension.lower() == ".nii.gz":
        output_image_filename = os.path.join(output_dir, output_basename + ".nii")
        nifti_writer(output_image_filename, reader)
    elif output_extension.lower() == ".isq":
        output_image_filename = os.path.join(output_dir, output_basename + ".ISQ")
        isq_writer(output_image_filename, reader)
    else:
        print()
        print("Error: output file extension must be ISQ or NII.")
        sys.exit(1)


def aim_isq_reader(input_image):
    """
    Reads an AIM or ISQ file and sets up the needed variables to be used to write an image.

    Parameters
    ----------
    input_image : string
        Path to the input image

    Returns
    -------
    reader: class object
        Output image

    """
    image_type = itk.Image[itk.ctype("signed short"), 3]
    reader = itk.ImageFileReader[image_type].New()
    image_io = itk.ScancoImageIO.New()
    reader.SetImageIO(image_io)
    reader.SetFileName(input_image)
    reader.Update()
    return reader

def nifti_writer(output_image_path, reader_output):
    """
    Writes a NIFTI image.

    Parameters
    ----------
    output_image : string
        Path to the output image

    reader_output: image reader class object
        Output data object

    Returns
    -------
    """
    output_image = itk_sitk(reader_output.GetOutput())
    sitk.WriteImage(output_image, str(output_image_path))

def nifti_reader(input_image):
    """
    Reads a NIFTI file and sets up the needed variables to be used to write an image.

    Parameters
    ----------
    input_image : string
        Path to the input image

    Returns
    -------
    reader: class object
        Output image

    """
    reader = sitk.ReadImage(input_image, sitk.sitkInt16)
    return reader

def isq_writer(input_image, reader):
    """
    Writes an ISQ image.

    Parameters
    ----------
    output_image : string
        Path to the output image

    reader_output: image reader class object
        Output data object

    Returns
    -------
    """
    outputImageISQ = sitk_itk(reader)
    image_type = itk.Image[itk.ctype("signed short"), 3]
    writer = itk.ImageFileWriter[image_type].New()
    image_io = itk.ScancoImageIO.New()
    writer.SetImageIO(image_io)
    writer.SetInput(outputImageISQ)
    writer.SetFileName(input_image)
    writer.Update()

    # Set header information
    image_io.SetEnergy(68)
    image_io.SetIntensity(1.47)
    image_io.SetReconstructionAlg(3)
    image_io.SetSite(4)
    image_io.SetScannerID(3401)
    image_io.SetPatientIndex(2567)
    image_io.SetMeasurementIndex(12778)
    image_io.SetSampleTime(100)
    image_io.SetScannerType(9)
    image_io.SetMuScaling(8192)
    image_io.SetNumberOfProjections(900)
    image_io.SetSliceIncrement(0.0609)
    image_io.SetSliceThickness(0.0609)

    writer.Write()