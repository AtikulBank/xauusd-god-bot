"""
Engine 6: Non-Equilibrium Thermodynamics
Entropy production for regime transition detection

Measures entropy production rate to detect when market
is far from equilibrium (impending regime change).
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class ThermodynamicState:
    """Thermodynamic state of market"""
    temperature: float      # Volatility proxy
    entropy: float          # Information entropy
    free_energy: float      # Available energy for work
    entropy_production: float
    equilibrium_distance: float


class NonEquilibriumThermodynamicsEngine:
    """
    Non-Equilibrium Thermodynamics Engine
    
    Models market as thermodynamic system:
    - Temperature ~ volatility
    - Entropy ~ randomness/disorder
    - Free energy ~ trend strength
    - Entropy production ~ rate of information creation
    
    High entropy production indicates far-from-equilibrium state,
    often preceding major regime changes.
    """
    
    def __init__(self, window: int = 100):
        self.window = window
        self.entropy_history: List[float] = []
        self.temperature_history: List[float] = []
        
    def compute_temperature(self, returns: np.ndarray) -> float:
        """
        Compute market "temperature" (volatility proxy)
        
        T = variance of returns (kinetic theory analogy)
        """
        if len(returns) < 2:
            return 0.01
        
        return float(np.var(returns))
    
    def compute_entropy(self, returns: np.ndarray, 
                       n_bins: int = 20) -> float:
        """
        Compute Shannon entropy of return distribution
        
        S = -Σ p_i * log(p_i)
        """
        if len(returns) < n_bins:
            return 0.0
        
        # Histogram
        hist, _ = np.histogram(returns, bins=n_bins, density=True)
        hist = hist[hist > 0]
        
        # Normalize
        hist = hist / np.sum(hist)
        
        # Entropy
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        
        return float(entropy)
    
    def compute_free_energy(self, returns: np.ndarray,
                           trend_strength: float = None) -> float:
        """
        Compute Helmholtz free energy
        
        F = U - T*S where:
        - U = internal energy (trend)
        - T = temperature
        - S = entropy
        
        High free energy indicates strong trends.
        """
        temperature = self.compute_temperature(returns)
        entropy = self.compute_entropy(returns)
        
        # Internal energy from trend
        if trend_strength is None:
            # Estimate from returns
            if len(returns) > 1:
                trend_strength = np.abs(np.mean(returns)) * np.sqrt(len(returns))
            else:
                trend_strength = 0.0
        
        # Free energy
        free_energy = trend_strength - temperature * entropy
        
        return float(free_energy)
    
    def compute_entropy_production_rate(self, returns: np.ndarray) -> float:
        """
        Compute entropy production rate
        
        σ = dS/dt
        
        High rate indicates rapid information creation (regime change)
        """
        if len(returns) < 2 * self.window:
            return 0.0
        
        # Entropy at two time points
        S1 = self.compute_entropy(returns[:-self.window])
        S2 = self.compute_entropy(returns[-self.window:])
        
        # Production rate
        rate = (S2 - S1) / self.window
        
        return float(rate)
    
    def compute_thermodynamic_force(self, prices: np.ndarray) -> float:
        """
        Compute thermodynamic force (gradient driving system)
        
        X = -∇F (negative gradient of free energy)
        """
        if len(prices) < 10:
            return 0.0
        
        # Simple gradient
        returns = np.diff(np.log(prices + 1e-10))
        
        # Force proportional to recent trend
        force = np.mean(returns[-10:])
        
        return float(force)
    
    def detect_phase_transition(self, returns: np.ndarray) -> Dict[str, Any]:
        """
        Detect thermodynamic phase transition
        
        Characterized by:
        - Diverging correlation length
        - Critical fluctuations
        - Scaling behavior
        """
        if len(returns) < 2 * self.window:
            return {
                'phase_transition': False,
                'criticality': 0.0,
                'correlation_length': 0.0
            }
        
        # Compute fluctuations at different scales
        fluctuations = []
        scales = [10, 20, 50, 100]
        
        for scale in scales:
            if scale <= len(returns):
                # Rolling variance at this scale
                var = np.var(returns[-scale:])
                fluctuations.append(var)
        
        if len(fluctuations) < 2:
            return {
                'phase_transition': False,
                'criticality': 0.0,
                'correlation_length': 0.0
            }
        
        # Critical scaling exponent
        log_scales = np.log(scales[:len(fluctuations)])
        log_fluct = np.log(np.array(fluctuations) + 1e-10)
        
        if len(log_scales) >= 2:
            slope = np.polyfit(log_scales, log_fluct, 1)[0]
            criticality = abs(slope) / 2.0
        else:
            criticality = 0.0
        
        # Correlation length (approximation)
        correlation_length = np.exp(criticality * 10)
        
        return {
            'phase_transition': criticality > 0.3,
            'criticality': min(1.0, criticality),
            'correlation_length': min(100, correlation_length)
        }
    
    def analyze(self, prices: np.ndarray,
               volumes: np.ndarray = None) -> Dict[str, Any]:
        """
        Complete non-equilibrium thermodynamics analysis
        
        Args:
            prices: Price time series
            volumes: Optional volume data
            
        Returns:
            Analysis results
        """
        returns = np.diff(np.log(prices + 1e-10))
        
        # Compute thermodynamic quantities
        temperature = self.compute_temperature(returns)
        entropy = self.compute_entropy(returns)
        free_energy = self.compute_free_energy(returns)
        entropy_production = self.compute_entropy_production_rate(returns)
        
        # Compute force
        force = self.compute_thermodynamic_force(prices)
        
        # Detect phase transition
        phase = self.detect_phase_transition(returns)
        
        # Equilibrium distance
        equilibrium_distance = abs(entropy_production)
        
        # Update history
        self.entropy_history.append(entropy)
        self.temperature_history.append(temperature)
        
        # Determine state
        if phase['phase_transition']:
            state = "CRITICAL"
        elif abs(entropy_production) > 0.1:
            state = "FAR_FROM_EQUILIBRIUM"
        elif abs(entropy_production) < 0.01:
            state = "NEAR_EQUILIBRIUM"
        else:
            state = "RELAXING"
        
        return {
            'temperature': temperature,
            'entropy': entropy,
            'free_energy': free_energy,
            'entropy_production_rate': entropy_production,
            'thermodynamic_force': force,
            'phase_transition': phase,
            'equilibrium_distance': equilibrium_distance,
            'system_state': state
        }
