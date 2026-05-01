"""
A quick script written to help extract labels from an existing segmentation

"""
import numpy as np
import SimpleITK as sitk
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('input_mask', type = str, help = "Path to input mask")
parser.add_argument('-label', type = int, default = 126, help = "Label id to extract from input mask")
args = parser.parse_args()

# read and convert image
input_path = Path(args.input_mask)
mask = sitk.ReadImage(input_path)
mask_np = sitk.GetArrayFromImage(mask)

# extract label id
new_mask_np = mask_np == args.label
new_mask = sitk.GetImageFromArray(new_mask_np.astype(int))

# write image
if input_path.name.endswith(".nii.gz"):
    base = input_path.name[:-7]  # strip ".nii.gz"
    output_path = input_path.with_name(f"{base}_{args.label}.nii.gz")
else:
    output_path = input_path.with_stem(f"{input_path.stem}_{args.label}")


new_mask.CopyInformation(mask)
sitk.WriteImage(new_mask, output_path)
print(f"Writing new binary mask extracted from label {args.label} to {output_path}")


# The data I am processing uses 126 as the trabecular label, 127 as cortical shell/periosteal