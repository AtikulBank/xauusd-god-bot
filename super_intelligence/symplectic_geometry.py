"""
Engine 5: Symplectic Geometry
Phase space for conserving market invariants

Uses Hamiltonian mechanics to model price-volume dynamics
as conservative systems, detecting hidden invariants.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class PhaseSpacePoint:
    """Point in symplectic phase space"""
    position: float  # Price
    momentum: float  # Volume-adjusted momentum
    energy: float    # Hamiltonian value
    symplectic_area: float


@dataclass
class HamiltonianSystem:
    """Hamiltonian system for market dynamics"""
    hamiltonian: float
    momentum: float
    position: float
    time_evolution: np.ndarray
    conserved_quantity: float


class SymplecticGeometryEngine:
    """
    Symplectic Geometry Engine
    
    Models market dynamics as Hamiltonian system in phase space.
    
    Key insights:
    - Price = position coordinate
    - Volume-adjusted returns = momentum
    - Hamiltonian (energy) is approximately conserved
    - Phase space volume preserved (Liouville's theorem)
    """
    
    def __init__(self):
        self.phase_space_history: List[PhaseSpacePoint] = []
        self.hamiltonian_history: List[float] = []
        
    def compute_momentum(self, prices: np.ndarray, 
                        volumes: np.ndarray) -> np.ndarray:
        """
        Compute market momentum (analogous to mechanical momentum)
        
        p = m * v where m ~ volume, v ~ price velocity
        """
        if len(prices) < 2 or len(volumes) < 2:
            return np.array([0.0])
        
        # Price velocity
        velocity = np.diff(prices)
        
        # Mass (volume proxy)
        mass = (volumes[:-1] + volumes[1:]) / 2.0
        
        # Momentum
        momentum = mass * velocity
        
        return momentum
    
    def compute_hamiltonian(self, prices: np.ndarray,
                           volumes: np.ndarray) -> float:
        """
        Compute Hamiltonian (total energy) of market system
        
        H = T(p) + V(q) where:
        - T(p) = kinetic energy ~ momentum² / mass
        - V(q) = potential energy ~ price deviation from mean
        """
        momentum = self.compute_momentum(prices, volumes)
        
        if len(momentum) == 0:
            return 0.0
        
        # Kinetic energy
        mass = volumes[-len(momentum):] if len(volumes) >= len(momentum) else np.ones(len(momentum))
        kinetic = np.sum(momentum**2 / (2 * mass + 1e-10))
        
        # Potential energy (mean reversion potential)
        mean_price = np.mean(prices)
        potential = 0.5 * np.sum((prices[-len(momentum):] - mean_price)**2)
        
        # Total Hamiltonian
        hamiltonian = kinetic + potential
        
        return float(hamiltonian)
    
    def compute_symplectic_form(self, prices: np.ndarray,
                               volumes: np.ndarray) -> np.ndarray:
        """
        Compute symplectic 2-form ω = dp ∧ dq
        
        Measures phase space area preservation
        """
        momentum = self.compute_momentum(prices, volumes)
        
        if len(momentum) < 2 or len(prices) < 2:
            return np.array([[1.0, 0.0], [0.0, 1.0]])
        
        # dp and dq
        dp = np.diff(momentum)
        dq = np.diff(prices[-len(dp)-1:])
        
        # Symplectic matrix
        omega = np.array([[0.0, 1.0], [-1.0, 0.0]])
        
        # Compute area
        symplectic_area = np.abs(np.sum(dp * dq))
        
        return omega * symplectic_area
    
    def detect_conserved_quantity(self, prices: np.ndarray,
                                 volumes: np.ndarray,
                                 window: int = 100) -> Dict[str, Any]:
        """
        Detect approximately conserved quantities in market dynamics
        
        True conserved quantities indicate hidden market invariants.
        """
        if len(prices) < window:
            return {
                'has_conserved': False,
                'conservation_quality': 0.0,
                'invariant_value': 0.0
            }
        
        # Compute Hamiltonian over sliding windows
        hamiltonians = []
        for i in range(len(prices) - window + 1):
            h = self.compute_hamiltonian(prices[i:i+window], volumes[i:i+window])
            hamiltonians.append(h)
        
        hamiltonians = np.array(hamiltonians)
        
        # Check conservation (low variance = conserved)
        if len(hamiltonians) > 1:
            mean_h = np.mean(hamiltonians)
            std_h = np.std(hamiltonians)
            
            conservation_quality = 1.0 - min(1.0, std_h / (abs(mean_h) + 1e-10))
        else:
            conservation_quality = 0.0
        
        return {
            'has_conserved': conservation_quality > 0.7,
            'conservation_quality': conservation_quality,
            'invariant_mean': float(np.mean(hamiltonians)) if len(hamiltonians) > 0 else 0.0,
            'invariant_std': float(np.std(hamiltonians)) if len(hamiltonians) > 0 else 0.0
        }
    
    def phase_portrait(self, prices: np.ndarray,
                      volumes: np.ndarray) -> List[PhaseSpacePoint]:
        """
        Generate phase portrait of market dynamics
        
        Returns trajectory in (price, momentum) space
        """
        momentum = self.compute_momentum(prices, volumes)
        
        points = []
        for i in range(len(momentum)):
            q = prices[i + len(prices) - len(momentum)]
            p = momentum[i]
            
            # Energy at this point
            mass = volumes[i] if i < len(volumes) else 1.0
            energy = p**2 / (2 * mass) + 0.5 * (q - np.mean(prices))**2
            
            points.append(PhaseSpacePoint(
                position=q,
                momentum=p,
                energy=energy,
                symplectic_area=0.0
            ))
        
        self.phase_space_history.extend(points)
        
        return points
    
    def analyze(self, prices: np.ndarray,
               volumes: np.ndarray) -> Dict[str, Any]:
        """
        Complete symplectic geometry analysis
        
        Args:
            prices: Price time series
            volumes: Volume time series
            
        Returns:
            Analysis results
        """
        # Compute conserved quantity
        conserved = self.detect_conserved_quantity(prices, volumes)
        
        # Current Hamiltonian
        current_h = self.compute_hamiltonian(prices, volumes)
        
        # Phase portrait
        phase_points = self.phase_portrait(prices, volumes)
        
        # Compute average energy
        if phase_points:
            avg_energy = np.mean([p.energy for p in phase_points])
        else:
            avg_energy = 0.0
        
        return {
            'hamiltonian': current_h,
            'conserved_quantity': conserved,
            'avg_energy': avg_energy,
            'phase_space_dim': 2,
            'n_points': len(phase_points),
            'system_type': 'conservative' if conserved['has_conserved'] else 'dissipative'
        }
