#!/usr/bin/env python
# -*- python -*-

import argparse
import importlib
import os
import pickle
import sys

from . import builtins
from . import rules
from . import utils
from .build_inputs import BuildInputs
from .environment import Environment

bfgfile = 'build.bfg'
envfile = '.bfg_environ'

def is_srcdir(path):
    return os.path.exists(os.path.join(path, bfgfile))

def samefile(path1, path2):
    if hasattr(os.path, 'samefile'):
        return os.path.samefile(path1, path2)
    else:
        # This isn't entirely accurate, but it's close enough, and should only
        # be necessary for Windows with Python 2.x.
        return os.path.realpath(path1) == os.path.realpath(path2)

def validate_build_directories(args):
    if not args.srcdir:
        raise ValueError('at least one of srcdir or builddir must be defined')

    if args.builddir:
        if not os.path.exists(args.srcdir):
            raise ValueError('{} does not exist'.format(args.srcdir))
        if not os.path.isdir(args.srcdir):
            raise ValueError('{} is not a directory'.format(args.srcdir))
    else:
        if os.path.exists(os.path.join(args.srcdir, bfgfile)):
            args.builddir = '.'
        else:
            args.srcdir, args.builddir = '.', args.srcdir

    if os.path.exists(args.builddir):
        if samefile(args.srcdir, args.builddir):
            raise ValueError('source and build directories must be different')
        if not os.path.isdir(args.builddir):
            raise ValueError('{} is not a directory'.format(args.builddir))

    if not is_srcdir(args.srcdir):
        raise ValueError('source directory must contain a build.bfg file')
    if is_srcdir(args.builddir):
        raise ValueError(
            'build directory must not contain a build.bfg file'
        )

    if not os.path.exists(args.builddir):
        os.mkdir(args.builddir)
    args.srcdir = os.path.abspath(args.srcdir)
    args.builddir = os.path.abspath(args.builddir)

def validate_regen_directories(args):
    if args.builddir:
        raise ValueError('foo')
    args.srcdir, args.builddir = None, os.path.abspath(args.srcdir or '.')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('srcdir', nargs='?', help='source directory')
    parser.add_argument('builddir', nargs='?', help='build directory')
    parser.add_argument('--backend', default='make', help='backend')
    parser.add_argument('--prefix', default='/usr', help='installation prefix')
    parser.add_argument('--regenerate', action='store_true',
                        help='regenerate build files')
    args = parser.parse_args()

    try:
        if args.regenerate:
            validate_regen_directories(args)
            env = pickle.load(open(os.path.join(args.builddir, envfile)))
        else:
            validate_build_directories(args)
            env = Environment(
                bfgpath=os.path.realpath(__file__),
                srcdir=args.srcdir,
                builddir=args.builddir,
                backend=args.backend,
                install_prefix=os.path.abspath(args.prefix)
            )
            pickle.dump(env, open(os.path.join(args.builddir, envfile), 'w'),
                        protocol=2)
    except Exception as e:
        parser.error(e)

    build = BuildInputs()
    os.chdir(env.srcdir)
    execfile(os.path.join(env.srcdir, bfgfile), builtins.bind(build, env))

    backend = importlib.import_module('.backends.{}'.format(env.backend),
                                      'bfg9000')
    backend.write(env, build)
