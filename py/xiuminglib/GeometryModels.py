"""
Classes of Common 3D Geometry Models

Xiuming Zhang, MIT CSAIL
June 2017
"""

class Obj(object):
    """
    Wavefront .obj format
    """

    def __init__(self, verts, faces):
        """
        Args:
            pts_cartesian: n-by-3 numpy array
                Each row consists of x, y and z, in order.

        Returns:
            pts_spherical: n-by-3 numpy array
                Each row consists of r, lat and lng (in radians), in order.
        """
