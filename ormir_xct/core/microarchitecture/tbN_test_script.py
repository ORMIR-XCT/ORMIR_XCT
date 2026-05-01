import SimpleITK as sitk
from ormir_xct.core.microarchitecture.trabecular_microarchitecture import trabecular_number
import argparse
from pathlib import Path

import time

parser = argparse.ArgumentParser()
parser.add_argument("-trab_mask", help = "Input trabecular mask", default = '/Users/samuelyu/Documents/Manske_Lab_Coop/test_data/Tb.N Test/2026 CSI/csi_0179_rl_v01_seg_126.nii.gz')
parser.add_argument("-bone_mask", help = "Input mask of bone", default = '/Users/samuelyu/Documents/Manske_Lab_Coop/test_data/Tb.N Test/2026 CSI/csi_0179_rl_v01_trab_mask.nii.gz')

args = parser.parse_args()

bone_mask = sitk.ReadImage(args.bone_mask)
trab_mask = sitk.ReadImage(args.trab_mask)
print("Started.")
begin = time.process_time()
tb_n = trabecular_number(trab_mask, bone_mask)
end = time.process_time()

print(f"(Processed in {end - begin:.6f}s): Trabecular Number for {Path(args.bone_mask).name} using mask {Path(args.trab_mask).name} is {tb_n}")



