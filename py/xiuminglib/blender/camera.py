"""
Utility functions for manipulating cameras in Blender

Xiuming Zhang, MIT CSAIL
July 2017
"""

import logging
from os import remove, rename
from os.path import abspath, dirname, basename
import bpy
import bmesh
import bpy_types
from mathutils import Vector, Matrix
import numpy as np
import cv2

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

    logging.info("%s: Done computing camera matrix. Image resolution used: w = %d; h = %d",
                 thisfunc, w * scale, h * scale)

    return cam_mat, int_mat, ext_mat


def get_camera_zbuffer(cam, save_to=None):
    """
    Get z-buffer of Blender camera
        Values are z components in camera-centered coordinate system:
            - x is horizontal
            - y is down (to align to the actual pixel coordinates)
            - right-handed: positive z is look-at direction and means "in front of camera"
        Origin is camera center, not image plane

    Args:
        cam: Camera object
            bpy_types.Object
        save_to: Path to which the .exr z-buffer will be saved
            String
            Optional; defaults to None (don't save)

    Returns:
        zbuffer: Camera z-buffer
            2D numpy array
    """
    thisfunc = thisfile + '->get_camera_zbuffer()'

    if save_to is None:
        outpath = '/tmp/zbuffer'
    elif save_to.endswith('.exr'):
        outpath = save_to[:-4]

    # Duplicate scene to avoid touching the original scene
    bpy.ops.scene.new(type='LINK_OBJECTS')

    scene = bpy.context.scene
    scene.camera = cam
    scene.use_nodes = True
    node_tree = scene.node_tree
    nodes = node_tree.nodes

    # Remove all nodes
    scene.use_nodes = True
    for node in nodes:
        nodes.remove(node)

    # Set up nodes for z pass
    nodes.new('CompositorNodeRLayers')
    nodes.new('CompositorNodeOutputFile')
    node_tree.links.new(nodes['Render Layers'].outputs[2], nodes['File Output'].inputs[0])
    nodes['File Output'].format.file_format = 'OPEN_EXR'
    nodes['File Output'].format.color_mode = 'RGB'
    nodes['File Output'].format.color_depth = '32' # full float
    nodes['File Output'].base_path = dirname(outpath)
    nodes['File Output'].file_slots[0].path = basename(outpath)

    # Render
    scene.cycles.samples = 1
    bpy.ops.render.render(write_still=True)

    w = scene.render.resolution_x
    h = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100.

    # Delete this new scene
    bpy.ops.scene.delete()

    # Load z-buffer as array
    exr_path = outpath + '%04d' % scene.frame_current + '.exr'
    im = cv2.imread(exr_path, cv2.IMREAD_UNCHANGED)
    assert (np.array_equal(im[:, :, 0], im[:, :, 1]) and np.array_equal(im[:, :, 0], im[:, :, 2])), \
        "BGR channels of the z-buffer should be all the same, but they are not"
    zbuffer = im[:, :, 0]

    # Delete or move the .exr as user wants
    if save_to is None:
        # User doesn't want it -- delete
        remove(exr_path)
    else:
        # User wants it -- rename
        rename(exr_path, outpath + '.exr')

    logging.info("%s: Got z-buffer of camera '%s'. Image resolution used: w = %d; h = %d",
                 thisfunc, cam.name, w * scale, h * scale)

    return zbuffer


def get_visible_verts_from(cam, ooi=None, ignore_occlusion=False, prec_eps=1e-6):
    """
    Get vertices that are visible (projected within frame AND unoccluded) from Blender camera
        You can opt to ignore depth ordering such that occluded vertices are also considered visible

    Args:
        cam: Camera object
            bpy_types.Object
        ooi: Object(s) of interest
            bpy_types.Object or list thereof
            Optional; defaults to None (all mesh objects)
        ignore_occlusion: Whether to ignore occlusion
            Boolean
            Optional; defaults to False
        prec_eps: Threshold for percentage difference between the query z value and buffered z value
                z_q considered equal to z_b when abs(z_q - z_b) / z_b < prec_eps
            Float
            Optional; defaults to 1e-6

    Returns:
        visible_vert_ind: Indices of vertices that are visible
            List of non-negative integers or dictionary thereof with object names as keys
    """
    thisfunc = thisfile + '->get_visible_verts_from()'

    if ooi is None:
        ooi = [o for o in bpy.data.objects if o.type == 'MESH']
    elif isinstance(ooi, bpy_types.Object):
        ooi = [ooi]

    scene = bpy.context.scene
    w, h = scene.render.resolution_x, scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100.

    # Get camera matrix
    cam_mat, _, ext_mat = get_camera_mat(cam)

    # Get z-buffer
    if not ignore_occlusion:
        zbuffer = get_camera_zbuffer(cam)

    visible_vert_ind = {}

    # For each object of interest
    for obj in ooi:

        # Get mesh data from object
        scene.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        mesh = bmesh.from_edit_mesh(obj.data)

        vert_ind = []
        # For each of its vertices
        for vert in mesh.verts:

            # Check if its projection falls inside frame
            v_world = obj.matrix_world * vert.co # local to world
            uv = np.array(cam_mat * v_world) # project to 2D
            uv = uv[:-1] / uv[-1]
            if uv[0] >= 0 and uv[0] < w * scale and uv[1] >= 0 and uv[1] < h * scale:

                # Yes
                if ignore_occlusion:
                    # Don't care occlusion -- consider visible already
                    vert_ind.append(vert.index)
                else:
                    # Proceed to check occlusion with z-buffer
                    v_cv = ext_mat * v_world # world to camera to CV
                    z = v_cv[-1]
                    z_min = zbuffer[int(uv[1]), int(uv[0])]
                    if (z - z_min) / z_min < prec_eps:
                        vert_ind.append(vert.index)

        visible_vert_ind[obj.name] = vert_ind

    logging.info("%s: Visibility test done with camera '%s'. Image resolution used: w = %d; h = %d",
                 thisfunc, cam.name, w * scale, h * scale)

    if len(visible_vert_ind.keys()) == 1:
        return list(visible_vert_ind.values())[0]
    else:
        return visible_vert_ind
