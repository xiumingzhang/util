from os import environ
from os.path import join
from abc import ABCMeta, abstractmethod

MAP_DIR = join(environ['MOON_DIR'], 'data', 'maps')
MODEL_DIR = join(environ['MOON_DIR'], 'output', 'planets')


# ABC
class Planet(metaclass=ABCMeta):
    radius = 0
    basemap_path = None
    elevmap_path = None

    def __init__(self, pos_horizon, rotmat):
        self.pos_horizon = pos_horizon
        self.rotmat = rotmat

    @abstractmethod
    def planet_type(self):
        pass


# Derived class
class Moon(Planet):
    radius = 1737400 # m
    basemap_path = join(MAP_DIR, 'Lunar_Clementine_UVVIS_750nm_Global_Mosaic_1.2km_lowres.jpg')
    elevmap_path = join(MAP_DIR, 'Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif')

    def planet_type(self):
        return 'moon'


# Derived class
class Earth(Planet):
    radius = 6378137 # m
    basemap_path = join(MAP_DIR, 'world.topo.bathy.200407.3x5400x2700_lowres.jpg')
    elevmap_path = None

    def planet_type(self):
        return 'earth'


# Derived class
class Sun(Planet):
    radius = 696000000 # m
    basemap_path = join(MAP_DIR, '700328main_20121014_003615_flat_lowres.jpg')
    elevmap_path = None

    def planet_type(self):
        return 'sun'
