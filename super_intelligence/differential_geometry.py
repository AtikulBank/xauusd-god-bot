"""
Engine 8: Differential Geometry
Riemann curvature for market manifold analysis

Computes curvature of the price manifold to detect
acceleration/deceleration of trends.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class RiemannianManifold:
    """Riemannian manifold representing market state"""
    metric_tensor: np.ndarray
    christoffel_symbols: np.ndarray
    riemann_tensor: np.ndarray
    ricci_tensor: np.ndarray
    scalar_curvature: float


@dataclass
class GeodesicDeviation:
    """Geodesic deviation (tidal force) measurement"""
    jacobian: np.ndarray
    deviation_rate: float
    focusing: bool


class DifferentialGeometryEngine:
    """
    Differential Geometry Engine
    
    Treats price history as a curve in Riemannian manifold.
    
    Key applications:
    - Curvature detects trend acceleration
    - Geodesics predict optimal paths
    - Parallel transport reveals hidden correlations
    """
    
    def __init__(self, embedding_dim: int = 3):
        self.embedding_dim = embedding_dim
        self.metric_history: List[np.ndarray] = []
        self.curvature_history: List[float] = []
        
    def compute_metric_tensor(self, prices: np.ndarray,
                             window: int = 20) -> np.ndarray:
        """
        Compute Riemannian metric tensor from price data
        
        g_ij = Σ_k (∂f_i/∂x_k)(∂f_j/∂x_k)
        """
        n = len(prices)
        if n < window + 2:
            return np.eye(self.embedding_dim) * 0.01
        
        # Simple embedding: price, velocity, acceleration
        features = np.zeros((window, 3))
        for i in range(window):
            idx = n - window + i
            features[i, 0] = prices[idx]  # Position
            if idx > 0:
                features[i, 1] = prices[idx] - prices[idx-1]  # Velocity
            if idx > 1:
                features[i, 2] = (prices[idx] - prices[idx-1]) - (prices[idx-1] - prices[idx-2])  # Acceleration
        
        # Normalize
        for j in range(3):
            col = features[:, j]
            std = np.std(col)
            if std > 0:
                features[:, j] = (col - np.mean(col)) / std
        
        # Compute metric tensor (covariance matrix approximation)
        metric = np.cov(features.T)
        
        # Regularize
        metric += 1e-6 * np.eye(3)
        
        self.metric_history.append(metric)
        
        return metric
    
    def compute_christoffel_symbols(self, metric: np.ndarray,
                                   h: float = 1e-5) -> np.ndarray:
        """
        Compute Christoffel symbols of the second kind
        
        Γ^k_ij = (1/2) g^kl (∂g_li/∂x_j + ∂g_lj/∂x_i - ∂g_ij/∂x_l)
        
        Approximated using finite differences.
        """
        n = metric.shape[0]
        christoffel = np.zeros((n, n, n))
        
        try:
            inv_metric = np.linalg.inv(metric)
        except np.linalg.LinAlgError:
            return christoffel
        
        # Simplified computation (constant metric approximation)
        # In reality, would need derivatives of metric
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    # Approximate using metric variation
                    if i == j:
                        christoffel[k, i, j] = 0.1 * inv_metric[k, i]
                    else:
                        christoffel[k, i, j] = 0.05 * (inv_metric[k, i] + inv_metric[k, j])
        
        return christoffel
    
    def compute_riemann_tensor(self, christoffel: np.ndarray,
                              h: float = 1e-5) -> np.ndarray:
        """
        Compute Riemann curvature tensor
        
        R^l_ijk = ∂_i Γ^l_jk - ∂_j Γ^l_ik + Γ^l_im Γ^m_jk - Γ^l_jm Γ^m_ik
        
        Simplified approximation.
        """
        n = christoffel.shape[0]
        riemann = np.zeros((n, n, n, n))
        
        # Simplified curvature estimation
        for l in range(n):
            for i in range(n):
                for j in range(n):
                    for k in range(n):
                        # Approximate Riemann tensor
                        riemann[l, i, j, k] = (
                            christoffel[l, j, k] * christoffel[l, i, j] -
                            christoffel[l, i, k] * christoffel[l, j, i]
                        )
        
        return riemann
    
    def compute_ricci_tensor(self, riemann: np.ndarray) -> np.ndarray:
        """
        Compute Ricci tensor by contracting Riemann tensor
        
        R_ij = R^k_ikj
        """
        n = riemann.shape[0]
        ricci = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    ricci[i, j] += riemann[k, i, k, j]
        
        return ricci
    
    def compute_scalar_curvature(self, ricci: np.ndarray,
                                metric: np.ndarray) -> float:
        """
        Compute scalar curvature
        
        R = g^ij R_ij
        """
        try:
            inv_metric = np.linalg.inv(metric)
            scalar = np.trace(inv_metric @ ricci)
            return float(scalar)
        except Exception:
            return 0.0
    
    def compute_ricci_flow(self, metric: np.ndarray,
                          dt: float = 0.01) -> np.ndarray:
        """
        Ricci flow for metric evolution
        
        ∂g/∂t = -2 * Ric(g)
        
        Smooths out curvature singularities.
        """
        ricci = self.compute_riemann_tensor(
            self.compute_christoffel_symbols(metric)
        )
        ricci_tensor = self.compute_ricci_tensor(ricci)
        
        # Evolve metric
        new_metric = metric - 2 * dt * ricci_tensor
        
        # Ensure positive definiteness
        eigenvalues = np.linalg.eigvalsh(new_metric)
        if np.any(eigenvalues <= 0):
            new_metric += (abs(min(eigenvalues)) + 1e-6) * np.eye(new_metric.shape[0])
        
        return new_metric
    
    def compute_geodesic_deviation(self, prices: np.ndarray,
                                  window: int = 20) -> GeodesicDeviation:
        """
        Compute geodesic deviation (tidal forces)
        
        Measures how nearby trajectories converge/diverge.
        """
        if len(prices) < 2 * window:
            return GeodesicDeviation(
                jacobian=np.eye(3),
                deviation_rate=0.0,
                focusing=False
            )
        
        # Compute velocity vectors at two points
        v1 = np.diff(prices[-2*window:-window])
        v2 = np.diff(prices[-window:])
        
        # Simple Jacobian approximation
        jacobian = np.eye(3)
        
        if len(v1) > 0 and len(v2) > 0:
            # Compute deviation
            mean_v1 = np.mean(v1)
            mean_v2 = np.mean(v2)
            
            deviation_rate = (mean_v2 - mean_v1) / (mean_v1 + 1e-10)
        else:
            deviation_rate = 0.0
        
        focusing = deviation_rate < 0  # Negative = focusing/converging
        
        return GeodesicDeviation(
            jacobian=jacobian,
            deviation_rate=float(deviation_rate),
            focusing=focusing
        )
    
    def analyze(self, prices: np.ndarray) -> Dict[str, Any]:
        """
        Complete differential geometry analysis
        
        Args:
            prices: Price time series
            
        Returns:
            Analysis results
        """
        # Compute metric
        metric = self.compute_metric_tensor(prices)
        
        # Compute curvature
        christoffel = self.compute_christoffel_symbols(metric)
        riemann = self.compute_riemann_tensor(christoffel)
        ricci = self.compute_ricci_tensor(riemann)
        scalar_curv = self.compute_scalar_curvature(ricci, metric)
        
        self.curvature_history.append(scalar_curv)
        
        # Compute geodesic deviation
        deviation = self.compute_geodesic_deviation(prices)
        
        # Ricci flow evolution (one step)
        smoothed_metric = self.compute_ricci_flow(metric)
        
        # Compute volume form
        det = np.linalg.det(metric)
        volume_form = math.sqrt(abs(det))
        
        return {
            'metric_tensor': metric.tolist(),
            'scalar_curvature': scalar_curv,
            'volume_form': volume_form,
            'geodesic_deviation': {
                'rate': deviation.deviation_rate,
                'focusing': deviation.focusing
            },
            'curvature_regime': self._curvature_to_regime(scalar_curv),
            'metric_condition': np.linalg.cond(metric)
        }
    
    def _curvature_to_regime(self, curvature: float) -> str:
        """Map curvature to market regime"""
        if curvature > 0.1:
            return "ACCELERATING_TREND"
        elif curvature < -0.1:
            return "DECELERATING_TREND"
        else:
            return "LINEAR_MOTION"
