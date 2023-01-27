import filecmp
import glob
import logging
import os
import pathlib
import shutil
import tempfile
import warnings
from typing import Optional
from typing import Union

import importlib_resources  # Replace with importlib.resources once only Py3.9+ is supported
import pkg_resources
from grpc.tools import protoc
from importlib_resources.abc import Traversable


__all__ = ["compile_proto_files"]


def compile_proto_files(target_package: str, protos_directory: Optional[str] = None) -> None:
    """Compile .proto files in a package to Python source.

    Creates Python files and ``.pyi`` type stubs from the ``.proto`` files
    in the ``target_package``. Proto files from all installed packages
    defining the ``ansys.tools.protoc_helper.proto_provider`` entry point
    are included as possible dependencies.

    Parameters
    ----------
    target_package :
        Path of the target package in which the generated Python files should
        be placed. If the ``target_package`` contains ``.proto`` files, they will
        be compiled. Otherwise, ``protos_directory`` needs to be specified.
    protos_directory :
        If specified, ``.proto`` files from this directory will be compiled,
        in addition to any ``.proto`` files that may already be in the
        ``target_package``.
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
            try:
                module = entry_point.load()
            except ImportError:
                logging.warning(f"Cannot load proto files from entry point {entry_point.name}")
            if ":" in entry_point.name:
                module_dest_name = entry_point.name.split(":", 1)[1]
            else:
                module_dest_name = module.__name__
            relpath = pathlib.Path(proto_include_dir, *(module_dest_name.split(".")))
            _recursive_copy(importlib_resources.files(module), relpath, relpath)

        command.append(f"--proto_path={proto_include_dir}")

        if protos_directory is not None:
            _recursive_copy(
                pathlib.Path(protos_directory),
                pathlib.Path(target_package),
                pathlib.Path(target_package),
            )

        target_protos = glob.glob(os.path.join(target_package, "**/*.proto"), recursive=True)
        if not target_protos:
            raise FileNotFoundError(
                "No '.proto' files found in the target package directory "
                f"'{os.path.abspath(target_package)}'."
            )
        command += target_protos

        exit_code = protoc.main(command)
        if exit_code != 0:
            raise RuntimeError(f"Proto file compilation failed, command '{' '.join(command)}'.")


def _recursive_copy(
    src_traversable: Union[Traversable, pathlib.Path],
    dest_path: pathlib.Path,
    root_dest_path: pathlib.Path,
) -> None:
    """Copy ``.proto`` files contained in a ``Traversable`` to a given location."""
    if isinstance(src_traversable, pathlib.Path):
        if root_dest_path in src_traversable.parents:
            logging.info(
                f"Skipping {src_traversable}, which is a subdirectory of "
                f"the target {root_dest_path}."
            )
            return

    if src_traversable.is_dir():
        for content in src_traversable.iterdir():
            _recursive_copy(content, dest_path / content.name, root_dest_path)
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
