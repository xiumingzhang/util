"""
Handling (Multi-Layer) OpenEXR Files

Xiuming Zhang, MIT CSAIL
August 2018
"""

from os import makedirs
from os.path import abspath, dirname, exists, join
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
          '%s/../../commandline/exr2npz.py' % dirname(abspath(__file__)),
          exr_path,
          npz_f])

    # Load this .npz
    data = np.load(npz_f)
    return data


def generate_depth_image(exr_prefix, outpath):
    """
    Combine an aliased, raw depth map and an anti-aliased alpha map into a .png image,
        with background being black, close to camera being bright, and far away being dark

    Args:
        exr_prefix: Common prefix of .exr paths
            String
        outpath: Path to the result .png file
            String
    """
    logger_name = thisfile + '->generate_depth_image()'

    # Load alpha
    arr = cv2.imread(exr_prefix + '_a.exr', cv2.IMREAD_UNCHANGED)
    assert (arr[:, :, 0] == arr[:, :, 1]).all() and (arr[:, :, 1] == arr[:, :, 2]).all(), \
        "A valid alpha map must have all three channels the same"
    alpha = arr[:, :, 0]

    # Load depth
    arr = cv2.imread(exr_prefix + '_z.exr', cv2.IMREAD_UNCHANGED)
    assert (arr[..., 0] == arr[..., 1]).all() and (arr[..., 1] == arr[..., 2]).all(), \
        "A valid depth map must have all three channels the same"
    depth = arr[..., 0] # these raw values are aliased, so only one crazy big value

    is_fg = depth < depth.max()
    max_val = depth[is_fg].max()
    depth[depth > max_val] = max_val # cap background depth at the object maximum depth
    min_val = depth.min()

    im = 255 * (max_val - depth) / (max_val - min_val) # [0, 255]

    # Anti-aliasing
    bg = np.zeros(im.shape)
    im = np.multiply(alpha, im) + np.multiply(1 - alpha, bg)
    cv2.imwrite(outpath, im.astype(int))

    logger.name = logger_name
    logger.info("Depth image generated at %s", outpath)


def generate_normal_image(exr_path, outpath):
    """
    Convert an RGBA .exr normal map to a .png normal image, with background being black
        and complying with industry standards (e.g., Adobe AE)

    Args:
        exr_path: Path to the .exr file to convert
            String
        outpath: Path to the result .png file
            String
    """
    logger_name = thisfile + '->generate_normal_image()'

    # Load RGBA .exr
    # cv2.imread() can't load more than three channels from .exr even with IMREAD_UNCHANGED
    # Has to go through IO. Maybe there's a better way?
    data = load_exr(exr_path)
    arr = np.dstack((data['B'], data['G'], data['R']))
    alpha = data['A']

    # [-1, 1]
    im = (1 - (arr / 2 + 0.5)) * 255
    bg = np.zeros(im.shape)
    alpha = np.dstack((alpha, alpha, alpha))
    im = np.multiply(alpha, im) + np.multiply(1 - alpha, bg)
    cv2.imwrite(outpath, im.astype(int))

    logger.name = logger_name
    logger.info("Normal image generated at %s", outpath)


def intrinsic_images_from_lighting_passes(exr_path, outdir):
    """
    Extract intrinsic images from a multi-layer .exr of lighting passes

    Args:
        exr_path: Path to the multi-layer .exr file
            String
        outdir: Directory to the result .png files to
            String
    """
    from xiuminglib import visualization as xv

    logger_name = thisfile + '->intrinsic_images_from_lighting_passes()'

    gamma = 4

    if not exists(outdir):
        makedirs(outdir)

    data = load_exr(exr_path)

    def collapse_passes(components):
        ch_arrays = []
        for ch in ['R', 'G', 'B']:
            comp_arrs = []
            for comp in components:
                comp_arrs.append(data[comp + '.' + ch])
            ch_array = np.sum(comp_arrs, axis=0) # sum components
            ch_arrays.append(ch_array)
        # Handle alpha channel
        first_alpha = data[components[0] + '.A']
        for ci in range(1, len(components)):
            assert (first_alpha == data[components[ci] + '.A']).all(), \
                "Alpha channels of all passes must be the same"
        ch_arrays.append(first_alpha)
        return np.dstack(ch_arrays)

    # Albedo
    albedo = collapse_passes(['diffuse_color', 'glossy_color'])
    xv.matrix_as_image(albedo, outpath=join(outdir, 'albedo.png'), gamma=gamma)

    # Shading
    shading = collapse_passes(['diffuse_indirect', 'diffuse_direct'])
    xv.matrix_as_image(shading, join(outdir, 'shading.png'), gamma=gamma)

    # # Specularity
    # specularity = collapse_passes(['glossy_indirect', 'glossy_direct'])
    # xv.matrix_as_image(specularity, join(outdir, 'specularity.png'))

    # Reconstruction vs. composite from Blender, just for sanity check
    recon = np.multiply(albedo, shading) # + specularity
    recon[:, :, 3] = albedo[:, :, 3] # can't add up alpha channels
    xv.matrix_as_image(recon, join(outdir, 'recon.png'), gamma=gamma)
    gt = collapse_passes(['composite'])
    xv.matrix_as_image(gt, join(outdir, 'gt.png'), gamma=gamma)

    logger.name = logger_name
    logger.info("Intrinsic images extracted to %s", outdir)
