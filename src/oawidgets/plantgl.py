""" Convert a PlantGL scene to k3d.

3D visualisation widgets in Jupyter.
"""
from openalea.plantgl.all import *
from random import randint
import matplotlib
import numpy as np
import k3d


def tomesh(geometry, d=None):
    """Return a mesh from a geometry object"""
    if d is None:
        d = Tesselator()

    geometry.apply(d)
    idl = [tuple(index) for index in list(d.discretization.indexList)]
    pts = [(pt.x, pt.y, pt.z) for pt in list(d.discretization.pointList)]
    mesh = k3d.mesh(vertices=pts, indices=idl)
    return mesh


def scene2mesh(scene):
    """Return a mesh from a scene"""
    d = Tesselator()
    indices, vertices, colors, attribute=[], [], [], []
    colordict={}
    count=-1
    offset=0
    for obj in scene:
        obj.geometry.apply(d)
        idl = np.array([tuple(index) for index in list(d.discretization.indexList)])+offset
        pts = [(pt.x, pt.y, pt.z) for pt in list(d.discretization.pointList)]

        vertices.extend(pts)
        color = obj.appearance.ambient
        color = (color.red, color.green, color.blue)
        if color not in colordict:
            count += 1
            colordict[color] = count
        offset += len(pts)
        attribute.extend([colordict[color]]*len(pts))
        indices.extend(idl.tolist())
    colors=np.array(colordict.keys())/255.
    if len(colors) == 1:
        colorhex = int(matplotlib.colors.rgb2hex(colors[0])[1:], 16)
        mesh = k3d.mesh(vertices=vertices, indices=indices)
        mesh.color=colorhex
    else:
        color_map = zip(list(np.array(colordict.values()) /
                             float(max(colordict.values()))),
                        colors[:,0],
                        colors[:,1],
                        colors[:,2])
        color_map.sort()
        #color_map=k3d.basic_color_maps.Jet
        attribute = list(np.array(attribute)/float(max(attribute)))
        mesh = k3d.mesh(vertices=vertices,
                        indices=indices,
                        attribute=attribute,
                        color_map=color_map)
    return mesh


def group_meshes_by_color(scene):
    """ Create one mesh by objects sharing the same color.
    """
    d = Tesselator()

    group_color = {}

    for obj in scene:
        color = obj.appearance.ambient
        color = (color.red, color.green, color.blue)

        group_color.setdefault(color, []).append(obj)


    meshes = [scene2mesh(objects) for objects in group_color.values()]
    return meshes


def PlantGL(pglobject, plot=None, group_by_color=True):
    """Return a k3d plot from PlantGL shape, geometry and scene objects"""
    if plot is None:
        plot = k3d.plot()

    if isinstance(pglobject, Geometry):
        mesh = tomesh(pglobject)
        plot += mesh
    elif isinstance(pglobject, Shape):
        mesh = tomesh(pglobject.geometry)
        mesh.color = pglobject.appearance.ambient.toUint()
        plot += mesh
    elif isinstance(pglobject, Scene):
        if group_by_color:
            meshes = group_meshes_by_color(pglobject)
            for mesh in meshes:
                plot += mesh
        else:
            mesh = scene2mesh(pglobject)
            plot += mesh

    plot.lighting = 3
    #plot.colorbar_object_id = randint(0, 1000)
    return plot


def mtg2mesh(g, property_name):
    """Return a mesh from a MTG object depending on a specific property"""
    d = Tesselator()
    geometry = g.property('geometry')
    prop = g.property(property_name)
    vertices, indices, attr = [], [], []
    offset = 0
    for vid, geom in geometry.iteritems():
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
    """Return a plot from a MTG object"""
    if plot is None:
        plot = k3d.plot()

    mesh = mtg2mesh(g, property_name)
    plot += mesh
    plot.lighting = 3
    plot.colorbar_object_id = randint(0,1000)
    return plot
