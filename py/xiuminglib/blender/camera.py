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
from mathutils import Vector, Matrix
import numpy as np
import cv2
import logging_colorer # noqa: F401 # pylint: disable=unused-import

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
        sensor_fit: Sensor fit; also see get_camera_matrix()
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


def intrinsics_compatible_with_scene(cam):
    """
    Check if camera intrinsic parameters (sensor size and pixel aspect ratio)
        are comptible with the current scene (render resolutions and their scale)

    Args:
        cam: Camera object
            bpy_types.Object

    Returns:
        comptible: Result
            Boolean
    """
    thisfunc = thisfile + '->intrinsics_compatible_with_scene()'

    # Camera
    sensor_width_mm = cam.data.sensor_width
    sensor_height_mm = cam.data.sensor_height

    # Scene
    scene = bpy.context.scene
    w = scene.render.resolution_x
    h = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100.
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

    # Do these parameters make sense together?
    mm_per_pix_horizontal = sensor_width_mm / (w * scale)
    mm_per_pix_vertical = sensor_height_mm / (h * scale)

    if mm_per_pix_horizontal / mm_per_pix_vertical == pixel_aspect_ratio:

        logging.info("%s: OK", thisfunc)

        return True

    else:
        compatible_sensor_height_mm = sensor_width_mm / w * h / pixel_aspect_ratio

        logging.error((
            "%s: Render resolutions (w = %d; h = %d), sensor size (w = %d; h = %d), and "
            "pixel aspect ratio (w / h = %f) don't make sense together. This could cause "
            "unexpected behaviors later. Consider using %f for sensor height"
        ), thisfunc, w, h, sensor_width_mm, sensor_height_mm, pixel_aspect_ratio, compatible_sensor_height_mm)

        return False


def get_camera_matrix(cam):
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
    thisfunc = thisfile + '->get_camera_matrix()'

    # Necessary scene update
    scene = bpy.context.scene
    scene.update()

    # Check if camera intrinsic parameters comptible with render settings
    if not intrinsics_compatible_with_scene(cam):
        raise ValueError("Render settings and camera intrinsic parameters mismatch")

    # Intrinsics

    f_mm = cam.data.lens
    sensor_width_mm = cam.data.sensor_width
    sensor_height_mm = cam.data.sensor_height
    w = scene.render.resolution_x
    h = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100.
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

    if cam.data.sensor_fit == 'VERTICAL':
        # h times pixel height must fit into sensor_height_mm
        # w / pixel_aspect_ratio times pixel width will then fit into sensor_width_mm
        s_v = h * scale / sensor_height_mm
        s_u = w * scale / pixel_aspect_ratio / sensor_width_mm
    else: # 'HORIZONTAL' or 'AUTO'
        # w times pixel width must fit into sensor_width_mm
        # h * pixel_aspect_ratio times pixel height will then fit into sensor_height_mm
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
    logging.warning("%s:     ... using w = %d; h = %d", thisfunc, w * scale, h * scale)

    return cam_mat, int_mat, ext_mat


def get_camera_zbuffer(cam, save_to=None, hide=None):
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
        hide: Names of objects to be hidden while rendering this camera's z-buffer
            String or list thereof
            Optional; defaults to None

    Returns:
        zbuffer: Camera z-buffer
            2D numpy array
    """
    thisfunc = thisfile + '->get_camera_zbuffer()'

    # Validate and standardize error-prone inputs
    if hide is not None:
        if not isinstance(hide, list):
            # A single object
            hide = [hide]
        for element in hide:
            assert isinstance(element, str), \
                "'hide' should contain object names (i.e., strings), not object(s) per se"

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

    # Hide objects from z-buffer, if necessary
    if hide is not None:
        orig_hide_render = {} # for later restoration
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                orig_hide_render[obj.name] = obj.hide_render
                obj.hide_render = obj.name in hide

    # Render
    scene.cycles.samples = 1
    scene.render.filepath = '/tmp/rgb.png' # redirect RGB rendering to avoid overwritting
    bpy.ops.render.render(write_still=True)

    w = scene.render.resolution_x
    h = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100.

    # Delete this new scene
    bpy.ops.scene.delete()

    # Restore objects' original render hide states, if necessary
    if hide is not None:
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.hide_render = orig_hide_render[obj.name]

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

    logging.info("%s: Got z-buffer of camera '%s'", thisfunc, cam.name)
    logging.warning("%s:     ... using w = %d; h = %d", thisfunc, w * scale, h * scale)

    return zbuffer


def get_visible_vertices(cam, obj, ignore_occlusion=False, prec_z_eps=1e-6, hide=None):
    """
    Get vertices that are visible (projected within frame AND unoccluded) from Blender camera
        You can opt to ignore z-buffer such that occluded vertices are also considered visible

    Args:
        cam: Camera object
            bpy_types.Object
        obj: Object of interest
            bpy_types.Object
        ignore_occlusion: Whether to ignore occlusion (including self-occlusion)
            Boolean
            Optional; defaults to False
        prec_z_eps: Threshold for percentage difference between the query z_q and buffered z_b
                z_q considered equal to z_b when abs(z_q - z_b) / z_b < prec_z_eps
            Float
            Optional; defaults to 1e-6
            Useless if ignore_occlusion
        hide: Names of objects to be hidden while rendering this camera's z-buffer
            String or list thereof
            Optional; defaults to None
            Useless if ignore_occlusion

    Returns:
        visible_vert_ind: Indices of vertices that are visible
            List of non-negative integers
    """
    thisfunc = thisfile + '->get_visible_vertices()'

    scene = bpy.context.scene
    w, h = scene.render.resolution_x, scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100.

    # Get camera matrix
    cam_mat, _, ext_mat = get_camera_matrix(cam)

    # Get z-buffer
    if not ignore_occlusion:
        zbuffer = get_camera_zbuffer(cam, hide=hide)

    # Get mesh data from object
    scene.objects.active = obj
    orig_obj_mode = obj.mode
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = bmesh.from_edit_mesh(obj.data)

    visible_vert_ind = []
    # For each of its vertices
    for vert in mesh.verts:

        # Check if its projection falls inside frame
        v_world = obj.matrix_world * vert.co # local to world
        uv = np.array(cam_mat * v_world) # project to 2D
        uv = uv[:-1] / uv[-1]
        if uv[0] >= 0 and uv[0] < w * scale and uv[1] >= 0 and uv[1] < h * scale:
            # Yes

            if ignore_occlusion:
                # Considered visible already
                visible_vert_ind.append(vert.index)
            else:
                # Proceed to check occlusion with z-buffer
                v_cv = ext_mat * v_world # world to camera to CV
                z = v_cv[-1]
                z_min = zbuffer[int(uv[1]), int(uv[0])]
                if (z - z_min) / z_min < prec_z_eps:
                    visible_vert_ind.append(vert.index)

    # Restore the object mode
    bpy.ops.object.mode_set(mode=orig_obj_mode)

    logging.info("%s: Visibility test done with camera '%s'", thisfunc, cam.name)
    logging.warning("%s:     ... using w = %d; h = %d", thisfunc, w * scale, h * scale)

    return visible_vert_ind
