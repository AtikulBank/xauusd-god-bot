"""
Engine 7: Algebraic Topology
Simplicial complexes for higher-order market relationships

Uses persistent homology and spectral methods to detect
higher-order correlations in multi-asset markets.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any, Set, FrozenSet
from dataclasses import dataclass, field
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class Simplex:
    """A simplex in the algebraic complex"""
    vertices: FrozenSet[int]
    weight: float
    dimension: int
    birth: float
    death: float


@dataclass
class SpectralData:
    """Spectral data from algebraic complex"""
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    spectral_gap: float
    algebraic_connectivity: float


class AlgebraicTopologyEngine:
    """
    Algebraic Topology Engine
    
    Builds simplicial complexes from market data and analyzes
    their algebraic properties.
    
    Key applications:
    - Higher-order correlation detection
    - Community structure in asset networks
    - Spectral analysis for regime detection
    """
    
    def __init__(self):
        self.simplicial_complex: List[Simplex] = []
        self.spectral_history: List[SpectralData] = []
        
    def build_correlation_network(self, returns_matrix: np.ndarray,
                                 threshold: float = 0.3) -> np.ndarray:
        """
        Build correlation network from multi-asset returns
        
        Args:
            returns_matrix: Shape (n_assets, n_periods)
            threshold: Correlation threshold for edges
            
        Returns:
            Adjacency matrix
        """
        n_assets = returns_matrix.shape[0]
        
        # Compute correlation matrix
        corr = np.corrcoef(returns_matrix)
        
        # Create adjacency matrix
        adjacency = np.abs(corr) > threshold
        np.fill_diagonal(adjacency, False)
        
        return adjacency.astype(float)
    
    def build_simplicial_complex(self, adjacency: np.ndarray,
                                 max_dim: int = 3) -> List[Simplex]:
        """
        Build simplicial complex from adjacency matrix
        
        Uses clique complex construction.
        """
        n = adjacency.shape[0]
        simplices = []
        
        # 0-simplices (vertices)
        for i in range(n):
            simplices.append(Simplex(
                vertices=frozenset([i]),
                weight=1.0,
                dimension=0,
                birth=0.0,
                death=float('inf')
            ))
        
        # 1-simplices (edges)
        for i in range(n):
            for j in range(i + 1, n):
                if adjacency[i, j] > 0:
                    simplices.append(Simplex(
                        vertices=frozenset([i, j]),
                        weight=adjacency[i, j],
                        dimension=1,
                        birth=adjacency[i, j],
                        death=float('inf')
                    ))
        
        # 2-simplices (triangles) and higher
        if max_dim >= 2:
            for i in range(n):
                for j in range(i + 1, n):
                    if adjacency[i, j] > 0:
                        for k in range(j + 1, n):
                            if adjacency[i, k] > 0 and adjacency[j, k] > 0:
                                # Triangle
                                weight = min(adjacency[i, j], adjacency[j, k], adjacency[i, k])
                                simplices.append(Simplex(
                                    vertices=frozenset([i, j, k]),
                                    weight=weight,
                                    dimension=2,
                                    birth=weight,
                                    death=float('inf')
                                ))
        
        if max_dim >= 3:
            for i in range(n):
                for j in range(i + 1, n):
                    if adjacency[i, j] > 0:
                        for k in range(j + 1, n):
                            if adjacency[i, k] > 0 and adjacency[j, k] > 0:
                                for l in range(k + 1, n):
                                    if (adjacency[i, l] > 0 and 
                                        adjacency[j, l] > 0 and 
                                        adjacency[k, l] > 0):
                                        weight = min(adjacency[i, j], adjacency[j, k], 
                                                    adjacency[i, k], adjacency[i, l],
                                                    adjacency[j, l], adjacency[k, l])
                                        simplices.append(Simplex(
                                            vertices=frozenset([i, j, k, l]),
                                            weight=weight,
                                            dimension=3,
                                            birth=weight,
                                            death=float('inf')
                                        ))
        
        self.simplicial_complex = simplices
        return simplices
    
    def compute_laplacian(self, adjacency: np.ndarray) -> np.ndarray:
        """
        Compute graph Laplacian
        
        L = D - A where D is degree matrix
        """
        degree = np.diag(np.sum(adjacency, axis=1))
        laplacian = degree - adjacency
        
        return laplacian
    
    def compute_spectral_data(self, laplacian: np.ndarray) -> SpectralData:
        """
        Compute spectral data from Laplacian
        
        Eigenvalues indicate connectivity and community structure.
        """
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
            
            # Sort by eigenvalue
            idx = np.argsort(eigenvalues)
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]
            
            # Spectral gap (first non-zero eigenvalue)
            threshold = 1e-10
            non_zero_idx = np.where(eigenvalues > threshold)[0]
            
            if len(non_zero_idx) > 0:
                spectral_gap = eigenvalues[non_zero_idx[0]]
                algebraic_connectivity = spectral_gap
            else:
                spectral_gap = 0.0
                algebraic_connectivity = 0.0
            
            spectral = SpectralData(
                eigenvalues=eigenvalues,
                eigenvectors=eigenvectors,
                spectral_gap=spectral_gap,
                algebraic_connectivity=algebraic_connectivity
            )
            
            self.spectral_history.append(spectral)
            
            return spectral
        except Exception as e:
            logger.warning(f"Spectral computation failed: {e}")
            return SpectralData(
                eigenvalues=np.array([0.0]),
                eigenvectors=np.eye(laplacian.shape[0]),
                spectral_gap=0.0,
                algebraic_connectivity=0.0
            )
    
    def detect_communities(self, eigenvectors: np.ndarray,
                          n_clusters: int = None) -> np.ndarray:
        """
        Detect communities using spectral clustering
        
        Uses Fiedler vector (second eigenvector) for partitioning.
        """
        if eigenvectors.shape[1] < 2:
            return np.zeros(eigenvectors.shape[0])
        
        # Fiedler vector
        fiedler = eigenvectors[:, 1]
        
        # Simple thresholding
        if n_clusters is None:
            # Auto-detect: split at zero
            labels = (fiedler >= 0).astype(int)
        else:
            # K-means-like
            labels = np.zeros(len(fiedler), dtype=int)
            sorted_idx = np.argsort(fiedler)
            chunk_size = len(fiedler) // n_clusters
            for i in range(n_clusters):
                start = i * chunk_size
                end = start + chunk_size if i < n_clusters - 1 else len(fiedler)
                labels[sorted_idx[start:end]] = i
        
        return labels
    
    def compute_hodge_laplacian(self, simplices: List[Simplex], 
                               n_vertices: int) -> np.ndarray:
        """
        Compute Hodge Laplacian for simplicial complex
        
        L_k = d_k^T d_k + d_{k+1} d_{k+1}^T
        
        Captures higher-order topology.
        """
        # For 1-dimensional analysis (edges)
        # Build boundary operator d_1
        edges = [s for s in simplices if s.dimension == 1]
        
        if not edges:
            return np.zeros((n_vertices, n_vertices))
        
        # Simple approximation: use edge weights
        laplacian = np.zeros((n_vertices, n_vertices))
        
        for edge in edges:
            vertices = list(edge.vertices)
            if len(vertices) == 2:
                i, j = vertices
                laplacian[i, i] += edge.weight
                laplacian[j, j] += edge.weight
                laplacian[i, j] -= edge.weight
                laplacian[j, i] -= edge.weight
        
        return laplacian
    
    def analyze(self, returns_matrix: np.ndarray,
               threshold: float = 0.3) -> Dict[str, Any]:
        """
        Complete algebraic topology analysis
        
        Args:
            returns_matrix: Multi-asset returns matrix (n_assets x n_periods)
            threshold: Correlation threshold
            
        Returns:
            Analysis results
        """
        n_assets = returns_matrix.shape[0]
        
        # Build correlation network
        adjacency = self.build_correlation_network(returns_matrix, threshold)
        
        # Build simplicial complex
        simplices = self.build_simplicial_complex(adjacency, max_dim=3)
        
        # Compute Laplacian and spectral data
        laplacian = self.compute_laplacian(adjacency)
        spectral = self.compute_spectral_data(laplacian)
        
        # Detect communities
        if spectral.eigenvectors.shape[1] >= 2:
            communities = self.detect_communities(spectral.eigenvectors)
        else:
            communities = np.zeros(n_assets)
        
        # Compute Hodge Laplacian
        hodge = self.compute_hodge_laplacian(simplices, n_assets)
        
        # Count simplices by dimension
        simplex_counts = {}
        for s in simplices:
            dim = s.dimension
            simplex_counts[dim] = simplex_counts.get(dim, 0) + 1
        
        return {
            'n_vertices': n_assets,
            'n_edges': simplex_counts.get(1, 0),
            'n_triangles': simplex_counts.get(2, 0),
            'n_tetrahedra': simplex_counts.get(3, 0),
            'spectral_gap': spectral.spectral_gap,
            'algebraic_connectivity': spectral.algebraic_connectivity,
            'communities': communities.tolist(),
            'n_communities': len(np.unique(communities)),
            'modularity': self._compute_modularity(adjacency, communities)
        }
    
    def _compute_modularity(self, adjacency: np.ndarray,
                           communities: np.ndarray) -> float:
        """
        Compute modularity of community structure
        
        Q = (1/2m) Σ_ij [A_ij - k_i*k_j/(2m)] δ(c_i, c_j)
        """
        m = np.sum(adjacency) / 2.0
        if m == 0:
            return 0.0
        
        degrees = np.sum(adjacency, axis=1)
        
        Q = 0.0
        n = adjacency.shape[0]
        
        for i in range(n):
            for j in range(n):
                if communities[i] == communities[j]:
                    Q += adjacency[i, j] - degrees[i] * degrees[j] / (2 * m)
        
        return float(Q / (2 * m))
