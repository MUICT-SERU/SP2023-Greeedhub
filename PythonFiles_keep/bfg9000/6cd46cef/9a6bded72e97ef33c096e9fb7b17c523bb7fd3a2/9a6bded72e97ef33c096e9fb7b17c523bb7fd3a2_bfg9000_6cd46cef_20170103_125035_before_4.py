import os.path
import re
import subprocess
from itertools import chain
from six.moves import filter as ifilter

from .ar import ArLinker
from .utils import darwin_install_name
from ..builtins.symlink import Symlink
from ..file_types import *
from ..iterutils import first, iterate, uniques
from ..path import Path, Root


class CcBuilder(object):
    def __init__(self, env, lang, name, command, cflags_name, cflags, ldflags,
                 ldlibs):
        self.brand = 'unknown'
        with open(os.devnull, 'wb') as devnull:
            try:
                output = subprocess.check_output(
                    '{} --version'.format(command),
                    shell=True, universal_newlines=True, stderr=devnull
                )
                if 'Free Software Foundation' in output:
                    self.brand = 'gcc'
                elif 'clang' in output:
                    self.brand = 'clang'
            except:
                pass

        self.compiler = CcCompiler(env, lang, name, command, cflags_name,
                                   cflags)
        try:
            self.pch_compiler = CcPchCompiler(env, lang, self.brand, name,
                                              command, cflags_name, cflags)
        except ValueError:
            self.pch_compiler = None

        self._linkers = {
            'executable': CcExecutableLinker(
                env, lang, name, command, ldflags, ldlibs
            ),
            'shared_library': CcSharedLibraryLinker(
                env, lang, name, command, ldflags, ldlibs
            ),
            'static_library': ArLinker(env, lang),
        }
        self.packages = CcPackageResolver(env, lang, command)

    @property
    def flavor(self):
        return 'cc'

    @property
    def auto_link(self):
        return False

    def linker(self, mode):
        return self._linkers[mode]


class CcBaseCompiler(object):
    def __init__(self, env, lang, rule_name, command_var, command, cflags_name,
                 cflags):
        self.platform = env.platform
        self.lang = lang

        self.rule_name = rule_name
        self.command_var = command_var
        self.command = command

        self.flags_var = cflags_name
        self.global_args = cflags

    @property
    def flavor(self):
        return 'cc'

    @property
    def deps_flavor(self):
        return None if self.lang in ('f77', 'f95') else 'gcc'

    @property
    def num_outputs(self):
        return 1

    @property
    def depends_on_libs(self):
        return False

    def __call__(self, cmd, input, output, deps=None, args=None):
        result = [cmd, '-x', self._langs[self.lang]]
        result.extend(iterate(args))
        result.extend(['-c', input])
        if deps:
            result.extend(['-MMD', '-MF', deps])
        result.extend(['-o', output])
        return result

    def _include_dir(self, directory):
        # Don't explicitly include default directories (e.g. /usr/include).
        # Doing so would break GCC 6 when #including stdlib.h:
        # <https://gcc.gnu.org/bugzilla/show_bug.cgi?id=70129>.
        if ( directory.path.root == Root.absolute and
             directory.path.string() in self.platform.include_dirs):
            return []
        elif directory.system:
            return ['-isystem', directory.path]
        else:
            return ['-I' + directory.path]

    def _include_pch(self, pch):
        return ['-include', pch.path.stripext()]

    def args(self, options, output, pkg=False):
        includes = getattr(options, 'includes', [])
        pch = getattr(options, 'pch', None)
        return sum((self._include_dir(i) for i in includes),
                   self._include_pch(pch) if pch else [])

    def link_args(self, mode, defines):
        args = []
        if ( mode in ['shared_library', 'static_library'] and
             self.platform.flavor != 'windows'):
            args.append('-fPIC')

        # We only need to define LIBFOO_EXPORTS/LIBFOO_STATIC macros on
        # platforms that have different import/export rules for libraries. We
        # approximate this by checking if the platform uses import libraries,
        # and only define the macros if it does.
        if self.platform.has_import_library:
            args.extend('-D' + i for i in defines)
        return args


