"""A utility for compiling '.proto' files to Python source."""
from ._compile_protos import *
from ._distutils_overrides import *

__version__ = "0.1.1"
__all__ = _compile_protos.__all__ + _distutils_overrides.__all__  # type: ignore
