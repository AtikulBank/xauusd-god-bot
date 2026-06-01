/**
 * market_types.h - Ultra-Low Latency Market Data Types
 * 
 * Hardware-level structs for zero-copy DMA and SIMD processing.
 * All structs are cache-line aligned for optimal memory access.
 */

#ifndef MARKET_TYPES_H
#define MARKET_TYPES_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Cache line size (64 bytes on x86-64)
#define CACHE_LINE_SIZE 64
#define ALIGN_CACHE __attribute__((aligned(CACHE_LINE_SIZE)))

// Maximum order book depth
#define MAX_OB_DEPTH 32

// Maximum number of price levels for SIMD processing
#define SIMD_WIDTH_512 8  // 8 doubles in AVX-512
#define SIMD_WIDTH_256 4  // 4 doubles in AVX-256

/**
 * Market Tick - Single tick from exchange
 * Size: 64 bytes (exactly one cache line)
 */
typedef struct ALIGN_CACHE {
    uint64_t timestamp_ns;      // Nanosecond timestamp
    uint64_t sequence;          // Packet sequence number
    double   bid_price;         // Best bid price
    double   ask_price;         // Best ask price
    double   bid_size;          // Bid size
    double   ask_size;          // Ask size
    double   last_price;        // Last trade price
    double   volume;            // Tick volume
    uint32_t flags;             // Bit flags (0: trade, 1: quote, 2: depth)
    uint16_t symbol_id;         // Symbol identifier
    uint8_t  padding[6];        // Padding to 64 bytes
} MarketTick;

/**
 * Order Book Level - Single price level
 */
typedef struct {
    double price;
    double size;
    uint32_t order_count;
    uint32_t padding;
} OrderBookLevel;

/**
 * Order Book Snapshot - Full L2 order book
 * Size: 512 bytes (8 cache lines)
 */
typedef struct ALIGN_CACHE {
    uint64_t timestamp_ns;
    uint64_t sequence;
    uint32_t symbol_id;
    uint32_t depth;
    OrderBookLevel bids[MAX_OB_DEPTH];
    OrderBookLevel asks[MAX_OB_DEPTH];
    uint8_t padding[32];  // Align to cache line
} OrderBook;

/**
 * Market State - Aggregated market analysis state
 * Used for SIMD vectorized calculations
 */
typedef struct ALIGN_CACHE {
    // Price data (8 doubles = 64 bytes for AVX-512)
    double prices[SIMD_WIDTH_512];      // Recent prices
    double returns[SIMD_WIDTH_512];     // Recent returns
    double volumes[SIMD_WIDTH_512];     // Recent volumes
    
    // Technical indicators
    double ema_fast;
    double ema_slow;
    double atr;
    double vwap;
    
    // Regime state
    double volatility;
    double momentum;
    double trend_strength;
    double regime_score;
    
    // Super-Intelligence outputs
    double tda_breakout;
    double info_geometry_curvature;
    double quantum_entanglement;
    double hyperbolic_hierarchy;
    double differential_curvature;
    
    // Trading state
    double direction;           // -1.0 to +1.0
    double confidence;          // 0.0 to 1.0
    double position_size;       // In lots
    uint32_t route_type;        // Bitmask: 1=momentum, 2=breakout, 4=mean_reversion, 8=scalp
    uint32_t execution_flags;   // Bitmask: 1=execute, 2=modify, 4=close
    
    uint8_t padding[32];
} MarketState;

/**
 * Trade Signal - Execution signal
 * Packed for fast transmission
 */
typedef struct ALIGN_CACHE {
    uint64_t timestamp_ns;
    uint32_t symbol_id;
    uint32_t signal_id;
    double   direction;         // +1.0 = buy, -1.0 = sell
    double   confidence;        // 0.0 to 1.0
    double   entry_price;       // Target entry price
    double   stop_loss;         // Stop loss price
    double   take_profit;       // Take profit price
    double   position_size;     // Size in lots
    uint32_t route_type;        // Route type bitmask
    uint32_t validation_flags;  // 1=risk_ok, 2=quantum_ok, 4=topology_ok
    uint32_t magic_number;      // Unique trade identifier
    uint32_t padding;
} TradeSignal;

/**
 * DMA Ring Buffer - For kernel bypass networking
 * Maps directly to NIC memory
 */
typedef struct ALIGN_CACHE {
    volatile uint64_t head;     // Producer index
    volatile uint64_t tail;     // Consumer index
    uint64_t size;              // Buffer size (must be power of 2)
    uint64_t mask;              // Size - 1
    void*    entries;           // Pointer to entry array
    uint64_t entry_size;        // Size of each entry
    uint64_t padding[5];        // Pad to cache line
} DMARingBuffer;

/**
 * Atomic State Machine - Bitwise execution trigger
 */
typedef struct ALIGN_CACHE {
    volatile uint64_t state;    // Current state bits
    uint64_t trigger_mask;      // Trigger condition mask
    uint64_t action_mask;       // Action to take
    uint64_t sequence;          // State sequence number
    uint64_t timestamp_ns;      // Last state change
    uint8_t  padding[24];       // Pad to cache line
} AtomicStateMachine;

/**
 * SIMD Aligned Array - For vectorized operations
 */
typedef struct {
    double data[SIMD_WIDTH_512] __attribute__((aligned(32)));
    uint32_t length;
    uint32_t capacity;
} SIMDArray;

/**
 * Calabi-Yau Vector - Market manifold coordinates
 * 10 dimensions for topological analysis
 */
typedef struct ALIGN_CACHE {
    double x[10];               // 10D coordinates
    double curvature;           // Manifold curvature
    double invariant;           // Topological invariant
    uint32_t regime;            // Regime classification
    uint32_t padding[3];
} CalabiYauVector;

// Bitmask constants for route types
#define ROUTE_MOMENTUM      0x01
#define ROUTE_BREAKOUT      0x02
#define ROUTE_MEAN_REVERT   0x04
#define ROUTE_SCALP         0x08
#define ROUTE_WAIT          0x00

// Bitmask constants for execution flags
#define EXECUTE_TRADE       0x01
#define MODIFY_POSITION     0x02
#define CLOSE_POSITION      0x04
#define EMERGENCY_CLOSE     0x08

// Bitmask constants for validation
#define VALID_RISK_OK       0x01
#define VALID_QUANTUM_OK    0x02
#define VALID_TOPOLOGY_OK   0x04
#define VALID_MACRO_OK      0x08
#define VALID_ALL_OK        0x0F

#ifdef __cplusplus
}
#endif

#endif // MARKET_TYPES_H
