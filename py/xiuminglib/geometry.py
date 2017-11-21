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


def cartesian2spherical(pts_cartesian, convention='lat-lng'):
    """
    Converts 3D Cartesian coordinates to spherical coordinates, following the convention below

    Args:
        pts_cartesian: Cartesian x, y and z
            Array_like of shape (3,) or (n, 3)
        convention: Convention for spherical coordinates
            'lat-lng' or 'theta-phi'
            Optional; defaults to 'lat-lng'

            'lat-lng'
                                            ^ z (lat = 90)
                                            |
                                            |
                       (lng = -90) ---------+---------> y (lng = 90)
                                          ,'|
                                        ,'  |
                   (lat = 0, lng = 0) x     | (lat = -90)

            'theta-phi'
                                            ^ z (theta = 0)
                                            |
                                            |
                       (phi = 270) ---------+---------> y (phi = 90)
                                          ,'|
                                        ,'  |
                (theta = 90, phi = 0) x     | (theta = 180)

    Returns:
        pts_spherical: Spherical coordinates (r, angle1, angle2) in radians
            Numpy array of same shape as input
    """
    pts_cartesian = np.array(pts_cartesian)

    # Validate inputs
    is_one_point = False
    if pts_cartesian.shape == (3,):
        is_one_point = True
        pts_cartesian = pts_cartesian.reshape(1, 3)
    elif pts_cartesian.ndim != 2 or pts_cartesian.shape[1] != 3:
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
    pts_r_lat_lng = np.stack((r, lat, lng), axis=-1) # let this new axis be the last dimension

    # Select output convention
    if convention == 'lat-lng':
        pts_spherical = pts_r_lat_lng
    elif convention == 'theta-phi':
        pts_spherical = _convert_spherical_conventions(pts_r_lat_lng, 'lat-lng_to_theta-phi')
    else:
        raise NotImplementedError(convention)

    if is_one_point:
        pts_spherical = pts_spherical.reshape(3)

    return pts_spherical


def _convert_spherical_conventions(pts_r_angle1_angle2, what2what):
    """
    Internal function converting between different conventions for spherical coordinates
        See cartesian2spherical() for conventions
    """
    if what2what == 'lat-lng_to_theta-phi':
        pts_r_theta_phi = np.zeros(pts_r_angle1_angle2.shape)
        # Radius is the same
        pts_r_theta_phi[:, 0] = pts_r_angle1_angle2[:, 0]
        # Angle 1
        pts_r_theta_phi[:, 1] = np.pi / 2 - pts_r_angle1_angle2[:, 1]
        # Angle 2
        ind = pts_r_angle1_angle2[:, 2] < 0
        pts_r_theta_phi[ind, 2] = 2 * np.pi + pts_r_angle1_angle2[ind, 2]
        pts_r_theta_phi[np.logical_not(ind), 2] = pts_r_angle1_angle2[np.logical_not(ind), 2]
        return pts_r_theta_phi

    elif what2what == 'theta-phi_to_lat-lng':
        pts_r_lat_lng = np.zeros(pts_r_angle1_angle2.shape)
        # Radius is the same
        pts_r_lat_lng[:, 0] = pts_r_angle1_angle2[:, 0]
        # Angle 1
        pts_r_lat_lng[:, 1] = np.pi / 2 - pts_r_angle1_angle2[:, 1]
        # Angle 2
        ind = pts_r_angle1_angle2[:, 2] > np.pi
        pts_r_lat_lng[ind, 2] = pts_r_angle1_angle2[ind, 2] - 2 * np.pi
        pts_r_lat_lng[np.logical_not(ind), 2] = pts_r_angle1_angle2[np.logical_not(ind), 2]
        return pts_r_lat_lng

    else:
        raise NotImplementedError(what2what)


def spherical2cartesian(pts_spherical, convention='lat-lng'):
    """
    Inverse of cartesian2spherical()

    See cartesian2spherical() for spherical convention, args and returns
    """
    thisfunc = thisfile + '->spherical2cartesian()'

    pts_spherical = np.array(pts_spherical)

    # Validate inputs
    is_one_point = False
    if pts_spherical.shape == (3,):
        is_one_point = True
        pts_spherical = pts_spherical.reshape(1, 3)
    elif pts_spherical.ndim != 2 or pts_spherical.shape[1] != 3:
        raise ValueError("Shape of input must be either (3,) or (n, 3)")

    # Degrees?
    if (np.abs(pts_spherical[:, 1:]) > 2 * np.pi).any():
        logging.warning("%s: Some input value falls outside [-2pi, 2pi]. Sure inputs are in radians?", thisfunc)

    # Convert to latitude-longitude convention, if necessary
    if convention == 'lat-lng':
        pts_r_lat_lng = pts_spherical
    elif convention == 'theta-phi':
        pts_r_lat_lng = _convert_spherical_conventions(pts_spherical, 'theta-phi_to_lat-lng')
    else:
        raise NotImplementedError(convention)

    # Compute x, y and z
    r = pts_r_lat_lng[:, 0]
    lat = pts_r_lat_lng[:, 1]
    lng = pts_r_lat_lng[:, 2]
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
    # Unit tests

    # cartesian2spherical() and spherical2cartesian()
    pts_car = np.array([[-1, 2, 3], [4, -5, 6], [3, 5, -8], [-2, -5, 2], [4, -2, -23]])
    print(pts_car)
    pts_sph = cartesian2spherical(pts_car)
    print(pts_sph)
    pts_car_recover = spherical2cartesian(pts_sph)
    print(pts_car_recover)
