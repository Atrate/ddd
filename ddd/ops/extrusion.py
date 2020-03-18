# ddd - D1D2D3
# Library for simple scene modelling.
# Jose Juan Montes 2020

import logging
import math
import random

from csg import geom as csggeom
from csg.core import CSG
import numpy as np
from shapely import geometry, affinity, ops
from shapely.geometry import shape
from trimesh import creation, primitives, boolean, transformations
import trimesh
from trimesh.base import Trimesh
from trimesh.path import segments
from trimesh.path.path import Path
from trimesh.scene.scene import Scene, append_scenes
from trimesh.visual.material import SimpleMaterial
from trimesh.scene.transforms import TransformForest
import copy
from trimesh.visual.texture import TextureVisuals
from matplotlib import colors
import json
import base64
from shapely.geometry.polygon import orient


# Get instance of logger for this module
logger = logging.getLogger(__name__)



def extrude_step(obj, shape, offset, cap=True):
    """
    Extrude a shape into another.
    """
    last_shape = obj.extra['_extrusion_last_shape']

    #obj = last_shape.individualize()
    #shape = shape.individualize()

    #obj_a.assert_single()
    #obj_b.assert_single()
    geom_a = last_shape.geom
    geom_b = shape.geom

    result = obj.copy()

    if geom_a.is_empty or geom_b.is_empty:
        #logger.debug("Extruding empty geometry.")
        return result

    if geom_b.type in ('MultiPolygon', 'GeometryCollection'):
        logger.warn("Cannot extrude a step to a 'MultiPolygon' or 'GeometryCollection'.")
        return result


    mesh = extrude_between_geoms(geom_a, geom_b, offset, obj.extra.get('_extrusion_last_offset', 0) )

    result.extra['_extrusion_last_shape'] = shape
    result.extra['_extrusion_last_offset'] = obj.extra.get('_extrusion_last_offset', 0) + offset

    vertices = list(result.mesh.vertices) if result.mesh else []
    faces = list(result.mesh.faces) if result.mesh else []

    # Remove previous last cap before extruding.
    last_cap_idx = result.extra.get('_extrusion_last_cap_idx', None)
    if last_cap_idx is not None:
        faces = faces[:last_cap_idx]

    faces =  faces + [[f[0] + len(vertices), f[1] + len(vertices), f[2] + len(vertices)] for f in mesh.faces]
    vertices = vertices + list(mesh.vertices)

    result.extra['_extrusion_last_cap_idx'] = len(faces)

    if cap:
        logger.warn("FIXME: remove intermediate caps, at least optionally.")
        cap_mesh = shape.triangulate().translate([0, 0, result.extra['_extrusion_last_offset']])
        faces = faces + [[f[0] + len(vertices), f[1] + len(vertices), f[2] + len(vertices)] for f in cap_mesh.mesh.faces]
        vertices = vertices + list(cap_mesh.mesh.vertices)

    # Merge
    mesh = Trimesh(vertices, faces)
    mesh.merge_vertices()
    result.mesh = mesh

    return result


def extrude_between_geoms(geom_a, geom_b, offset, _base_height):

    vertices = []
    vertices.extend([(x, y, _base_height) for x, y, *z in geom_a.exterior.coords])
    vertices_b_idx = len(vertices)
    vertices.extend([(x, y, _base_height + offset) for x, y, *z in geom_b.exterior.coords])

    shape_a_idx = 0
    shape_b_idx = 0

    def va(shape_a_idx): return vertices[shape_a_idx % len(geom_a.exterior.coords)]
    def vb(shape_b_idx): return vertices[(shape_b_idx % len(geom_b.exterior.coords)) + vertices_b_idx]
    def ang(v): return (math.atan2(v[1], v[0]) + (math.pi * 2)) % (math.pi * 2)
    def diff(va, vb): return  [va[0] - vb[0], va[1] - vb[1], va[2] - vb[2]]
    def distsqr(v): return v[0] * v[0] + v[1] * v[1] + v[2] * v[2]

    faces = []
    finished_a = False
    finished_b = False
    last_tri = None
    while not (finished_a and finished_b):
        la = distsqr(diff(va(shape_a_idx + 1), vb(shape_b_idx)))
        lb = distsqr(diff(vb(shape_b_idx + 1), va(shape_a_idx)))
        aa = ang(va(shape_a_idx))
        aan = ang(va(shape_a_idx + 1))
        ab = ang(vb(shape_b_idx))
        abn = ang(vb(shape_b_idx + 1))

        norm = 'l2'
        if norm == 'angle':
            advance_b = (abs(abn - aa) < abs(aan - ab))
        elif norm == 'l2':
            advance_b = lb < la

        if advance_b:
            ntri = [shape_a_idx, shape_b_idx + vertices_b_idx, (shape_b_idx + 1) % len(geom_b.exterior.coords) + vertices_b_idx]
            if not finished_b: shape_b_idx +=1
        else:
            ntri = [shape_a_idx, shape_b_idx + vertices_b_idx, (shape_a_idx + 1) % len(geom_a.exterior.coords)]
            if not finished_a: shape_a_idx +=1

        if last_tri == ntri: break

        faces.append(ntri)
        last_tri = ntri
        #print(ntri)

        if shape_a_idx >= len(geom_a.exterior.coords):
            shape_a_idx = 0
            finished_a = True
        if shape_b_idx >= len(geom_b.exterior.coords):
            shape_b_idx = 0
            finished_b = True

    return Trimesh(vertices, faces)
