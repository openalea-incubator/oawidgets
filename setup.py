#!/usr/bin/env python
# -*- coding: utf-8 -*-

# {# pkglts, pysetup.kwds
# format setup arguments

from setuptools import setup, find_packages


short_descr = "OpenAlea Widgets for Jupyter"
readme = open('README.rst').read()
history = open('HISTORY.rst').read()

# find packages
pkgs = find_packages('src')

setup_kwds = dict(
    name='oawidgets',
    version="1.0.0",
    description=short_descr,
    long_description=readme + '\n\n' + history,
    author="Baptiste Brument, Christophe Pradal",
    author_email="brument.bcb@gmail.com, christophe.pradal@cirad.fr",
    url='https://github.com/openalea-incubator/oawidgets',
    license='cecill-c',
    zip_safe=False,

    packages=pkgs,
    package_dir={'': 'src'},
    entry_points={},
    keywords='openalea, jupyter, widgets, MTG, lpy, plantgl, 3D',
    )
# #}
# change setup_kwds below before the next pkglts tag

# do not change things below
# {# pkglts, pysetup.call
setup(**setup_kwds)
# #}
