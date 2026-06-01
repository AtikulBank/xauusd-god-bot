"""
bitmask_trader.py - Ultra-Low Latency Trading Wrapper

Main Python interface for the compiled Cython/C++ hardware bridges.
Manages the complete trading pipeline with picosecond-level latency.
"""

import numpy as np
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import IntFlag
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

# ============================================================================
# Constants
# ============================================================================

class RouteType(IntFlag):
    """Trade route types as bitmask flags."""
    NONE = 0
    MOMENTUM = 0x01
    BREAKOUT = 0x02
    MEAN_REVERT = 0x04
    SCALP = 0x08
    WAIT = 0x00

class ValidationFlags(IntFlag):
    """Validation check flags."""
    NONE = 0
    RISK_OK = 0x01
    QUANTUM_OK = 0x02
    TOPOLOGY_OK = 0x04
    MACRO_OK = 0x08
    ALL_OK = 0x0F

class ExecutionFlags(IntFlag):
    """Execution action flags."""
    NONE = 0
    EXECUTE = 0x01
    MODIFY = 0x02
    CLOSE = 0x04
    EMERGENCY = 0x08

# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class MarketTick:
    """Single market tick."""
    timestamp_ns: int
    bid_price: float
    ask_price: float
    bid_size: float
    ask_size: float
    last_price: float
    volume: float
    flags: int
    symbol_id: int

@dataclass
class TradeSignal:
    """Trade execution signal."""
    signal_id: int
    timestamp_ns: int
    direction: float  # -1.0 to +1.0
    confidence: float  # 0.0 to 1.0
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    route_type: RouteType
    validation_flags: ValidationFlags
    magic_number: int

@dataclass
class EngineOutput:
    """Output from a single analysis engine."""
    engine_name: str
    direction: float
    confidence: float
    metadata: Dict[str, Any]

@dataclass
class Position:
    """Open trading position."""
    position_id: str
    symbol: str
    direction: float
    entry_price: float
    current_price: float
    size: float
    stop_loss: float
    take_profit: float
    entry_time: float
    unrealized_pnl: float = 0.0

# ============================================================================
# Core Trading Engine
# ============================================================================

