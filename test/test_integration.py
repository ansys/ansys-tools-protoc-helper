"""Integration tests for end-to-end tests of the protoc-helper."""
import subprocess


def test_dependency_compile(create_test_pkg_wheel, install_test_pkg, test_venv):
    create_test_pkg_wheel("testpkg-hello-protos")
    install_test_pkg("testpkg-greeter-protos")
    subprocess.check_call([f"{test_venv.python}", "-c", "import testpkg.api.greeter.v0"])