class CcCompiler(CcBaseCompiler):
    _langs = {
        'c'     : 'c',
        'c++'   : 'c++',
        'objc'  : 'objective-c',
        'objc++': 'objective-c++',
        'f77'   : 'f77',
        'f95'   : 'f95',
        'java'  : 'java',
    }

    def __init__(self, env, lang, name, command, cflags_name, cflags):
        CcBaseCompiler.__init__(self, env, lang, name, name, command,
                                cflags_name, cflags)

    def output_file(self, name, options):
        # XXX: MinGW's object format doesn't appear to be COFF...
        return ObjectFile(Path(name + '.o'), self.platform.object_format,
                          self.lang)


class CcPchCompiler(CcCompiler):
    _langs = {
        'c'     : 'c-header',
        'c++'   : 'c++-header',
        'objc'  : 'objective-c-header',
        'objc++': 'objective-c++-header',
    }

    def __init__(self, env, lang, brand, name, command, cflags_name, cflags):
        if lang == 'java':
            raise ValueError('Java has no precompiled headers')
        CcBaseCompiler.__init__(self, env, lang, name + '_pch', name, command,
                                cflags_name, cflags)
        self._brand = brand

    def output_file(self, name, options):
        ext = '.gch' if self._brand == 'gcc' else '.pch'
        return PrecompiledHeader(Path(name + ext), self.lang)


class CcLinker(object):
    flags_var = 'ldflags'
    libs_var = 'ldlibs'

    __allowed_langs = {
        'c'     : {'c'},
        'c++'   : {'c', 'c++', 'f77', 'f95'},
        'objc'  : {'c', 'objc', 'f77', 'f95'},
        'objc++': {'c', 'c++', 'objc', 'objc++', 'f77', 'f95'},
        'f77'   : {'c', 'f77', 'f95'},
        'f95'   : {'c', 'f77', 'f95'},
        # XXX: Include other languages that should work here?
        'java'  : {'java'},
    }

    def __init__(self, env, lang, rule_name, command_var, command, ldflags,
                 ldlibs):
        self.env = env
        self.lang = lang

        self.rule_name = rule_name
        self.command_var = command_var
        self.command = command

        self.global_args = ldflags
        self.global_libs = ldlibs

        # Create a regular expression to extract the library name for linking
        # with -l.
        lib_formats = [r'lib(.*)\.a']
        if not self.platform.has_import_library:
            so_ext = re.escape(self.platform.shared_library_ext)
            lib_formats.append(r'lib(.*)' + so_ext)
        # XXX: Include Cygwin here too?
        if self.platform.name == 'windows':
            lib_formats.append(r'(.*)\.lib')
        self._lib_re = re.compile('(?:' + '|'.join(lib_formats) + ')$')

    def _extract_lib_name(self, library):
        basename = library.path.basename()
        m = self._lib_re.match(basename)
        if not m:
            raise ValueError("'{}' is not a valid library name"
                             .format(basename))

        # Get the first non-None group from the match.
        return next(ifilter( None, m.groups() ))

    @property
    def platform(self):
        return self.env.platform

    @property
    def flavor(self):
        return 'cc'

    def can_link(self, format, langs):
        return (format == self.platform.object_format and
                self.__allowed_langs[self.lang].issuperset(langs))

    @property
    def num_outputs(self):
        return 1

    def __call__(self, cmd, input, output, libs=None, args=None):
        result = [cmd] + self._always_args
        result.extend(iterate(args))
        result.extend(iterate(input))
        result.extend(iterate(libs))
        result.extend(['-o', output])
        return result

    @property
    def _always_args(self):
        return []

    def _lib_dirs(self, libraries, extra_dirs):
        dirs = uniques(chain(
            (i.path.parent() for i in iterate(libraries)
             if not isinstance(i, StaticLibrary)),
            extra_dirs
        ))
        return ['-L' + i for i in dirs]

    def _rpath(self, libraries, output):
        if not self.platform.has_rpath:
            return []

        start = output.path.parent()
        paths = uniques(i.path.parent().relpath(start) for i in libraries
                        if isinstance(i, SharedLibrary))
        if not paths:
            return []

        if output.format == 'elf':
            base = '$ORIGIN'
            return ['-Wl,-rpath,{}'.format(':'.join(
                base if i == '.' else os.path.join(base, i) for i in paths
            ))]
        elif output.format == 'mach-o':
            base = '@executable_path'
            return ( ['-Wl,-headerpad_max_install_names'] +
                     ['-Wl,-rpath,{}'.format(os.path.join(base, i))
                      for i in paths] )
        else:
            raise ValueError('unrecognized object format "{}"'
                             .format(output.format))

    def _entry_point(self, entry_point):
        # This only applies to GCJ. XXX: Move GCJ-stuff to a separate class?
        if self.lang == 'java' and entry_point:
            return ['--main={}'.format(entry_point)]
        return []

    def args(self, options, output, pkg=False):
        libraries = getattr(options, 'all_libs', [])
        lib_dirs = getattr(options, 'lib_dirs', [])
        entry_point = getattr(options, 'entry_point', None)
        return ( self._lib_dirs(libraries, lib_dirs) +
                 self._rpath(libraries, first(output)) +
                 self._entry_point(entry_point))

    def _link_lib(self, library):
        if isinstance(library, WholeArchive):
            if self.platform.name == 'darwin':
                return ['-Wl,-force_load', library.path]
            return ['-Wl,--whole-archive', library.path,
                    '-Wl,--no-whole-archive']
        elif isinstance(library, StaticLibrary):
            return [library.path]

        # If we're here, we have a SharedLibrary (or possibly just a Library
        # in the case of MinGW).
        return ['-l' + self._extract_lib_name(library)]

    def always_libs(self, primary):
        # XXX: Don't just asssume that these are these are the right libraries
        # to use. For instance, clang users might want to use libc++ instead.
        libs = []
        if self.lang in ('c++', 'objc++') and not primary:
            libs.append('-lstdc++')
        if self.lang in ('objc', 'objc++'):
            libs.append('-lobjc')
        if self.lang in ('f77', 'f95') and not primary:
            libs.append('-lgfortran')
        return libs

    def libs(self, options, output, pkg=False):
        libraries = getattr(options, 'all_libs', [])
        return sum((self._link_lib(i) for i in libraries), [])

    def post_install(self, output):
        if not self.platform.has_rpath:
            return None

        if output.format == 'elf':
            tool = self.env.tool('patchelf')
        elif output.format == 'mach-o':
            tool = self.env.tool('install_name_tool')
        else:
            raise ValueError('unrecognized object format "{}"'
                             .format(output.format))
        return tool(tool, output, output.runtime_deps)


