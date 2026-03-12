"""ORMIR-XCT: tools for high-resolution CT image processing."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("ormir-xct")
except PackageNotFoundError:
    __version__ = "unknown"

from . import core

__all__ = ["core", "__version__"]
