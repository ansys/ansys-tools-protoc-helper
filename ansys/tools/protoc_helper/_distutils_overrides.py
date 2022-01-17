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

__all__ = ["BuildPyCommand", "DevelopCommand", "CMDCLASS_OVERRIDE"]


class _CompileProtosMixin:
    """Mixin class which adds .proto compilation to a command."""

    def run(self):
        try:
            target_dir = self.distribution.package_dir[""]
        except (KeyError, TypeError):
            target_dir = "."
        compile_proto_files(target_dir)
        super().run()


class BuildPyCommand(_CompileProtosMixin, build_py):
    """Command to compile .proto files while building the package wheel.

    Override for the ``build_py`` command which adds compilation of
    .proto files to Python source.
    """


class DevelopCommand(_CompileProtosMixin, develop):
    """Command to compile .proto files during editable installs.

    Override for the ``develop`` command which adds compilation of
    .proto files to Python source.
    """


CMDCLASS_OVERRIDE = {"build_py": BuildPyCommand, "develop": DevelopCommand}
