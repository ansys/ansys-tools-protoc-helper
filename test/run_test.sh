#!/bin/bash

set -e

TEST_WORKDIR=$(realpath $(dirname "$0"))
PROTOC_HELPER_DIR=$(realpath $TEST_WORKDIR"/../pyansys_protoc_helper")

# check that we are in a virtualenv..
python -c 'import sys; assert hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.prefix != sys.base_prefix)'

pushd $TEST_WORKDIR
# ---- INSTALL PREREQUISITES ----
# We need versions of pip and setuptools that understand the 'pyproject.toml' - based build, at least
pip install -U pip setuptools==42
# It seems cython is needed because we pin an older version of grpcio-tools that doesn't have a wheel for newer Python versions.
# TODO: Check if we can get around having it as a prerequisite by requiring it somewhere in the package itself.
pip install cython
pip install git+https://github.com/cookiecutter/cookiecutter.git@2.0.2#egg=cookiecutter # NOTE: using v2 for the '--replay-file' option

# ---- CREATE TEST PACKAGES ----
rm -rf ./ansys-*-protos
cookiecutter -f --no-input ../template_project  product_name=hello protos_dir=../hello
cookiecutter -f ../template_project --replay-file=greeter.json

# ---- BUILD 'pyansys_protoc_helper' WHEEL ----
# Note that we use a local directory as a 'PyPI replacement', since we don't
# yet want to publish the package, but the subsequent builds need to find
# it for the build-time dependencies.
rm -rf local_dist
mkdir local_dist
pushd $PROTOC_HELPER_DIR
pip wheel -w $TEST_WORKDIR/local_dist/ .
popd

# ---- DOWNLOAD ADDITIONAL DEPENDENCIES TO 'local_dist' ----
# We could instead use PyPI _and_ the local directory, but this is unsafe because
# a package on PyPI could shadow 'pyansys_protoc_helper' (see example 10 on
# https://pip.pypa.io/en/stable/cli/pip_install/#examples).
pushd ./local_dist
pip download setuptools wheel grpcio-tools==1.0.0 protobuf==3.19.1 mypy-protobuf # cython?
popd

# ---- BUILD 'ansys-hello-protos' WHEEL, INSTALL 'ansys-greeter-protos' ----
pip wheel --no-index --find-links=./local_dist -w ./local_dist ./ansys-hello-protos/
pip install --no-index --find-links=./local_dist ./ansys-greeter-protos/
