import setuptools

from ansys.tools.protoc_helper import CMDCLASS_OVERRIDE


if __name__ == "__main__":
    setuptools.setup(
        name="testpkg-greeter-protos",
        author="ANSYS, Inc.",
        python_requires=">=3.7",
        install_requires=["grpcio~=1.0", "protobuf~=3.0", "testpkg-hello-protos"],
        packages=setuptools.find_namespace_packages(".", include=("testpkg.*",)),
        package_data={
            "": ["*.proto", "*.pyi", "py.typed"],
        },
        entry_points={
            "ansys.tools.protoc_helper.proto_provider": {
                "testpkg.api.greeter.v0=testpkg.api.greeter.v0"
            },
        },
        cmdclass=CMDCLASS_OVERRIDE,
    )
