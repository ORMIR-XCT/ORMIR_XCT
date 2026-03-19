"""
Created by: Michael Kuczynski
Created on: June 9th, 2022

Description: Reimplementation of the IPL JSW Analysis
              as part of the ORMIR 2022 workshop.

Overview of JSW Steps:
  1. Image padding (ignored as not needed in Python)
  2. Dilation
  3. Erosion
  4. Threshold out JS Mask
  5. DT sphere filling
  6. Compute JSW parameters

Usage: python jsw_main.py JOINT_SEG.nii

Inputs:
   1. Joint segmentation image (binary)

Outputs:
  1. Joint Space Mask Image (MHA/NIFTI)
  2. Joint Space Output (text file)
"""

import os
import argparse
import SimpleITK as sitk

from ormir_xct.core.joint_space_analysis.jsw_morphometry import (
    jsw_dilate,
    jsw_erode,
    jsw_pad,
    jsw_parameters,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jsw-main",
        description="Reimplementation of the IPL joint space width analysis workflow.",
    )
    parser.add_argument(
        "joint_seg", type=str, help="Path to the joint segmentation image"
    )
    parser.add_argument(
        "--voxel-size",
        type=float,
        default=0.0607,
        help="Voxel size in mm (default: 0.0607)",
    )
    parser.add_argument(
        "--write-intermediate",
        action="store_true",
        help="Write intermediate dilated, eroded, and mask images",
    )
    return parser


def run(
    joint_seg: str,
    voxel_size: float = 0.0607,
    write_intermediate: bool = False,
) -> int:
    output_path = os.path.dirname(joint_seg)
    filename = os.path.basename(joint_seg)
    basename = os.path.splitext(filename)[0]

    img = sitk.ReadImage(joint_seg, sitk.sitkUInt8)

    print("Padding image...")
    pad_image = jsw_pad(img)

    print("Dilating image...")
    dilated_image = jsw_dilate(pad_image)

    print("Eroding image...")
    eroded_image, js_mask, dilated_js_mask = jsw_erode(dilated_image, pad_image)

    if write_intermediate:
        sitk.WriteImage(
            dilated_image, os.path.join(output_path, f"{basename}_DILATE.nii")
        )
        sitk.WriteImage(
            eroded_image, os.path.join(output_path, f"{basename}_ERODE.nii")
        )
        sitk.WriteImage(js_mask, os.path.join(output_path, f"{basename}_JS_MASK.nii"))
        sitk.WriteImage(
            dilated_js_mask,
            os.path.join(output_path, f"{basename}_DILATED_JS_MASK.nii"),
        )

    print("Computing thickness...")
    dt_img, jsw_params = jsw_parameters(
        pad_image,
        dilated_js_mask,
        basename,
        output_path,
        js_mask,
        voxel_size,
        True,
        False,
    )

    dt_img.SetOrigin(js_mask.GetOrigin())
    dt_img.SetSpacing(js_mask.GetSpacing())
    dt_img.SetDirection(js_mask.GetDirection())

    dt_img = sitk.Mask(dt_img, js_mask)

    dt_path = os.path.join(output_path, f"{basename}_DT.nii")
    print(f"Writing thickness map to {dt_path}")
    sitk.WriteImage(dt_img, dt_path)

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    return run(
        joint_seg=args.joint_seg,
        voxel_size=args.voxel_size,
        write_intermediate=args.write_intermediate,
    )


if __name__ == "__main__":
    raise SystemExit(main())
