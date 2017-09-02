"""
Utility Functions for Simple Math Operations

Xiuming Zhang, MIT CSAIL
August 2017
"""

import logging
from os.path import abspath
import numpy as np
from scipy.sparse.linalg import eigsh
import logging_colorer # noqa: F401 # pylint: disable=unused-import

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


def pca(data_mat, n_pcs=None, use_scipy=False):
    """
    Perform PCA on data via eigendecomposition of covariance matrix

    Args:
        data_mat: Data matrix of n data points in the m-D space
            Array_like of shape (m, n); each column is a point
        n_pcs: Number of top PC's requested
            Positive integer < m
            Optional; defaults to m - 1
        use_scipy: Whether to use scipy's sparse.linalg.eigsh()
            Useful when numpy's linalg.eigh() gives bizarre results
            Boolean
            Optional; defaults to False

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
        n_pcs = data_mat.shape[0] - 1

    # Compute covariance matrix of data
    covmat = np.cov(data_mat) # doesn't matter whether data_mat are centered
    # covmat is real and symmetric in theory, but may not be so due to numerical issues

    # Compute eigenvalues and eigenvectors
    if use_scipy:
        # Largest (in magnitude) n_pcs eigenvalues
        eig_vals, eig_vecs = eigsh(covmat, k=n_pcs, which='LM')
        # eig_vals in ascending order
        # eig_vecs columns are normalized eigenvectors

        pcvars = eig_vals[::-1] # descending
        pcs = eig_vecs[:, ::-1]
    else:
        # eigh() prevents complex eigenvalues, compared with eig()
        eig_vals, eig_vecs = np.linalg.eigh(covmat)
        # eig_vals in ascending order
        # eig_vecs columns are normalized eigenvectors

        # FIXME -- sometimes the eigenvalues are not sorted? Subnormals appear. All zero eigenvectors
        sort_ind = eig_vals.argsort() # ascending
        eig_vals = eig_vals[sort_ind]
        eig_vecs = eig_vecs[:, sort_ind]

        pcvars = eig_vals[:-(n_pcs + 1):-1] # descending
        pcs = eig_vecs[:, :-(n_pcs + 1):-1]

    # Center and then project data points to PC space
    data_mean = np.mean(data_mat, axis=1)
    data_mat_centered = data_mat - np.tile(data_mean.reshape(-1, 1), (1, data_mat.shape[1]))
    projs = np.dot(pcs.T, data_mat_centered)

    return pcvars, pcs, projs, data_mean
