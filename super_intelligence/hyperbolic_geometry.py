"""
Engine 4: Hyperbolic Geometry
Poincaré Ball model for hierarchical market structures

Embeds market data in hyperbolic space to capture tree-like
hierarchical relationships between assets and regimes.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class HyperbolicPoint:
    """Point in Poincaré Ball model"""
    coordinates: np.ndarray  # In Poincaré ball (|x| < 1)
    hyperbolic_norm: float
    projection_type: str  # 'radial', 'angular', 'mixed'


@dataclass
class HyperbolicEmbedding:
    """Complete hyperbolic embedding of market data"""
    points: List[HyperbolicPoint]
    curvature: float
    tree_depth: float
    hierarchy_score: float


class HyperbolicGeometryEngine:
    """
    Hyperbolic Geometry Engine
    
    Uses Poincaré Ball model to embed market data in hyperbolic space.
    
    Hyperbolic space is ideal for:
    - Hierarchical clustering of market regimes
    - Capturing tree-like structures in price action
    - Efficient embedding of high-dimensional data
    """
    
    def __init__(self, embedding_dim: int = 3, curvature: float = -1.0):
        self.embedding_dim = embedding_dim
        self.curvature = curvature  # Negative for hyperbolic
        
        # Poincaré ball radius (usually 1)
        self.ball_radius = 1.0 - 1e-5
        
        # Embedding history
        self.embeddings: List[HyperbolicEmbedding] = []
        
    def exponential_map(self, point: np.ndarray, 
                       tangent_vector: np.ndarray) -> np.ndarray:
        """
        Exponential map: maps tangent vector to Poincaré ball
        
        exp_x(v) = x ⊕ (tanh(||v||_x / (1-r²)^(1/2)) * v / ||v||_x)
        
        Args:
            point: Base point in Poincaré ball
            tangent_vector: Vector in tangent space
            
        Returns:
            Mapped point in Poincaré ball
        """
        # Norm in hyperbolic space
        lambda_x = 2.0 / (1.0 - np.sum(point**2))
        
        # Norm of tangent vector
        v_norm = np.linalg.norm(tangent_vector)
        
        if v_norm < 1e-10:
            return point.copy()
        
        # Scaling factor
        scale = np.tanh(lambda_x * v_norm * abs(self.curvature)**0.5) / v_norm
        
        # Mapped point
        mapped = point + scale * tangent_vector
        
        # Project back to ball if needed
        norm = np.linalg.norm(mapped)
        if norm >= self.ball_radius:
            mapped = mapped * (self.ball_radius / norm) * 0.99
        
        return mapped
    
    def logarithmic_map(self, point: np.ndarray,
                       target: np.ndarray) -> np.ndarray:
        """
        Logarithmic map: maps from Poincaré ball to tangent space
        
        log_x(y) = (2 / (λ_x * (1-||y||²))) * arctanh(||-x ⊕ y||) * (-x ⊕ y) / ||-x ⊕ y||
        """
        # Mobius addition: -x ⊕ y
        mobius = self._mobius_addition(-point, target)
        
        # Norm of Mobius result
        mobius_norm = np.linalg.norm(mobius)
        
        if mobius_norm < 1e-10:
            return np.zeros_like(point)
        
        # Lambda at point
        lambda_x = 2.0 / (1.0 - np.sum(point**2))
        
        # Tangent vector
        scale = (2.0 / (lambda_x * (1.0 - np.sum(target**2)))) * np.arctanh(mobius_norm)
        
        tangent = scale * mobius / mobius_norm
        
        return tangent
    
    def _mobius_addition(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Möbius addition in Poincaré ball
        
        x ⊕ y = ((1 + 2<x,y> + ||y||²)x + (1-||x||²)y) / (1 + 2<x,y> + ||x||²||y||²)
        """
        num = (1.0 + 2.0 * np.dot(x, y) + np.sum(y**2)) * x + \
              (1.0 - np.sum(x**2)) * y
        den = 1.0 + 2.0 * np.dot(x, y) + np.sum(x**2) * np.sum(y**2)
        
        return num / den
    
    def hyperbolic_distance(self, x: np.ndarray, y: np.ndarray) -> float:
        """
        Compute hyperbolic distance between two points
        
        d(x,y) = 2 * arctanh(||-x ⊕ y||) * |κ|^(-1/2)
        """
        # Mobius addition
        mobius = self._mobius_addition(-x, y)
        mobius_norm = np.linalg.norm(mobius)
        
        # Clamp for numerical stability
        mobius_norm = min(mobius_norm, 1.0 - 1e-10)
        
        # Hyperbolic distance
        distance = 2.0 * np.arctanh(mobius_norm) / abs(self.curvature)**0.5
        
        return float(distance)
    
    def embed_prices(self, prices: np.ndarray, 
                    window: int = 100) -> HyperbolicEmbedding:
        """
        Embed price data in hyperbolic space
        
        Uses Takens embedding followed by hyperbolic projection.
        """
        if len(prices) < window:
            window = len(prices)
        
        # Simple feature extraction
        features = []
        for i in range(len(prices) - window + 1):
            segment = prices[i:i+window]
            
            # Features: return, volatility, skewness, kurtosis
            returns = np.diff(np.log(segment + 1e-10))
            feat = np.array([
                np.mean(returns),
                np.std(returns),
                float(np.mean((returns - np.mean(returns))**3)) / (np.std(returns)**3 + 1e-10),
                float(np.mean((returns - np.mean(returns))**4)) / (np.std(returns)**4 + 1e-10) - 3
            ])
            features.append(feat)
        
        features = np.array(features)
        
        # Normalize features to [-1, 1]
        for j in range(features.shape[1]):
            col = features[:, j]
            min_val, max_val = np.min(col), np.max(col)
            if max_val > min_val:
                features[:, j] = 2.0 * (col - min_val) / (max_val - min_val) - 1.0
        
        # Project to Poincaré ball
        points = []
        for i in range(len(features)):
            # Initial projection (normalize to unit ball)
            feat = features[i]
            norm = np.linalg.norm(feat)
            
            if norm > 0:
                # Scale to ball radius
                point = feat / (norm + 1.0) * self.ball_radius * 0.9
            else:
                point = np.zeros(self.embedding_dim)
            
            # Pad or truncate to embedding_dim
            if len(point) < self.embedding_dim:
                point = np.pad(point, (0, self.embedding_dim - len(point)))
            else:
                point = point[:self.embedding_dim]
            
            hp = HyperbolicPoint(
                coordinates=point,
                hyperbolic_norm=np.linalg.norm(point),
                projection_type='radial'
            )
            points.append(hp)
        
        # Compute tree depth (how hierarchical)
        tree_depth = self._compute_tree_depth(points)
        
        # Compute hierarchy score
        hierarchy_score = self._compute_hierarchy_score(points)
        
        embedding = HyperbolicEmbedding(
            points=points,
            curvature=self.curvature,
            tree_depth=tree_depth,
            hierarchy_score=hierarchy_score
        )
        
        self.embeddings.append(embedding)
        
        return embedding
    
    def _compute_tree_depth(self, points: List[HyperbolicPoint]) -> float:
        """Compute effective tree depth of embedding"""
        if len(points) < 2:
            return 0.0
        
        # Compute pairwise distances
        distances = []
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                d = self.hyperbolic_distance(
                    points[i].coordinates, 
                    points[j].coordinates
                )
                distances.append(d)
        
        # Tree depth approximated by max distance / mean distance
        if len(distances) > 0:
            return max(distances) / (np.mean(distances) + 1e-10)
        
        return 1.0
    
    def _compute_hierarchy_score(self, points: List[HyperbolicPoint]) -> float:
        """
        Compute hierarchy score based on radial distribution
        
        Points closer to origin represent higher-level hierarchy.
        """
        norms = [p.hyperbolic_norm for p in points]
        
        if len(norms) < 2:
            return 0.5
        
        # Coefficient of variation of norms
        mean_norm = np.mean(norms)
        std_norm = np.std(norms)
        
        cv = std_norm / (mean_norm + 1e-10)
        
        # High CV indicates hierarchical structure
        return min(1.0, cv)
    
    def detect_hierarchy_changes(self, prices: np.ndarray,
                                window: int = 50) -> Dict[str, Any]:
        """
        Detect changes in market hierarchy structure
        
        Sudden changes in hierarchy indicate regime shifts.
        """
        if len(prices) < 2 * window:
            return {
                'hierarchy_change': False,
                'change_magnitude': 0.0,
                'confidence': 0.0
            }
        
        # Embed two windows
        embed_prev = self.embed_prices(prices[:-window], window)
        embed_curr = self.embed_prices(prices[-window:], window)
        
        # Compare hierarchy scores
        hierarchy_change = abs(embed_curr.hierarchy_score - embed_prev.hierarchy_score)
        
        # Compare tree depths
        depth_change = abs(embed_curr.tree_depth - embed_prev.tree_depth)
        
        # Combined change magnitude
        change_magnitude = (hierarchy_change + depth_change) / 2.0
        
        # Confidence
        confidence = min(1.0, change_magnitude * 2)
        
        return {
            'hierarchy_change': change_magnitude > 0.3,
            'hierarchy_prev': embed_prev.hierarchy_score,
            'hierarchy_curr': embed_curr.hierarchy_score,
            'tree_depth_prev': embed_prev.tree_depth,
            'tree_depth_curr': embed_curr.tree_depth,
            'change_magnitude': change_magnitude,
            'confidence': confidence
        }
    
    def predict_target(self, prices: np.ndarray) -> HyperbolicPoint:
        """
        Predict next price level using hyperbolic geodesics
        
        Finds optimal path in hyperbolic space to predict future.
        """
        embedding = self.embed_prices(prices)
        
        if len(embedding.points) < 2:
            return HyperbolicPoint(
                coordinates=np.zeros(self.embedding_dim),
                hyperbolic_norm=0.0,
                projection_type='prediction'
            )
        
        # Last two points
        p1 = embedding.points[-2].coordinates
        p2 = embedding.points[-1].coordinates
        
        # Compute tangent vector (direction of movement)
        tangent = self.logarithmic_map(p1, p2)
        
        # Extrapolate in tangent space
        future_tangent = tangent * 1.5  # 1.5x step
        
        # Map back to ball
        future_point = self.exponential_map(p2, future_tangent)
        
        return HyperbolicPoint(
            coordinates=future_point,
            hyperbolic_norm=np.linalg.norm(future_point),
            projection_type='prediction'
        )
    
    def analyze(self, prices: np.ndarray) -> Dict[str, Any]:
        """
        Complete hyperbolic geometry analysis
        
        Args:
            prices: Price time series
            
        Returns:
            Analysis results
        """
        # Embed prices
        embedding = self.embed_prices(prices)
        
        # Detect hierarchy changes
        hierarchy_change = self.detect_hierarchy_changes(prices)
        
        # Predict target
        target = self.predict_target(prices)
        
        # Compute overall hyperbolic complexity
        if embedding.points:
            norms = [p.hyperbolic_norm for p in embedding.points]
            complexity = np.std(norms) / (np.mean(norms) + 1e-10)
        else:
            complexity = 0.0
        
        return {
            'curvature': self.curvature,
            'n_points': len(embedding.points),
            'tree_depth': embedding.tree_depth,
            'hierarchy_score': embedding.hierarchy_score,
            'hierarchy_change': hierarchy_change,
            'hyperbolic_complexity': complexity,
            'prediction': {
                'coordinates': target.coordinates.tolist(),
                'norm': target.hyperbolic_norm
            }
        }


if __name__ == "__main__":
    # Test Hyperbolic Geometry engine
    engine = HyperbolicGeometryEngine()
    
    # Generate synthetic price data
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(200) * 0.5)
    
    print("Testing Hyperbolic Geometry Engine...")
    result = engine.analyze(prices)
    
    print(f"Curvature: {result['curvature']:.4f}")
    print(f"Tree Depth: {result['tree_depth']:.4f}")
    print(f"Hierarchy Score: {result['hierarchy_score']:.4f}")
    print(f"Hyperbolic Complexity: {result['hyperbolic_complexity']:.4f}")
    print(f"Hierarchy Change Detected: {result['hierarchy_change']['hierarchy_change']}")
