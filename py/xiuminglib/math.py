"""
Utility Functions for Simple Math Operations

Xiuming Zhang, MIT CSAIL
August 2017
"""

import logging
from os.path import abspath
import numpy as np
import logging_colorer # noqa: F401 # pylint: disable=unused-import

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


def pca(data_mat, n_pcs=None):
    """
    Perform PCA on data via eigendecomposition of covariance matrix

    Args:
        data_mat: Data matrix of n data points in the m-D space
            Array_like of shape (m, n); each column is a point
        n_pcs: Number of top PC's requested
            Positive integer <= m
            Optional; defaults to m (i.e., all)

    Returns:
        pcvars: PC variances (eigenvalues of covariance matrix) in descending order
            Numpy array of length n_pcs
        pcs: Corresponding PC's (normalized eigenvectors)
            Numpy array of shape (m, n_pcs); each column is a PC
        projs: Data points centered and then projected to the n_pcs-D PC space
            Numpy array of shape (n_pcs, n); each column is a point
        data_mean: Mean that can be used to recover raw data
            Numpy array of length m
    """
    data_mat = np.array(data_mat) # not centered

    if n_pcs is None:
        n_pcs = data_mat.shape[0]

    # Compute covariance matrix of data
    covmat = np.cov(data_mat) # np.cov() centers data first
    # covmat is real and symmetric in theory, but may not be so due to numerical issues

    # Compute eigenvalues and eigenvectors
    # eigh() prevents complex eigenvalues, compared with eig()
    eig_vals, eig_vecs = np.linalg.eigh(covmat)
    # eig_vals in ascending order
    # eig_vecs columns are normalized eigenvectors

    pcvars = eig_vals[:-(n_pcs + 1):-1] # ascending
    pcs = eig_vecs[:, :-(n_pcs + 1):-1]

    # Center and then project data points to PC space
    data_mean = np.mean(data_mat, axis=1)
    data_mat_centered = data_mat - np.tile(data_mean.reshape(-1, 1), (1, data_mat.shape[1]))
    projs = np.dot(pcs.T, data_mat_centered)

    return pcvars, pcs, projs, data_mean
