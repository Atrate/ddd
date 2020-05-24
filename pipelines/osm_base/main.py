# ddd - DDD123
# Library for procedural scene modelling.
# Jose Juan Montes 2020

from ddd.osm import osm
from ddd.pipeline.decorators import dddtask
from ddd.ddd import ddd
import sys
from ddd.osm.augment.mapillary import MapillaryClient
import pyproj
from ddd.geo import terrain
from ddd.osm.osm import project_coordinates


@dddtask()
def start_run(pipeline, root):
    """
    Run at initial stage, load data.
    """
    pass

'''
@dddtask(log=True)
def stage_10_preprocess_features(pipeline, osm):
    #pipeline.data['osm'].preprocess_features()
    #osm.preprocess_features()
    pass

@dddtask(parent="stage_01_preprocess_features", log=True)
def preprocess_features(pipeline, osm):
    #pipeline.data['osm'].preprocess_features()
    osm.preprocess_features()
'''

@dddtask(filter=lambda o: o.geom, log=True)  # and o.geom.type in ('Point', 'Polygon', 'MultiPolygon') .. and o.geom.type == 'Polygon' |  ... path="/Features", select=r'["geom:type"="Polygon"]'
def osm_10_crop_extended_area(pipeline, osm, root, obj):
    """Crops to extended area size to avoid working with huge areas."""

    # TODO: Crop centroids of buildings and lines and entire areas...

    #pipeline.data['osm'].preprocess_features()
    #osm.preprocess_features()
    obj = obj.intersection(osm.area_filter2)

    return obj

@dddtask(select='[osm:element="relation"]')
def osm_11_remove_relations():
    # TEMPORARY ? they shall be simmply not picked
    #obj = obj.material(ddd.mats.outline)
    #obj.extra['ddd:enabled'] = False
    return False  # TODO: return... ddd.REMOVE APPLY:REMOVE ?... (depends on final api for this)


'''
@dddtask(select='[osm:boundary]')
def stage_11_hide_relations(obj):
    obj = obj.material(ddd.mats.outline)
    #obj.data['ddd:visible': False]
    return False

@dddtask(select='[osm:boundary]')
def stage_11_hide_boundaries(obj):
    obj = obj.material(ddd.mats.outline)
    #obj.data['ddd:visible': False]
    return False
'''

@dddtask(log=True)
def osm_20_preprocess_features(pipeline, osm, root):
    """
    TODO: Currently done in builder, move here.
    """
    #pipeline.data['osm'].preprocess_features()
    #osm.preprocess_features()  # Currently done
    #root.show()
    #root.save("/tmp/osm-20-features.svg")
    #root.save("/tmp/osm-20-features.json")
    #sys.exit(1)
    pass

@dddtask(log=True)
def osm_30_create_root_nodes(root, osm):
    items = ddd.group2(name="Items")  # 1D
    root.append(items)
    items = ddd.group2(name="Ways")  # 1D
    root.append(items)
    items = ddd.group2(name="Areas")  # 2D
    root.append(items)
    items = ddd.group2(name="Buildings")  # 2D
    root.append(items)

    #root.dump(data=True)

@dddtask(path="/Features/*", select='[geom:type="Point"]', log=True)  #  , select='[geom:type="Point"]'  , parent="stage_30_generate_items_node")
def osm_30_generate_items(root, osm, obj):
    """Generate items for point features."""
    item = obj.copy(name="Item: %s" % obj.name)
    item = item.material(ddd.mats.highlight)
    root.find("/Items").append(item)

@dddtask(log=True)  #  , select='[geom:type="Point"]'  , parent="stage_30_generate_items_node")
def osm_31_process_items(root, osm, obj):
    """Generate items for point features."""
    #root.save("/tmp/osm-31-items.svg")
    pass

'''
@dddtask(path="/Features/*", select='[geom:type="LineString"]', log=True)
def osm_40_generate_ways(root, obj):
    # Ways depend on buildings
    item = obj.copy(name="Way: %s" % obj.name)

    item = item.material(ddd.mats.asphalt)
    root.find("/Ways").append(item)

    ## ?? osm.ways.generate_ways_1d()

@dddtask(log=True)
def osm_45_process_ways(pipeline, osm, root, logger):
    osm.ways_1d = root.find("/Ways")
    osm.ways.split_ways_1d()
    root.find("/Ways").replace(osm.ways_1d)


# Generate buildings
##osm.buildings.generate_buildings_2d()
@dddtask(path="/Areas/*", select='[geom:type="Polygon"]', log=True)
def osm_260_generate_buildings(root, obj):
    # Ways depend on buildings
    item = obj.copy(name="Building: %s" % obj.name)
    root.find("/Buildings").append(item)
    ## ?? osm.ways.generate_ways_1d()

@dddtask(log=True)
def osm_260_preprocess_buildings(pipeline, osm, root, logger):
    osm.buildings.preprocess_buildings_2d()
    osm.buildings.generate_buildings_2d()

@dddtask(log=True)
def osm_265_process_buildings(pipeline, osm, root, logger):
    osm.buildings.preprocess_buildings_2d()
    osm.buildings.generate_buildings_2d()


@dddtask(path="/Features/*", select='[geom:type="Polygon"]', log=True)
def osm_250_generate_areas(root, obj):
    # Ways depend on buildings
    item = obj.copy(name="Area: %s" % obj.name)
    root.find("/Areas").append(item)
    ## ?? osm.ways.generate_ways_1d()

@dddtask(log=True)
def osm_255_process_areas(pipeline, osm, root, logger):
    pass
'''


