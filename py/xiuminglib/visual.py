"""
Utility Functions for Visualizations

Xiuming Zhang, MIT CSAIL
June 2017
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def matrix_as_heatmap(mat, outpath=None):
    """
    Visualizes a matrix as heatmap

    Args:
        mat: 2D numpy array
        outpath: path string
            If not given, visualization is saved to './heatmap.png'

    Returns:
        None
    """

    figsize = 14
    plt.figure(figsize=(figsize, figsize))
    ax = plt.gca()

    # Generate heatmap with matrix entries
    im = ax.imshow(mat)

    # Colorbar
    # Create an axes on the right side of ax. The width of cax will be 2%
    # of ax and the padding between cax and ax will be fixed at 0.1 inch.
    cax = make_axes_locatable(ax).append_axes('right', size='2%', pad=0.1)
    plt.colorbar(im, cax=cax)

    # Save plot
    if outpath is None:
        outpath = './heatmap.png'
    plt.savefig(outpath, bbox_inches='tight')
