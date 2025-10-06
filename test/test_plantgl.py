import openalea.plantgl.all as pgl
from openalea.oawidgets.plantgl import PlantGL
from openalea.oawidgets.plantgl import MTG as MTGPlantGL
from openalea.mtg import MTG

import pathlib

data = pathlib.Path(__file__).parent.resolve() / "data"


def test_scene():
    scene = pgl.Scene()
    c = pgl.NurbsCurve2D(
        [(0, 0, 1), (0.5, 1, 1), (1, 2, 1), (0.5, 3, 1), (0, 4, 1), (0, 4, 1)]
    )
    scene.add(pgl.Sphere(5))
    scene.add(c)
    scene.add(pgl.Text("test"))

    p = PlantGL(scene)
    assert p is not None


def test_object():
    s = pgl.Sphere()

    p = PlantGL(s)
    assert p is not None


def test_curve():
    c = pgl.NurbsCurve2D(
        [(0, 0, 1), (0.5, 1, 1), (1, 2, 1), (0.5, 3, 1), (0, 4, 1), (0, 4, 1)]
    )

    p = PlantGL(c)
    assert p is not None


def test_groupbycolor():
    scene = pgl.Scene()
    c = pgl.NurbsCurve2D(
        [(0, 0, 1), (0.5, 1, 1), (1, 2, 1), (0.5, 3, 1), (0, 4, 1), (0, 4, 1)]
    )
    scene.add(pgl.Sphere(5))
    scene.add(c)

    p = PlantGL(scene, group_by_color=False)
    assert p is not None


def test_property():
    scene = pgl.Scene()
    scene.add(pgl.Sphere(5))

    property = [1.0, 0.0]

    p = PlantGL(scene, property=property, group_by_color=False)
    assert p is not None


def test_text():
    scene = pgl.Scene()
    scene.add(pgl.Text("test"))

    p = PlantGL(scene)
    assert p is not None


def test_mtg():
    g = MTG(data / "boutdenoylum2.mtg")

    p = MTGPlantGL(g, "edge_type")
    assert p is not None
