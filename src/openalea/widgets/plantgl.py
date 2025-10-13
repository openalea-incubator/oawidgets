""" Convert a PlantGL scene to k3d.

3D visualisation widgets in Jupyter.
"""
from __future__ import absolute_import

from openalea.plantgl.all import *
import matplotlib
import numpy as np
import k3d

import six
from six.moves import zip


def tomesh(geometry, d=None, side='front'):
    """Return a mesh from a geometry object"""
    isCurve = False
    if geometry.isACurve():
        isCurve = True
    
    if d is None:
        d = Tesselator() if not isCurve else Discretizer()

    geometry.apply(d)

    if isCurve:
        pts = [(pt.x, pt.y, pt.z) for pt in list(d.result.pointList)]
        mesh = k3d.line(pts, shader='mesh')
    else:
        idl = [tuple(index) for index in list(d.discretization.indexList)]
        pts = [(pt.x, pt.y, pt.z) for pt in list(d.discretization.pointList)]
        mesh = k3d.mesh(vertices=pts, indices=idl, side=side)
    return mesh

def curve2mesh(crv, property=None):
    """Return a mesh from a curve"""
    d = Discretizer()
    indices, vertices, colors, attribute=[], [], [], []
    colordict={}
    count=-1
    offset=0
    for obj in crv:
        status = obj.apply(d)
        pts = [(pt.x, pt.y, pt.z) for pt in list(d.result.pointList)]

        vertices.extend(pts)
        color = obj.appearance.ambient
        color = (color.red, color.green, color.blue)
        if color not in colordict:
            count += 1
            colordict[color] = count
        offset += len(pts)
        attribute.extend([colordict[color]]*len(pts))

    colors=np.array(list(colordict.keys()))/255.
    if property is not None:
        property = np.repeat(np.array(property), [3]*len(property))
        mesh = k3d.line(vertices, shader='mesh', attribute=property, color_map=k3d.basic_color_maps.Jet, color_range=[min(property), max(property)])
    elif len(colors) == 1:
        colorhex = int(matplotlib.colors.rgb2hex(colors[0])[1:], 16)
        mesh = k3d.line(vertices, shader='mesh')
        mesh.color=colorhex
    else:
        color_map = list(zip(list(np.array(list(colordict.values())) /
                             float(max(colordict.values()))),
                        colors[:,0],
                        colors[:,1],
                        colors[:,2]))
        color_map.sort()
        #color_map=k3d.basic_color_maps.Jet
        attribute = list(np.array(attribute)/float(max(attribute)))
        mesh = k3d.line(vertices, shader='mesh', attribute=attribute, color_map=color_map)

    return mesh

def scene2mesh(scene, property=None, side='front'):
    """Return a mesh from a scene"""
    d = Tesselator()
    indices, vertices, colors, attribute=[], [], [], []
    colordict={}
    count=-1
    offset=0
    opacity = 1.0
    curves, texts, meshes = [], [], []
    for obj in scene:
        opacity = 1.0
        if isinstance(obj.geometry, Text):
            pos = obj.geometry.position
            texts.append(k3d.text(obj.geometry.string, [pos.x, pos.y, pos.z], label_box=False, color=0xaaaaaa))
            continue
        if obj.geometry.isACurve():
            curves.append(obj)
            continue
        obj.geometry.apply(d)
        idl = np.array([tuple(index) for index in list(d.discretization.indexList)])+offset
        pts = [(pt.x, pt.y, pt.z) for pt in list(d.discretization.pointList)]

        vertices.extend(pts)
        color = obj.appearance.ambient
        color = (color.red, color.green, color.blue)
        opacity = 1 - obj.appearance.transparency
        if color not in colordict:
            count += 1
            colordict[color] = count
        offset += len(pts)
        attribute.extend([colordict[color]]*len(pts))
        indices.extend(idl.tolist())
    colors=np.array(list(colordict.keys()))/255.
    if property is not None:
        property = np.repeat(np.array(property), [3]*len(property))
        mesh = k3d.mesh(vertices=vertices, indices=indices, attribute=property,
                        color_map=k3d.basic_color_maps.Jet,
                        color_range=[min(property), max(property)],
                        side=side, opacity=opacity)
    elif len(colors) == 1:
        colorhex = int(matplotlib.colors.rgb2hex(colors[0])[1:], 16)
        mesh = k3d.mesh(vertices=vertices, indices=indices, side=side, opacity=opacity)
        mesh.color=colorhex
    else:
        try:
            color_map = list(zip(list(np.array(list(colordict.values())) /
                                 float(max(colordict.values()))),
                            colors[:,0],
                            colors[:,1],
                            colors[:,2]))
            color_map.sort()
            attribute = list(np.array(attribute)/float(max(attribute)))
            mesh = k3d.mesh(vertices=vertices,
                            indices=indices,
                            attribute=attribute,
                            color_map=color_map,
                            side=side,
                            opacity=opacity)
        except ValueError:
            mesh = k3d.mesh(vertices=vertices,
                            indices=indices,
                            attribute=attribute,
                            side=side,
                            opacity=opacity)

    meshes = [mesh]
    if curves:
        meshes.extend([curve2mesh([crv]) for crv in curves])
        print("Display %d curves"%len(curves))

    if texts:
        meshes.extend(texts)
    return meshes


