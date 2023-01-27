import setuptools

from ansys.tools.protoc_helper import create_cmdclass_override


if __name__ == "__main__":
    setuptools.setup(
        name="testpkg-hello3-protos",
        author="ANSYS, Inc.",
        python_requires=">=3.7",
        install_requires=["grpcio~=1.0", "protobuf~=3.0"],
        package_dir={"": "src/py"},
        packages=setuptools.find_namespace_packages("src/py", include=("testpkg.*",)),
        package_data={
            "": ["*.proto", "*.pyi", "py.typed"],
        },
        entry_points={
            "ansys.tools.protoc_helper.proto_provider": {"testpkg.api.hello3=testpkg.api.hello3"},
        },
        cmdclass=create_cmdclass_override(protos_directory="src"),
    )
