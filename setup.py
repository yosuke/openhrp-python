#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''openhrp

Copyright (C) 2010
    Yosuke Matsusaka
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

openhrp install script.

'''


from distutils import errors
from distutils import log
from distutils import util
from distutils.cmd import Command
from distutils.core import setup
from distutils.command import build
import os
import os.path
import subprocess
import sys


def gen_idl_name(dir, name):
    '''Generate IDL file name from directory prefix and IDL module name.'''
    return os.path.join(dir, name + '.idl')


class BuildIDL(Command):
    '''Implemented the build IDL subcommand.'''

    description = 'Generate Python stubs from IDL files'

    user_options = [('omniidl=', 'i', 'omniidl program used to build stubs'),
                    ('idldir=',  'd', 'directory where IDL files reside')
                    ]

    def initialize_options(self):
        self.idl_dir  = None
        self.omniidl = None
        self.omniidl_params = ['-bpython']
        self.idl_files = ['CollisionDetector', 'Controller', 'DynamicsSimulator',
                          'ModelLoader', 'OnlineViewer', 'OpenHRPCommon',
                          'PathPlanner', 'ViewSimulator', 'World']

    def finalize_options(self):
        if not self.omniidl:
            self.omniidl = 'omniidl'
        if not self.idl_dir:
            self.idl_dir = os.path.join(os.getcwd(), 'openhrp', 'hrpidl')

    def compile_idl(self, cmd, params, files):
        log.info('{0} {1} {2}'.format(cmd, ' '.join(params), ' '.join(files)))
        process = subprocess.Popen([cmd] + params + files,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                cwd=self.idl_dir)
        stdout, stderr = process.communicate()
        log.info(stdout)
        if process.returncode != 0:
            raise errors.DistutilsExecError('Error compiling IDL \
({0})'.format(process.returncode))

    def run(self):
        util.execute(self.compile_idl,
                     (self.omniidl, self.omniidl_params,
                         [gen_idl_name(self.idl_dir, idl_file) \
                                 for idl_file in self.idl_files]),
                     msg='Generating python stubs from IDL files')


class CustomBuild(build.build):
    def has_pure_modules(self):
        return self.distribution.has_pure_modules()

    def has_c_libraries(self):
        return self.distribution.has_c_libraries()

    def has_ext_modules(self):
        return self.distribution.has_ext_modules()

    def has_scripts(self):
        return self.distribution.has_scripts()

    def has_idl_files(self):
        return True

    sub_commands = [('build_idl', has_idl_files),
                    ('build_py', has_pure_modules),
                    ('build_clib', has_c_libraries),
                    ('build_ext', has_ext_modules),
                    ('build_scripts', has_scripts)
                    ]


setup(name='openhrp',
      version='0.0.1',
      description='Python API and command line tools for interacting with OpenHRP corba servers.',
      long_description='Python API and command line tools for interacting with OpenHRP corba servers.',
      author='Yosuke Matsusaka',
      author_email='yosuke.matsusaka@aist.go.jp',
      url='http://github.com/yosuke/openhrp-python',
      license='EPL',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: EPL License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          ],
      packages=['openhrp',
                'openhrp.hrpidl',
                'openhrp.hrpidl.OpenHRP',
                'openhrp.hrpidl.OpenHRP__POA'],
      cmdclass={'build':CustomBuild, 'build_idl': BuildIDL}
      )


# vim: tw=79
