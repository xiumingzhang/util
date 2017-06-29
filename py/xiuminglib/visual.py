"""
Utility Functions for Visualizations

Xiuming Zhang, MIT CSAIL
June 2017
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import cv2


def matrix_as_heatmap(mat, outpath='./matrix_as_heatmap.png', figtitle=None):
    """
    Visualizes a matrix as heatmap

    Args:
        mat: Matrix to visualize as heatmp
            2D numpy array
        outpath: Path to which the visualization is saved
            String
            Optional; defaults to './matrix_as_heatmap.png'
        figtitle: Figure title
            String
            Optional; defaults to None (no title)

    Returns:
        None
    """
    figsize = 14
    plt.figure(figsize=(figsize, figsize))
    ax = plt.gca()

    # Set title
    if figtitle is not None:
        ax.set_title(figtitle)

    # Generate heatmap with matrix entries
    im = ax.imshow(mat)

    # Colorbar
    # Create an axes on the right side of ax. The width of cax will be 2%
    # of ax and the padding between cax and ax will be fixed at 0.1 inch.
    cax = make_axes_locatable(ax).append_axes('right', size='2%', pad=0.1)
    plt.colorbar(im, cax=cax)

    # Save plot
    plt.savefig(outpath, bbox_inches='tight')


def verts_on_texmap(u, v, texmap, outpath='./verts_on_texmap.png', figtitle=None):
    """
    Visualizes which points on texture map the vertices map to

    Args:
        u, v: UV coordinates of the vertices
            1D numpy array

        (0, 1)
            ^ v
            |
            |
            |
            |
            +-----------> (1, 0)
        (0, 0)        u

        texmap: loaded texture map or its path
            h-by-w (grayscale) or h-by-w-by-3 (color) numpy array or string
        outpath: Path to which the visualization is saved
            String
            Optional; defaults to './verts_on_texmap.png'
        figtitle: Figure title
            String
            Optional; defaults to None (no title)

    Returns:
        None
    """
    figsize = 50
    fig = plt.figure(figsize=(figsize, figsize))
    if figtitle is not None:
        fig.suptitle(figtitle)

    # Preprocess input
    if isinstance(texmap, str):
        texmap = cv2.imread(texmap, cv2.IMREAD_UNCHANGED)
    elif isinstance(texmap, np.ndarray):
        assert (len(texmap.shape) == 2 or len(texmap.shape) == 3), \
            "'texmap' must be either h-by-w (grayscale) or h-by-w-by-3 (color)"
    else:
        raise TypeError("Wrong input format for 'texmap'")

    # Count number of vertices falling into each cell of the texture map
    h, w = texmap.shape[:2]
    ind2 = np.floor(u * w)
    ind1 = np.floor(v * h)
    ind2[ind2 == w] = w - 1
    ind1[ind1 == h] = h - 1
    ind2 = ind2.astype(int)
    ind1 = ind1.astype(int)
    sample_count = np.zeros((h, w))
    np.add.at(sample_count, (ind1, ind2), 1) # unbuffered in-place operation
    # 'a[[0, 0]] += 1' will only increment the first element once because of buffering
    # whereas 'add.at(a, [0, 0], 1)' will increment the first element twice

    # Modify colormap so that 0 is transparent
    cmap = plt.get_cmap('Reds')
    cmap_colors = cmap(np.arange(cmap.N))
    cmap_colors[0, -1] = 0 # set transparent
    cmap_mod = ListedColormap(cmap_colors)

    # Figure 1: sample count
    ax = fig.add_subplot(211)
    im = ax.imshow(sample_count, cmap=cmap_mod)
    cax = make_axes_locatable(ax).append_axes('right', size='2%', pad=0.1)
    plt.colorbar(im, cax=cax)

    # Figure 2: selection mask over texture image
    ax = fig.add_subplot(212)
    ax.imshow(texmap)
    im = ax.imshow(sample_count, cmap=cmap_mod)
    cax = make_axes_locatable(ax).append_axes('right', size='2%', pad=0.1)
    plt.colorbar(im, cax=cax)

    # Save plot
    plt.savefig(outpath, bbox_inches='tight')
