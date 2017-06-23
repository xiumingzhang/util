"""
Image Processing Functions

Xiuming Zhang, MIT CSAIL
June 2017
"""

from os.path import abspath
from warnings import warn
import logging
import numpy as np
import cv2
from scipy.interpolate import RectBivariateSpline

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


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


def interp2(im, query_pts):
    """
    Query interpolated values of float lactions (bivariate spline approximation)

    Args:
        im: h-by-w or h-by-w-by-c numpy array
            Each channel is interpolated independently.
        query_pts: n-by-2 numpy array
            +-----------> dim1
            |
            |
            |
            v dim0

    Returns:
        interp_val: n-by-c numpy array
    """

    # Figure out image size and number of channels
    if len(im.shape) == 3:
        h, w, c = im.shape
        if c == 1: # single dimension
            im = im[:, :, 0]
    elif len(im.shape) == 2:
        h, w = im.shape
        c = 1
    else:
        raise ValueError("'im' must have either two or three dimensions")

    # Validate inputs
    assert (len(query_pts.shape) == 2), "'query_pts' must have exactly two dimensions"
    assert (query_pts.shape[1] == 2), "Second dimension of 'query_pts' must be 2"

    x = np.arange(h)
    y = np.arange(w)
    query_x = query_pts[:, 0]
    query_y = query_pts[:, 1]

    if c == 1: # Single channel
        z = im
        spline_obj = RectBivariateSpline(x, y, z)
        logging.info("%s: Interpolation started", thisfile)
        interp_val = spline_obj.__call__(query_x, query_y, grid=False)
        logging.info("%s: Interpolation done", thisfile)
    else: # Multiple channels
        warn("Support for 'im' having multiple channels has not been thoroughly tested!")
        interp_val = np.zeros((len(query_x), c))
        for i in range(c):
            z = im[:, :, i]
            spline_obj = RectBivariateSpline(x, y, z)
            logging.info("%s: Interpolation started for channel %d/%d", thisfile, i + 1, c)
            interp_val[:, i] = spline_obj.__call__(query_x, query_y, grid=False)
            logging.info("%s: Interpolation done for channel %d/%d", thisfile, i + 1, c)

    return interp_val
