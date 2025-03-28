from openalea.plantgl.all import *
from random import randint

s = Sphere()
scene = Scene()

def color():
    return Material(ambient=Color3(randint(0,255), randint(0,255), randint(0,255)))

# Build four Spheres at different positions
for i in range(4):
    si = Translated((2*(i%2),2*(i//2),0), s)
    scene.add(Shape(si, color()))

