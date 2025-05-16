import itk
import SimpleITK as sitk
from ormir_xct.util.sitk_itk import sitk_itk

#---------------#
# NIFTI Reading
#---------------#
nifti_read_path = "example/test.nii"
isq_write_path = "/test/test.isq"

output_image = sitk.ReadImage(nifti_read_path, sitk.sitkInt16)
outputImageISQ = sitk_itk(output_image)

#---------------#
# ISQ Writing
#---------------#
image_type = itk.Image[itk.ctype("signed short"), 3]
writer = itk.ImageFileWriter[image_type].New()
image_io = itk.ScancoImageIO.New()
writer.SetImageIO(image_io)
writer.SetInput(outputImageISQ)
writer.SetFileName(isq_write_path)
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