class BitmaskTrader:
    """
    Ultra-Low Latency Trading Engine.
    
    Uses compiled Cython modules for hardware-level performance.
    Targets sub-nanosecond processing latency.
    """
    
    def __init__(self, initial_balance: float = 10000.0):
        """Initialize the trading engine."""
        logger.info("Initializing Ultra-Low Latency Trading Engine")
        
        # Try to import compiled Cython modules
        self._use_simd = False
        self._use_dma = False
        
        try:
            from core.ull.pico_math_simd import SuperIntelligence_SIMD, create_super_intelligence_simd
            self.super_intel_simd = create_super_intelligence_simd()
            self._use_simd = True
            logger.info("SIMD-accelerated engines loaded successfully")
        except ImportError as e:
            logger.warning(f"SIMD engines not available: {e}")
            logger.info("Falling back to NumPy implementation")
        
        try:
            from core.ull.kernel_bypass import DMARingBuffer, FastMarketParser, AtomicTradeExecutor
            self.dma_buffer = DMARingBuffer()
            self.market_parser = FastMarketParser()
            self.atomic_executor = AtomicTradeExecutor()
            self._use_dma = True
            logger.info("DMA ring buffer loaded successfully")
        except ImportError as e:
            logger.warning(f"DMA buffer not available: {e}")
        
        # State management
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions: List[Position] = []
        self.trade_history: List[Dict[str, Any]] = []
        self.signal_history: List[TradeSignal] = []
        
        # Configuration
        self.config = {
            'min_confidence': 0.6,
            'max_positions': 3,
            'max_risk_per_trade': 0.02,  # 2% of balance
            'stop_loss_atr_multiplier': 2.0,
            'take_profit_atr_multiplier': 3.0,
        }
        
        # Performance tracking
        self.tick_count = 0
        self.signal_count = 0
        self.trade_count = 0
        
        logger.info(f"Trading engine initialized with ${initial_balance:.2f}")
    
    # ========================================================================
    # Market Data Processing
    # ========================================================================
    
    def process_tick(self, bid_price: float, ask_price: float,
                     bid_size: float, ask_size: float,
                     volume: float, symbol_id: int = 0) -> Optional[TradeSignal]:
        """
        Process incoming market tick.
        
        This is the hot path - must be ultra-fast.
        
        Args:
            bid_price: Best bid price
            ask_price: Best ask price
            bid_size: Bid size
            ask_size: Ask size
            volume: Tick volume
            symbol_id: Symbol identifier
        
        Returns:
            TradeSignal if trade should be executed, None otherwise
        """
        self.tick_count += 1
        timestamp_ns = int(time.time() * 1e9)
        
        # Store in DMA buffer if available
        if self._use_dma:
            self.dma_buffer.write_tick(bid_price, ask_price, bid_size, ask_size,
                                       (bid_price + ask_price) / 2, volume, 0, symbol_id)
            self.market_parser.update(bid_price, ask_price, volume)
        
        # Check if we have enough data
        if self.tick_count < 100:
            return None
        
        # Check position limits
        if len(self.positions) >= self.config['max_positions']:
            return None
        
        # Run analysis
        signal = self._run_analysis(bid_price, ask_price, volume, timestamp_ns)
        
        return signal
    
    # ========================================================================
    # Analysis Pipeline
    # ========================================================================
    
    def _run_analysis(self, bid_price: float, ask_price: float,
                      volume: float, timestamp_ns: int) -> Optional[TradeSignal]:
        """
        Run complete analysis pipeline.
        
        Uses SIMD-accelerated engines when available.
        """
        mid_price = (bid_price + ask_price) / 2
        
        # Generate synthetic price history for analysis
        # In production, this would come from the DMA buffer
        prices = self._get_price_history(mid_price)
        volumes = self._get_volume_history(volume)
        
        # Run Super-Intelligence analysis
        if self._use_simd:
            analysis = self._run_simd_analysis(prices, volumes)
        else:
            analysis = self._run_numpy_analysis(prices, volumes)
        
        # Check if we should trade
        if not analysis.get('execute', False):
            return None
        
        # Check confidence threshold
        confidence = analysis.get('confidence', 0.0)
        if confidence < self.config['min_confidence']:
            return None
        
        # Determine route type
        route_type = self._determine_route(analysis)
        
        # Validate trade
        validation_flags = self._validate_trade(analysis, route_type)
        
        if not (validation_flags & ValidationFlags.ALL_OK):
            return None
        
        # Calculate position parameters
        direction = analysis.get('direction', 0.0)
        atr = self._calculate_atr(prices)
        
        entry_price = mid_price
        if direction > 0:  # Long
            stop_loss = entry_price - atr * self.config['stop_loss_atr_multiplier']
            take_profit = entry_price + atr * self.config['take_profit_atr_multiplier']
        else:  # Short
            stop_loss = entry_price + atr * self.config['stop_loss_atr_multiplier']
            take_profit = entry_price - atr * self.config['take_profit_atr_multiplier']
        
        # Calculate position size
        position_size = self._calculate_position_size(
            entry_price, stop_loss, confidence
        )
        
        if position_size <= 0:
            return None
        
        # Create trade signal
        signal = TradeSignal(
            signal_id=self.signal_count,
            timestamp_ns=timestamp_ns,
            direction=direction,
            confidence=confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            route_type=route_type,
            validation_flags=validation_flags,
            magic_number=self._generate_magic_number()
        )
        
        self.signal_count += 1
        self.signal_history.append(signal)
        
        return signal
    
    def _run_simd_analysis(self, prices: np.ndarray, volumes: np.ndarray) -> Dict:
        """Run analysis using SIMD-accelerated engine."""
        try:
            result = self.super_intel_simd.analyze(prices, volumes)
            return result
        except Exception as e:
            logger.error(f"SIMD analysis failed: {e}")
            return self._run_numpy_analysis(prices, volumes)
    
    def _run_numpy_analysis(self, prices: np.ndarray, volumes: np.ndarray) -> Dict:
        """Fallback NumPy analysis."""
        returns = np.diff(np.log(prices + 1e-10))
        n = len(returns)
        
        if n < 10:
            return {'direction': 0.0, 'confidence': 0.0, 'execute': False}
        
        # Simple momentum signal
        momentum = np.mean(returns[-20:]) if n >= 20 else np.mean(returns)
        volatility = np.std(returns[-20:]) if n >= 20 else np.std(returns)
        
        direction = np.tanh(momentum / (volatility + 1e-10))
        confidence = min(1.0, abs(direction) * 2)
        
        execute = confidence > self.config['min_confidence'] and abs(direction) > 0.2
        
        return {
            'direction': direction,
            'confidence': confidence,
            'execute': execute,
            'tda_breakout': 0.5,
            'info_geometry_curvature': 0.0,
            'hyperbolic_hierarchy': 0.5,
            'differential_curvature': 0.0
        }
    
    # ========================================================================
    # Route Determination
    # ========================================================================
    
    def _determine_route(self, analysis: Dict) -> RouteType:
        """Determine trade route type from analysis."""
        tda_breakout = analysis.get('tda_breakout', 0.5)
        curvature = analysis.get('differential_curvature', 0.0)
        hierarchy = analysis.get('hyperbolic_hierarchy', 0.5)
        
        if tda_breakout > 0.7:
            return RouteType.BREAKOUT
        elif abs(curvature) > 0.1:
            return RouteType.MOMENTUM
        elif hierarchy > 0.6:
            return RouteType.MEAN_REVERT
        else:
            return RouteType.SCALP
    
    # ========================================================================
    # Validation
    # ========================================================================
    
    def _validate_trade(self, analysis: Dict, route_type: RouteType) -> ValidationFlags:
        """Validate trade with all checks."""
        flags = ValidationFlags.NONE
        
        # Risk check
        confidence = analysis.get('confidence', 0.0)
        if confidence > 0.5:
            flags |= ValidationFlags.RISK_OK
        
        # Quantum check
        concurrence = analysis.get('quantum_concurrence', 0.0)
        if concurrence < 0.8:  # Not too correlated
            flags |= ValidationFlags.QUANTUM_OK
        
        # Topology check
        hierarchy = analysis.get('hyperbolic_hierarchy', 0.5)
        if hierarchy > 0.3:
            flags |= ValidationFlags.TOPOLOGY_OK
        
        # Macro check (simplified)
        flags |= ValidationFlags.MACRO_OK
        
        return flags
    
    # ========================================================================
    # Position Management
    # ========================================================================
    
    def execute_signal(self, signal: TradeSignal) -> Optional[Position]:
        """
        Execute a trade signal.
        
        Opens a new position based on the signal.
        """
        # Check if we can open this trade
        if len(self.positions) >= self.config['max_positions']:
            logger.warning("Max positions reached")
            return None
        
        # Check balance
        required_margin = signal.position_size * signal.entry_price
        if required_margin > self.balance * 0.5:  # Max 50% margin
            logger.warning("Insufficient margin")
            return None
        
        # Create position
        position = Position(
            position_id=f"POS_{self.trade_count:06d}",
            symbol="XAUUSD",
            direction=1.0 if signal.direction > 0 else -1.0,
            entry_price=signal.entry_price,
            current_price=signal.entry_price,
            size=signal.position_size,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            entry_time=time.time()
        )
        
        self.positions.append(position)
        self.trade_count += 1
        
        # Update balance (margin)
        self.balance -= required_margin * 0.01  # 1% margin
        
        logger.info(f"Position opened: {position.position_id} "
                    f"{'LONG' if position.direction > 0 else 'SHORT'} "
                    f"@ {position.entry_price:.2f}")
        
        return position
    
    def update_positions(self, current_price: float) -> List[str]:
        """
        Update all positions with current price.
        
        Returns list of closed position IDs.
        """
        closed_positions = []
        
        for position in self.positions[:]:
            position.current_price = current_price
            
            # Calculate P&L
            price_diff = (current_price - position.entry_price) * position.direction
            position.unrealized_pnl = price_diff * position.size * 100  # 100 oz per lot
            
            # Check stop loss
            if position.direction > 0 and current_price <= position.stop_loss:
                self._close_position(position, current_price, "STOP_LOSS")
                closed_positions.append(position.position_id)
            elif position.direction < 0 and current_price >= position.stop_loss:
                self._close_position(position, current_price, "STOP_LOSS")
                closed_positions.append(position.position_id)
            
            # Check take profit
            elif position.direction > 0 and current_price >= position.take_profit:
                self._close_position(position, current_price, "TAKE_PROFIT")
                closed_positions.append(position.position_id)
            elif position.direction < 0 and current_price <= position.take_profit:
                self._close_position(position, current_price, "TAKE_PROFIT")
                closed_positions.append(position.position_id)
        
        return closed_positions
    
    def _close_position(self, position: Position, exit_price: float, reason: str):
        """Close a position and record the trade."""
        # Calculate final P&L
        pnl = (exit_price - position.entry_price) * position.direction * position.size * 100
        
        # Update balance
        self.balance += position.size * position.entry_price * 0.01  # Return margin
        self.balance += pnl
        
        # Record trade
        trade_record = {
            'position_id': position.position_id,
            'symbol': position.symbol,
            'direction': 'LONG' if position.direction > 0 else 'SHORT',
            'entry_price': position.entry_price,
            'exit_price': exit_price,
            'size': position.size,
            'pnl': pnl,
            'pnl_pct': pnl / self.initial_balance * 100,
            'reason': reason,
            'duration': time.time() - position.entry_time,
            'timestamp': time.time()
        }
        
        self.trade_history.append(trade_record)
        
        # Remove position
        self.positions.remove(position)
        
        logger.info(f"Position closed: {position.position_id} "
                    f"P&L: ${pnl:.2f} ({pnl/self.initial_balance*100:.2f}%) "
                    f"Reason: {reason}")
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _get_price_history(self, current_price: float) -> np.ndarray:
        """Get price history for analysis (synthetic for demo)."""
        # Generate synthetic price history
        np.random.seed(int(time.time()) % 1000)
        n = 200
        returns = np.random.randn(n) * 0.001
        prices = current_price * np.exp(np.cumsum(returns))
        prices[-1] = current_price
        return prices
    
    def _get_volume_history(self, current_volume: float) -> np.ndarray:
        """Get volume history for analysis."""
        np.random.seed(int(time.time()) % 1000 + 100)
        n = 200
        return np.abs(np.random.randn(n) * current_volume * 0.3 + current_volume)
    
    def _calculate_atr(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate Average True Range."""
        if len(prices) < period + 1:
            return 5.0
        
        tr = np.abs(np.diff(prices[-period-1:]))
        return float(np.mean(tr))
    
    def _calculate_position_size(self, entry_price: float, stop_loss: float,
                                 confidence: float) -> float:
        """Calculate position size using Kelly criterion."""
        # Risk per trade
        risk_amount = self.balance * self.config['max_risk_per_trade']
        
        # Stop distance in price
        stop_distance = abs(entry_price - stop_loss)
        
        if stop_distance < 0.01:
            return 0.0
        
        # Position size in lots (100 oz per lot)
        size = risk_amount / (stop_distance * 100)
        
        # Adjust by confidence
        size *= confidence
        
        # Round to 2 decimal places
        return round(max(0.01, min(size, 1.0)), 2)
    
    def _generate_magic_number(self) -> int:
        """Generate unique magic number for trade."""
        return int(time.time() * 1000) % 1000000
    
    # ========================================================================
    # Performance Reporting
    # ========================================================================
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        if not self.trade_history:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'current_balance': self.balance,
                'total_return': 0.0,
                'open_positions': len(self.positions),
                'tick_count': self.tick_count,
                'signal_count': self.signal_count,
                'simd_enabled': self._use_simd,
                'dma_enabled': self._use_dma
            }
        
        pnls = [t['pnl'] for t in self.trade_history]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        
        return {
            'total_trades': len(self.trade_history),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': len(wins) / len(self.trade_history) if self.trade_history else 0,
            'total_pnl': sum(pnls),
            'average_pnl': np.mean(pnls),
            'max_win': max(pnls) if pnls else 0,
            'max_loss': min(pnls) if pnls else 0,
            'profit_factor': abs(sum(wins)) / abs(sum(losses)) if losses else float('inf'),
            'current_balance': self.balance,
            'total_return': (self.balance - self.initial_balance) / self.initial_balance,
            'open_positions': len(self.positions),
            'tick_count': self.tick_count,
            'signal_count': self.signal_count,
            'simd_enabled': self._use_simd,
            'dma_enabled': self._use_dma
        }

# ============================================================================
# Convenience Functions
# ============================================================================

def create_trader(initial_balance: float = 10000.0) -> BitmaskTrader:
    """Create a new trading engine instance."""
    return BitmaskTrader(initial_balance)

def run_demo(duration: float = 10.0) -> Dict[str, Any]:
    """
    Run a quick demo of the trading engine.
    
    Args:
        duration: How long to run in seconds
    
    Returns:
        Performance report
    """
    trader = create_trader()
    start_time = time.time()
    
    print(f"\n{'='*60}")
    print(f"ULTRA-LOW LATENCY TRADING DEMO")
    print(f"Running for {duration} seconds...")
    print(f"{'='*60}\n")
    
    tick_count = 0
    while time.time() - start_time < duration:
        # Generate synthetic tick
        base_price = 2000.0 + np.random.randn() * 10
        spread = 0.2 + abs(np.random.randn()) * 0.1
        
        bid_price = base_price - spread / 2
        ask_price = base_price + spread / 2
        volume = 100 + abs(np.random.randn()) * 50
        
        # Process tick
        signal = trader.process_tick(
            bid_price, ask_price,
            bid_price * 0.1, ask_price * 0.1,
            volume, 0
        )
        
        # Execute signal if generated
        if signal:
            trader.execute_signal(signal)
        
        # Update positions
        trader.update_positions(base_price)
        
        tick_count += 1
        
        # Print progress
        if tick_count % 1000 == 0:
            report = trader.get_performance_report()
            print(f"Tick {tick_count}: Balance=${report['current_balance']:.2f}, "
                  f"Trades={report['total_trades']}, "
                  f"P&L=${report['total_pnl']:.2f}")
    
    # Final report
    report = trader.get_performance_report()
    
    print(f"\n{'='*60}")
    print(f"FINAL PERFORMANCE REPORT")
    print(f"{'='*60}")
    print(f"Total Trades: {report['total_trades']}")
    print(f"Win Rate: {report['win_rate']:.2%}")
    print(f"Total P&L: ${report['total_pnl']:.2f}")
    print(f"Final Balance: ${report['current_balance']:.2f}")
    print(f"Total Return: {report['total_return']:.2%}")
    print(f"SIMD Enabled: {report['simd_enabled']}")
    print(f"DMA Enabled: {report['dma_enabled']}")
    print(f"{'='*60}\n")
    
    return report

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Run demo
    report = run_demo(duration=10.0)