def group_meshes_by_color(scene, side='front'):
    """ Create one mesh by objects sharing the same color.
    """

    group_color = {}
    texts = []

    for obj in scene:
        if isinstance(obj.geometry, Text):
            pos = obj.geometry.position
            texts.append(k3d.text(obj.geometry.string, [pos.x, pos.y, pos.z], label_box=False, color=0xaaaaaa))
            continue
        color = obj.appearance.ambient
        color = (color.red, color.green, color.blue)

        group_color.setdefault(color, []).append(obj)

    curves = {}
    k_to_pop = []
    for k, obj in group_color.items():
        if obj[0].geometry.isACurve():
            curves[k] = obj
            k_to_pop.append(k)
    for k in k_to_pop:
        group_color.pop(k)

    meshes_scene = [scene2mesh(objects, side=side)[0] for objects in group_color.values()]
    # only one curve element in group_color - so take that element to split its lines
    if curves:
        meshes_crv = [curve2mesh([obj]) for obj in list(curves.values())[0]]
        meshes_scene.extend(meshes_crv)

    if texts:
        meshes_scene.extend(texts)
    return meshes_scene


def PlantGL(pglobject, plot=None, group_by_color=True, property=None, side='front'):
    """Return a k3d plot from PlantGL shape, geometry and scene objects"""
    if plot is None:
        plot = k3d.plot()

    if isinstance(pglobject, Geometry):
        mesh = tomesh(pglobject, side=side)
        plot += mesh
    elif isinstance(pglobject, Shape):
        mesh = tomesh(pglobject.geometry, side=side)
        mesh.color = pglobject.appearance.ambient.toUint()
        plot += mesh
    elif isinstance(pglobject, Scene):
        if group_by_color:
            meshes = group_meshes_by_color(pglobject, side=side)
            for mesh in meshes:
                plot += mesh
        else:
            meshes = scene2mesh(pglobject, property, side=side)
            for mesh in meshes:
                plot += mesh

    plot.lighting = 3
    #plot.colorbar_object_id = randint(0, 1000)
    return plot


def mtg2mesh(g, property_name):
    """Return a mesh from an MTG object depending on a specific property"""
    d = Tesselator()
    geometry = g.property('geometry')
    prop = g.property(property_name)
    vertices, indices, attr = [], [], []
    offset = 0
    for vid, geom in six.iteritems(geometry):
        if vid in prop:
            geom.apply(d)
            idl = np.array([tuple(index) for index in list(d.discretization.indexList)])+offset
            pts = [(pt.x, pt.y, pt.z) for pt in list(d.discretization.pointList)]
            vertices.extend(pts)
            offset += len(pts)
            indices.extend(idl.tolist())
            attr.extend([prop[vid]]*len(pts))
        #else:
        #    attr.extend([0]*len(pts))
    mesh = k3d.mesh(vertices=vertices,
                        indices=indices,
                        attribute=attr,
                        color_map=k3d.basic_color_maps.Jet)
    return mesh


def MTG(g, property_name, plot=None):
    """Return a plot from an MTG object"""
    if plot is None:
        plot = k3d.plot()

    mesh = mtg2mesh(g, property_name)
    plot += mesh
    plot.lighting = 3
    return plot
