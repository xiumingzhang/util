"""
Utility Functions for Visualizations

Xiuming Zhang, MIT CSAIL
June 2017
"""

from os import makedirs
from os.path import dirname, exists
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable
import cv2


def plot_wrapper(*args, outpath='./plot.png', figtitle=None, **kwargs):
    """
    Plot an array as curve

    Args:
        *args, **kwargs: Positional and/or keyword parameters that plot() takes
            See documentation for matplotlib.pyplot.plot()
        outpath: Path to which the visualization is saved
            String
            Optional; defaults to './plot.png'
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

    plt.plot(*args, **kwargs)

    plt.grid()

    # Make directory, if necessary
    outdir = dirname(outpath)
    if not exists(outdir):
        makedirs(outdir)

    # Save plot
    plt.savefig(outpath, bbox_inches='tight')


def scatter_on_image(im, pts, size=2, bgr=(0, 0, 255), outpath='./scatter_on_image.png'):
    """
    Scatter plot on top of an image

    Args:
        im: Image to scatter on
            h-by-w (grayscale) or h-by-w-by-3 (RGB) numpy array
        pts: Coordinates of the scatter point(s)
            +-----------> dim1
            |
            |
            |
            v dim0
            Array_like of length 2 or shape (n, 2)
        size: Size(s) of scatter points
            Positive float or array_like thereof of length n
            Optional; defaults to 2
        bgr: BGR color(s) of scatter points
            3-tuple of integers ranging from 0 to 255 or array_like thereof of shape (n, 3)
            Optional; defaults to (0, 0, 255), i.e., all red
        outpath: Path to which the visualization is saved
            String
            Optional; defaults to './scatter_on_image.png'
    """
    thickness = -1 # for filled circles

    # Standardize inputs

    if im.ndim == 2: # grayscale
        im = np.stack((im, im, im), axis=2) # to BGR

    pts = np.array(pts)
    if pts.ndim == 1:
        pts = pts.reshape(-1, 2)
    n_pts = pts.shape[0]

    if isinstance(size, int):
        size = np.array([size] * n_pts)
    else:
        size = np.array(size)

    bgr = np.array(bgr)
    if bgr.ndim == 1:
        bgr = np.tile(bgr, (n_pts, 1))

    # FIXME -- necessary, probably due to OpenCV bugs?
    im = im.copy()

    # Put on scatter points
    for i in range(pts.shape[0]):
        uv = tuple(pts[i, ::-1].astype(int))
        color = (int(bgr[i, 0]), int(bgr[i, 1]), int(bgr[i, 2]))
        cv2.circle(im, uv, size[i], color, thickness)

    # Make directory, if necessary
    outdir = dirname(outpath)
    if not exists(outdir):
        makedirs(outdir)

    # Write to disk
    cv2.imwrite(outpath, im)


def matrix_as_heatmap(mat, center_around_zero=False, outpath='./matrix_as_heatmap.png', figtitle=None):
    """
    Visualizes a matrix as heatmap

    Args:
        mat: Matrix to visualize as heatmp
            2D numpy array that may contain NaN's that will be plotted white
        center_around_zero: Whether to center colorbar around 0 (so that zero is no color, i.e., white)
            Useful when matrix consists of both positive and negative values, and 0 means "nothing"
            Boolean
            Optional; defaults to False (default colormap and auto range)
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

    if center_around_zero:
        # vmin and vmax are set such that 0 is always no color (white)
        v_abs_max = max(abs(np.min(mat)), abs(np.max(mat)))
        v_max, v_min = v_abs_max, -v_abs_max
        plt.set_cmap('bwr') # blue for negative, white for zero, red for positive

        # Generate heatmap with matrix entries
        im = ax.imshow(mat, interpolation='none', vmin=v_min, vmax=v_max)
    else:
        # Generate heatmap with matrix entries
        im = ax.imshow(mat, interpolation='none')

    # Colorbar
    # Create an axes on the right side of ax; width will be 4% of ax,
    # and the padding between cax and ax will be fixed at 0.1 inch
    cax = make_axes_locatable(ax).append_axes('right', size='4%', pad=0.2)
    plt.colorbar(im, cax=cax)

    # Make directory, if necessary
    outdir = dirname(outpath)
    if not exists(outdir):
        makedirs(outdir)

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

    # Make directory, if necessary
    outdir = dirname(outpath)
    if not exists(outdir):
        makedirs(outdir)

    # Save plot
    plt.savefig(outpath, bbox_inches='tight')