class CcExecutableLinker(CcLinker):
    def __init__(self, env, lang, name, command, ldflags, ldlibs):
        CcLinker.__init__(self, env, lang, name + '_link', name, command,
                          ldflags, ldlibs)

    def output_file(self, name, options):
        path = Path(name + self.platform.executable_ext)
        return Executable(path, self.platform.object_format)


class CcSharedLibraryLinker(CcLinker):
    def __init__(self, env, lang, name, command, ldflags, ldlibs):
        CcLinker.__init__(self, env, lang, name + '_linklib', name, command,
                          ldflags, ldlibs)

    @property
    def num_outputs(self):
        return 2 if self.platform.has_import_library else 1

    def __call__(self, cmd, input, output, libs=None, args=None):
        result = CcLinker.__call__(self, cmd, input, first(output), libs, args)
        if self.platform.has_import_library:
            result.append('-Wl,--out-implib=' + output[1])
        return result

    def post_build(self, build, options, output):
        if isinstance(output, VersionedSharedLibrary):
            # Make symlinks for the various versions of the shared lib.
            Symlink(build, output.soname, output)
            Symlink(build, output.link, output.soname)
            return output.link

    def output_file(self, name, options):
        version = getattr(options, 'version', None)
        soversion = getattr(options, 'soversion', None)

        head, tail = os.path.split(name)
        fmt = self.platform.object_format

        def lib(head, tail, prefix='lib', suffix=''):
            return Path(os.path.join(
                head, prefix + tail + self.platform.shared_library_ext + suffix
            ))

        if self.platform.has_import_library:
            dllprefix = 'cyg' if self.platform.name == 'cygwin' else 'lib'
            dllname = lib(head, tail, dllprefix)
            impname = lib(head, tail, suffix='.a')
            dll = DllLibrary(dllname, fmt, impname)
            return [dll, dll.import_lib]
        elif version and self.platform.has_versioned_library:
            if self.platform.name == 'darwin':
                real = lib(head, '{}.{}'.format(tail, version))
                soname = lib(head, '{}.{}'.format(tail, soversion))
            else:
                real = lib(head, tail, suffix='.{}'.format(version))
                soname = lib(head, tail, suffix='.{}'.format(soversion))
            link = lib(head, tail)
            return VersionedSharedLibrary(real, fmt, soname, link)
        else:
            return SharedLibrary(lib(head, tail), fmt)

    @property
    def _always_args(self):
        shared = '-dynamiclib' if self.platform.name == 'darwin' else '-shared'
        return CcLinker._always_args.fget(self) + [shared, '-fPIC']

    def _soname(self, library):
        if isinstance(library, VersionedSharedLibrary):
            soname = library.soname
        else:
            soname = library

        if self.platform.name == 'darwin':
            return ['-install_name', darwin_install_name(soname)]
        else:
            return ['-Wl,-soname,' + soname.path.basename()]

    def args(self, options, output, pkg=False):
        args = CcLinker.args(self, options, output, pkg)
        if not pkg:
            args.extend(self._soname(first(output)))
        return args


