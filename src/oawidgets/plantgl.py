from openalea.plantgl.all import *
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
    indices, vertices, colors, attributes=[], [], [], []
    colordict={}
    count=-1
    offset=0
    for obj in scene:
	obj.geometry.apply(d)
	idl = np.array([tuple(index) for index in list(d.discretization.indexList)])+offset
    	pts = [(pt.x, pt.y, pt.z) for pt in list(d.discretization.pointList)]
        color = obj.appearance.ambient
        color = (color.red, color.green, color.blue)
        if not(color in colordict):
            count+=1
            colordict[color]=count
        attributes.append(colordict[color])
        offset += len(pts)
        indices.extend(idl.tolist())
    colors=np.array(colordict.keys())/255.
    color_map=zip(list(np.array(colordict.values())/float(max(colordict.values()))), colors[:,0], colors[:,1], colors[:,2])
    attributes = list(np.array(attributes)/float(max(attributes)))
    print attributes
    print color_map
    if len(color_map) == 1:
    	mesh = k3d.mesh(vertices=vertices, indices=indices, color=rgb2hex(colordict.keys()))
    else:
    	mesh = k3d.mesh(vertices=vertices, indices=indices, attributes=attributes, color_map=color_map)
    return mesh


def PlantGL(pglobject, plot=None):
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
        for sh in pglobject:
            PlantGL(sh,plot)
    return plot

def PlantGLscene(pglobject, plot=None):
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
        mesh = scene2mesh(pglobject)
        plot += mesh
    return plot
