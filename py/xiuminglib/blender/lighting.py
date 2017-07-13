"""
Utility functions for manipulating lights Blender

Xiuming Zhang, MIT CSAIL
July 2017
"""

import logging
from warnings import warn
from os.path import abspath
import numpy as np
import bpy

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


def add_light_area(xyz=(0, 0, 0), rot_vec_rad=(0, 0, 0), name=None, energy=1, size=1):
    """
    Add area light to current scene

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
        energy: Light intensity
            Float
            Optional; defaults to 1
        size: Plane size
            Float
            Optional; defaults to 1

    Returns:
        area: Handle of added light
            bpy_types.Object
    """
    thisfunc = thisfile + '->add_light_area()'

    if (np.abs(rot_vec_rad) > 2 * np.pi).any():
        warn("Some input value falls outside [-2pi, 2pi]. Are you sure inputs are in radians?")

    bpy.ops.object.lamp_add(type='AREA', location=xyz, rotation=rot_vec_rad)
    area = bpy.context.active_object

    if name is not None:
        area.name = name

    # Strength
    area.data.size = size
    if bpy.data.scenes['Scene'].render.engine == 'CYCLES':
        area.data.node_tree.nodes['Emission'].inputs[1].default_value = energy
    else:
        raise NotImplementedError("Area light strength for Blender Internal")

    logging.info("%s: Area light added", thisfunc)

    return area


def add_light_point(xyz=(0, 0, 0), name=None, energy=1):
    """
    Add omnidirectional point lighting to current scene

    Args:
        xyz: Location
            3-tuple of floats
            Optional; defaults to (0, 0, 0)
        name: Light object name
            String
            Optional
        energy: Light intensity
            Float
            Optional; defaults to 1

    Returns:
        point: Handle of added light
            bpy_types.Object
    """
    thisfunc = thisfile + '->add_light_point()'

    bpy.ops.object.lamp_add(type='POINT', location=xyz)
    point = bpy.context.active_object

    if name is not None:
        point.name = name

    # Strength
    if bpy.data.scenes['Scene'].render.engine == 'CYCLES':
        point.data.node_tree.nodes['Emission'].inputs[1].default_value = energy
    else:
        raise NotImplementedError("Point light strength for Blender Internal")

    logging.info("%s: Omnidirectional point light added", thisfunc)

    return point
