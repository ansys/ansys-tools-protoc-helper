"""Integration tests for end-to-end tests of the protoc-helper."""
import contextlib
import os
import pathlib
import shutil
import subprocess
import tempfile
import types
import venv

import pytest

from conftest import PKG_ROOT_DIR, TEST_DATA_DIR


@pytest.fixture
def test_venv(tmpdir):
    """Create a temporary virtual environment for the test."""
    venv_dir = tmpdir / "venv"
    venv.main([str(venv_dir)])
    if os.name == "nt":  # Windows
        script_dir = venv_dir / "Scripts"
        python_bin = script_dir / "python.exe"
        pip_bin = script_dir / "pip.exe"
    else:  # Linux
        script_dir = venv_dir / "bin"
        python_bin = script_dir / "python"
        pip_bin = script_dir / "pip"
    test_venv = types.SimpleNamespace(python=python_bin, pip=pip_bin)
    subprocess.check_call([str(test_venv.python), "--version"])  # for info only
    subprocess.check_call([str(test_venv.pip), "install", "wheel"])
    yield test_venv


@pytest.fixture
def local_pkg_index(test_venv, tmpdir):
    """Create a temporary local directory to use as a package index."""
    pkg_idx_dir = tmpdir / "pkg_idx"
    extra_deps = ["wheel"]
    subprocess.check_call(
        [
            str(test_venv.pip),
            "download",
            "-d",
            str(pkg_idx_dir),
        ]
        + extra_deps
    )
    subprocess.check_call(
        [
            str(test_venv.pip),
            "wheel",
            "-w",
            str(pkg_idx_dir),
            f"{PKG_ROOT_DIR}",
        ]
    )
    yield pkg_idx_dir


@contextlib.contextmanager
def copy_test_package(pkgname):
    """Copy the test package to a temporary location.

    This is done to avoid changes in the test package (such as the
    creation of Python files) caused by building their wheels to
    propagate to subsequent test runs.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        dest_dir = pathlib.Path(tmp_dir) / pkgname
        shutil.copytree(TEST_DATA_DIR / pkgname, dest_dir)
        yield dest_dir


@pytest.fixture
def create_test_pkg_wheel(local_pkg_index, test_venv):
    """Create the wheel for a test package, and store it at the local package index."""

    def inner(pkgname):
        with copy_test_package(pkgname) as pkg_dir:
            subprocess.check_call(
                [
                    str(test_venv.pip),
                    "wheel",
                    "--no-index",
                    f"--find-links={local_pkg_index}",
                    "-w",
                    str(local_pkg_index),
                    str(pkg_dir),
                ]
            )

    return inner


@pytest.fixture
def install_test_pkg(local_pkg_index, test_venv):
    """Install a test package into the temporary test venv."""

    def inner(pkgname):
        subprocess.check_call(
            [
                str(test_venv.pip),
                "install",
                "--no-index",
                f"--find-links={local_pkg_index}",
                str(TEST_DATA_DIR / pkgname),
            ]
        )

    return inner


def test_dependency_compile(create_test_pkg_wheel, install_test_pkg, test_venv):
    """Test installation of the ``testpkg-greeter-protos`` package."""
    create_test_pkg_wheel("testpkg-hello-protos")
    install_test_pkg("testpkg-greeter-protos")
    subprocess.check_call(
        [
            str(test_venv.python),
            "-c",
            (
                "from testpkg.api.greeter.v0 import greeter_pb2, greeter_pb2_grpc, "
                + "greeter2_pb2, greeter2_pb2_grpc, greeter3_pb2, greeter3_pb2_grpc"
            ),
        ]
    )
