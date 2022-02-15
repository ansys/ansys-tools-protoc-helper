import filecmp
import glob
import os
import pathlib
import shutil
import tempfile
import warnings

import importlib_resources  # Replace with importlib.resources once only Py3.9+ is supported
import pkg_resources
from grpc.tools import protoc
from importlib_resources.abc import Traversable


__all__ = ["compile_proto_files"]


def compile_proto_files(target_package: str) -> None:
    """Compile .proto files in a package to Python source.

    Creates Python files and ``.pyi`` type stubs from the ``.proto`` files
    in the ``target_package``. Proto files from all installed packages
    defining the ``ansys.tools.protoc_helper.proto_provider`` entry point
    are included as possible dependencies.

    Parameters
    ----------
    target_package :
        Path of the package whose ``.proto`` files should be compiled.
    """
    command = [
        "grpc_tools.protoc",
        f"--python_out={target_package}",
        f"--grpc_python_out={target_package}",
        f"--mypy_out={target_package}",
        f"--mypy_grpc_out={target_package}",
        f"--proto_path={target_package}",
    ]
    with tempfile.TemporaryDirectory() as proto_include_dir:
        for entry_point in pkg_resources.iter_entry_points(
            "ansys.tools.protoc_helper.proto_provider"
        ):
            module = entry_point.load()
            if ":" in entry_point.name:
                module_dest_name = entry_point.name.split(":", 1)[1]
            else:
                module_dest_name = module.__name__
            relpath = pathlib.Path(proto_include_dir, *(module_dest_name.split(".")))
            _recursive_copy(importlib_resources.files(module), relpath)

        command.append(f"--proto_path={proto_include_dir}")

        target_protos = glob.glob(os.path.join(target_package, "**/*.proto"), recursive=True)
        command += target_protos

        exit_code = protoc.main(command)
        if exit_code != 0:
            raise RuntimeError(f"Proto file compilation failed, command '{' '.join(command)}'.")


def _recursive_copy(src_traversable: Traversable, dest_path: pathlib.Path) -> None:
    """Copy ``.proto`` files contained in a ``Traversable`` to a given location."""
    if src_traversable.is_dir():
        for content in src_traversable.iterdir():  # type: ignore
            _recursive_copy(content, dest_path / content.name)
    else:
        assert src_traversable.is_file()
        filename = src_traversable.name
        if filename.endswith(".proto"):
            os.makedirs(dest_path.parent, exist_ok=True)
            with importlib_resources.as_file(src_traversable) as src_path:
                if dest_path.exists():
                    if not filecmp.cmp(src_path, dest_path):
                        warnings.warn(
                            f"Duplicate, non-identical files '{dest_path}' found "
                            "when collectiong .proto dependencies."
                        )
                else:
                    shutil.copyfile(src_path, dest_path)
