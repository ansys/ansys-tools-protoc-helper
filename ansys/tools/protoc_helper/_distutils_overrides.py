# type: ignore
# Type checking causes problems with the mixin approach used here. This
# could be overcome by subclassing '_CompileProtosMixin' from
# 'distutils.core.Command', but mypy *also* doesn't recognize that
# this class has a 'distribution' attribute. Overall, it's not worth
# the extra overhead.
"""Defines setuptools commands to execute the proto compilation.

Define commands which can be used in the setuptools ``cmdclass``
directive to override the default behavior, and compile the .proto
files before the command is executed.
"""
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop

from ._compile_protos import compile_proto_files

__all__ = ["CMDCLASS_OVERRIDE", "create_cmdclass_override"]


class _CompileProtosMixin:
    """Mixin class which adds .proto compilation to a command."""

    CUSTOM_PROTOS_DIR = None

    def run(self):
        try:
            target_dir = self.distribution.package_dir[""]
        except (KeyError, TypeError):
            target_dir = "."
        try:
            protos_directory = self.distribution.package_dir[self.CUSTOM_PROTOS_DIR]
        except (KeyError, TypeError):
            protos_directory = self.CUSTOM_PROTOS_DIR
        compile_proto_files(target_dir, protos_directory=protos_directory)
        super().run()


def create_cmdclass_override(protos_directory=None):
    """Create the ``cmdclass`` options for compiling protobuf files.

    Creates the override classes, to be passed as the ``cmdclass`` argument
    to ``setuptools.setup``, for compiling ``.proto`` files during the
    package build process.

    Parameters
    ----------
    protos_directory :
        Directory path containing the protobuf files, relative to the
        package root. If unspecified, only protobuf files inside the
        package source will be considered.
    """

    class BuildPyCommand(_CompileProtosMixin, build_py):
        """Command to compile .proto files while building the package wheel.

        Override for the ``build_py`` command which adds compilation of
        .proto files to Python source.
        """

        CUSTOM_PROTOS_DIR = protos_directory

    class DevelopCommand(_CompileProtosMixin, develop):
        """Command to compile .proto files during editable installs.

        Override for the ``develop`` command which adds compilation of
        .proto files to Python source.
        """

        CUSTOM_PROTOS_DIR = protos_directory

    return {"build_py": BuildPyCommand, "develop": DevelopCommand}


CMDCLASS_OVERRIDE = create_cmdclass_override()
