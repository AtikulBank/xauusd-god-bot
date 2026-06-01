"""
Engine 3: Quantum Entanglement Correlation
Simulates quantum correlations between market assets

Uses density matrices and Bell inequalities to detect
non-classical correlations in multi-asset markets.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class DensityMatrix:
    """Quantum density matrix for market state"""
    matrix: np.ndarray
    purity: float
    von_neumann_entropy: float
    entanglement_measure: float


@dataclass
class BellState:
    """Bell inequality test result"""
    s_value: float  # CHSH inequality S parameter
    classical_bound: float
    quantum_bound: float
    violation: bool
    entanglement_detected: bool


class QuantumEntanglementEngine:
    """
    Quantum Entanglement Correlation Engine
    
    Simulates quantum correlations between market assets using
    density matrices and Bell inequalities.
    
    Non-classical correlations indicate regime changes and
    hidden dependencies not captured by classical statistics.
    """
    
    def __init__(self, n_assets: int = 2):
        self.n_assets = n_assets
        self.density_matrices: List[DensityMatrix] = []
        self.bell_violations: List[BellState] = []
        
        # Quantum state parameters
        self.coherence_factor = 0.5
        self.entanglement_threshold = 0.3
        
    def create_density_matrix(self, returns1: np.ndarray, 
                             returns2: np.ndarray) -> DensityMatrix:
        """
        Create density matrix from correlated asset returns
        
        Maps classical correlations to quantum density matrix
        using Jordan-Wigner-like transformation.
        """
        n = len(returns1)
        if n != len(returns2) or n < 10:
            # Return identity matrix
            rho = np.eye(4) / 4
            return DensityMatrix(
                matrix=rho,
                purity=0.25,
                von_neumann_entropy=np.log(4),
                entanglement_measure=0.0
            )
        
        # Normalize returns
        r1 = (returns1 - np.mean(returns1)) / (np.std(returns1) + 1e-10)
        r2 = (returns2 - np.mean(returns2)) / (np.std(returns2) + 1e-10)
        
        # Compute classical correlation
        correlation = np.mean(r1 * r2)
        
        # Create density matrix for two-qubit system
        # |00>, |01>, |10>, |11> basis
        rho = np.zeros((4, 4))
        
        # Diagonal elements (populations)
        p00 = 0.25 * (1 + correlation)
        p11 = 0.25 * (1 + correlation)
        p01 = 0.25 * (1 - correlation)
        p10 = 0.25 * (1 - correlation)
        
        rho[0, 0] = p00
        rho[1, 1] = p01
        rho[2, 2] = p10
        rho[3, 3] = p11
        
        # Add off-diagonal elements (coherence/entanglement)
        coherence = self.coherence_factor * np.exp(-1.0 / (abs(correlation) + 0.1))
        
        # Bell state-like off-diagonal
        rho[0, 3] = coherence
        rho[3, 0] = coherence
        rho[1, 2] = coherence * 0.5
        rho[2, 1] = coherence * 0.5
        
        # Normalize
        trace = np.trace(rho)
        if trace > 0:
            rho = rho / trace
        
        # Compute purity
        purity = np.real(np.trace(rho @ rho))
        
        # Compute von Neumann entropy
        eigenvalues = np.linalg.eigvalsh(rho)
        eigenvalues = eigenvalues[eigenvalues > 0]
        vn_entropy = -np.sum(eigenvalues * np.log2(eigenvalues + 1e-10))
        
        # Compute entanglement measure (concurrence approximation)
        entanglement = self._compute_concurrence(rho)
        
        dm = DensityMatrix(
            matrix=rho,
            purity=purity,
            von_neumann_entropy=vn_entropy,
            entanglement_measure=entanglement
        )
        
        self.density_matrices.append(dm)
        
        return dm
    
    def _compute_concurrence(self, rho: np.ndarray) -> float:
        """
        Compute concurrence (entanglement measure) for two-qubit state
        
        Concurrence C = max(0, λ1 - λ2 - λ3 - λ4)
        where λi are eigenvalues of √(√ρ ρ̃ √ρ) in decreasing order
        """
        try:
            # Spin flip matrix
            sigma_y = np.array([[0, -1j], [1j, 0]])
            sigma_y_y = np.kron(sigma_y, sigma_y)
            
            # Tilde rho = (σy ⊗ σy) ρ* (σy ⊗ σy)
            rho_tilde = sigma_y_y @ np.conj(rho) @ sigma_y_y
            
            # Compute R = sqrt(sqrt(ρ) ρ̃ sqrt(ρ))
            sqrt_rho = self._matrix_sqrt(rho)
            R = sqrt_rho @ rho_tilde @ sqrt_rho
            sqrt_R = self._matrix_sqrt(R)
            
            # Eigenvalues
            eigenvalues = np.sort(np.real(np.linalg.eigvalsh(sqrt_R)))[::-1]
            
            # Concurrence
            concurrence = max(0, eigenvalues[0] - eigenvalues[1] - eigenvalues[2] - eigenvalues[3])
            
            return float(concurrence)
        except Exception:
            return 0.0
    
    def _matrix_sqrt(self, M: np.ndarray) -> np.ndarray:
        """Compute matrix square root"""
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(M)
            eigenvalues = np.maximum(eigenvalues, 0)
            sqrt_eigenvalues = np.sqrt(eigenvalues)
            return eigenvectors @ np.diag(sqrt_eigenvalues) @ eigenvectors.T
        except Exception:
            return np.eye(M.shape[0])
    
    def test_bell_inequality(self, returns1: np.ndarray,
                            returns2: np.ndarray) -> BellState:
        """
        Test CHSH Bell inequality for quantum correlations
        
        Classical bound: |S| ≤ 2
        Quantum bound (Tsirelson): |S| ≤ 2√2 ≈ 2.828
        """
        if len(returns1) < 50 or len(returns2) < 50:
            return BellState(
                s_value=0.0,
                classical_bound=2.0,
                quantum_bound=2.828,
                violation=False,
                entanglement_detected=False
            )
        
        # Create density matrix
        dm = self.create_density_matrix(returns1, returns2)
        rho = dm.matrix
        
        # Compute CHSH S parameter
        # S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
        
        # Measurement bases (optimized for S)
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
        
        def expectation(rho, angle1, angle2):
            """Compute correlation expectation value"""
            # Pauli matrices
            sigma_z = np.array([[1, 0], [0, -1]])
            sigma_x = np.array([[0, 1], [1, 0]])
            
            # Measurement operators
            A = np.cos(angle1) * sigma_z + np.sin(angle1) * sigma_x
            B = np.cos(angle2) * sigma_z + np.sin(angle2) * sigma_x
            
            A_full = np.kron(A, np.eye(2))
            B_full = np.kron(np.eye(2), B)
            
            return np.real(np.trace(rho @ A_full @ B_full))
        
        # Compute S with optimal angles
        E1 = expectation(rho, angles[0], angles[0])
        E2 = expectation(rho, angles[0], angles[1])
        E3 = expectation(rho, angles[2], angles[0])
        E4 = expectation(rho, angles[2], angles[1])
        
        S = E1 - E2 + E3 + E4
        
        # Check violation
        classical_bound = 2.0
        quantum_bound = 2 * np.sqrt(2)
        
        violation = abs(S) > classical_bound
        entanglement = violation or dm.entanglement_measure > self.entanglement_threshold
        
        bell_state = BellState(
            s_value=float(S),
            classical_bound=classical_bound,
            quantum_bound=quantum_bound,
            violation=violation,
            entanglement_detected=entanglement
        )
        
        self.bell_violations.append(bell_state)
        
        return bell_state
    
    def compute_quantum_mutual_information(self, rho: np.ndarray) -> float:
        """
        Compute quantum mutual information
        
        I(A:B) = S(ρA) + S(ρB) - S(ρAB)
        """
        try:
            # Reduced density matrices
            n = rho.shape[0]
            n_sys = int(np.sqrt(n))
            
            rho_A = np.trace(rho.reshape(n_sys, n_sys, n_sys, n_sys), axis1=1, axis2=3)
            rho_B = np.trace(rho.reshape(n_sys, n_sys, n_sys, n_sys), axis1=0, axis2=2)
            
            # Von Neumann entropies
            def vn_entropy(dm):
                eigenvalues = np.linalg.eigvalsh(dm)
                eigenvalues = eigenvalues[eigenvalues > 0]
                return -np.sum(eigenvalues * np.log2(eigenvalues + 1e-10))
            
            S_A = vn_entropy(rho_A)
            S_B = vn_entropy(rho_B)
            S_AB = vn_entropy(rho)
            
            mutual_info = S_A + S_B - S_AB
            
            return float(max(0, mutual_info))
        except Exception:
            return 0.0
    
    def detect_anomalous_correlation(self, returns1: np.ndarray,
                                    returns2: np.ndarray) -> Dict[str, Any]:
        """
        Detect anomalous (non-classical) correlations between assets
        
        Anomalous correlations often precede regime changes.
        """
        # Test Bell inequality
        bell = self.test_bell_inequality(returns1, returns2)
        
        # Create density matrix
        dm = self.create_density_matrix(returns1, returns2)
        
        # Compute quantum mutual information
        qmi = self.compute_quantum_mutual_information(dm.matrix)
        
        # Classical mutual information (for comparison)
        # Using binning approximation
        hist_2d, _, _ = np.histogram2d(returns1, returns2, bins=10)
        p_xy = hist_2d / np.sum(hist_2d)
        p_x = np.sum(p_xy, axis=1)
        p_y = np.sum(p_xy, axis=0)
        
        # Classical MI
        cmi = 0.0
        for i in range(len(p_x)):
            for j in range(len(p_y)):
                if p_xy[i, j] > 0 and p_x[i] > 0 and p_y[j] > 0:
                    cmi += p_xy[i, j] * np.log2(p_xy[i, j] / (p_x[i] * p_y[j]))
        
        # Quantum advantage
        quantum_advantage = max(0, qmi - cmi)
        
        return {
            'bell_s_value': bell.s_value,
            'bell_violation': bell.violation,
            'entanglement_detected': bell.entanglement_detected,
            'concurrence': dm.entanglement_measure,
            'purity': dm.purity,
            'von_neumann_entropy': dm.von_neumann_entropy,
            'quantum_mutual_info': qmi,
            'classical_mutual_info': cmi,
            'quantum_advantage': quantum_advantage,
            'anomaly_score': quantum_advantage + bell.s_value / 2.828
        }
    
    def analyze(self, prices1: np.ndarray,
               prices2: np.ndarray) -> Dict[str, Any]:
        """
        Complete quantum entanglement analysis on two price series
        
        Args:
            prices1: First price series
            prices2: Second price series
            
        Returns:
            Analysis results
        """
        # Compute returns
        returns1 = np.diff(np.log(prices1 + 1e-10))
        returns2 = np.diff(np.log(prices2 + 1e-10))
        
        # Detect anomalous correlations
        result = self.detect_anomalous_correlation(returns1, returns2)
        
        # Add regime indicator
        if result['entanglement_detected']:
            result['regime'] = "ENTANGLED_REGIME"
        elif result['anomaly_score'] > 0.5:
            result['regime'] = "ANOMALOUS_CORRELATION"
        else:
            result['regime'] = "CLASSICAL_REGIME"
        
        return result


if __name__ == "__main__":
    # Test Quantum Entanglement engine
    engine = QuantumEntanglementEngine()
    
    # Generate correlated price data
    np.random.seed(42)
    t = np.linspace(0, 100, 200)
    
    # Create correlated returns
    base = np.random.randn(200) * 0.5
    noise1 = np.random.randn(200) * 0.2
    noise2 = np.random.randn(200) * 0.2
    
    returns1 = base + noise1
    returns2 = 0.7 * base + 0.3 * np.random.randn(200) * 0.5 + noise2
    
    prices1 = 100 + np.cumsum(returns1)
    prices2 = 100 + np.cumsum(returns2)
    
    print("Testing Quantum Entanglement Engine...")
    result = engine.analyze(prices1, prices2)
    
    print(f"Bell S-value: {result['bell_s_value']:.4f}")
    print(f"Bell Violation: {result['bell_violation']}")
    print(f"Entanglement Detected: {result['entanglement_detected']}")
    print(f"Concurrence: {result['concurrence']:.4f}")
    print(f"Quantum Mutual Info: {result['quantum_mutual_info']:.4f}")
    print(f"Classical Mutual Info: {result['classical_mutual_info']:.4f}")
    print(f"Quantum Advantage: {result['quantum_advantage']:.4f}")
    print(f"Regime: {result['regime']}")
