import itk
import SimpleITK as sitk
from ormir_xct.util.sitk_itk import itk_sitk

#---------------#
# ISQ Reading
#---------------#
isq_read_path = "example/C0004255.ISQ"
nifti_write_path = "test/test4.nii"

image_type = itk.Image[itk.ctype("signed short"), 3]
reader = itk.ImageFileReader[image_type].New()
image_io = itk.ScancoImageIO.New()
reader.SetImageIO(image_io)
reader.SetFileName(isq_read_path)
reader.Update()

#---------------#
# NIFTI Writing
#---------------#
output_image = itk_sitk(reader.GetOutput())
sitk.WriteImage(output_image, str(nifti_write_path))
