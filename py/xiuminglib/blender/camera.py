"""
Utility functions for manipulating cameras in Blender

Xiuming Zhang, MIT CSAIL
July 2017
"""

import logging
from os.path import abspath
import bpy
from mathutils import Vector

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


def add_camera(xyz=(0, 0, 0), rot_vec_rad=(0, 0, 0), name=None, proj_model='PERSP', f=35, sensor_fit='HORIZONTAL', sensor_size=32):
    """
    Add camera to current scene

    Args:
        xyz: Location
            3-tuple of floats
            Optional; defaults to (0, 0, 0)
        rot_vec_rad: Rotation angle in radians around x, y and z
            3-tuple of floats
            Optional; defaults to (0, 0, 0)
        name: Light object name
            String
            Optional
        proj_model: Camera projection model
            'PERSP', 'ORTHO', or 'PANO'
            Optional; defaults to 'PERSP'
        f: Focal length in mm
            Float
            Optional; defaults to 35
        sensor_fit: Sensor fit
            'HORIZONTAL' or 'VERTICAL'
            Optional; defaults to 'HORIZONTAL'
        sensor_size: Sensor width if 'HORIZONTAL' or height if 'VERTICAL' in mm
            Float
            Optional; defaults to 32

    Returns:
        cam: Handle of added camera
            bpy_types.Object
    """
    thisfunc = thisfile + '->add_camera()'

    bpy.ops.object.camera_add()
    cam = bpy.context.active_object

    if name is not None:
        cam.name = name

    cam.location = xyz
    cam.rotation_euler = rot_vec_rad

    cam.data.type = proj_model
    cam.data.lens = f
    cam.data.sensor_fit = sensor_fit
    if sensor_fit == 'HORIZONTAL':
        cam.data.sensor_width = sensor_size
    else:
        cam.data.sensor_height = sensor_size

    logging.info("%s: Camera added", thisfunc)

    return cam


def point_camera_to(cam, xyz_target):
    """
    Point camera to target

    Args:
        cam: Camera object
            bpy_types.Object
        xyz_target: Target point
            3-tuple of floats
    """
    thisfunc = thisfile + '->point_camera_to()'

    xyz_target = Vector(xyz_target)
    direction = xyz_target - cam.location
    # Find quaternion that rotates '-Z' so that it aligns with 'direction'
    # This rotation is not unique because the rotated camera can still rotate about direction vector
    # Specifying 'Y' gives the rotation quaternion with camera's 'Y' pointing up
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

    logging.info("%s: Camera pointed to %s", thisfunc, xyz_target)

    return cam
