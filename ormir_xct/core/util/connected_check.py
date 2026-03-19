"""
Created by:   Michael Kuczynski
Created on:   Sept. 09, 2022

Description: Uses connected component labelling to check if a joint
              segmentation is connected (i.e., JS = 0).
"""

import SimpleITK as sitk


def connected_check(image):
    """
    Runs a connected component analysis on a binary image and returns the
    number of components in the image.

    Parameters
    ----------
    image_path : SimpleITK.Image
        Path to the binary image.

    Returns
    -------
    labels : int
        Number of labels in the binary image. -1 is returned if the image can't
        be read in.
    """

    image_conn = sitk.ConnectedComponent(image, True)
    conn_list = sitk.RelabelComponent(image_conn, sortByObjectSize=True)

    label_stats = sitk.LabelShapeStatisticsImageFilter()
    label_stats.Execute(conn_list)
    labels = label_stats.GetNumberOfLabels()

    return labels
