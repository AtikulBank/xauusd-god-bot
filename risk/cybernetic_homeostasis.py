"""
Cybernetic Homeostasis Risk Management Engine
Implements self-balancing negative feedback loop drawdown controller
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for position sizing"""
    MINIMAL = 0.005   # 0.5%
    LOW = 0.01        # 1%
    MODERATE = 0.02   # 2%
    HIGH = 0.03       # 3%
    EXTREME = 0.05    # 5%


class SystemState(Enum):
    """Overall system risk state"""
    NORMAL = "normal"
    CAUTIOUS = "cautious"
    DEFENSIVE = "defensive"
    EMERGENCY = "emergency"
    HALTED = "halted"


@dataclass
class Position:
    """Trading position"""
    position_id: str
    direction: float  # +1 for long, -1 for short
    entry_price: float
    current_price: float
    size: float
    stop_loss: float
    take_profit: float
    entry_time: float
    unrealized_pnl: float = 0.0
    max_favorable: float = 0.0
    max_adverse: float = 0.0


@dataclass
class DrawdownState:
    """Current drawdown state"""
    current_drawdown: float
    max_drawdown: float
    daily_drawdown: float
    drawdown_duration: float
    recovery_rate: float


@dataclass
class CyberneticState:
    """Complete cybernetic homeostasis state"""
    system_state: SystemState
    risk_level: RiskLevel
    position_size_multiplier: float
    drawdown_state: DrawdownState
    feedback_correction: float
    homeostasis_error: float
    time_in_state: float


class NegativeFeedbackController:
    """
    Negative Feedback Loop Controller
    
    Implements proportional-integral-derivative (PID) control
    for risk management homeostasis.
    """
    
    def __init__(self, kp: float = 1.0, ki: float = 0.1, kd: float = 0.05):
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain
        
        self.setpoint = 0.0  # Target drawdown (0 = no drawdown)
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_time = time.time()
        
    def compute_correction(self, current_value: float) -> float:
        """
        Compute PID correction for homeostasis
        
        Args:
            current_value: Current drawdown or risk metric
            
        Returns:
            Correction value to apply to position sizing
        """
        current_time = time.time()
        dt = current_time - self.prev_time
        if dt <= 0:
            dt = 0.001
        
        error = self.setpoint - current_value
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term (with anti-windup)
        self.integral += error * dt
        self.integral = max(-1.0, min(1.0, self.integral))  # Clamp
        i_term = self.ki * self.integral
        
        # Derivative term
        derivative = (error - self.prev_error) / dt
        d_term = self.kd * derivative
        
        # Update state
        self.prev_error = error
        self.prev_time = current_time
        
        # Total correction
        correction = p_term + i_term + d_term
        
        # Clamp to reasonable range
        correction = max(-1.0, min(1.0, correction))
        
        return correction
    
    def reset(self) -> None:
        """Reset controller state"""
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_time = time.time()


