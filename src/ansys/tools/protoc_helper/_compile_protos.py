import contextlib
import glob
import importlib.resources
import os
import pathlib
import shutil
import tempfile
import types
import typing

import pkg_resources

__all__ = ["compile_proto_files"]


def compile_proto_files(target_package: str) -> None:
    from grpc.tools import protoc

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
    yield from (
        entry_point.load()
        for entry_point in pkg_resources.iter_entry_points(
            "ansys.tools.protoc_helper.proto_provider"
        )
    )


@contextlib.contextmanager
def _proto_directory(module: types.ModuleType) -> typing.Iterator[str]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        relpath = pathlib.Path(tmp_dir, *(module.__name__.split(".")))
        for filename in importlib.resources.contents(module):
            if filename.endswith(".proto"):
                with importlib.resources.path(module, filename) as src_path:
                    dest_path = relpath / filename
                    os.makedirs(dest_path.parent, exist_ok=True)
                    shutil.copyfile(src_path, relpath / filename)
        yield tmp_dir
