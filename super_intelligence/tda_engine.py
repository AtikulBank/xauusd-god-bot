"""
Engine 1: Topological Data Analysis (TDA)
Persistent Homology for multi-dimensional holes in financial geometry

Detects topological features before volatile breakouts using
Vietoris-Rips complex and persistent homology.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass, field
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class Simplex:
    """A simplex in the Vietoris-Rips complex"""
    vertices: Tuple[int, ...]
    birth: float
    death: float
    dimension: int


@dataclass
class PersistenceBar:
    """A bar in the persistence diagram"""
    birth: float
    death: float
    dimension: int
    persistence: float


@dataclass
class TopologicalFeature:
    """Extracted topological feature from market data"""
    feature_id: str
    betti_number: int
    persistence: float
    stability: float
    regime_indicator: str
    breakout_probability: float


class TopologicalDataAnalysisEngine:
    """
    Topological Data Analysis Engine
    
    Uses Persistent Homology to detect multi-dimensional holes
    in financial geometry before volatile breakouts.
    
    Implements Vietoris-Rips complex construction and
    persistence diagram computation for regime detection.
    """
    
    def __init__(self, embedding_dim: int = 3, max_edge_length: float = 1.0):
        self.embedding_dim = embedding_dim
        self.max_edge_length = max_edge_length
        self.persistence_threshold = 0.1
        
        # State tracking
        self.price_history: List[float] = []
        self.volume_history: List[float] = []
        self.embeddings: List[np.ndarray] = []
        self.persistence_diagrams: List[List[PersistenceBar]] = []
        
        # Betti number history for regime detection
        self.betti_history: List[Dict[int, int]] = []
        
    def takens_embedding(self, prices: np.ndarray, 
                        embedding_dim: int = None, 
                        time_delay: int = None) -> np.ndarray:
        """
        Takens' Embedding Theorem for phase space reconstruction
        
        Maps 1D price series into higher-dimensional embedding
        that preserves topological properties.
        
        Args:
            prices: 1D price array
            embedding_dim: Dimension of embedding (default: self.embedding_dim)
            time_delay: Time delay between coordinates (default: auto)
            
        Returns:
            Embedding matrix of shape (n_points, embedding_dim)
        """
        if embedding_dim is None:
            embedding_dim = self.embedding_dim
            
        if time_delay is None:
            # Auto-select time delay using first minimum of AMI
            time_delay = self._estimate_time_delay(prices)
        
        n = len(prices)
        n_points = n - (embedding_dim - 1) * time_delay
        
        if n_points <= 0:
            return np.zeros((1, embedding_dim))
        
        embedding = np.zeros((n_points, embedding_dim))
        
        for i in range(embedding_dim):
            embedding[:, i] = prices[i * time_delay: i * time_delay + n_points]
        
        return embedding
    
    def _estimate_time_delay(self, prices: np.ndarray) -> int:
        """Estimate optimal time delay using first minimum of AMI"""
        if len(prices) < 50:
            return 1
        
        # Compute autocorrelation
        autocorr = np.correlate(prices - np.mean(prices), 
                               prices - np.mean(prices), mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0]
        
        # Find first zero crossing
        for i in range(1, len(autocorr)):
            if autocorr[i] < 0:
                return i
        
        return min(10, len(prices) // 10)
    
    def compute_distance_matrix(self, points: np.ndarray) -> np.ndarray:
        """
        Compute pairwise Euclidean distance matrix
        
        Args:
            points: Point cloud of shape (n_points, dimensions)
            
        Returns:
            Distance matrix of shape (n_points, n_points)
        """
        n = points.shape[0]
        dist_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(points[i] - points[j])
                dist_matrix[i, j] = dist
                dist_matrix[j, i] = dist
        
        return dist_matrix
    
    def build_vietoris_rips(self, distance_matrix: np.ndarray, 
                           epsilon: float) -> List[Tuple[int, ...]]:
        """
        Build Vietoris-Rips complex at given scale
        
        Args:
            distance_matrix: Pairwise distance matrix
            epsilon: Scale parameter
            
        Returns:
            List of simplices (as tuples of vertex indices)
        """
        n = distance_matrix.shape[0]
        simplices = []
        
        # 0-simplices (vertices)
        for i in range(n):
            simplices.append((i,))
        
        # 1-simplices (edges)
        for i in range(n):
            for j in range(i + 1, n):
                if distance_matrix[i, j] <= epsilon:
                    simplices.append((i, j))
        
        # 2-simplices (triangles)
        for i in range(n):
            for j in range(i + 1, n):
                if distance_matrix[i, j] <= epsilon:
                    for k in range(j + 1, n):
                        if (distance_matrix[i, k] <= epsilon and 
                            distance_matrix[j, k] <= epsilon):
                            simplices.append((i, j, k))
        
        # 3-simplices (tetrahedra) - optional, for higher-dimensional features
        if self.embedding_dim >= 3:
            for i in range(n):
                for j in range(i + 1, n):
                    if distance_matrix[i, j] <= epsilon:
                        for k in range(j + 1, n):
                            if distance_matrix[i, k] <= epsilon and distance_matrix[j, k] <= epsilon:
                                for l in range(k + 1, n):
                                    if (distance_matrix[i, l] <= epsilon and
                                        distance_matrix[j, l] <= epsilon and
                                        distance_matrix[k, l] <= epsilon):
                                        simplices.append((i, j, k, l))
        
        return simplices
    
    def compute_persistence(self, prices: np.ndarray, 
                           volumes: np.ndarray = None) -> List[PersistenceBar]:
        """
        Compute persistence diagram from price data
        
        Args:
            prices: Price time series
            volumes: Optional volume data for weighting
            
        Returns:
            List of persistence bars
        """
        if len(prices) < 50:
            return []
        
        # Compute Takens embedding
        embedding = self.takens_embedding(prices)
        
        if embedding.shape[0] < 10:
            return []
        
        # Compute distance matrix
        dist_matrix = self.compute_distance_matrix(embedding)
        
        # Compute persistence using persistent homology
        bars = []
        
        # Get all unique distances
        unique_distances = np.unique(dist_matrix[dist_matrix > 0])
        
        # Track component births and deaths
        n_points = embedding.shape[0]
        components = {i: i for i in range(n_points)}  # Union-Find
        component_birth = {i: 0.0 for i in range(n_points)}
        
        # Simple persistent homology for H0 and H1
        edge_births = {}
        
        for epsilon in np.sort(unique_distances):
            # Find new edges at this scale
            for i in range(n_points):
                for j in range(i + 1, n_points):
                    if dist_matrix[i, j] == epsilon:
                        # Check if vertices are in different components
                        root_i = self._find_root(components, i)
                        root_j = self._find_root(components, j)
                        
                        if root_i != root_j:
                            # Edge connects different components -> H0 bar dies
                            birth = component_birth[root_i]
                            death = epsilon
                            persistence = death - birth
                            
                            if persistence > self.persistence_threshold:
                                bars.append(PersistenceBar(
                                    birth=birth,
                                    death=death,
                                    dimension=0,
                                    persistence=persistence
                                ))
                            
                            # Merge components
                            components[root_j] = root_i
                            component_birth[root_i] = min(
                                component_birth[root_i], 
                                component_birth[root_j]
                            )
                        else:
                            # Edge within component -> potential H1 cycle
                            if (i, j) not in edge_births:
                                edge_births[(i, j)] = epsilon
            
            # Detect H1 cycles (simplified)
            if epsilon > 0.1:
                # Count triangles with all edges present
                triangles = self._count_holes(dist_matrix, epsilon)
                for _ in range(triangles):
                    bars.append(PersistenceBar(
                        birth=epsilon * 0.5,
                        death=epsilon,
                        dimension=1,
                        persistence=epsilon * 0.5
                    ))
        
        # Add remaining H0 bars
        unique_roots = set(self._find_root(components, i) for i in range(n_points))
        for root in unique_roots:
            bars.append(PersistenceBar(
                birth=component_birth[root],
                death=float('inf'),
                dimension=0,
                persistence=float('inf')
            ))
        
        self.persistence_diagrams.append(bars)
        return bars
    
    def _find_root(self, components: Dict[int, int], x: int) -> int:
        """Find root of element in Union-Find"""
        while components[x] != x:
            components[x] = components[components[x]]  # Path compression
            x = components[x]
        return x
    
    def _count_holes(self, dist_matrix: np.ndarray, epsilon: float) -> int:
        """Count number of H1 holes at given scale"""
        n = dist_matrix.shape[0]
        edge_count = np.sum(dist_matrix <= epsilon) - n
        triangle_count = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                if dist_matrix[i, j] <= epsilon:
                    for k in range(j + 1, n):
                        if (dist_matrix[i, k] <= epsilon and 
                            dist_matrix[j, k] <= epsilon):
                            triangle_count += 1
        
        # Euler characteristic: V - E + F = 1 - b0 + b1
        # Approximate b1 from Euler characteristic
        euler = n - edge_count + triangle_count
        b0 = 1  # Connected component
        b1 = 1 - euler + b0
        
        return max(0, b1)
    
    def compute_betti_numbers(self, bars: List[PersistenceBar]) -> Dict[int, int]:
        """
        Compute Betti numbers from persistence diagram
        
        Betti numbers count topological features:
        - b0: number of connected components
        - b1: number of 1-dimensional holes (cycles)
        - b2: number of 2-dimensional voids
        """
        betti = {0: 0, 1: 0, 2: 0}
        
        for bar in bars:
            if bar.death == float('inf') or bar.persistence > self.persistence_threshold:
                betti[bar.dimension] = betti.get(bar.dimension, 0) + 1
        
        # At least one connected component
        if betti[0] == 0:
            betti[0] = 1
        
        return betti
    
    def detect_regime(self, betti: Dict[int, int], 
                     persistence: float) -> str:
        """
        Detect market regime from topological features
        
        Args:
            betti: Betti numbers
            persistence: Average persistence
            
        Returns:
            Regime string
        """
        b0 = betti.get(0, 1)
        b1 = betti.get(1, 0)
        
        # High b1 with high persistence -> trending with cycles
        if b1 > 2 and persistence > 0.3:
            return "TRENDING_CYCLIC"
        
        # Low b1, low persistence -> ranging/chaotic
        elif b1 <= 1 and persistence < 0.2:
            return "RANGING_CHAOTIC"
        
        # Medium b1 -> transitioning
        elif b1 > 1:
            return "TRANSITIONING"
        
        else:
            return "STABLE"
    
    def predict_breakout(self, prices: np.ndarray, 
                        volumes: np.ndarray = None) -> TopologicalFeature:
        """
        Predict breakout probability based on topological complexity
        
        High topological complexity (many persistent features) often
        precedes volatile breakouts.
        
        Args:
            prices: Price time series
            volumes: Optional volume data
            
        Returns:
            TopologicalFeature with breakout prediction
        """
        # Compute persistence
        bars = self.compute_persistence(prices, volumes)
        
        # Compute Betti numbers
        betti = self.compute_betti_numbers(bars)
        
        # Compute average persistence
        finite_bars = [b for b in bars if b.death != float('inf')]
        avg_persistence = np.mean([b.persistence for b in finite_bars]) if finite_bars else 0.0
        
        # Compute stability (ratio of persistent to total features)
        total_features = len(bars)
        persistent_features = len([b for b in finite_bars if b.persistence > self.persistence_threshold])
        stability = persistent_features / max(1, total_features)
        
        # Detect regime
        regime = self.detect_regime(betti, avg_persistence)
        
        # Breakout probability based on:
        # 1. High H1 count (many cycles building)
        # 2. Increasing persistence over time
        # 3. Low stability (imminent change)
        breakout_prob = 0.0
        
        # Factor 1: H1 complexity
        breakout_prob += 0.3 * min(1.0, betti.get(1, 0) / 3.0)
        
        # Factor 2: Persistence
        breakout_prob += 0.3 * min(1.0, avg_persistence / 0.5)
        
        # Factor 3: Instability
        breakout_prob += 0.2 * (1.0 - stability)
        
        # Factor 4: Regime transition
        if regime == "TRANSITIONING":
            breakout_prob += 0.2
        
        # Update history
        self.betti_history.append(betti)
        if len(self.betti_history) > 100:
            self.betti_history = self.betti_history[-100:]
        
        return TopologicalFeature(
            feature_id=f"TDA_{len(self.persistence_diagrams)}",
            betti_number=betti.get(1, 0),
            persistence=avg_persistence,
            stability=stability,
            regime_indicator=regime,
            breakout_probability=min(1.0, breakout_prob)
        )
    
    def analyze(self, prices: np.ndarray, 
               volumes: np.ndarray = None) -> Dict[str, Any]:
        """
        Complete TDA analysis on price data
        
        Args:
            prices: Price time series
            volumes: Optional volume data
            
        Returns:
            Dictionary with all analysis results
        """
        feature = self.predict_breakout(prices, volumes)
        
        # Get persistence diagram summary
        bars = self.persistence_diagrams[-1] if self.persistence_diagrams else []
        
        return {
            'betti_numbers': self.compute_betti_numbers(bars),
            'avg_persistence': feature.persistence,
            'stability': feature.stability,
            'regime': feature.regime_indicator,
            'breakout_probability': feature.breakout_probability,
            'n_features': len(bars),
            'h1_count': feature.betti_number
        }


if __name__ == "__main__":
    # Test TDA engine
    engine = TopologicalDataAnalysisEngine()
    
    # Generate synthetic price data
    np.random.seed(42)
    t = np.linspace(0, 100, 500)
    prices = 100 + 10 * np.sin(0.1 * t) + np.cumsum(np.random.randn(500) * 0.5)
    
    print("Testing TDA Engine...")
    result = engine.analyze(prices)
    
    print(f"Betti Numbers: {result['betti_numbers']}")
    print(f"Average Persistence: {result['avg_persistence']:.4f}")
    print(f"Stability: {result['stability']:.4f}")
    print(f"Regime: {result['regime']}")
    print(f"Breakout Probability: {result['breakout_probability']:.4f}")
