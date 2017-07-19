"""
Utility functions for manipulating cameras in Blender

Xiuming Zhang, MIT CSAIL
July 2017
"""

import logging
from os.path import abspath
import bpy
from mathutils import Vector, Matrix

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


def add_camera(xyz=(0, 0, 0), rot_vec_rad=(0, 0, 0), name=None, proj_model='PERSP', f=35, sensor_fit='HORIZONTAL', sensor_width=32, sensor_height=18):
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
        sensor_fit: Sensor fit; also see get_camera_mat()
            'HORIZONTAL' or 'VERTICAL'
            Optional; defaults to 'HORIZONTAL'
        sensor_width: Sensor width in mm
            Float
            Optional; defaults to 32
        sensor_height: Sensor height in mm
            Float
            Optional; defaults to 18

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
    cam.data.sensor_width = sensor_width
    cam.data.sensor_height = sensor_height

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


def get_camera_mat(cam):
    """
    Get camera matrix from Blender camera

    Args:
        cam: Camera object
            bpy_types.Object

    Returns:
        cam_mat: Camera matrix, product of intrinsics and extrinsics
            3-by-4 Matrix
        int_mat: Camera intrinsics
            3-by-4 Matrix
        ext_mat: Camera extrinsics
            4-by-4 Matrix
    """
    thisfunc = thisfile + '->get_camera_mat()'

    # Necessary scene update
    scene = bpy.context.scene
    scene.update()

    # Intrinsics

    f_mm = cam.data.lens
    sensor_width_mm = cam.data.sensor_width
    sensor_height_mm = cam.data.sensor_height
    w = scene.render.resolution_x
    h = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100.
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

    if cam.data.sensor_fit == 'VERTICAL':
        # h times of pixel height must fit into sensor_height_mm
        # w / pixel_aspect_ratio times of pixel width will then fit into sensor_width_mm
        s_v = h * scale / sensor_height_mm
        s_u = w * scale / pixel_aspect_ratio / sensor_width_mm
    else: # 'HORIZONTAL' or 'AUTO'
        # w times of pixel width must fit into sensor_width_mm
        # h * pixel_aspect_ratio times of pixel height will then fit into sensor_height_mm
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
        s_u = w * scale / sensor_width_mm
        s_v = h * scale * pixel_aspect_ratio / sensor_height_mm

    skew = 0 # only use rectangular pixels
    int_mat = Matrix((
        (s_u * f_mm, skew, w * scale / 2),
        (0, s_v * f_mm, h * scale / 2),
        (0, 0, 1)))

    # Extrinsics

    # Three coordinate systems involved:
    #   1. World coordinates: "world"
    #   2. Blender camera coordinates: "cam"
    #        - x is horizontal
    #        - y is up
    #        - right-handed: negative z is look-at direction
    #   3. Desired computer vision camera coordinates: "cv"
    #        - x is horizontal
    #        - y is down (to align to the actual pixel coordinates)
    #        - right-handed: positive z is look-at direction

    rotmat_cam2cv = Matrix((
        (1, 0, 0),
        (0, -1, 0),
        (0, 0, -1)))

    # matrix_world defines local-to-world transformation, i.e.,
    # where is local (x, y, z) in world coordinate system?
    t, rot_euler = cam.matrix_world.decompose()[0:2]

    # World to Blender camera
    rotmat_world2cam = rot_euler.to_matrix().transposed() # equivalent to inverse
    t_world2cam = rotmat_world2cam * -t

    # World to computer vision camera
    rotmat_world2cv = rotmat_cam2cv * rotmat_world2cam
    t_world2cv = rotmat_cam2cv * t_world2cam

    ext_mat = Matrix((
        rotmat_world2cv[0][:] + (t_world2cv[0],),
        rotmat_world2cv[1][:] + (t_world2cv[1],),
        rotmat_world2cv[2][:] + (t_world2cv[2],)))

    # Camera matrix
    cam_mat = int_mat * ext_mat

    logging.info("%s: Done computing camera matrix", thisfunc)

    return cam_mat, int_mat, ext_mat
