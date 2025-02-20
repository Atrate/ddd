# ddd - DDD123
# Library for simple scene modelling.
# Jose Juan Montes and Contributors 2019-2021

import random

import noise
import pyproj

from ddd.core.exception import DDDException
from ddd.ddd import ddd
from ddd.geo.elevation import ElevationModel


#dem_file = '/home/jjmontes/git/ddd/data/dem/eudem/eudem_dem_5deg_n40w010.tif'  # Galicia, Salamanca
#dem_file = '/home/jjmontes/git/ddd/data/dem/eudem/eudem_dem_5deg_n40e000.tif'  # Vilanova i la Geltrú
#dem_file = '/home/jjmontes/git/ddd/data/dem/eudem/eudem_dem_5deg_n40w005.tif'  # Madrid, Huesca
#dem_file = '/home/jjmontes/git/ddd/data/dem/eudem11/eu_dem_v11_E30N20.TIF'  # France, La Rochelle
#dem_file = '/home/jjmontes/git/ddd/data/dem/eudem11/eu_dem_v11_E50N30.TIF'  # Riga, Latvia
#dem_file = '/home/jjmontes/git/ddd/data/dem/srtm/srtm_40_19.tif'  # Cape Town, from: https://dwtkns.com/srtm/


# TODO: Move to terrain utils outside "geo"
def terrain_grid(bounds, detail=1.0, height=1.0, scale=0.025):
    '''
    If bounds is a single number, it's used as L1 distance.
    '''

    if isinstance(bounds, float):
        distance = bounds
        bounds = [-distance, -distance, distance, distance]

    mesh = ddd.grid3(bounds, detail=detail)

    #func = lambda x, y: 2.0 * noise.pnoise2(x, y, octaves=3, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024)
    def func(x, y):
        val = height * noise.pnoise2(x * scale, y * scale, octaves=2, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0)
        #print("%s, %s = %s" % (x, y, val))
        return val
    #func = lambda x, y: random.uniform(0, 2)
    mesh = mesh.elevation_func(func)

    return mesh



transformer = None  # remove globals, move into classes

def transformer_ddd_to_geo(ddd_proj):
    global transformer
    if transformer is None:
        transformer = pyproj.Transformer.from_proj(ddd_proj, 'epsg:4326', always_xy=True)  # for old DEM files
        #transformer = pyproj.Transformer.from_proj(ddd_proj, pyproj.Proj(init='epsg:3035'))  # for EUDEM 1.1 files

    return transformer

def transform_ddd_to_geo(ddd_proj, point):
    x, y = transformer_ddd_to_geo(ddd_proj).transform(point[0], point[1])
    return [x, y]


def terrain_geotiff(bounds, ddd_proj, detail=1.0):
    """
    Generates a square grid and applies terrain elevation to it.
    """
    # TODO: we should load the chunk as a heightmap, and load via terrain_heightmap for reuse
    #elevation = ElevationChunk.load('/home/jjmontes/git/ddd/data/elevation/eudem/eudem_dem_5deg_n40w010.tif')
    #elevation = ElevationChunk.load(dem_file)
    elevation = ElevationModel.instance()

    mesh = terrain_grid(bounds, detail=detail)
    func = lambda x, y, z, i: [x, y, elevation.value(transform_ddd_to_geo(ddd_proj, [x, y]))]
    mesh = mesh.vertex_func(func)
    #mesh.mesh.invert()
    return mesh

def terrain_geotiff_elevation_apply(obj, ddd_proj):
    elevation = ElevationModel.instance()
    #print(transform_ddd_to_geo(ddd_proj, [obj.mesh.vertices[0][ 0], obj.mesh.vertices[0][1]]))
    func = lambda x, y, z, i: [x, y, z + elevation.value(transform_ddd_to_geo(ddd_proj, [x, y]))]
    obj = obj.vertex_func(func)
    #mesh.mesh.invert()
    return obj

def terrain_geotiff_min_elevation_apply(obj, ddd_proj):
    elevation = ElevationModel.instance()

    min_h = None
    for v in obj.vertex_iterator():
        v_h = elevation.value(transform_ddd_to_geo(ddd_proj, [v[0], v[1]]))
        if min_h is None:
            min_h = v_h
        if v_h < min_h:
            min_h = v_h

    if min_h is None:
        raise DDDException("Cannot calculate min value for elevation: %s" % obj)

    #func = lambda x, y, z, i: [x, y, z + min_h]
    obj = obj.translate([0, 0, min_h])
    obj.extra['_terrain_geotiff_min_elevation_apply:elevation'] = min_h
    #mesh.mesh.invert()
    return obj

def terrain_geotiff_max_elevation_apply(obj, ddd_proj):
    elevation = ElevationModel.instance()

    max_h = None
    for v in obj.vertex_iterator():
        v_h = elevation.value(transform_ddd_to_geo(ddd_proj, [v[0], v[1]]))
        if max_h is None:
            max_h = v_h
        if v_h > max_h:
            max_h = v_h

    if max_h is None:
        raise DDDException("Cannot calculate max value for elevation: %s" % obj)

    #func = lambda x, y, z, i: [x, y, z + max_h]
    obj = obj.translate([0, 0, max_h])
    obj.extra['_terrain_geotiff_max_elevation_apply:elevation'] = max_h
    #mesh.mesh.invert()
    return obj
