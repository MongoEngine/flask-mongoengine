import sys

VERSION = (0, 7, 5)
if sys.version_info >= (3, 0):
    unicode = str
    basestring = (str, bytes)
else:
    unicode = unicode
    basestring = basestring

def get_version():
    if isinstance(VERSION[-1], basestring):
        return '.'.join(map(str, VERSION[:-1])) + VERSION[-1]
    return '.'.join(map(str, VERSION))

__version__ = get_version()
