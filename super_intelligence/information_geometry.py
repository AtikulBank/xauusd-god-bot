"""
Engine 2: Information Geometry
Fisher-Rao Metric manifold for probability distributions

Computes geodesics on statistical manifolds to find optimal
parameter trajectories for market models.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class StatisticalManifold:
    """Point on a statistical manifold"""
    parameters: np.ndarray
    fisher_metric: np.ndarray
    curvature: float
    geodesic_distance: float


@dataclass
class GeodesicPath:
    """Geodesic path between two points on manifold"""
    start_point: np.ndarray
    end_point: np.ndarray
    path_points: List[np.ndarray]
    length: float
    christoffel_symbols: np.ndarray


class InformationGeometryEngine:
    """
    Information Geometry Engine
    
    Uses Fisher-Rao metric to compute distances between probability
    distributions representing market states.
    
    Geodesics on this manifold represent optimal parameter transitions
    for market regime changes.
    """
    
    def __init__(self, manifold_dim: int = 3):
        self.manifold_dim = manifold_dim
        self.metric_history: List[np.ndarray] = []
        self.curvature_history: List[float] = []
        
        # Natural gradient parameters
        self.learning_rate = 0.01
        self.metric_regularization = 1e-6
        
    def fisher_information_matrix(self, params: np.ndarray, 
                                 log_likelihood_grad: np.ndarray) -> np.ndarray:
        """
        Compute Fisher Information Matrix
        
        F_ij = E[∂log p(x|θ)/∂θ_i * ∂log p(x|θ)/∂θ_j]
        
        Args:
            params: Model parameters
            log_likelihood_grad: Gradient of log-likelihood
            
        Returns:
            Fisher Information Matrix
        """
        n_params = len(params)
        
        # For Gaussian market model, FIM has closed form
        # Simplified computation for demonstration
        fisher = np.zeros((n_params, n_params))
        
        for i in range(n_params):
            for j in range(n_params):
                fisher[i, j] = log_likelihood_grad[i] * log_likelihood_grad[j]
        
        # Add regularization for numerical stability
        fisher += self.metric_regularization * np.eye(n_params)
        
        return fisher
    
    def compute_fisher_metric(self, prices: np.ndarray, 
                             window: int = 50) -> np.ndarray:
        """
        Compute Fisher metric for market return distribution
        
        Models returns as mixture of Gaussians and computes
        information-geometric quantities.
        
        Args:
            prices: Price time series
            window: Window for local computation
            
        Returns:
            Fisher metric tensor
        """
        if len(prices) < window + 1:
            return np.eye(self.manifold_dim) * 0.01
        
        # Compute returns
        returns = np.diff(np.log(prices[-window-1:]))
        
        # Estimate parameters of return distribution
        mu = np.mean(returns)
        sigma = np.std(returns)
        skew = float(np.mean((returns - mu)**3)) / (sigma**3 + 1e-10)
        
        # Parameters: [mean, variance, skewness]
        params = np.array([mu, sigma**2, skew])
        
        # Compute score function (gradient of log-likelihood)
        score = self._compute_score(returns, params)
        
        # Fisher Information Matrix
        fisher = self.fisher_information_matrix(params, score)
        
        self.metric_history.append(fisher)
        
        return fisher
    
    def _compute_score(self, returns: np.ndarray, 
                      params: np.ndarray) -> np.ndarray:
        """
        Compute score function ∂log p(x|θ)/∂θ
        
        For skew-normal distribution (approximation)
        """
        mu, sigma_sq, skew = params
        sigma = np.sqrt(sigma_sq + 1e-10)
        
        n = len(returns)
        score = np.zeros(3)
        
        # Simplified score computation
        z = (returns - mu) / sigma
        
        # d/dmu
        score[0] = np.sum(z) / sigma
        
        # d/d(sigma^2)
        score[1] = np.sum(z**2 - 1) / (2 * sigma_sq)
        
        # d/dskew
        score[2] = np.sum(z**3 - 3*z) / (6 + 1e-10)
        
        return score / n
    
    def inverse_fisher_metric(self, fisher: np.ndarray) -> np.ndarray:
        """
        Compute inverse Fisher metric (natural gradient preconditioner)
        
        G^{-1} converts Euclidean gradients to natural gradients
        """
        try:
            return np.linalg.inv(fisher)
        except np.linalg.LinAlgError:
            return np.linalg.pinv(fisher)
    
    def compute_curvature(self, fisher: np.ndarray) -> float:
        """
        Compute scalar curvature of statistical manifold
        
        High curvature indicates rapid regime changes.
        """
        try:
            # Simplified curvature from metric determinant
            det = np.linalg.det(fisher)
            trace = np.trace(fisher)
            
            # Approximate curvature
            curvature = np.log(abs(det) + 1e-10) - np.log(trace + 1e-10)
            
            self.curvature_history.append(curvature)
            
            return float(curvature)
        except Exception as e:
            logger.warning(f"Curvature computation failed: {e}")
            return 0.0
    
    def geodesic_distance(self, fisher1: np.ndarray, 
                         fisher2: np.ndarray) -> float:
        """
        Compute geodesic distance between two points on statistical manifold
        
        Uses KL-divergence approximation for Fisher metric distance.
        """
        try:
            # Affine-invariant Riemannian metric
            # d(M1, M2) = ||log(M1^{-1/2} M2 M1^{-1/2})||_F
            
            inv_sqrt = self._matrix_sqrt_inv(fisher1)
            product = inv_sqrt @ fisher2 @ inv_sqrt
            
            # Matrix logarithm (approximation)
            log_product = self._matrix_log(product)
            
            # Frobenius norm
            distance = np.sqrt(np.sum(log_product**2))
            
            return float(distance)
        except Exception as e:
            logger.warning(f"Geodesic distance computation failed: {e}")
            return 0.0
    
    def _matrix_sqrt_inv(self, M: np.ndarray) -> np.ndarray:
        """Compute M^{-1/2}"""
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(M)
            eigenvalues = np.maximum(eigenvalues, 1e-10)
            sqrt_inv = eigenvectors @ np.diag(1.0 / np.sqrt(eigenvalues)) @ eigenvectors.T
            return sqrt_inv
        except Exception:
            return np.linalg.pinv(M)
    
    def _matrix_log(self, M: np.ndarray) -> np.ndarray:
        """Compute matrix logarithm (approximation via eigendecomposition)"""
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(M)
            eigenvalues = np.maximum(eigenvalues, 1e-10)
            log_eigenvalues = np.log(eigenvalues)
            return eigenvectors @ np.diag(log_eigenvalues) @ eigenvectors.T
        except Exception:
            return np.zeros_like(M)
    
    def natural_gradient(self, gradient: np.ndarray, 
                        fisher: np.ndarray) -> np.ndarray:
        """
        Compute natural gradient using Fisher information
        
        Natural gradient = G^{-1} * Euclidean gradient
        
        This follows the steepest ascent direction on the manifold.
        """
        inv_fisher = self.inverse_fisher_metric(fisher)
        return inv_fisher @ gradient
    
    def compute_geodesic(self, params_start: np.ndarray, 
                        params_end: np.ndarray,
                        n_steps: int = 20) -> GeodesicPath:
        """
        Compute geodesic path between two parameter points
        
        Uses simple Euler integration on the manifold.
        """
        path = [params_start.copy()]
        
        current = params_start.copy()
        step_size = 1.0 / n_steps
        
        for i in range(n_steps):
            # Direction towards endpoint
            direction = params_end - current
            
            # Update along geodesic
            current = current + step_size * direction
            path.append(current.copy())
        
        # Compute path length
        length = 0.0
        for i in range(len(path) - 1):
            length += np.linalg.norm(path[i+1] - path[i])
        
        return GeodesicPath(
            start_point=params_start,
            end_point=params_end,
            path_points=path,
            length=length,
            christoffel_symbols=np.zeros((self.manifold_dim, self.manifold_dim, self.manifold_dim))
        )
    
    def detect_regime_transition(self, prices: np.ndarray,
                               window: int = 50) -> Dict[str, Any]:
        """
        Detect regime transition using information geometry
        
        Sudden changes in curvature indicate regime transitions.
        """
        if len(prices) < 2 * window:
            return {
                'transition_detected': False,
                'curvature_change': 0.0,
                'confidence': 0.0
            }
        
        # Compute Fisher metric for two windows
        fisher_prev = self.compute_fisher_metric(prices[:-window], window)
        fisher_curr = self.compute_fisher_metric(prices[-window:], window)
        
        # Compute curvature for each
        curvature_prev = self.compute_curvature(fisher_prev)
        curvature_curr = self.compute_curvature(fisher_curr)
        
        # Compute change
        curvature_change = abs(curvature_curr - curvature_prev)
        
        # Compute geodesic distance
        geo_distance = self.geodesic_distance(fisher_prev, fisher_curr)
        
        # Transition detection
        threshold = 0.5
        transition_detected = curvature_change > threshold or geo_distance > 1.0
        
        # Confidence based on magnitude
        confidence = min(1.0, (curvature_change + geo_distance) / 2.0)
        
        return {
            'transition_detected': transition_detected,
            'curvature_change': curvature_change,
            'geodesic_distance': geo_distance,
            'curvature_prev': curvature_prev,
            'curvature_curr': curvature_curr,
            'confidence': confidence
        }
    
    def analyze(self, prices: np.ndarray) -> Dict[str, Any]:
        """
        Complete information geometry analysis
        
        Args:
            prices: Price time series
            
        Returns:
            Analysis results
        """
        # Compute current Fisher metric
        fisher = self.compute_fisher_metric(prices)
        
        # Compute curvature
        curvature = self.compute_curvature(fisher)
        
        # Detect regime transition
        transition = self.detect_regime_transition(prices)
        
        # Natural gradient for optimization
        # (would be used in training)
        dummy_gradient = np.ones(self.manifold_dim)
        natural_grad = self.natural_gradient(dummy_gradient, fisher)
        
        return {
            'fisher_metric': fisher.tolist(),
            'curvature': curvature,
            'manifold_volume': float(np.sqrt(np.linalg.det(fisher))),
            'regime_transition': transition,
            'natural_gradient_norm': float(np.linalg.norm(natural_grad))
        }


if __name__ == "__main__":
    # Test Information Geometry engine
    engine = InformationGeometryEngine()
    
    # Generate synthetic price data
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(200) * 0.5)
    
    print("Testing Information Geometry Engine...")
    result = engine.analyze(prices)
    
    print(f"Curvature: {result['curvature']:.4f}")
    print(f"Manifold Volume: {result['manifold_volume']:.4f}")
    print(f"Regime Transition Detected: {result['regime_transition']['transition_detected']}")
    print(f"Confidence: {result['regime_transition']['confidence']:.4f}")
