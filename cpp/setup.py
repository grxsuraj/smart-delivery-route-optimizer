from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "route_engine",
        ["dijkstra.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=["-std=c++17"],
    ),
]

setup(
    name="route_engine",
    version="1.0",
    ext_modules=ext_modules,
)

# Build with:
#   pip install pybind11 --break-system-packages
#   cd cpp
#   python setup.py build_ext --inplace
#
# This produces route_engine*.so which app.py imports directly.
