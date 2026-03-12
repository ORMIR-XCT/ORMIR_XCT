import os
import argparse
import SimpleITK as sitk

from ormir_xct.core.segmentation.autocontour import autocontour_gobj


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate proximal, distal, and combined masks from GOBJ contours."
    )
    parser.add_argument("image_path", type=str, help="Input image path")
    parser.add_argument(
        "dst_gobj_path",
        type=str,
        help="Distal contour from UCT_EVALUATION",
    )
    parser.add_argument(
        "prx_gobj_path",
        type=str,
        help="Proximal contour from UCT_EVALUATION",
    )
    return parser


def run(image_path: str, dst_gobj_path: str, prx_gobj_path: str) -> int:
    image_dir = os.path.dirname(image_path)
    basename = os.path.splitext(os.path.basename(image_path))[0]

    prx_mask_path = os.path.join(image_dir, basename + "_PRX_MASK.nii")
    dst_mask_path = os.path.join(image_dir, basename + "_DST_MASK.nii")
    mask_path = os.path.join(image_dir, basename + "_MASK.nii")

    dst_mask, prx_mask, mask = autocontour_gobj(
        image_path, dst_gobj_path, prx_gobj_path
    )

    print(f"Writing mask to {mask_path}")
    sitk.WriteImage(mask, mask_path)

    print(f"Writing proximal mask to {prx_mask_path}")
    sitk.WriteImage(prx_mask, prx_mask_path)

    print(f"Writing distal mask to {dst_mask_path}")
    sitk.WriteImage(dst_mask, dst_mask_path)

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return run(args.image_path, args.dst_gobj_path, args.prx_gobj_path)


if __name__ == "__main__":
    raise SystemExit(main())
