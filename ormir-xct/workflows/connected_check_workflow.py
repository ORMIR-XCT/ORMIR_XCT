import argparse
import os

import SimpleITK as sitk


from ormir_xct.joint_space_analysis.connected_check import connected_check



def connected_check_workflow():
    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("handOA_dir", type=str)
    
    args = parser.parse_args()


    # Loop through HandOA samples
    # Each HandOA study ID will have 3 joints to check: DIP2, DIP3, TMC
    for folder in os.listdir(args.handOA_dir):
        # Get the next folder
        next_folder = os.path.join(args.handOA_dir, folder)

        if os.path.isdir(next_folder):
            print("Checking if joint is connected for: " + str(next_folder))

            # Get study ID number
            study_name = os.path.basename(next_folder)
            study_id = os.path.basename(next_folder)[-3:]

            # DIP2 joint
            dip2_path = os.path.join(next_folder, study_id + "_DIP2_MASK.nii")
            dip2_img = sitk.ReadImage(dip2_path, sitk.sitkUInt8)
            print("\tDIP2 segmentation: " + str(dip2_path))

            dip2_labels = connected_check(dip2_img)
            if dip2_labels > 1:
                print("\tDIP2 segmentation NOT CONNECTED")
            elif dip2_labels == 1:
                print("\tDIP2 segmentation is CONNECTED")
            else:
                print("\tDIP2 segmentation has 0 labels")

            # DIP3 joint
            dip3_path = os.path.join(next_folder, study_id + "_DIP3_MASK.nii")
            dip3_img = sitk.ReadImage(dip3_path, sitk.sitkUInt8)
            print("\tDIP3 segmentation: " + str(dip3_img))

            dip3_labels = connected_check(dip3_path)
            if dip3_labels > 1:
                print("\tDIP3 segmentation NOT CONNECTED")
            elif dip3_labels == 1:
                print("\tDIP3 segmentation is CONNECTED")
            else:
                print("\tDIP3 segmentation has 0 labels")

            # TMC joint
            stack_reg_folder = os.path.join(next_folder, "stackRegistrationOutput")
            tmc_path = os.path.join(stack_reg_folder, "FULL_IMAGE_MASK.nii")
            tmc_img = sitk.ReadImage(tmc_path, sitk.sitkUInt8)
            print("\tTMC segmentation: " + str(tmc_path))

            tmc_labels = connected_check(tmc_img)
            if tmc_labels > 1:
                print("\tTMC segmentation NOT CONNECTED")
            elif tmc_labels == 1:
                print("\tTMC segmentation is CONNECTED")
            else:
                print("\tTMC segmentation has 0 labels")

            print("************************************")


if __name__ == "__main__":
    connected_check_workflow()