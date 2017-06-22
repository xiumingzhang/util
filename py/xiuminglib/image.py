"""
Image Processing Functions

Xiuming Zhang, MIT CSAIL
June 2017
"""

import numpy as np
import cv2


def binarize(im):
    """
    Binarizes images

    Args:
        im: numpy array of any interger type (uint8, uint16, etc.)
            If h-by-w, binarize each pixel at datatype midpoint.
            If h-by-w-3, convert to grayscale and treat as h-by-w.

    Returns:
        im_bin: binarized h-by-w numpy array of only 0's and 1's
    """

    # Compute threshold from datatype
    maxval = np.iinfo(im.dtype).max

    # RGB to grayscale
    if len(im.shape) == 3 and im.shape[2] == 3: # h-by-w-by-3
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    if len(im.shape) == 2: # h-by-w
        im_bin = im
        logicalmap = im > maxval / 2
        im_bin[logicalmap] = 1
        im_bin[np.logical_not(logicalmap)] = 0
    else:
        raise TypeError("'im' is neither h-by-w nor h-by-w-by-3")

    return im_bin


def remove_islands(im, connectivity, min_n_pixels):
    """
    Removes small islands of pixels from a binary image

    Args:
        im: 2D numpy array of only 0's and 1's
        connectivity: can only be 4 or 8
        min_n_pixels: minimum island size to keep

    Returns:
        im_clean: numpy array of 0's and 1's with small islands removed
    """

    # Validate inputs
    assert (len(im.shape) == 2), "'im' needs to have exactly two dimensions"
    assert np.array_equal(np.unique(im), np.array([0, 1])), "'im' needs to contain only 0's and 1's"
    assert (connectivity == 4 or connectivity == 8), "'connectivity' must be either 4 or 8"

    # Find islands, big or small
    nlabels, labelmap, leftx_topy_bbw_bbh_npix, _ = \
        cv2.connectedComponentsWithStats(im, connectivity)

    # Figure out background is 0 or 1
    bgval = im[labelmap == 0][0]

    # Set small islands to background value
    im_clean = im
    for i in range(1, nlabels): # skip the 0th island -- background
        island_size = leftx_topy_bbw_bbh_npix[i, -1]
        if island_size < min_n_pixels:
            im_clean[labelmap == i] = bgval

    return im_clean
