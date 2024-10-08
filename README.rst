***************************
protobuf compilation helper
***************************

A utility to compile ``.proto`` files to Python source when building the package wheel. It supports dependencies to ``.proto`` files of different packages.

Quickstart
~~~~~~~~~~

The simplest way to get started is using the `template repository <https://github.com/ansys/ansys-api-template>`_.

Manual use
~~~~~~~~~~

To manually enable the use of ``ansys-tools-protoc-helper`` in your project, the following things need to be defined:

-   A ``pyproject.toml`` file with the following contents:

    .. code::

        [build-system]
        requires = ["setuptools>=42.0", "wheel", "ansys-tools-protoc-helper", <additional_dependencies>]
        build-backend = "setuptools.build_meta:__legacy__"

    where ``<additional_dependencies>`` are the packages that you depend on for ``.proto`` files.

-   In the ``setuptools`` configuration (either ``setup.cfg`` or ``setup.py``). We only show the ``setuptools.setup()`` keywords (``setup.py`` variant) here:

    -   Run-time dependencies on the same ``<additional_dependencies>`` used above:

        .. code:: python

            install_requires=[grpcio, protobuf, <additional_dependencies>],

        Refer to the `gRPC version strategy`_ section for details on which ``grpc`` and ``protobuf`` versions can be used.

    -   The ``package_data`` declares additional file names which are included in the package:

        .. code:: python

            package_data={
                "": ["*.proto", "*.pyi", "py.typed"],
            }

        Note that ``*.proto`` is only needed if other packages should be able to depend on the ``*.proto`` files defined in your package.

        The ``py.typed`` file is used to communicate that the package contains type information, see `PEP 561 <https://www.python.org/dev/peps/pep-0561/>`_. This file needs to be manually added.

    -   The ``cmdclass`` is used to specify that some ``setuptools`` commands should be executed by ``ansys-tools-protoc-helper``:

        .. code:: python

            from ansys.tools.protoc_helper import CMDCLASS_OVERRIDE

            setup(
                <...>,
                cmdclass=CMDCLASS_OVERRIDE
            )

        The two commands which are overridden can also be specified individually. This may be useful in particular if you want to use the ``setup.cfg`` format:

        .. code:: python

            from ansys.tools.protoc_helper import BuildPyCommand, DevelopCommand

            setup(
                <...>,
                cmdclass={"build_py": BuildPyCommand, "develop": DevelopCommand}
            )

    -   If other projects should be able to depend on the ``.proto`` files contained in your project, an `entry point <https://packaging.python.org/en/latest/specifications/entry-points/>`_ needs to be defined declaring the presence of the ``*.proto`` files:

        .. code:: python

            entry_points={
                "ansys.tools.protoc_helper.proto_provider": {
                    "<your.package.name>=<your.package.name>"
                },
            },

        where ``<your.package.name>`` is the _importable_ name of your package. In other words, ``import <your.package.name>`` should work after installing the package.

        By default, the ``.proto`` files will be copied to ``your/package/name``. If a different location should be used, append a semicolon to the entry point name, followed by the dot-separated target location:

        .. code:: python

            entry_points={
                "ansys.tools.protoc_helper.proto_provider": {
                    "<your.package.name>:<target.location>=<your.package.name>"
                },
            },

For a complete example, see the ``test/test_data/testpkg-greeter-protos`` package.

gRPC version strategy
~~~~~~~~~~~~~~~~~~~~~

The ``ansys-tools-protoc-helper`` pins the versions of ``gRPC`` and ``protobuf`` that it depends on, in the ``dependencies = ...`` section of the `pyproject.toml <https://github.com/ansys/ansys-tools-protoc-helper/blob/main/pyproject.toml>`_ file.

For your own project, you can use any version of ``grpcio`` and ``protobuf`` that's newer (or equal) to the version pinned here, as long as it is the same major version.

For example, if ``ansys-tools-protoc-helper`` pins

.. code::

    dependencies = [
        "grpcio-tools==1.20.0",
        "protobuf==3.19.3",
    ]

your own dependencies could be ``grpcio-tools~=1.20``, ``protobuf~=3.19`` (using the ``~=`` `compatible version operator <https://www.python.org/dev/peps/pep-0440/#compatible-release>`_).

.. note::

    The ``protoc`` compiler version used is determined by the ``grpcio-tools`` package, *not* the ``protobuf`` dependency. The ``grpcio-tools==1.20.0`` uses ``protoc==3.7.0``.


The versions pinned by ``ansys-tools-protoc-helper`` were originally chosen as follows:

- The first version of ``grpcio-tools`` for which binary wheels are available on PyPI, for at least one of the Python versions we support.
- The first version of ``protobuf`` which is compatible with ``mypy-protobuf``, for generating type stubs.

Upgrade plans
^^^^^^^^^^^^^

The current plan for upgrading ``grpcio-tools`` and ``protobuf`` is as follows:

+----------------------------------------+----------------+--------------------------+----------------------+--------------------+-----------------------+
| ``ansys-tools-protoc-helper`` version  | release date   | ``grpcio-tools`` version | ``protobuf`` version | ``protoc`` version | Python version support|
+========================================+================+==========================+======================+====================+=======================+
| ``0.2.x``                              | 2022-12-09     | ``1.20.x``               | ``3.19.3``           | ``3.7.x``          | 3.7 - 3.10            |
+----------------------------------------+----------------+--------------------------+----------------------+--------------------+-----------------------+
| ``0.3.x``                              | 2023-02-20     | ``1.25.x``               | ``3.19.3``           | ``3.8.x``          | 3.7 - 3.10            |
+----------------------------------------+----------------+--------------------------+----------------------+--------------------+-----------------------+
| ``0.4.x``                              | 2023-02-20     | ``1.44.x``               | ``3.19.3``           | ``3.19.2``         | 3.7 - 3.10            |
+----------------------------------------+----------------+--------------------------+----------------------+--------------------+-----------------------+
| ``0.5.x``                              | 2024-09-02     | ``1.49.x``               | ``4.21.x``           | ``3.21.5``         | 3.9 - 3.11            |
+----------------------------------------+----------------+--------------------------+----------------------+--------------------+-----------------------+
| ``0.6.x``                              | TBD            | ``1.59.x``               | ``4.24.x``           | ``3.24.3``         | 3.10 - 3.12           |
+----------------------------------------+----------------+--------------------------+----------------------+--------------------+-----------------------+

The strategy for these upgrades is as follows:

- Upgrade ``grpcio-tools`` as necessary. For example, ``0.5.x`` enables building with Python ``3.11``.
- Match the version of ``protobuf`` to the version of ``protoc`` bundled into ``grpcio-tools``, or at least ``3.19.3``.
- Each upgrade is a breaking upgrade for the semantic version. Since we are currently using ``0.x`` versions, the minor version is bumped.

The ``protobuf`` Python runtime introduced a backwards-incompatible change with version ``4.21`` (matching protoc release ``3.21``). Code generated with ``protoc==3.19`` or newer should be compatible with the ``4.x`` runtime, which corresponds to the ``0.4`` release of ``ansys-tools-protoc-helper``.

If you need to support a specific *older* version of protobuf and / or gRPC, we encourage pinning ``ansys-tools-protoc-helper`` to its minor version.
