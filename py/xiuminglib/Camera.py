"""
Utility Functions for Camera (Back-)Projections

Xiuming Zhang, MIT CSAIL
November 2017
"""

# TODO: change to class

import logging
from os.path import abspath
import numpy as np
import logging_colorer # noqa: F401 # pylint: disable=unused-import

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


# Not unit-tested
def extrinsics_from_lookat(cam_origin, up):
    """
    Compute camera extrinsics---rotation and translation that transform a point from object space to
        camera space---for a camera that looks at the object space origin

    Args:
        cam_origin: Camera (x, y, z) in object space
            Array_like of three floats
        up: Upward direction in rendered images specified in object space
            Array_like of three floats

    Returns:
        ext_mat: Camera extrinsics
            (3, 4)-numpy array of floats
    """
    cam_origin = np.array(cam_origin)
    up = np.array(up)

    # Two coordinate systems involved:
    #   1. Object space: "obj"
    #   2. Desired computer vision camera coordinates: "cv"
    #        - x is horizontal, pointing right (to align with pixel coordinates)
    #        - y is vertical, pointing down
    #        - right-handed: positive z is the look-at direction

    # cv axes expressed in obj space
    cvz_obj = np.zeros(3) - cam_origin
    cvx_obj = np.cross(cvz_obj, up)
    cvy_obj = np.cross(cvz_obj, cvx_obj)
    # Normalize
    cvz_obj = cvz_obj / np.linalg.norm(cvz_obj)
    cvx_obj = cvx_obj / np.linalg.norm(cvx_obj)
    cvy_obj = cvy_obj / np.linalg.norm(cvy_obj)

    # Compute rotation from obj to cv: R
    # R(1, 0, 0)^T = cvx_obj gives first column of R
    # R(0, 1, 0)^T = cvy_obj gives second column of R
    # R(0, 0, 1)^T = cvz_obj gives third column of R
    rot_obj2cv = np.vstack((cvx_obj, cvy_obj, cvz_obj)).T

    # Extrinsics
    ext_mat = rot_obj2cv.dot(np.array([[1, 0, 0, -cam_origin[0]],
                                       [0, 1, 0, -cam_origin[1]],
                                       [0, 0, 1, -cam_origin[2]]]))

    return ext_mat


# Not unit-tested
def get_projection_matrix(f_mm, w_mm, h, w, ext_mat):
    """
    Generate camera projection matrix from intrinsics and extrinsics, assuming (at least):
        - Same focal length for x and y directions
        - No skewing
        - Unit pixel aspect ratio

    Args:
        f_mm: Camera focal length in mm
            Float
        w_mm: Sensor width in mm
            Float
        h, w: Number of pixels vertically and horizontally, respectively
            Float
        ext_mat: Camera extrinsics
            (3, 4)-array_like of floats

    Returns:
        proj_mat: Projection matrix
            (3, 4)-numpy array of floats
    """
    f = f_mm * w / w_mm

    int_mat = np.array([[f, 0, w / 2],
                        [0, f, h / 2],
                        [0, 0, 1]])

    return int_mat.dot(ext_mat)


if __name__ == '__main__':
    # Unit tests
    pass