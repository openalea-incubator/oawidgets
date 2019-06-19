from openalea.plantgl.all import *
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

def PlantGL(pglobject, plot=None):
    """Return a k3d plot from PlantGL shape, geometry and scene objects"""
    if plot is None:
        plot = k3d.plot()
    d = Discretizer()

    if isinstance(pglobject, Geometry):
        mesh = tomesh(pglobject)
        plot += mesh
    elif isinstance(pglobject, Shape):
        mesh = tomesh(pglobject.geometry)
        plot += mesh
    elif isinstance(pglobject, Scene):
        for sh in pglobject:
            mesh = tomesh(sh.geometry)
            plot+= mesh
    return plot
