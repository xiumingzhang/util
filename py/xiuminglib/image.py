"""
Image Processing Functions

Xiuming Zhang, MIT CSAIL
June 2017
"""

from os.path import abspath
import logging
import numpy as np
import cv2
from scipy.interpolate import RectBivariateSpline, interp2d
import logging_colorer # noqa: F401 # pylint: disable=unused-import

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


def binarize(im):
    """
    Binarizes images

    Args:
        im: Image to binarize
            Numpy array of any interger type (uint8, uint16, etc.)
                - If h-by-w, binarize each pixel at datatype midpoint
                - If h-by-w-3, convert to grayscale and treat as h-by-w

    Returns:
        im_bin: Binarized image
            h-by-w numpy array of only 0's and 1's
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


def remove_islands(im, min_n_pixels, connectivity=4):
    """
    Removes small islands of pixels from a binary image

    Args:
        im: Input binary image
            2D numpy array of only 0's and 1's
        min_n_pixels: Minimum island size to keep
            Integer
        connectivity: Definition of "connected"
            Either 4 or 8
            Optional; defaults to 4

    Returns:
        im_clean: Output image with small islands removed
            2D numpy array of 0's and 1's
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


def query_float_locations(im, query_pts, method='bilinear'):
    """
    Query interpolated values of float lactions on image using
        1. Bilinear interpolation (default)
            - Can break big matrices into patches and work locally
        2. Bivariate spline interpolation
            - Fitting a global spline, so memory-intensive and shows global effects

    Pixel values are considered as values at pixel centers. E.g., if im[0, 1] is 0.68,
        then f(0.5, 1.5) is deemed to evaluate to 0.68 exactly

    Args:
        im: Rectangular grid of data
            h-by-w or h-by-w-by-c numpy array
            Each of c channels is interpolated independently
        query_pts: Query locations
            Array-like of shape (n, 2) or (2,)
            +-----------> dim1
            |
            |
            |
            v dim0
        method: Interpolation method
            'spline' or 'bilinear'
            Optional; defaults to 'bilinear'

    Returns:
        interp_val: Interpolated values at query locations
            Numpy array of shape (n, c) or (c,)
    """
    thisfunc = thisfile + '->query_float_locations()'

    # Figure out image size and number of channels
    if im.ndim == 3:
        h, w, c = im.shape
        if c == 1: # single dimension
            im = im[:, :, 0]
    elif im.ndim == 2:
        h, w = im.shape
        c = 1
    else:
        raise ValueError("'im' must have either two or three dimensions")

    # Validate inputs
    query_pts = np.array(query_pts)
    is_one_point = False
    if query_pts.shape == (2,):
        is_one_point = True
        query_pts = query_pts.reshape(1, 2)
    elif query_pts.ndim != 2 or query_pts.shape[1] != 2:
        raise ValueError("Shape of input must be either (2,) or (n, 2)")

    # Querying one point, very likely in a loop -- no printing
    if is_one_point:
        logging.getLogger().setLevel(logging.WARN)

    x = np.arange(h) + 0.5 # pixel center
    y = np.arange(w) + 0.5
    query_x = query_pts[:, 0]
    query_y = query_pts[:, 1]

    if np.min(query_x) < 0 or np.max(query_x) > h or np.min(query_y) < 0 or np.max(query_y) > w:
        logging.warning("%s: Sure you want to query points outside 'im'?", thisfunc)

    if c == 1:
        # Single channel

        z = im

        logging.info("%s: Interpolation (method: %s) started", thisfunc, method)

        if method == 'spline':
            spline_obj = RectBivariateSpline(x, y, z)
            interp_val = spline_obj(query_x, query_y, grid=False)

        elif method == 'bilinear':
            f = interp2d(y, x, z, kind='linear')
            interp_val = f(query_y, query_x)

        else:
            raise NotImplementedError("Other interplation methods")

        logging.info("%s:     ... done", thisfunc)

    else:
        # Multiple channels

        logging.warning("%s: Support for 'im' having multiple channels has not been thoroughly tested!", thisfunc)
        interp_val = np.zeros((len(query_x), c))
        for i in range(c):

            z = im[:, :, i]

            logging.info("%s: Interpolation (method: %s) started for channel %d/%d", thisfunc, method, i + 1, c)

            if method == 'spline':
                spline_obj = RectBivariateSpline(x, y, z)
                interp_val[:, i] = spline_obj(query_x, query_y, grid=False)

            elif method == 'bilinear':
                f = interp2d(y, x, z, kind='linear')
                interp_val[:, i] = f(query_y, query_x)

            else:
                raise NotImplementedError("Other interplation methods")

            logging.info("%s:     ... done", thisfunc)

    if is_one_point:
        interp_val = interp_val.reshape(c)

    return interp_val
