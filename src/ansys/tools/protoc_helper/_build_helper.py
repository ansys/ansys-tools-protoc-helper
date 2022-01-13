import os
import glob
import shutil
import pathlib
import tempfile
import pkg_resources
import importlib.resources

__all__ = ["build_proto_py"]

def build_proto_py(dest_package):
    from grpc.tools import protoc
    command = [
        "grpc_tools.protoc",
        f"--python_out={dest_package}",
        f"--grpc_python_out={dest_package}",
        f"--mypy_out={dest_package}",
        f"--mypy_grpc_out={dest_package}",
        f"--proto_path={dest_package}"
    ]
    with tempfile.TemporaryDirectory() as tmp_dir:
        for entry_point in pkg_resources.iter_entry_points("pyansys_protoc_helper.proto_provider"):
            module = entry_point.load()
            relpath = pathlib.Path(tmp_dir, *(module.__name__.split('.')))
            relpath.mkdir(exist_ok=True, parents=True)
            # TODO: handle nested paths
            for filename in importlib.resources.contents(module):
                if filename.endswith(".proto"):
                    with importlib.resources.path(module, filename) as src_path:
                        shutil.copyfile(src_path, relpath / filename)

        command.append(f"--proto_path={tmp_dir}")

        target_protos = glob.glob(os.path.join(dest_package, "**/*.proto"), recursive=True)
        command += target_protos

        exit_code = protoc.main(
            command
        )
        if exit_code != 0:
            raise RuntimeError(f"Proto file compilation failed, command '{' '.join(command)}'.")
