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
import bmesh
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
    thisfunc = thisfile + '->remove_object()'

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


def setup_diffuse_nodetree(obj):
    """
    Set up a simple diffuse node tree for imported object bundled with texture map

    Args:
        obj: Object bundled with texture map
            bpy_types.Object
    """
    thisfunc = thisfile + '->setup_diffuse_nodetree()'

    if bpy.context.scene.render.engine != 'CYCLES':
        raise NotImplementedError("Only Cycles is supported for now")

    obj.active_material.use_nodes = True
    node_tree = obj.active_material.node_tree
    node_tree.nodes.new('ShaderNodeTexImage')
    node_tree.nodes['Image Texture'].image = obj.active_material.active_texture.image
    node_tree.links.new(
        node_tree.nodes['Image Texture'].outputs[0],
        node_tree.nodes['Diffuse BSDF'].inputs[0]
    )

    logging.info("%s: Diffuse node tree set up for  %s", thisfunc, obj.name)


def get_bmesh(obj):
    """
    Get Blender mesh data from object

    Args:
        obj: Object
            bpy_types.Object

    Returns:
        bm: Blender mesh data
            BMesh
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    return bm


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

    # All objects need to be in 'OBJECT' mode to apply modifiers -- maybe a Blender bug?
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


def select_mesh_elements_by_vertices(obj, vert_ind, select_type):
    """
    Select vertices or their associated edges/faces in edit mode

    Args:
        obj: Object
            bpy_types.Object
        vert_ind: A single vertex index or a list of many
            Non-negative integer or list thereof
        select_type: Type of mesh elements to select
            'vertex', 'edge' or 'face'
    """
    thisfunc = thisfile + '->select_mesh_elements_by_vertices()'

    if isinstance(vert_ind, int):
        vert_ind = [vert_ind]

    # Edit mode
    scene = bpy.context.scene
    scene.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')

    # Deselect all
    bpy.ops.mesh.select_mode(type='FACE')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.mesh.select_all(action='DESELECT')

    bm = bmesh.from_edit_mesh(obj.data)
    bvs = bm.verts

    bvs.ensure_lookup_table()
    for i in vert_ind:
        bv = bvs[i]

        if select_type == 'vertex':
            bv.select = True

        # Select all edges with this vertex at an end
        elif select_type == 'edge':
            for be in bv.link_edges:
                be.select = True

        # Select all faces with this vertex
        elif select_type == 'face':
            for bf in bv.link_faces:
                bf.select = True

        else:
            raise ValueError("Wrong selection type")

    # Update viewport
    scene.objects.active = scene.objects.active

    logging.info("%s: Selected %s elements of %s", thisfunc, select_type, obj.name)
