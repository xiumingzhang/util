"""
Utility functions for manipulating Blender scenes

Xiuming Zhang, MIT CSAIL
July 2017
"""

import logging
from os import makedirs, remove
from os.path import join, abspath, basename, dirname, exists
import cv2
import bpy
import logging_colorer # noqa: F401 # pylint: disable=unused-import

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


def set_cycles(w=None, h=None, n_samples=None):
    """
    Set up Cycles as rendering engine

    Args:
        w: Width of render in pixels
            Integer
            Optional; no change if not given
        h: Height of render in pixels
            Integer
            Optional; no change if not given
        n_samples: Number of samples
            Integer
            Optional; no change if not given
    """
    thisfunc = thisfile + '->set_cycles()'

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    cycles = scene.cycles

    cycles.use_progressive_refine = True
    if n_samples is not None:
        cycles.samples = n_samples
    cycles.max_bounces = 100
    cycles.min_bounces = 10
    cycles.caustics_reflective = False
    cycles.caustics_refractive = False
    cycles.diffuse_bounces = 10
    cycles.glossy_bounces = 4
    cycles.transmission_bounces = 4
    cycles.volume_bounces = 0
    cycles.transparent_min_bounces = 8
    cycles.transparent_max_bounces = 64

    # Avoid grainy renderings (fireflies)
    world = bpy.data.worlds['World']
    world.cycles.sample_as_light = True
    cycles.blur_glossy = 5
    cycles.sample_clamp_indirect = 5

    # Ensure no background node
    world.use_nodes = True
    try:
        world.node_tree.nodes.remove(world.node_tree.nodes['Background'])
    except KeyError:
        pass

    # # Use GPU
    # bpy.context.user_preferences.system.compute_device_type = 'CUDA'
    # bpy.context.user_preferences.system.compute_device = 'CUDA_' + str(randint(0, 3))
    # scene.cycles.device = 'GPU'

    scene.render.tile_x = 16 # 256 optimal for GPU
    scene.render.tile_y = 16 # 256 optimal for GPU
    if w is not None:
        scene.render.resolution_x = w
    if h is not None:
        scene.render.resolution_y = h
    scene.render.resolution_percentage = 100
    scene.render.use_file_extension = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'

    logging.info("%s: Cycles set up as rendering engine", thisfunc)


def save_to_file(outpath, delete_overwritten=False):
    """
    Save current scene to .blend file

    Args:
        outpath: Path to save scene to, e.g., '~/foo.blend'
            String
        delete_overwritten: Whether to delete or keep as .blend1 the same-name file
            Boolean
            Optional; defaults to False
    """
    thisfunc = thisfile + '->save_to_file()'

    outdir = dirname(outpath)
    if not exists(outdir):
        makedirs(outdir)
    elif exists(outpath) and delete_overwritten:
        remove(outpath)

    bpy.ops.file.autopack_toggle()
    bpy.ops.wm.save_as_mainfile(filepath=outpath)

    logging.info("%s: Saved to %s", thisfunc, outpath)


def render_to_file(outpath, text=None, cam_names=None, hide=None):
    """
    Render current scene to images with cameras in scene

    Args:
        outpath: Path to save render to, e.g., '~/foo.png'
            String
        text: What text to be overlaid on image and how
            Dictionary of the following format
            {
                'contents': 'Hello World!',
                'bottom_left_corner': (50, 50),
                'font_scale': 1,
                'bgr': (255, 0, 0),
                'thickness': 2
            }
            Optional; defaults to None
        cam_names: Name(s) of camera(s) through which scene is rendered
            String or list thereof
            Optional; defaults to None (render all cameras)
        hide: What objects should be hidden from which camera
            Dictionary of the following format
            {
                'name-of-cam1': 'name-of-obj1',
                'name-of-cam2': ['name-of-obj1', 'name-of-obj2']
                    ...
            }
            Optional; defaults to None

    Returns:
        result_path: Path(s) to the rendering ('outpath' prefixed by camera name)
            String or list thereof
    """
    thisfunc = thisfile + '->render_to_file()'

    if isinstance(cam_names, str):
        cam_names = [cam_names]

    outdir = dirname(outpath)
    if not exists(outdir):
        makedirs(outdir)

    result_path = []

    # Render with all cameras
    for cam in bpy.data.objects:
        if cam.type == 'CAMERA':
            if cam_names is None or cam.name in cam_names:

                # Set active camera
                bpy.context.scene.camera = cam

                # Prepend camera name
                outpath_final = join(dirname(outpath), cam.name + '_' + basename(outpath))
                bpy.context.scene.render.filepath = outpath_final
                result_path.append(outpath_final)

                # Optionally set object visibility in rendering
                for obj in bpy.data.objects:
                    if obj.type == 'MESH':
                        if hide is not None:
                            ignore_list = hide.get(cam.name, []) # if no such key, returns empty list
                            if not isinstance(ignore_list, list):
                                # Single object
                                ignore_list = [ignore_list]
                            obj.hide_render = obj.name in ignore_list
                        else:
                            obj.hide_render = False

                # Render
                bpy.ops.render.render(write_still=True)

                # Optionally overlay text
                if text is not None:
                    im = cv2.imread(outpath_final, cv2.IMREAD_UNCHANGED)
                    cv2.putText(im, text['contents'], text['bottom_left_corner'],
                                cv2.FONT_HERSHEY_SIMPLEX, text['font_scale'], text['bgr'], text['thickness'])
                    cv2.imwrite(outpath_final, im)

                logging.info("%s: Rendered with camera '%s'", thisfunc, cam.name)

    if len(result_path) == 1:
        return result_path[0]
    else:
        return result_path


def easyset(w=None, h=None, n_samples=None, ao=None):
    """
    Set some of the scene attributes more easily

    Args:
        w: Width of render in pixels
            Integer
            Optional; no change if not given
        h: Height of render in pixels
            Integer
            Optional; no change if not given
        n_samples: Number of samples
            Integer
            Optional; no change if not given
        ao: Ambient occlusion
            Boolean
            Optional; no change if not given
    """
    scene = bpy.context.scene

    if w is not None:
        scene.render.resolution_x = w

    if h is not None:
        scene.render.resolution_y = h

    # Number of samples
    if n_samples is not None:
        if scene.render.engine == 'CYCLES':
            scene.cycles.samples = n_samples
        else:
            raise NotImplementedError("Rendering engines other than Cycles")

    # Ambient occlusion
    if ao is not None:
        bpy.context.scene.world.light_settings.use_ambient_occlusion = ao
