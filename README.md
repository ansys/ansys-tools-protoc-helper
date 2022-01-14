# protobuf compilation helper

A utility to compile ``.proto`` files to Python source when building the package wheel. It supports dependencies to ``.proto`` files of different packages.

## Quickstart

The simplest way to get started is using the template [TODO: link to template]().

## Manual use

To manually enable the use of `ansys-tools-protoc-helper` in your project, the following things need to be defined:

- A ``pyproject.toml`` file with the following contents:

    ```
    [build-system]
    requires = ["setuptools>=42.0", "wheel", "ansys-tools-protoc-helper", <additional_dependencies>]
    build-backend = "setuptools.build_meta:__legacy__"
    ```

  where ``<additional_dependencies>`` are the packages that you depend on for ``.proto`` files.

- In the ``setuptools`` configuration (either `setup.cfg` or `setup.py`). We only show the ``setuptools.setup()`` keywords (``setup.py`` variant) here:

    - Run-time dependencies on the same ``<additional_dependencies>`` used above:
        ```python
        install_requires=[grpcio, protobuf, <additional_dependencies>],
        ```
      Refer to [the gRPC versioning strategy](#grpc-versioning-strategy) section for details on which ``grpc`` and ``protobuf`` versions can be used.

    - The ``package_data`` declares additional file names which are included in the package:
        ```python
        package_data={
            "": ["*.proto", "*.pyi", "py.typed"],
        }
        ```
      Note that ``*.proto`` is only needed if other packages should be able to depend on the ``*.proto`` files defined in your package.

      The `py.typed` file is used to communicate that the package contains type information, see [PEP 561](https://www.python.org/dev/peps/pep-0561/). This file needs to be manually added.

    - If other projects should be able to depend on the ``.proto`` files contained in your project, an [entry point](https://packaging.python.org/en/latest/specifications/entry-points/) needs to be defined declaring the presence of the ``*.proto`` files:
        ```python
        entry_points={
            "ansys.tools.protoc_helper.proto_provider": {
                "<your.package.name>=<your.package.name>"
            },
        },
        ```
      where ``<your.package.name>`` is the _importable_ name of your package. In other words, ``import <your.package.name>`` should work after installing the package.

For a complete example, see the ``test/test_data/testpkg-greeter-protos`` package.

## gRPC version strategy

The `ansys-tools-protoc-helper` pins the versions of `gRPC` and `protobuf` that it depends on, in the `dependencies = ...` section of the [`pyproject.toml`](pyproject.toml) file.

For your own project, you can use any version of ``grpcio`` and ``protobuf`` that's newer (or equal) to the version pinned here, as long as it is the same major version.

For example, if `ansys-tools-protoc-helper` pins
```toml
dependencies = [
    "grpcio-tools==1.17.0",
    "protobuf==3.19.3",
]
```
your own dependencies could be `grpcio-tools~=1.17`, `protobuf~=3.19` (using the `~=` [compatible version operator](https://www.python.org/dev/peps/pep-0440/#compatible-release)).

The versions pinned by `ansys-tools-protoc-helper` are chosen as follows:
- The first version of `grpcio-tools` for which binary wheels are available on PyPI, for at least one of the Python versions we support.
- The first version of `protobuf` which is compatible with `mypy-protobuf`, for generating type stubs.
