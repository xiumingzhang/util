"""
Utility Functions for Simple Geometry Processing

Xiuming Zhang, MIT CSAIL
June 2017
"""

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
        pts_cartesian: n-by-3 numpy array
            Each row consists of x, y and z, in order.

    Returns:
        pts_spherical: n-by-3 numpy array
            Each row consists of r, lat and lng (in radians), in order.
    """

    # Validate inputs
    assert (len(pts_cartesian.shape) == 2), "'pts' must be a 2D array"
    assert (pts_cartesian.shape[1] == 3), "Second dimension of 'pts' must be 3"

    # Compute r
    r = np.sqrt(np.sum(np.square(pts_cartesian), axis=1))

    # Compute latitude
    z = pts_cartesian[:, 2]
    lat = np.arcsin(z / r)

    # Compute longitude
    x = pts_cartesian[:, 0]
    y = pts_cartesian[:, 1]
    lng = np.arctan2(y, x) # choosing the quadrant correctly

    # Assemble and return
    pts_spherical = np.stack((r, lat, lng), axis=-1) # let this new axis be the last dimension
    return pts_spherical


def spherical2cartesian(pts_spherical):
    """
    Inverse of cartesian2spherical

    See cartesian2spherical for spherical convention, args and returns
    """

    # Validate inputs
    assert (len(pts_spherical.shape) == 2), "'pts' must be a 2D array"
    assert (pts_spherical.shape[1] == 3), "Second dimension of 'pts' must be 3"

    # Compute x, y and z
    r = pts_spherical[:, 0]
    lat = pts_spherical[:, 1]
    lng = pts_spherical[:, 2]
    z = r * np.sin(lat)
    x = r * np.cos(lat) * np.cos(lng)
    y = r * np.cos(lat) * np.sin(lng)

    # Assemble and return
    pts_cartesian = np.stack((x, y, z), axis=-1) # let this new axis be the last dimension
    return pts_cartesian


if __name__ == '__main__':
    # cartesian2spherical
    pts_car = np.array([[-1, 2, 3], [4, -5, 6], [3, 5, -8], [-2, -5, 2], [4, -2, -23]])
    print(pts_car)
    pts_sph = cartesian2spherical(pts_car)
    print(pts_sph)
    pts_car_recover = spherical2cartesian(pts_sph)
    print(pts_car_recover)
