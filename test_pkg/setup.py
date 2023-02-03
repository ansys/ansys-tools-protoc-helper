import pathlib
import shutil

import setuptools
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop

# NOTE: since the commands are implemented directly here, testing needs
# to be done without build isolation, i.e. using 'python -m build --no-isolation'


class CmdMixin:
    def _get_src(self):
        src_dir = "src/dir_b"
        try:
            src_dir = self.distribution.package_dir[src_dir]
        except (KeyError, TypeError):
            pass
        src_dir = pathlib.Path(src_dir)
        return src_dir / "pkg_name" / "sub" / "b" / "b.py"

    def _get_dest(self):
        try:
            target_dir = self.distribution.package_dir[""]
        except (KeyError, TypeError):
            target_dir = "."
        target_dir = pathlib.Path(target_dir)
        return target_dir / "pkg_name" / "sub" / "b" / "b.py"

    def run(self):
        src = self._get_src()
        dest = self._get_dest()
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)

    def get_source_files(self):
        return super().get_source_files() + [str(self._get_src())]

    def get_outputs(self):
        return super().get_outputs() + ["{build_lib}/pkg_name/sub/b/b.py"]

    def get_output_mapping(self):
        res = super().get_output_mapping()
        res["{build_lib}/pkg_name/sub/b/b.py"] = str(self._get_src())
        return res


class BuildPyCommand(CmdMixin, build_py):
    pass


class DevelopCommand(CmdMixin, develop):
    pass


if __name__ == "__main__":
    setuptools.setup(
        name="test-pkg",
        author="ANSYS, Inc.",
        python_requires=">=3.7",
        package_dir={"": "src/dir_a"},
        packages=setuptools.find_namespace_packages(
            "src/dir_a", include=("pkg_name.*",)
        )
        + setuptools.find_namespace_packages("src/dir_b", include=("pkg_name.*",)),
        package_data={
            "": ["*.py"],
        },
        cmdclass={"build_py": BuildPyCommand, "develop": DevelopCommand},
    )
