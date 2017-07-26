"""
Utility functions for manipulating objects in Blender

Xiuming Zhang, MIT CSAIL
July 2017

Contributor(s): Xingyuan Sun
"""

import logging
import re
from os.path import abspath
import numpy as np
import bpy
from mathutils import Matrix
import logging_colorer # noqa: F401 # pylint: disable=unused-import

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


def remove_object(name_pattern):
    """
    Remove object from current scene

    Args:
        name_pattern: Names of objects to remove
            String (regex supported)
            Use '.*' to remove all objects
    """
    thisfunc = thisfile + '->clear_all()'

    # Regex
    assert (name_pattern != '*'), "Want to match everything? Correct regex for this is '.*'"
    name_pattern = re.compile(name_pattern)

    objs = bpy.data.objects
    removed = []
    for obj in objs:
        if name_pattern.match(obj.name):
            obj.select = True
            removed.append(obj.name)
        else:
            obj.select = False
    bpy.ops.object.delete()

    logging.info("%s: Removed from scene: %s", thisfunc, removed)


def add_object(model_path, rot_mat=((1, 0, 0), (0, 1, 0), (0, 0, 1)), trans_vec=(0, 0, 0), scale=1, name=None):
    """
    Add object to current scene, the low-level way

    Args:
        model_path: Path to object to add
            String
        rot_mat: 3D rotation matrix PRECEDING translation
            Tuple, list or numpy array; must be effectively 3-by-3
            Optional; defaults to identity matrix
        trans_vec: 3D translation vector FOLLOWING rotation
            Tuple, list or numpy array; must be of length 3
            Optional; defaults to zero vector
        scale: Scale of the object
            Float
            Optional; defaults to 1
        name: Object name after import
            String
            Optional; defaults to name specified in model

    Returns:
        obj: Handle(s) of imported object(s)
            bpy_types.Object or list thereof
    """
    thisfunc = thisfile + '->add_object()'

    # Import
    if model_path.endswith('.obj'):
        bpy.ops.import_scene.obj(filepath=model_path, axis_forward='-Z', axis_up='Y')
    else:
        raise NotImplementedError("Importing model of this type")

    obj_list = []
    for i, obj in enumerate(bpy.context.selected_objects):

        # Rename
        if name is not None:
            if len(bpy.context.selected_objects) == 1:
                obj.name = name
            else:
                obj.name = name + '_' + str(i)

        # Compute world matrix
        trans_4x4 = Matrix.Translation(trans_vec)
        rot_4x4 = Matrix(rot_mat).to_4x4()
        scale_4x4 = Matrix(np.eye(4)) # don't scale here
        obj.matrix_world = trans_4x4 * rot_4x4 * scale_4x4

        # Scale
        obj.scale = (scale, scale, scale)

        obj_list.append(obj)

    logging.info("%s: Imported: %s", thisfunc, model_path)

    if len(obj_list) == 1:
        return obj_list[0]
    else:
        return obj_list


def subdivide_mesh(obj, n_subdiv=2):
    """
    Subdivide mesh of object

    Args:
        obj: Object whose mesh is to be subdivided
            bpy_types.Object
        n_subdiv: Number of subdivision levels
            Integer
            Optional; defaults to 2
    """
    thisfunc = thisfile + '->subdivide_mesh()'

    # All objects need to be in 'EDIT' mode to apply modifiers -- maybe a Blender bug?
    for o in bpy.data.objects:
        bpy.context.scene.objects.active = o
        bpy.ops.object.mode_set(mode='OBJECT')
        o.select = False
    obj.select = True
    bpy.context.scene.objects.active = obj

    bpy.ops.object.modifier_add(type='SUBSURF')
    obj.modifiers['Subsurf'].subdivision_type = 'CATMULL_CLARK'
    obj.modifiers['Subsurf'].levels = n_subdiv
    obj.modifiers['Subsurf'].render_levels = n_subdiv

    # Apply modifier
    bpy.ops.object.modifier_apply(modifier='Subsurf', apply_as='DATA')

    logging.info("%s: Subdivided mesh of %s", thisfunc, obj.name)
