import sys
import os
from distutils.version import LooseVersion

CYTHON_VERSION = '0.23.4'

# WindowsError is not defined on unix systems
try:
    WindowsError
except NameError:
    class WindowsError(Exception):
        pass


def cython(pyx_files, working_path=''):
    """Use Cython to convert the given files to C.

    Parameters
    ----------
    pyx_files : list of str
        The input .pyx files.

    """
    # Do not build cython files if target is clean
    if len(sys.argv) >= 2 and sys.argv[1] == 'clean':
        return

    try:
        from Cython import __version__
        if LooseVersion(__version__) < CYTHON_VERSION:
            raise RuntimeError('Cython >= %s needed to build scikit-image' % CYTHON_VERSION)

        from Cython.Build import cythonize
    except ImportError:
        # If cython is not found, the build will make use of
        # the distributed .c files if present
        c_files = [f.replace('.pyx.in', '.c').replace('.pyx', '.c') for f in pyx_files]
        for cfile in [os.path.join(working_path, f) for f in c_files]:
            if not os.path.isfile(cfile):
                raise RuntimeError('Cython >= %s is required to build scikit-image from git checkout' \
                                   % CYTHON_VERSION)

        print("Cython >= %s not found; falling back to pre-built %s" \
              % (CYTHON_VERSION, " ".join(c_files)))
    else:
        for pyxfile in [os.path.join(working_path, f) for f in pyx_files]:

            if pyxfile.endswith('.pyx.in'):
                process_tempita_pyx(pyxfile)
                pyxfile = pyxfile.replace('.pyx.in', '.pyx')

            cythonize(pyxfile)


def process_tempita_pyx(fromfile):
    try:
        try:
            from Cython import Tempita as tempita
        except ImportError:
            import tempita
    except ImportError:
        raise Exception('Building requires Tempita: '
                        'pip install --user Tempita')
    template = tempita.Template.from_filename(fromfile,
                                              encoding=sys.getdefaultencoding())
    pyxcontent = template.substitute()
    if not fromfile.endswith('.pyx.in'):
        raise ValueError("Unexpected extension of %s." % fromfile)

    pyxfile = os.path.splitext(fromfile)[0]    # split off the .in ending
    with open(pyxfile, "w") as f:
        f.write(pyxcontent)
