"""
CYTHON COMPILATION SETUP - Ultra-Low Latency Build System
=========================================================
Setup.py for compiling all Cython extensions with maximum optimization.

Compiler Flags:
- AVX-512 SIMD vectorization
- Fast math operations
- No bounds checking
- No Python GIL release for critical sections
- Link-time optimization (LTO)
"""

import os
import sys
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

# Optimization flags for maximum performance
EXTRA_COMPILE_ARGS = [
    '-O3',                      # Maximum optimization
    '-march=native',            # Optimize for local CPU
    '-mavx512f',                # Enable AVX-512 floating point
    '-mavx512dq',               # Enable AVX-512 doubleword
    '-mavx512vl',               # Enable AVX-512 vector length
    '-ffast-math',              # Fast floating point operations
    '-funroll-loops',           # Unroll loops for speed
    '-finline-functions',       # Inline small functions
    '-fomit-frame-pointer',     # Omit frame pointer for speed
    '-DNDEBUG',                 # Disable assertions
    '-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION',
]

# For Linux with GCC
if sys.platform == 'linux':
    EXTRA_COMPILE_ARGS.extend([
        '-flto',                # Link-time optimization
        '-fuse-ld=gold',        # Use gold linker for speed
        '-fno-plt',             # Avoid PLT overhead
        '-fstack-protector-strong',  # Stack protection
    ])

# For macOS with Clang
elif sys.platform == 'darwin':
    EXTRA_COMPILE_ARGS.extend([
        '-flto',
        '-fno-plt',
    ])

# Include directories
INCLUDE_DIRS = [
    np.get_include(),
    os.path.join(os.path.dirname(__file__), '..', 'super_intelligence'),
    os.path.join(os.path.dirname(__file__), '..', 'modules_1_80'),
    os.path.join(os.path.dirname(__file__), '..', 'execution'),
    os.path.join(os.path.dirname(__file__), '..', 'risk'),
    os.path.join(os.path.dirname(__file__), '..', 'data_streams'),
    os.path.join(os.path.dirname(__file__), '..', 'simd_routines'),
]

# Library directories for SIMD
LIBRARY_DIRS = []

# Libraries to link
LIBRARIES = [
    'm',        # Math library
    'pthread',  # POSIX threads
]

# Cython extensions to compile
EXTENSIONS = [
    # Super Intelligence Modules
    Extension(
        'super_intelligence.quantum_manifolds',
        sources=['../super_intelligence/quantum_manifolds.pyx'],
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        libraries=LIBRARIES,
        extra_compile_args=EXTRA_COMPILE_ARGS,
        language='c',
    ),
    Extension(
        'super_intelligence.fluid_wave_chaos',
        sources=['../super_intelligence/fluid_wave_chaos.pyx'],
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        libraries=LIBRARIES,
        extra_compile_args=EXTRA_COMPILE_ARGS,
        language='c',
    ),
    Extension(
        'super_intelligence.non_commutative_lob',
        sources=['../super_intelligence/non_commutative_lob.pyx'],
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        libraries=LIBRARIES,
        extra_compile_args=EXTRA_COMPILE_ARGS,
        language='c',
    ),
    Extension(
        'super_intelligence.rough_volatility',
        sources=['../super_intelligence/rough_volatility.pyx'],
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        libraries=LIBRARIES,
        extra_compile_args=EXTRA_COMPILE_ARGS,
        language='c',
    ),
    
    # Feature Matrix
    Extension(
        'modules_1_80.feature_matrix',
        sources=['../modules_1_80/feature_matrix.pyx'],
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        libraries=LIBRARIES,
        extra_compile_args=EXTRA_COMPILE_ARGS,
        language='c',
    ),
    
    # Execution Engine
    Extension(
        'execution.kernel_bypass_gateway',
        sources=['../execution/kernel_bypass_gateway.pyx'],
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        libraries=LIBRARIES,
        extra_compile_args=EXTRA_COMPILE_ARGS,
        language='c',
    ),
    
    # SIMD Routines
    Extension(
        'simd_routines.avx512_math',
        sources=['../simd_routines/avx512_math.pyx'],
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        libraries=LIBRARIES,
        extra_compile_args=EXTRA_COMPILE_ARGS,
        language='c',
    ),
    
    # Data Streams
    Extension(
        'data_streams.ring_buffer',
        sources=['../data_streams/ring_buffer.pyx'],
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        libraries=LIBRARIES,
        extra_compile_args=EXTRA_COMPILE_ARGS,
        language='c',
    ),
]

setup(
    name='quantum_hft_bot',
    version='3.0.0',
    description='Quantum HFT Trading Bot - Cython Optimized',
    author='Quantum Quant Systems',
    author_email='quant@systems.dev',
    url='https://github.com/quantum-hft/bot',
    ext_modules=cythonize(
        EXTENSIONS,
        compiler_directives={
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
            'initializedcheck': False,
            'language_level': 3,
            'binding': True,
            'embedsignature': True,
            'always_allow_keywords': False,
            'annotation_typing': True,
            'infer_types': True,
        },
        nthreads=8,  # Parallel compilation
    ),
    include_dirs=[np.get_include()],
    python_requires='>=3.10',
    install_requires=[
        'numpy>=1.24.0',
        'cython>=3.0.0',
        'scipy>=1.10.0',
        'pandas>=2.0.0',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
)

if __name__ == '__main__':
    print("=" * 70)
    print("  QUANTUM HFT BOT - CYTHON COMPILATION")
    print("  Building with AVX-512 SIMD optimizations")
    print("=" * 70)
    setup()
