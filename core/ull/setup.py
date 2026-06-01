"""
setup.py - Cython Compilation Setup

Compiles the ultra-low latency Cython modules for maximum performance.
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

# Compiler flags for maximum optimization
compiler_directives = {
    'language_level': 3,
    'boundscheck': False,
    'wraparound': False,
    'cdivision': True,
    'nonecheck': False,
    'initializedcheck': False,
    'overflowcheck': False,
    'overflowcheck.fold': False,
    'emit_code_comments': False,
    'annotate': False,
}

# C compiler flags
c_flags = [
    '-O3',                    # Maximum optimization
    '-march=native',          # Use native CPU instructions
    '-mtune=native',          # Tune for current CPU
    '-ffast-math',            # Fast math operations
    '-funroll-loops',         # Unroll loops
    '-fvectorize',            # Auto-vectorize
    '-ffp-contract=fast',     # Fast floating point
    '-DNDEBUG',               # Disable assertions
]

# Define extensions
extensions = [
    Extension(
        "core.ull.kernel_bypass",
        ["core/ull/kernel_bypass.pyx"],
        include_dirs=[np.get_include(), "core/ull"],
        extra_compile_args=c_flags + ['-fPIC'],
        extra_link_args=['-shared'],
        language="c",
    ),
    Extension(
        "core.ull.pico_math_simd",
        ["core/ull/pico_math_simd.pyx"],
        include_dirs=[np.get_include(), "core/ull"],
        extra_compile_args=c_flags + ['-fPIC', '-mavx2', '-mfma'],
        extra_link_args=['-shared'],
        language="c",
    ),
]

setup(
    name="ull_trading",
    version="1.0.0",
    description="Ultra-Low Latency Trading Engine with SIMD acceleration",
    author="Quantum Systems Architect",
    packages=["core.ull"],
    ext_modules=cythonize(
        extensions,
        compiler_directives=compiler_directives,
        nthreads=4,
    ),
    include_dirs=[np.get_include()],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "cython>=0.29.0",
    ],
)