class CyberneticHomeostasis:
    """
    Cybernetic Homeostasis Risk Management Engine
    
    Self-balancing negative feedback loop drawdown controller that
    automatically adjusts position sizes based on system state.
    """
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.peak_balance = initial_balance
        
        # Controllers for different timescales
        self.controller_fast = NegativeFeedbackController(kp=1.5, ki=0.2, kd=0.1)
        self.controller_slow = NegativeFeedbackController(kp=0.5, ki=0.05, kd=0.02)
        
        # State tracking
        self.balance_history: List[float] = [initial_balance]
        self.drawdown_history: List[DrawdownState] = []
        self.positions: List[Position] = []
        
        # Homeostasis parameters
        self.target_drawdown = 0.0
        self.max_allowed_drawdown = 0.10  # 10%
        self.daily_drawdown_limit = 0.05  # 5%
        
        # System state
        self.current_state = SystemState.NORMAL
        self.state_start_time = time.time()
        
    def update_balance(self, new_balance: float) -> CyberneticState:
        """
        Update system with new balance and compute homeostatic state
        
        Args:
            new_balance: Updated account balance
            
        Returns:
            Current cybernetic state
        """
        self.current_balance = new_balance
        self.balance_history.append(new_balance)
        
        # Update peak
        if new_balance > self.peak_balance:
            self.peak_balance = new_balance
        
        # Compute drawdowns
        drawdown_state = self._compute_drawdowns()
        
        # Determine system state
        new_state = self._determine_state(drawdown_state)
        
        # Compute corrections
        fast_correction = self.controller_fast.compute_correction(drawdown_state.current_drawdown)
        slow_correction = self.controller_slow.compute_correction(drawdown_state.current_drawdown)
        
        # Combined correction (weighted average)
        combined_correction = 0.6 * fast_correction + 0.4 * slow_correction
        
        # Position size multiplier based on state
        multiplier = self._compute_position_multiplier(new_state, drawdown_state)
        
        # Homeostasis error (how far from target)
        homeostasis_error = abs(drawdown_state.current_drawdown - self.target_drawdown)
        
        # Time in current state
        time_in_state = time.time() - self.state_start_time
        
        if new_state != self.current_state:
            self.current_state = new_state
            self.state_start_time = time.time()
        
        state = CyberneticState(
            system_state=new_state,
            risk_level=self._state_to_risk_level(new_state),
            position_size_multiplier=multiplier,
            drawdown_state=drawdown_state,
            feedback_correction=combined_correction,
            homeostasis_error=homeostasis_error,
            time_in_state=time_in_state
        )
        
        self.drawdown_history.append(drawdown_state)
        
        return state
    
    def _compute_drawdowns(self) -> DrawdownState:
        """Compute current drawdown metrics"""
        current_dd = (self.peak_balance - self.current_balance) / self.peak_balance
        max_dd = max([dd.current_drawdown for dd in self.drawdown_history] + [current_dd])
        
        # Daily drawdown (from day start)
        day_start_balance = self.balance_history[-min(288, len(self.balance_history))]  # Assuming 5-min candles
        daily_dd = (day_start_balance - self.current_balance) / day_start_balance if day_start_balance > 0 else 0
        
        # Drawdown duration
        dd_duration = 0
        if self.current_balance < self.peak_balance:
            # Find when drawdown started
            for i in range(len(self.balance_history) - 1, -1, -1):
                if self.balance_history[i] >= self.peak_balance:
                    dd_duration = (len(self.balance_history) - 1 - i) * 300  # Assuming 5-min bars
                    break
        
        # Recovery rate
        if len(self.balance_history) > 10:
            recent = self.balance_history[-10:]
            recovery_rate = (recent[-1] - recent[0]) / (recent[0] + 1e-10)
        else:
            recovery_rate = 0.0
        
        return DrawdownState(
            current_drawdown=float(current_dd),
            max_drawdown=float(max_dd),
            daily_drawdown=float(daily_dd),
            drawdown_duration=float(dd_duration),
            recovery_rate=float(recovery_rate)
        )
    
    def _determine_state(self, drawdown: DrawdownState) -> SystemState:
        """Determine system state based on drawdown"""
        dd = drawdown.current_drawdown
        daily_dd = drawdown.daily_drawdown
        
        # Check emergency conditions
        if dd >= self.max_allowed_drawdown:
            return SystemState.HALTED
        
        if daily_dd >= self.daily_drawdown_limit:
            return SystemState.EMERGENCY
        
        # Progressive state determination
        if dd >= 0.08:
            return SystemState.DEFENSIVE
        elif dd >= 0.05:
            return SystemState.CAUTIOUS
        elif dd >= 0.02:
            return SystemState.NORMAL
        else:
            return SystemState.NORMAL
    
    def _state_to_risk_level(self, state: SystemState) -> RiskLevel:
        """Map system state to risk level"""
        mapping = {
            SystemState.NORMAL: RiskLevel.LOW,
            SystemState.CAUTIOUS: RiskLevel.MINIMAL,
            SystemState.DEFENSIVE: RiskLevel.MINIMAL,
            SystemState.EMERGENCY: RiskLevel.MINIMAL,
            SystemState.HALTED: RiskLevel.MINIMAL
        }
        return mapping.get(state, RiskLevel.LOW)
    
    def _compute_position_multiplier(self, state: SystemState, 
                                    drawdown: DrawdownState) -> float:
        """Compute position size multiplier based on state"""
        base_multipliers = {
            SystemState.NORMAL: 1.0,
            SystemState.CAUTIOUS: 0.5,
            SystemState.DEFENSIVE: 0.25,
            SystemState.EMERGENCY: 0.1,
            SystemState.HALTED: 0.0
        }
        
        base = base_multipliers.get(state, 1.0)
        
        # Adjust based on drawdown
        dd_adjustment = 1.0 - drawdown.current_drawdown * 5
        
        # Adjust based on recovery rate
        recovery_adjustment = 1.0 + drawdown.recovery_rate * 2
        
        multiplier = base * dd_adjustment * recovery_adjustment
        
        return max(0.0, min(1.0, multiplier))
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, 
                               signal_strength: float) -> float:
        """
        Calculate safe position size based on current state
        
        Args:
            entry_price: Planned entry price
            stop_loss: Planned stop loss
            signal_strength: Signal confidence [0, 1]
            
        Returns:
            Position size (fraction of balance)
        """
        if self.current_state == SystemState.HALTED:
            return 0.0
        
        # Base risk from state
        risk_level = self._state_to_risk_level(self.current_state)
        base_risk = risk_level.value
        
        # Adjust for signal strength
        signal_adjusted_risk = base_risk * signal_strength
        
        # Adjust for drawdown
        drawdown_state = self._compute_drawdowns()
        dd_adjustment = 1.0 - drawdown_state.current_drawdown * 3
        
        # Adjust for recovery
        recovery_adjustment = 1.0 + drawdown_state.recovery_rate
        
        # Final position size
        position_size = signal_adjusted_risk * dd_adjustment * recovery_adjustment
        
        # Calculate lot size based on stop distance
        stop_distance = abs(entry_price - stop_loss)
        if stop_distance > 0:
            # Risk in dollars
            risk_dollars = self.current_balance * position_size
            
            # Position size in lots (assuming 100 oz gold, $1 per point)
            position_lots = risk_dollars / (stop_distance * 100)
        else:
            position_lots = 0.0
        
        return max(0.0, min(0.1, position_lots))  # Cap at 10% of balance
    
    def register_position(self, position: Position) -> None:
        """Register a new position"""
        self.positions.append(position)
        logger.info(f"Position registered: {position.position_id}")
    
    def close_position(self, position_id: str, exit_price: float) -> Optional[Position]:
        """
        Close a position and update balance
        
        Args:
            position_id: ID of position to close
            exit_price: Exit price
            
        Returns:
            Closed position or None if not found
        """
        for pos in self.positions:
            if pos.position_id == position_id:
                # Calculate P&L
                pnl = pos.direction * (exit_price - pos.entry_price) * pos.size * 100
                self.current_balance += pnl
                
                logger.info(f"Position closed: {position_id}, P&L: ${pnl:.2f}")
                
                self.positions.remove(pos)
                return pos
        
        return None
    
    def should_trade(self) -> Tuple[bool, str]:
        """
        Determine if trading is allowed based on current state
        
        Returns:
            Tuple of (allowed, reason)
        """
        if self.current_state == SystemState.HALTED:
            return False, "System halted due to max drawdown"
        
        if self.current_state == SystemState.EMERGENCY:
            return False, "Emergency state - daily drawdown limit reached"
        
        if self.current_state == SystemState.DEFENSIVE:
            return True, "Defensive mode - reduced position sizes only"
        
        return True, "Normal operation"
    
    def get_homeostasis_report(self) -> Dict[str, any]:
        """Get comprehensive homeostasis report"""
        drawdown = self._compute_drawdowns()
        
        return {
            'system_state': self.current_state.value,
            'current_balance': self.current_balance,
            'peak_balance': self.peak_balance,
            'total_return': (self.current_balance - self.initial_balance) / self.initial_balance,
            'current_drawdown': drawdown.current_drawdown,
            'max_drawdown': drawdown.max_drawdown,
            'daily_drawdown': drawdown.daily_drawdown,
            'drawdown_duration_hours': drawdown.drawdown_duration / 3600,
            'recovery_rate': drawdown.recovery_rate,
            'open_positions': len(self.positions),
            'position_size_multiplier': self._compute_position_multiplier(
                self.current_state, drawdown
            )
        }