@dddtask(log=True)
def osm_99_rest(pipeline, osm, root, logger):

    #self.features_2d.filter(lambda o: o.extra.get('osm:building:part', None) is not None).dump()

    root.save("/tmp/tile.json")
    root.save("/tmp/tile.svg")
    #sys.exit(1)


    # Add mapillary items
    # TODO: Move to separate task and rule module, separate point generation from image/metadata generation
    mc = MapillaryClient()
    transformer = pyproj.Transformer.from_proj(osm.osm_proj, osm.ddd_proj)
    transformer2 = pyproj.Transformer.from_proj(osm.ddd_proj, osm.osm_proj)
    query_coords = osm.area_crop2.centroid().geom.coords[0]
    query_coords = project_coordinates(query_coords, transformer2)
    data = mc.images_list(query_coords, limit=200)
    for feature in data['features'][:]:

        key = feature['properties']['key']
        pano = feature['properties']['pano']
        camera_angle = feature['properties']['ca']
        geom = feature['geometry']
        coords = geom['coordinates']
        #coords = (float(coords[0]) * 111000.0, float(coords[1]) * 111000.0)

        coords = project_coordinates(coords, transformer)
        print("Image: %s  CameraAngle: %s  Pano: %s  Coords: %s" % (key, camera_angle, pano, coords))

        mc.request_image(key)
        image = mc.image_textured(feature).scale([3, 3, 3])
        image_height = 1.5
        image = image.translate([0, 1, 0])
        image = image.rotate([0, 0, (0 + (-camera_angle)) * ddd.DEG_TO_RAD])
        image = image.translate([coords[0], coords[1], image_height])

        cam = ddd.cube(d=0.05).translate([coords[0], coords[1], image_height]).material(ddd.mats.highlight)
        image.append(cam)

        image = terrain.terrain_geotiff_min_elevation_apply(image, osm.ddd_proj)

        osm.other_3d.append(image)

    osm.other_3d.save("/tmp/mapi.glb")


    # TODO: Shall already be done earlier
    osm.features_2d = root.find("/Features")
    osm.items_1d = root.find("/Items")
    #osm.ways_1d = root.find("/Ways")
    #osm.buildings_2d = root.find("/Buildings")

    # Generate items for point features
    ##osm.items.generate_items_1d()

    # Roads sorted + intersections + metadata
    osm.ways.generate_ways_1d()
    osm.ways.split_ways_1d()

    #root.dump()
    #sys.exit(1)

    # Generate buildings
    osm.buildings.preprocess_buildings_2d()
    osm.buildings.generate_buildings_2d()

    # Ways depend on buildings
    osm.ways.generate_ways_2d()

    osm.areas.generate_areas_2d()
    osm.areas.generate_areas_2d_interways()  # and assign types

    osm.areas.generate_areas_2d_postprocess()
    osm.areas.generate_areas_2d_postprocess_water()

    # Associate features (amenities, etc) to 2D objects (buildings, etc)
    osm.buildings.link_features_2d()

    # Coastline and ground
    osm.areas.generate_coastline_3d(osm.area_crop if osm.area_crop else osm.area_filter)  # must come before ground
    osm.areas.generate_ground_3d(osm.area_crop if osm.area_crop else osm.area_filter) # separate in 2d + 3d, also subdivide (calculation is huge - core dump-)

    # Generates items defined as areas (area fountains, football fields...)
    osm.items2.generate_items_2d()  # Objects related to areas (fountains, playgrounds...)

    # Road props (traffic lights, lampposts, fountains, football fields...) - needs. roads, areas, coastline, etc... and buildings
    osm.ways.generate_props_2d()  # Objects related to ways

    # 2D output (before cropping, crop here -so buildings and everything is cropped-)
    #self.save_tile_2d("/tmp/osm2d.png")
    #self.save_tile_2d("/tmp/osm2d.svg")

    # Crop if necessary
    if osm.area_crop:
        logger.info("Cropping to: %s" % (osm.area_crop.bounds, ))
        crop = ddd.shape(osm.area_crop)
        osm.areas_2d = osm.areas_2d.intersection(crop)
        osm.ways_2d = {k: osm.ways_2d[k].intersection(crop) for k in osm.layer_indexes}

        #osm.items_1d = osm.items_1d.intersect(crop)
        osm.items_1d = ddd.group([b for b in osm.items_1d.children if osm.area_crop.contains(b.geom.centroid)], empty=2)
        osm.items_2d = ddd.group([b for b in osm.items_2d.children if osm.area_crop.contains(b.geom.centroid)], empty=2)
        osm.buildings_2d = ddd.group([b for b in osm.buildings_2d.children if osm.area_crop.contains(b.geom.centroid)], empty=2)

    # 3D Build

    # Ways 3D
    osm.ways.generate_ways_3d()
    osm.ways.generate_ways_3d_intersections()
    # Areas 3D
    osm.areas.generate_areas_3d()
    # Buildings 3D
    osm.buildings.generate_buildings_3d()

    # Walls and fences(!) (2D?)

    # Urban decoration (trees, fountains, etc)
    osm.items.generate_items_3d()
    osm.items2.generate_items_3d()

    # Generate custom items
    osm.customs.generate_customs()


    # Final grouping
    scene = [osm.areas_3d, osm.ground_3d, osm.water_3d,
             #osm.sidewalks_3d_lm1, osm.walls_3d_lm1, osm.ceiling_3d_lm1,
             #osm.sidewalks_3d_l1, osm.walls_3d_l1, osm.floor_3d_l1,
             osm.buildings_3d, osm.items_3d,
             osm.other_3d, osm.roadlines_3d]
    scene = ddd.group(scene + list(osm.ways_3d.values()), name="Scene")

    pipeline.root = scene
    #return scene

