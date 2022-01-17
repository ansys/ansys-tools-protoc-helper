"""Pytest configuration file."""
import pathlib

TEST_ROOT_DIR = pathlib.Path(__file__).parent
PKG_ROOT_DIR = TEST_ROOT_DIR.parent
TEST_DATA_DIR = TEST_ROOT_DIR / "test_data"
