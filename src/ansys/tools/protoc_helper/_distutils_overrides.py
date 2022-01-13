from setuptools.command.build_py import build_py
from setuptools.command.develop import develop

from ._build_helper import build_proto_py

__all__ = ["BuildPyCommand", "DevelopCommand", "CMDCLASS_OVERRIDE"]

class _CompileProtosMixin:
    def run(self):
        build_proto_py(self.distribution.package_dir[''])
        super().run()

class BuildPyCommand(_CompileProtosMixin, build_py):
    pass

class DevelopCommand(_CompileProtosMixin, develop):
    pass

CMDCLASS_OVERRIDE = {"build_py": BuildPyCommand, "develop": DevelopCommand}
