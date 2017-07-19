"""
Utility Functions for Simple Geometry Processing

Xiuming Zhang, MIT CSAIL
June 2017
"""

from warnings import warn
import numpy as np


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
            List/tuple/etc. that can be converted to a numpy array of shape '(3,)' or '(n, 3)'

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
    pts_spherical = np.array(pts_spherical)

    # Validate inputs
    is_one_point = False
    if pts_spherical.shape == (3,):
        is_one_point = True
        pts_spherical = pts_spherical.reshape(1, 3)
    elif len(pts_spherical.shape) != 2 or pts_spherical.shape[1] != 3:
        raise ValueError("Shape of input must be either (3,) or (n, 3)")

    # Degrees?
    if (np.abs(pts_spherical) > 2 * np.pi).any():
        warn("Some input value falls outside [-2pi, 2pi]. Are you sure inputs are in radians?")

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


if __name__ == '__main__':
    # cartesian2spherical
    pts_car = np.array([[-1, 2, 3], [4, -5, 6], [3, 5, -8], [-2, -5, 2], [4, -2, -23]])
    print(pts_car)
    pts_sph = cartesian2spherical(pts_car)
    print(pts_sph)
    pts_car_recover = spherical2cartesian(pts_sph)
    print(pts_car_recover)
