"""
Utility Functions for Simple Geometry Processing

Xiuming Zhang, MIT CSAIL
June 2017
"""

import logging
from os.path import abspath
import numpy as np
import logging_colorer # noqa: F401 # pylint: disable=unused-import

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


def cartesian2spherical(pts_cartesian):
    """
    Converts 3D Cartesian coordinates to spherical coordinates, following the convention below

                                ^ z (lat = 90)
                                |
                                |
           (lng = -90) ---------+---------> y (lng = 90)
                              ,'|
                            ,'  |
                          x     | (lat = -90)

    Args:
        pts_cartesian: Cartesian x, y and z
            Array_like of shape '(3,)' or '(n, 3)'

    Returns:
        pts_spherical: Spherical r, lat and lng (in radians)
            Numpy array of same shape as input
    """
    pts_cartesian = np.array(pts_cartesian)

    # Validate inputs
    is_one_point = False
    if pts_cartesian.shape == (3,):
        is_one_point = True
        pts_cartesian = pts_cartesian.reshape(1, 3)
    elif len(pts_cartesian.shape) != 2 or pts_cartesian.shape[1] != 3:
        raise ValueError("Shape of input must be either (3,) or (n, 3)")

    # Compute r
    r = np.sqrt(np.sum(np.square(pts_cartesian), axis=1))

    # Compute latitude
    z = pts_cartesian[:, 2]
    lat = np.arcsin(z / r)

    # Compute longitude
    x = pts_cartesian[:, 0]
    y = pts_cartesian[:, 1]
    lng = np.arctan2(y, x) # choosing the quadrant correctly

    # Assemble
    pts_spherical = np.stack((r, lat, lng), axis=-1) # let this new axis be the last dimension

    if is_one_point:
        pts_spherical = pts_spherical.reshape(3)

    return pts_spherical


def spherical2cartesian(pts_spherical):
    """
    Inverse of cartesian2spherical

    See cartesian2spherical for spherical convention, args and returns
    """
    thisfunc = thisfile + '->spherical2cartesian()'

    pts_spherical = np.array(pts_spherical)

    # Validate inputs
    is_one_point = False
    if pts_spherical.shape == (3,):
        is_one_point = True
        pts_spherical = pts_spherical.reshape(1, 3)
    elif len(pts_spherical.shape) != 2 or pts_spherical.shape[1] != 3:
        raise ValueError("Shape of input must be either (3,) or (n, 3)")

    # Degrees?
    if (np.abs(pts_spherical[:, 1:]) > 2 * np.pi).any():
        logging.warning("%s: Some input value falls outside [-2pi, 2pi]. Sure inputs are in radians?", thisfunc)

    # Compute x, y and z
    r = pts_spherical[:, 0]
    lat = pts_spherical[:, 1]
    lng = pts_spherical[:, 2]
    z = r * np.sin(lat)
    x = r * np.cos(lat) * np.cos(lng)
    y = r * np.cos(lat) * np.sin(lng)

    # Assemble and return
    pts_cartesian = np.stack((x, y, z), axis=-1) # let this new axis be the last dimension

    if is_one_point:
        pts_cartesian = pts_cartesian.reshape(3)

    return pts_cartesian


def moeller_trumbore(ray_orig, ray_dir, tri_v0, tri_v1, tri_v2):
    """
    Decides if a ray intersects with a triangle using the Moeller-Trumbore algorithm
        O + tD = (1 - u - v) * V0 + u * V1 + v * V2

    Args:
        ray_orig: Ray origin O
            Array_like of three floats
        ray_dir: Ray direction D (not necessarily normalized)
            Array_like of three floats
        tri_v0, tri_v1, tri_v2: Vertices of the triangle V0, V1, V2
            Array_likes of three floats

    Returns:
        u, v: Barycentric coordinates. Intersection is in triangle (including on an edge
                or at a vertex) if u >= 0, v >= 0, and u + v <= 1
            Float
        t: Distance coefficient from O to intersection along D. Intersection is
                between O and O + tD if 0 < t < 1
            Float
    """

    # Validate inputs
    ray_orig = np.array(ray_orig)
    ray_dir = np.array(ray_dir)
    tri_v0 = np.array(tri_v0)
    tri_v1 = np.array(tri_v1)
    tri_v2 = np.array(tri_v2)
    assert (ray_orig.shape == (3,)), "'ray_orig' must be of length 3"
    assert (ray_dir.shape == (3,)), "'ray_dir' must be of length 3"
    assert (tri_v0.shape == (3,)), "'tri_v0' must be of length 3"
    assert (tri_v1.shape == (3,)), "'tri_v1' must be of length 3"
    assert (tri_v2.shape == (3,)), "'tri_v2' must be of length 3"

    M = np.array([-ray_dir, tri_v1 - tri_v0, tri_v2 - tri_v0]).T # noqa: N806
    y = (ray_orig - tri_v0).T
    t, u, v = np.linalg.solve(M, y)

    return u, v, t


if __name__ == '__main__':
    # cartesian2spherical
    pts_car = np.array([[-1, 2, 3], [4, -5, 6], [3, 5, -8], [-2, -5, 2], [4, -2, -23]])
    print(pts_car)
    pts_sph = cartesian2spherical(pts_car)
    print(pts_sph)
    pts_car_recover = spherical2cartesian(pts_sph)
    print(pts_car_recover)
