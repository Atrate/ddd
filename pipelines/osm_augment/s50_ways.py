# ddd - DDD123
# Library for procedural scene modelling.
# Jose Juan Montes 2020


from ddd.ddd import ddd
from ddd.geo import terrain
from ddd.osm import osm
from ddd.pipeline.decorators import dddtask

# Lamps, signs, traffic signals, road signs, roadlines...

#@dddtask(order="45.20.+.+")
@dddtask(order="55.10.+.+")
def osm_augment_ways2(root, osm, pipeline, logger):
    """
    Standard augmentation for OSM ways. This includes lamps (according to osm:lit and config) and
    traffic lights (if not present).
    """
    pipeline.data['_lamps'] = root.select('["osm:highway" = "street_lamp"]')

@dddtask(path="/Ways/*", select='["ddd:way:lamps" = True]')  # shall be osm:lit?
def osm_augment_ways_2d_lamps(root, osm, pipeline, logger, obj):
    """
    """
    #lamps = root.select('["osm:highway" = "street_lamp"]')
    if not obj.extra['osm:feature_2d'].buffer(35.0, cap_style=ddd.CAP_ROUND).intersects(pipeline.data['_lamps']):
        osm.ways2.generate_lamps(pipeline, obj)

@dddtask(path="/Ways/*", select='["ddd:way:traffic_signals"]')
def osm_augment_ways_2d_traffic_signals(root, osm, pipeline, obj):
    """
    Traffic lights.
    """
    osm.ways2.generate_traffic_signals(pipeline, obj)

@dddtask(path="/Ways/*", select='["ddd:way:traffic_signs"]')
def osm_augment_ways_2d_traffic_signs(root, osm, pipeline, obj):
    """
    """
    osm.ways2.generate_traffic_signs(pipeline, obj)