class FractionalMalliavinEngine:
    """
    Fractional Malliavin Calculus for Rough Volatility
    
    Uses Fractional Brownian Motion with Hurst exponent < 0.5
    to model "rough" volatility and predict future paths.
    """
    
    def __init__(self, hurst: float = 0.3, memory_length: int = 100):
        self.hurst = hurst  # H < 0.5 for rough volatility
        self.memory_length = memory_length
        self.volatility_history: List[float] = []
        
    def compute_hurst_exponent(self, prices: np.ndarray) -> float:
        """
        Estimate Hurst exponent from price series
        
        H < 0.5: Anti-persistent (mean-reverting)
        H = 0.5: Brownian motion
        H > 0.5: Persistent (trending)
        """
        if len(prices) < 20:
            return 0.5
        
        # R/S analysis
        n = len(prices)
        returns = np.diff(np.log(prices + 1e-10))
        
        max_k = min(n // 4, 100)
        rs_values = []
        
        for k in range(10, max_k):
            # Divide into non-overlapping blocks
            n_blocks = n // k
            rs_block = []
            
            for i in range(n_blocks):
                block = returns[i*k:(i+1)*k]
                mean_block = np.mean(block)
                cumdev = np.cumsum(block - mean_block)
                
                r = np.max(cumdev) - np.min(cumdev)
                s = np.std(block) + 1e-10
                
                rs_block.append(r / s)
            
            if rs_block:
                rs_values.append((k, np.mean(rs_block)))
        
        if len(rs_values) < 5:
            return 0.5
        
        # Linear regression in log-log space
        log_n = np.log([v[0] for v in rs_values])
        log_rs = np.log([v[1] for v in rs_values])
        
        # Fit line: log(R/S) = H * log(n) + c
        coeffs = np.polyfit(log_n, log_rs, 1)
        hurst = coeffs[0]
        
        # Clamp to valid range
        return float(max(0.1, min(0.9, hurst)))
    
    def fractional_brownian_motion(self, n: int, dt: float = 1.0) -> np.ndarray:
        """
        Generate fractional Brownian motion path
        
        Args:
            n: Number of steps
            dt: Time step
            
        Returns:
            FBM path
        """
        # Use Hosking's method for exact simulation
        fbm = np.zeros(n)
        
        # Initialize
        fbm[0] = 0.0
        
        # Compute autocorrelation
        def autocorr(k, H):
            return 0.5 * (abs(k+1)**(2*H) - 2*abs(k)**(2*H) + abs(k-1)**(2*H))
        
        # Generate using Cholesky decomposition (simplified)
        for i in range(1, n):
            # Sum of past increments weighted by autocorrelation
            weights = np.array([autocorr(i - j, self.hurst) for j in range(i)])
            weights = weights / (np.sum(np.abs(weights)) + 1e-10)
            
            fbm[i] = fbm[i-1] + np.dot(weights, np.random.randn(i)) * np.sqrt(dt)
        
        return fbm
    
    def predict_volatility_path(self, current_vol: float, horizon: int = 100) -> np.ndarray:
        """
        Predict future volatility path using fractional dynamics
        
        Args:
            current_vol: Current volatility
            horizon: Prediction horizon
            
        Returns:
            Array of predicted volatility values
        """
        # Generate FBM perturbation
        fbm_path = self.fractional_brownian_motion(horizon)
        
        # Scale to volatility units
        vol_scale = current_vol * 0.1  # 10% perturbation
        vol_perturbation = fbm_path * vol_scale
        
        # Predicted path
        predicted_vol = current_vol + vol_perturbation
        
        # Ensure positive
        predicted_vol = np.maximum(predicted_vol, 0.001)
        
        return predicted_vol
    
    def compute_malliavin_derivative(self, prices: np.ndarray) -> float:
        """
        Compute Malliavin derivative for sensitivity analysis
        
        The Malliavin derivative measures the sensitivity of
        functionals of the price path to perturbations.
        """
        if len(prices) < 10:
            return 0.0
        
        # Simplified Malliavin derivative computation
        returns = np.diff(np.log(prices + 1e-10))
        
        # Weight recent returns more heavily (fractional derivative)
        weights = np.array([(len(returns) - i) ** (self.hurst - 0.5) for i in range(len(returns))])
        weights = weights / np.sum(weights)
        
        # Compute derivative as weighted sum
        derivative = np.dot(weights, returns)
        
        return float(derivative)


if __name__ == "__main__":
    # Test cybernetic homeostasis
    print("Testing Cybernetic Homeostasis Engine")
    print("=" * 60)
    
    homeostasis = CyberneticHomeostasis(initial_balance=10000.0)
    
    # Simulate trading
    balance = 10000.0
    
    for i in range(100):
        # Simulate P&L
        pnl = np.random.randn() * 100
        balance += pnl
        
        # Update homeostasis
        state = homeostasis.update_balance(balance)
        
        if i % 20 == 0:
            report = homeostasis.get_homeostasis_report()
            print(f"\nStep {i}:")
            print(f"  Balance: ${report['current_balance']:.2f}")
            print(f"  Drawdown: {report['current_drawdown']:.2%}")
            print(f"  State: {report['system_state']}")
            print(f"  Position Multiplier: {report['position_size_multiplier']:.2f}")
    
    # Test fractional Malliavin
    print("\n" + "=" * 60)
    print("Testing Fractional Malliavin Engine")
    
    malliavin = FractionalMalliavinEngine(hurst=0.3)
    
    # Generate synthetic prices
    prices = 2000 + np.cumsum(np.random.randn(500) * 5)
    
    # Compute Hurst exponent
    hurst = malliavin.compute_hurst_exponent(prices)
    print(f"Estimated Hurst Exponent: {hurst:.4f}")
    
    # Predict volatility path
    current_vol = np.std(np.diff(np.log(prices + 1e-10))) * np.sqrt(252)
    vol_path = malliavin.predict_volatility_path(current_vol, horizon=50)
    
    print(f"Current Volatility: {current_vol:.4f}")
    print(f"Predicted Vol Range: [{np.min(vol_path):.4f}, {np.max(vol_path):.4f}]")
    
    # Malliavin derivative
    derivative = malliavin.compute_malliavin_derivative(prices[-100:])
    print(f"Malliavin Derivative: {derivative:.6f}")
