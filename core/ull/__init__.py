"""
core.ull - Ultra-Low Latency Trading Module

Hardware-level trading engine with:
- Kernel bypass (DMA ring buffer)
- SIMD-accelerated mathematics (AVX-512)
- Bitwise atomic state machine
- Zero-copy memory access

Target latency: Sub-nanosecond (10^-9 seconds)
"""

__version__ = "1.0.0"
__author__ = "Quantum Systems Architect"

# Import main components
from .bitmask_trader import (
    BitmaskTrader,
    create_trader,
    run_demo,
    RouteType,
    ValidationFlags,
    ExecutionFlags,
    MarketTick,
    TradeSignal,
    Position
)

# Try to import compiled modules
try:
    from .kernel_bypass import (
        DMARingBuffer,
        FastMarketParser,
        AtomicTradeExecutor,
        simd_log_returns,
        simd_ema,
        simd_stddev,
        simd_dot_product,
        zeta_pivot_levels,
        fluid_velocity,
        fisher_information_matrix,
        distance_matrix
    )
    _HAS_DMA = True
except ImportError:
    _HAS_DMA = False

try:
    from .pico_math_simd import (
        SuperIntelligence_SIMD,
        create_super_intelligence_simd,
        fast_analyze,
        TDAEngine_SIMD,
        InfoGeometry_SIMD,
        QuantumEntanglement_SIMD,
        HyperbolicGeometry_SIMD,
        SymplecticGeometry_SIMD,
        NonEquilibriumThermo_SIMD,
        AlgebraicTopology_SIMD,
        DifferentialGeometry_SIMD,
        CategoryTheory_SIMD,
        MeasureTheory_SIMD
    )
    _HAS_SIMD = True
except ImportError:
    _HAS_SIMD = False


def get_system_info() -> dict:
    """Get information about available ULL components."""
    return {
        'version': __version__,
        'dma_available': _HAS_DMA,
        'simd_available': _HAS_SIMD,
        'components': {
            'kernel_bypass': _HAS_DMA,
            'simd_math': _HAS_SIMD,
            'bitmask_trader': True,
        }
    }


def print_system_info():
    """Print system information."""
    info = get_system_info()
    
    print("\n" + "="*60)
    print("ULTRA-LOW LATENCY TRADING SYSTEM")
    print("="*60)
    print(f"Version: {info['version']}")
    print(f"DMA Ring Buffer: {'✓ ENABLED' if info['dma_available'] else '✗ DISABLED'}")
    print(f"SIMD Acceleration: {'✓ ENABLED' if info['simd_available'] else '✗ DISABLED'}")
    print(f"Bitmask Trader: ✓ ENABLED")
    print("="*60 + "\n")


# Auto-compile if needed
if __name__ == "__main__":
    print_system_info()
