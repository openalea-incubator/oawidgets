# -*- coding: utf-8 -*-
"""
===========
lpymagic
===========

Magics for interacting with LPy via openalea.lpy.

.. note::

  The ``openalea.lpy`` module needs to be installed separately and
  can be obtained using ``conda``.

Usage
=====

``%lpy``

{LPY_DOC}

``%lpy_rule``

{LPY_RULE_DOC}

``%lpy_axiom``

{LPY_AXIOM_DOC}


"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2013-2019 Christophe Pradal
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import tempfile, os
from glob import glob
from shutil import rmtree

import numpy as np
import openalea.lpy as lpy
from openalea.plantgl.all import Viewer

from openalea.mtg import MTG
from openalea.mtg.io import mtg2lpy, lpy2mtg

from xml.dom import minidom


from IPython.core.displaypub import publish_display_data
from IPython.core.magic import (Magics, magics_class, line_magic,
                                line_cell_magic, needs_local_scope)
from IPython.testing.skipdoctest import skip_doctest
from IPython.core.magic_arguments import (
    argument, magic_arguments, parse_argstring
)
from IPython.utils.py3compat import unicode_to_str
from IPython.display import Image, display


_mimetypes = {'png' : 'image/png',
             'svg' : 'image/svg+xml',
             'jpg' : 'image/jpeg',
             'jpeg': 'image/jpeg'}

@magics_class
class LpyMagics(Magics):
    """A set of magics useful for interactive work with Lpy
    """
    def __init__(self, shell):
        """
        Parameters
        ----------
        shell : IPython shell

        """
        super(LpyMagics, self).__init__(shell)
        self._lsys = lpy.Lsystem()
        self._plot_format = 'png'

        # Allow publish_display_data to be overridden for
        # testing purposes.
        self._publish_display_data = publish_display_data


    def _plot3d(self, scene, format='png'):
        """
        Baptise
        TODO: Replace by the k3d plantgl connection.
        """
        fn = tempfile.mktemp(suffix='.'+format)
        Viewer.frameGL.setBgColor(255,255,255)
        #Viewer.animation(True)
        Viewer.display(scene)
        Viewer.saveSnapshot(fn, format)
        img = open(fn, 'rb').read()
        os.unlink(fn)
        return img


    @skip_doctest
    @line_magic
    def lpy_axiom(self, line):
        '''
        Line-level magic that define the Lsystm Axiom to Lpy.

        `line` should be made up of a string or an AxialTree available in the
        IPython namespace::

            In [1]: X = 'F(10)[(+30)F(1)]A'

            In [10]: %lpy_axiom X

            In [11]: %%lpy -n 10
            Out[11]: 2.0

        '''
        axiom = line
        axiom = unicode_to_str(axiom)
        self._lsys.axiom = axiom


    @skip_doctest
    @line_magic
    def lpy_rule(self, line):
        '''
        TODO : Update the doc string
        Line-level magic that pulls a variable from Lpy.

            In [1]: %lpy_axiom 'A'
            In [2]: %lpy_rule 'A --> F A'
            In [3]: %%lpy -n 10

        '''
        rule = unicode_to_str(line)
        self._lsys.addRule(rule)



    @skip_doctest
    @magic_arguments()
    @argument(
        '-i', '--input', action='append',
        help='Names of input variable from shell.user_ns to be assigned to LPy variables of the same names. Multiple names can be passed separated only by commas with no whitespace.'
        )
    @argument(
        '-o', '--output', action='append',
        help='Names of variables to be pushed from lpy to shell.user_ns after executing cell body. Multiple names can be passed separated only by commas with no whitespace.'
        )
    @argument(
        '-w', '--workstring', action='append',
        help='Axial tree string or MTG to be set to Lpy before executing cell '
             'body. '
        )
    @argument(
        '-a', '--axialtree', action='append',
        help='Names of axial tree variable to be pulled from Lpy after executing cell '
             'body. '
        )
    @argument(
        '-g', '--mtg', action='append',
        help='Names of MTG variable to be pulled from Lpy after executing cell '
             'body. '
        )
    @argument(
        '-s', '--scene', action='append',
        help='Name of scene variable to be pulled from LPy after executing cell.'
        )
    @argument(
        '-n', '--nbstep', action='append',
        help='Number of steps to be run by LPy..'
        )
    @argument(
        '-f', '--format', action='store',
        help='Plot format (png, svg or jpg).'
        )

    @needs_local_scope
    @argument(
        'code',
        nargs='*',
        )
    @line_cell_magic
    def lpy(self, line, cell=None, local_ns=None):
        '''
        .. todo:: Update the docstring

        Execute code in Lpy, and pull some of the results back into the
        Python namespace.

            In [9]: %lpy -w axiom -n 10 -g

        As a cell, this will run a block of Lpy code, without returning any
        value::

            In [10]: %%lpy
               ....: p = [-2, -1, 0, 1, 2]
               ....: polyout(p, 'x')

            -2*x^4 - 1*x^3 + 0*x^2 + 1*x^1 + 2

        In the notebook, plots are published as the output of the cell, e.g.

        %lpy plot([1 2 3], [4 5 6])

        will create a line plot.

        Objects can be passed back and forth between Lpy and IPython via the
        -i and -o flags in line::

            In [14]: Z = np.array([1, 4, 5, 10])

            In [15]: %lpy -i Z mean(Z)
            Out[15]: array([ 5.])


            In [16]: %lpy -o W W = Z * mean(Z)
            Out[16]: array([  5.,  20.,  25.,  50.])

            In [17]: W
            Out[17]: array([  5.,  20.,  25.,  50.])

        The size and format of output plots can be specified::

            In [18]: %%lpy -s 600,800 -f svg
                ...: plot([1, 2, 3]);

        '''
        args = parse_argstring(self.lpy, line)

        # arguments 'code' in line are prepended to the cell lines
        if cell is None:
            code = ''
            return_output = True
        else:
            code = cell
            return_output = False

        code = ' '.join(args.code) + code
        code = unicode_to_str(code)


        # if there is no local namespace then default to an empty dict
        if local_ns is None:
            local_ns = {}


        parameters = {}
        if args.input:
            for input in ','.join(args.input).split(','):
                input = unicode_to_str(input)
                if input =='*':
                    parameters.update(self.shell.user_ns)
                else:
                    try:
                        val = local_ns[input]
                    except KeyError:
                        val = self.shell.user_ns[input]
                    parameters[input] = val

        if parameters:
            self._lsys.context().updateNamespace(parameters)
        if code:
            self._lsys.setCode(code, parameters)


        #################################################
        # set, input

        workstring = ''
        if args.workstring:
            workstring = args.workstring[0]
            workstring = unicode_to_str(workstring)
            try:
                workstring = local_ns[workstring]
            except KeyError:
                workstring = self.shell.user_ns[workstring]
            except:
                pass

            if isinstance(workstring, str):
                self._lsys.makeCurrent()
                workstring = lpy.AxialTree(workstring)
                self._lsys.done()
            elif isinstance(workstring, MTG):
                workstring = mtg2lpy(workstring,self._lsys)
            else:
                pass

            # try:
            #     ws = local_ns[workstring]
            # except KeyError:
            #     ws = self.shell.user_ns[workstring]


        n = 1
        if args.nbstep:
           n = int(args.nbstep[0])

        if workstring:
            tree = self._lsys.iterate(workstring,n)
        else:
           n = self._lsys.derivationLength

        c_iter = self._lsys.getLastIterationNb()
        if not workstring:
            workstring = self._lsys.axiom
        if len(parameters) > 0:
            self._lsys.context().updateNamespace(parameters)

        print 'DEBUG: ', workstring, c_iter, n
        tree = self._lsys.iterate(workstring,c_iter,n)

        if args.axialtree:
            axial_name = unicode_to_str(args.axialtree[0])
            self.shell.push({axial_name: tree})


        scene = self._lsys.sceneInterpretation(tree)
        if args.scene and scene:
            self.shell.push({args.scene[0]: scene})

        mtg = None
        if args.mtg:
            mtg_name = unicode_to_str(args.mtg[0])
            mtg = lpy2mtg(tree, self._lsys, scene=scene)
            self.shell.push({mtg_name: mtg})

        if args.format is not None:
            plot_format = args.format
        else:
            plot_format = 'png'


        key = 'LpyMagic.Lpy'
        display_data = {}

        # Publish text output
        """
        if text_output:
            display_data.append((key, {'text/plain': text_output}))
        """
        # Publish images
        image = self._plot3d(scene, format=plot_format)

        plot_mime_type = _mimetypes.get(plot_format, 'image/png')
        #width, height = [int(s) for s in size.split(',')]
        #for image in images:
        display_data[plot_mime_type]= image

        """
        if args.output:
            for output in ','.join(args.output).split(','):
                output = unicode_to_str(output)
                self.shell.push({output: self._oct.get(output)})
        """
        #for source, data in display_data:
        #    self._publish_display_data(source, data)
        self._publish_display_data(data=display_data)

        if return_output:
            return tree if not mtg else mtg


    @skip_doctest
    @magic_arguments()
    @argument(
        '-w', '--workstring', action='append',
        help='Axial tree string or MTG to be set to Lpy before executing cell '
             'body. '
        )
    @argument(
        '-a', '--axialtree', action='append',
        help='Names of axial tree variable to be pulled from Lpy after executing cell '
             'body. '
        )
    @argument(
        '-s', '--scene', action='append',
        help='Name of scene variable to be pulled from LPy after executing cell.'
        )
    @argument(
        '-g', '--mtg', action='append',
        help='Name of MTG variable to be pulled from LPy after executing cell.'
        )

    @argument(
        '-n', '--nbstep', action='append',
        help='Number of steps to be run by LPy..'
        )

    @argument(
        '-f', '--format', action='store',
        help='Plot format (png, svg or jpg).'
        )

    @needs_local_scope
    @line_cell_magic
    def lpy_iter(self, line, cell=None, local_ns=None):
        '''
        Execute code in Lpy, and pull some of the results back into the
        Python namespace.

            In [9]: %lpy X = [1 2; 3 4]; mean(X)
            Out[9]: array([[ 2., 3.]])

        As a cell, this will run a block of Lpy code, without returning any
        value::

            In [10]: %%lpy
               ....: p = [-2, -1, 0, 1, 2]
               ....: polyout(p, 'x')

            -2*x^4 - 1*x^3 + 0*x^2 + 1*x^1 + 2

        In the notebook, plots are published as the output of the cell, e.g.

        %lpy plot([1 2 3], [4 5 6])

        will create a line plot.

        Objects can be passed back and forth between Lpy and IPython via the
        -i and -o flags in line::

            In [14]: Z = np.array([1, 4, 5, 10])

            In [15]: %lpy -i Z mean(Z)
            Out[15]: array([ 5.])


            In [16]: %lpy -o W W = Z * mean(Z)
            Out[16]: array([  5.,  20.,  25.,  50.])

            In [17]: W
            Out[17]: array([  5.,  20.,  25.,  50.])

        The size and format of output plots can be specified::

            In [18]: %%lpy -s 600,800 -f svg
                ...: plot([1, 2, 3]);

        '''
        args = parse_argstring(self.lpy, line)

        # arguments 'code' in line are prepended to the cell lines
        return_output = True


        # if there is no local namespace then default to an empty dict
        if local_ns is None:
            local_ns = {}

        workstring = self._lsys.axiom
        if args.workstring:
            workstring = ','.join(args.workstring).split(',')[0]
            workstring = unicode_to_str(workstring)

            try:
                ws = local_ns[workstring]
            except KeyError:
                ws = self.shell.user_ns[workstring]

            if isinstance(ws,MTG):
                workstring = mtg2lpy(ws,self._lsys)
            else:
                workstring = ws



        n0 = self._lsys.getLastIterationNb()
        n = self._lsys.derivationLength-n0

        if args.nbstep:
           n = int(args.nbstep[0])

        tree = self._lsys.iterate(workstring,n0,n)

        if args.axialtree:
            axial_name = unicode_to_str(args.axialtree[0])
            self.shell.push({axial_name: tree})

        scene = self._lsys.sceneInterpretation(tree)
        if args.scene:
            self.shell.push({args.scene[0]: scene})

        g = None
        if args.mtg:
            mtg_name = unicode_to_str(args.mtg[0])
            g = lpy2mtg(tree, self._lsys, scene=scene)
            self.shell.push({mtg_name: g})

        if args.format is not None:
            plot_format = args.format
        else:
            plot_format = 'png'


        key = 'LpyMagic.Lpy'
        display_data = []

        # Publish text output
        """
        if text_output:
            display_data.append((key, {'text/plain': text_output}))
        """
        # Publish images
        images = [self._plot3d(scene, format=plot_format)]

        plot_mime_type = _mimetypes.get(plot_format, 'image/png')
        #width, height = [int(s) for s in size.split(',')]
        for image in images:
            display_data.append((key, {plot_mime_type: image}))

        """
        if args.output:
            for output in ','.join(args.output).split(','):
                output = unicode_to_str(output)
                self.shell.push({output: self._oct.get(output)})
        """
        for source, data in display_data:
            self._publish_display_data(source, data)

        if return_output:
            return tree if not args.mtg else g

__doc__ = __doc__.format(
    LPY_DOC = ' '*8 + LpyMagics.lpy.__doc__,
    LPY_AXIOM_DOC = ' '*8 + LpyMagics.lpy_axiom.__doc__,
    LPY_RULE_DOC = ' '*8 + LpyMagics.lpy_rule.__doc__,
    LPY_ITER_DOC = ' '*8 + LpyMagics.lpy_iter.__doc__,
    )


def load_ipython_extension(ip):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext oawidgets.lpymagic` or be configured to be
    autoloaded by IPython at startup time.
    """
    ip.register_magics(LpyMagics)
