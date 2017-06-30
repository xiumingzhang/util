"""
Utility Functions for Visualizations

Xiuming Zhang, MIT CSAIL
June 2017
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
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
    cax = make_axes_locatable(ax).append_axes('right', size='2%', pad=0.2)
    plt.colorbar(im, cax=cax)

    # Save plot
    plt.savefig(outpath, bbox_inches='tight')


def uv_on_texmap(u, v, texmap, ft=None, outpath='./uv_on_texmap.png', figtitle=None):
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

        texmap: Loaded texture map or its path
            h-by-w (grayscale) or h-by-w-by-3 (color) numpy array or string
        ft: Texture faces
            List of lists of integers starting from 1, e.g., '[[1, 2, 3], [], [2, 3, 4, 5], ...]'
            Optional; defaults to None. If provided, use it to connect UV points
        outpath: Path to which the visualization is saved
            String
            Optional; defaults to './uv_on_texmap.png'
        figtitle: Figure title
            String
            Optional; defaults to None (no title)
    """
    figsize = 50
    dc = 'r' # color
    ds = 4 # size of UV dots
    lc = 'b' # color
    lw = 1 # width of edges connecting UV dots

    fig = plt.figure(figsize=(figsize, figsize))
    if figtitle is not None:
        fig.title(figtitle)

    # Preprocess input
    if isinstance(texmap, str):
        texmap = cv2.imread(texmap, cv2.IMREAD_UNCHANGED)
    elif isinstance(texmap, np.ndarray):
        assert (len(texmap.shape) == 2 or len(texmap.shape) == 3), \
            "'texmap' must be either h-by-w (grayscale) or h-by-w-by-3 (color)"
    else:
        raise TypeError("Wrong input format for 'texmap'")

    h, w = texmap.shape[:2]
    x = u * w
    y = (1 - v) * h
    # (0, 0)
    #   +----------->
    #   |          x
    #   |
    #   |
    #   v y

    # UV dots
    ax = fig.gca()
    ax.set_xlim([min(0, min(x)), max(w, max(x))])
    ax.set_ylim([max(h, max(y)), min(0, min(y))])
    im = ax.imshow(texmap, cmap='gray')
    ax.scatter(x, y, c=dc, s=ds)
    ax.set_aspect('equal')

    # Also connect these dots
    if ft is not None:
        lines = []
        for vert_id in ft:
            if len(vert_id) > 0:
                # For each face
                ind = [i - 1 for i in vert_id]
                n_verts = len(ind)
                for i in range(n_verts):
                    lines.append([
                        (x[ind[i]], y[ind[i]]), # starting point
                        (x[ind[(i + 1) % n_verts]], y[ind[(i + 1) % n_verts]]) # ending point
                    ])
        line_collection = LineCollection(lines, linewidths=lw, colors=lc)
        ax.add_collection(line_collection)

    # Colorbar
    # Create an axes on the right side of ax. The width of cax will be 2%
    # of ax and the padding between cax and ax will be fixed at 0.1 inch.
    cax = make_axes_locatable(ax).append_axes('right', size='2%', pad=0.2)
    plt.colorbar(im, cax=cax)

    # Save plot
    plt.savefig(outpath, bbox_inches='tight')
