"""
Handling (Multi-Layer) OpenEXR Files

Xiuming Zhang, MIT CSAIL
August 2018
"""

from os.path import abspath, dirname
import numpy as np
import cv2

import config
logger, thisfile = config.create_logger(abspath(__file__))


def load_exr(exr_path):
    """
    Load .exr as a dict, by converting it to a .npz and loading that .npz

    Args:
        exr_path: Path to the .exr file
            String

    Returns:
        data: Loaded OpenEXR data
            dict
    """
    from time import time
    from subprocess import call

    # Convert to .npz
    npz_f = '/tmp/%s.npz' % time()
    call(['python2',
          '%s/../commandline/exr2npz.py' % dirname(abspath(__file__)),
          exr_path,
          npz_f])

    # Load this .npz
    data = np.load(npz_f)
    return data


def map2im(exr_path, map_type, outpath):
    """
    Convert a .exr map to a .png image, by scaling, offsetting, and inverting
        For depth, background is black; close to camera is bright, and far away is dark,
            as a result of inverting
        For normal, background is black; inverting is applied to comply with industry
            standards (e.g., AE)

    Args:
        exr_path: Path to the .exr file to convert
            String
        map_type: Map type
            'depth' or 'normal'
        outpath: Path to the result .png file
            String
    """
    logger_name = thisfile + '->map2im()'

    if map_type not in ('depth', 'normal'):
        raise NotImplementedError(map_type)

    # Load RGBA .exr
    # cv2.imread() can't load more than three channels from .exr even with IMREAD_UNCHANGED
    # Has to go through IO. Maybe there's a better way?
    data = load_exr(exr_path)
    arr = np.dstack((data['B'], data['G'], data['R']))
    alpha = data['A']

    if map_type == 'normal':
        # [-1, 1]
        im = (1 - (arr / 2 + 0.5)) * 255
        bg = np.zeros(im.shape)
        alpha = np.dstack((alpha, alpha, alpha))
        im = np.multiply(alpha, im) + np.multiply(1 - alpha, bg)
        cv2.imwrite(outpath, im.astype(int))
    else:
        assert (arr[..., 0] == arr[..., 1]).all() and (arr[..., 0] == arr[..., 2]).all(), \
            "A valid depth map must have all three channels the same"
        arr = arr[..., 0] # these raw values are NOT anti-aliased, so only one crazy big value
        is_fg = arr < arr.max()
        min_val, max_val = arr[is_fg].min(), arr[is_fg].max()
        im = np.zeros(arr.shape)
        im[is_fg] = 255 * (max_val - arr[is_fg]) / (max_val - min_val)
        bg = np.zeros(im.shape)
        im = np.multiply(alpha, im) + np.multiply(1 - alpha, bg) # anti-aliasing done here
        cv2.imwrite(outpath, im.astype(int))

    logger.name = logger_name
    logger.info("%s converted to %s", exr_path, outpath)
