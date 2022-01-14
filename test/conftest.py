import os
import pathlib
import subprocess
import tempfile
import types
import venv

import pytest

TEST_ROOT_DIR = pathlib.Path(__file__).parent
PKG_ROOT_DIR = TEST_ROOT_DIR.parent
TEST_DATA_DIR = TEST_ROOT_DIR / "test_data"


@pytest.fixture
def test_venv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        print(tmp_dir)

        venv_dir = pathlib.Path(tmp_dir) / "venv"
        venv.main([str(venv_dir)])
        if os.name == "nt":  # Windows
            script_dir = venv_dir / "Scripts"
            python_bin = script_dir / "python.exe"
            pip_bin = script_dir / "pip.exe"
        else:  # Linux
            script_dir = venv_dir / "bin"
            python_bin = script_dir / "python"
            pip_bin = script_dir / "pip"
        yield types.SimpleNamespace(python=python_bin, pip=pip_bin)


@pytest.fixture
def local_pkg_index(test_venv):
    with tempfile.TemporaryDirectory() as tmp_dir:
        extra_deps = ["wheel"]
        subprocess.check_call(
            [
                test_venv.pip,
                "download",
                "-d",
                tmp_dir,
            ]
            + extra_deps
        )
        subprocess.check_call(
            [
                f"{test_venv.pip}",
                "wheel",
                "-w",
                f"{tmp_dir}",
                f"{PKG_ROOT_DIR}",
            ]
        )
        yield tmp_dir


@pytest.fixture
def create_test_pkg_wheel(local_pkg_index, test_venv):
    def inner(pkgname):
        subprocess.check_call(
            [
                f"{test_venv.pip}",
                "wheel",
                "--no-index",
                f"--find-links={local_pkg_index}",
                "-w",
                f"{local_pkg_index}",
                f"{TEST_DATA_DIR / pkgname}",
            ]
        )

    return inner


@pytest.fixture
def install_test_pkg(local_pkg_index, test_venv):
    def inner(pkgname):
        subprocess.check_call(
            [
                f"{test_venv.pip}",
                "install",
                "--no-index",
                f"--find-links={local_pkg_index}",
                f"{TEST_DATA_DIR / pkgname}",
            ]
        )

    return inner
