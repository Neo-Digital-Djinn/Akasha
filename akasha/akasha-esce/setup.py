"""
setup.py for akasha-esce

Debian 13 installation:
    sudo apt install python3-dev build-essential
    pip install .          # production
    pip install -e .       # editable / dev

The C extension (esce._core) compiles from core/esce_core.c.
"""

from setuptools import setup, Extension, find_packages
import os

core_c = os.path.join(os.path.dirname(__file__), "core", "esce_core.c")

_core_ext = Extension(
    name="esce._core",
    sources=[core_c],
    # Debian 13 python3-dev puts headers in the standard location;
    # no extra include_dirs needed for vanilla CPython.
    extra_compile_args=["-O2", "-Wall"],
)

setup(
    name="akasha-esce",
    version="1.1.0",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    ext_modules=[_core_ext],
    entry_points={
        "console_scripts": [
            "esce = esce.cli:main",
        ]
    },
)
