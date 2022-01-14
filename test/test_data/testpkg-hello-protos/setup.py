import setuptools

from ansys.tools.protoc_helper import CMDCLASS_OVERRIDE


if __name__ == "__main__":
    setuptools.setup(
        name="testpkg-hello-protos",
        author="ANSYS, Inc.",
        python_requires=">=3.7",
        install_requires=["grpcio~=1.0", "protobuf~=3.0"],
        packages=setuptools.find_namespace_packages(".", include=("testpkg.*",)),
        package_data={
            "": ["*.proto", "*.pyi", "py.typed"],
        },
        entry_points={
            "ansys.tools.protoc_helper.proto_provider": {"testpkg.api.hello=testpkg.api.hello"},
        },
        cmdclass=CMDCLASS_OVERRIDE,
    )
