# type: ignore
# Type checking causes problems with the mixin approach used here. This
# could be overcome by subclassing '_CompileProtosMixin' from
# 'distutils.core.Command', but mypy *also* doesn't recognize that
# this class has a 'distribution' attribute. Overall, it's not worth
# the extra overhead.
"""Defines setuptools commands to execute the proto compilation

Define commands which can be used in the setuptools ``cmdclass``
directive to override the default behavior, and compile the .proto
files before the command is executed.
"""
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop

from ._compile_protos import compile_proto_files

__all__ = ["BuildPyCommand", "DevelopCommand", "CMDCLASS_OVERRIDE"]


class _CompileProtosMixin:
    def run(self):
        compile_proto_files(self.distribution.package_dir[""])
        super().run()


class BuildPyCommand(_CompileProtosMixin, build_py):
    pass


class DevelopCommand(_CompileProtosMixin, develop):
    pass


CMDCLASS_OVERRIDE = {"build_py": BuildPyCommand, "develop": DevelopCommand}
