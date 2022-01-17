import contextlib
import glob
import os
import pathlib
import shutil
import tempfile
import types
import typing

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
    with contextlib.ExitStack() as exit_stack:
        for module in _dependency_modules():
            module_proto_dir = exit_stack.enter_context(_proto_directory(module))
            command.append(f"--proto_path={module_proto_dir}")

        target_protos = glob.glob(os.path.join(target_package, "**/*.proto"), recursive=True)
        command += target_protos

        exit_code = protoc.main(command)
        if exit_code != 0:
            raise RuntimeError(f"Proto file compilation failed, command '{' '.join(command)}'.")


def _dependency_modules() -> typing.Iterator[types.ModuleType]:
    """Yield all modules that provide ``.proto`` files."""
    yield from (
        entry_point.load()
        for entry_point in pkg_resources.iter_entry_points(
            "ansys.tools.protoc_helper.proto_provider"
        )
    )


@contextlib.contextmanager
def _proto_directory(module: types.ModuleType) -> typing.Iterator[str]:
    """Copy the ``.proto`` files from a module into a temporary directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        relpath = pathlib.Path(tmp_dir, *(module.__name__.split(".")))
        _recursive_copy(importlib_resources.files(module), relpath.parent)
        yield tmp_dir


def _recursive_copy(src_traversable: Traversable, dest_path: pathlib.Path) -> None:
    """Copy ``.proto`` files contained in a ``Traversable`` to a given location."""
    if src_traversable.is_dir():
        sub_dest_path = dest_path / src_traversable.name
        for content in src_traversable.iterdir():  # type: ignore
            _recursive_copy(content, sub_dest_path)
    else:
        assert src_traversable.is_file()
        filename = src_traversable.name
        if filename.endswith(".proto"):
            os.makedirs(dest_path, exist_ok=True)
            with importlib_resources.as_file(src_traversable) as src_path:
                shutil.copyfile(src_path, dest_path / filename)