class CcPackageResolver(object):
    def __init__(self, env, lang, command):
        value = env.getvar('CPATH')
        include_dirs = value.split(os.pathsep) if value else []

        self.include_dirs = [i for i in uniques(chain(
            include_dirs, env.platform.include_dirs
        )) if os.path.exists(i)]

        system_lib_dirs = []
        with open(os.devnull, 'wb') as devnull:
            try:
                # XXX: Will this work for cross-compilation?
                output = subprocess.check_output(
                    '{} -print-search-dirs'.format(command),
                    shell=True, universal_newlines=True, stderr=devnull
                )
                m = re.search(r'^libraries: (.*)', output, re.MULTILINE)
                system_lib_dirs = re.split(os.pathsep, m.group(1))
            except:
                pass

        value = env.getvar('LIBRARY_PATH')
        user_lib_dirs = value.split(os.pathsep) if value else []

        # XXX: Handle sysroot one day?
        all_lib_dirs = ( os.path.abspath(re.sub('^=', '', i))
                         for i in chain(user_lib_dirs, system_lib_dirs) )
        self.lib_dirs = [i for i in uniques(chain(
            all_lib_dirs, env.platform.lib_dirs
        )) if os.path.exists(i)]

        self.lang = lang
        self.platform = env.platform

    def header(self, name, search_dirs=None):
        if search_dirs is None:
            search_dirs = self.include_dirs

        for base in search_dirs:
            if os.path.exists(os.path.join(base, name)):
                return HeaderDirectory(Path(base, Root.absolute), None,
                                       system=True, external=True)

        raise IOError("unable to find header '{}'".format(name))

    def library(self, name, kind='any', search_dirs=None):
        if search_dirs is None:
            search_dirs = self.lib_dirs

        libnames = []
        if kind in ('any', 'shared'):
            libname = 'lib' + name + self.platform.shared_library_ext
            if self.platform.has_import_library:
                libnames.append((libname + '.a', ImportLibrary, {}))
            else:
                libnames.append((libname, SharedLibrary, {}))
        if kind in ('any', 'static'):
            libnames.append(('lib' + name + '.a', StaticLibrary,
                             {'lang': self.lang}))

        # XXX: Include Cygwin here too?
        if self.platform.name == 'windows':
            # We don't actually know what kind of library this is. It could be
            # a static library or an import library (which we classify as a
            # kind of shared lib).
            libnames.append((name + '.lib', Library))

        for base in search_dirs:
            for libname, libkind, extra_kwargs in libnames:
                fullpath = os.path.join(base, libname)
                if os.path.exists(fullpath):
                    return libkind(Path(fullpath, Root.absolute),
                                   format=self.platform.object_format,
                                   external=True, **extra_kwargs)

        raise IOError("unable to find library '{}'".format(name))
