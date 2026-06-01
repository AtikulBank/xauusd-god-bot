"""
Engine 10: Measure Theory
Lebesgue integration for risk measure computation

Uses measure-theoretic foundations for robust risk measures
and probability distributions on market states.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class MeasureSpace:
    """Measure space for market states"""
    sigma_algebra: List[str]  # Measurable sets
    measure: Dict[str, float]  # Measure values
    total_measure: float
    support: np.ndarray


@dataclass
class RiskMeasure:
    """Coherent risk measure"""
    name: str
    value: float
    subadditive: bool
    monotone: bool
    translation_invariant: bool


class MeasureTheoryEngine:
    """
    Measure Theory Engine
    
    Provides rigorous mathematical foundation for:
    - Risk measures (VaR, CVaR, Expected Shortfall)
    - Probability measures on market states
    - Measure-theoretic integration for pricing
    
    Uses Lebesgue integration concepts for robust computation.
    """
    
    def __init__(self):
        self.measure_history: List[MeasureSpace] = []
        
    def create_empirical_measure(self, returns: np.ndarray,
                                n_bins: int = 20) -> MeasureSpace:
        """
        Create empirical probability measure from returns
        
        μ(A) = (1/n) Σ_i 1_A(x_i)
        """
        # Create bins
        hist, bin_edges = np.histogram(returns, bins=n_bins, density=True)
        
        # Normalize to probability measure
        bin_width = bin_edges[1] - bin_edges[0]
        probabilities = hist * bin_width
        
        # Ensure total measure = 1
        total = np.sum(probabilities)
        if total > 0:
            probabilities = probabilities / total
        
        # Create sigma algebra (intervals)
        sigma_algebra = [f"bin_{i}" for i in range(n_bins)]
        
        measure_dict = dict(zip(sigma_algebra, probabilities))
        
        # Support of measure
        support = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        space = MeasureSpace(
            sigma_algebra=sigma_algebra,
            measure=measure_dict,
            total_measure=1.0,
            support=support
        )
        
        self.measure_history.append(space)
        
        return space
    
    def lebesgue_integral(self, function: np.ndarray,
                         measure: MeasureSpace) -> float:
        """
        Compute Lebesgue integral of function with respect to measure
        
        ∫ f dμ = Σ_i f(x_i) μ({x_i})
        
        More robust than Riemann integral for discontinuous functions.
        """
        # Get function values at support points
        f_values = function[:len(measure.support)]
        
        # Get measures
        m_values = np.array([measure.measure.get(s, 0) for s in measure.sigma_algebra[:len(f_values)]])
        
        # Lebesgue integral
        integral = np.sum(f_values * m_values)
        
        return float(integral)
    
    def compute_var(self, returns: np.ndarray,
                   alpha: float = 0.05) -> RiskMeasure:
        """
        Compute Value at Risk (VaR)
        
        VaR_α = inf{x : P(X ≤ x) ≥ α}
        
        Note: VaR is NOT subadditive (not coherent).
        """
        var_value = np.percentile(returns, alpha * 100)
        
        return RiskMeasure(
            name=f"VaR_{alpha}",
            value=float(var_value),
            subadditive=False,
            monotone=True,
            translation_invariant=True
        )
    
    def compute_cvar(self, returns: np.ndarray,
                    alpha: float = 0.05) -> RiskMeasure:
        """
        Compute Conditional Value at Risk (CVaR) / Expected Shortfall
        
        CVaR_α = E[X | X ≤ VaR_α]
        
        CVaR IS subadditive (coherent risk measure).
        """
        var = np.percentile(returns, alpha * 100)
        
        # Expected value of returns below VaR
        tail_returns = returns[returns <= var]
        
        if len(tail_returns) > 0:
            cvar = np.mean(tail_returns)
        else:
            cvar = var
        
        return RiskMeasure(
            name=f"CVaR_{alpha}",
            value=float(cvar),
            subadditive=True,
            monotone=True,
            translation_invariant=True
        )
    
    def compute_spectral_risk_measure(self, returns: np.ndarray,
                                      risk_aversion: float = 2.0) -> float:
        """
        Compute spectral risk measure
        
        A_φ(E[X]) = -∫_0^1 φ(p) F_X^{-1}(p) dp
        
        Where φ is the risk aversion spectrum.
        """
        # Sort returns
        sorted_returns = np.sort(returns)
        n = len(sorted_returns)
        
        # Risk aversion spectrum (exponential weighting)
        p = np.linspace(0, 1, n)
        phi = np.exp(-risk_aversion * p)
        phi = phi / np.sum(phi)  # Normalize
        
        # Spectral risk measure
        srm = -np.sum(phi * sorted_returns)
        
        return float(srm)
    
    def compute_entropic_risk_measure(self, returns: np.ndarray,
                                     theta: float = 1.0) -> float:
        """
        Compute entropic risk measure
        
        ER_θ(X) = -(1/θ) log(E[e^{-θX}])
        """
        # Moment generating function
        mgf = np.mean(np.exp(-theta * returns))
        
        # Entropic risk
        erm = -(1.0 / theta) * np.log(mgf + 1e-10)
        
        return float(erm)
    
    def compute_wasserstein_distance(self, measure1: MeasureSpace,
                                    measure2: MeasureSpace) -> float:
        """
        Compute Wasserstein distance (Earth Mover's Distance) between measures
        
        W_1(μ, ν) = ∫ |F_μ(x) - F_ν(x)| dx
        """
        # Get support points
        support1 = measure1.support
        support2 = measure2.support
        
        # Create CDFs
        def create_cdf(support, measure_dict):
            cdf = np.zeros(len(support))
            cumsum = 0
            for i, s in enumerate(support):
                # Find measure for this point
                for key, val in measure_dict.items():
                    if isinstance(key, str) and key.startswith("bin_"):
                        bin_idx = int(key.split("_")[1])
                        if bin_idx == i:
                            cumsum += val
                            break
                cdf[i] = cumsum
            return cdf
        
        cdf1 = create_cdf(support1, measure1.measure)
        cdf2 = create_cdf(support2, measure2.measure)
        
        # Interpolate to common support
        common_support = np.linspace(
            max(support1[0], support2[0]),
            min(support1[-1], support2[-1]),
            100
        )
        
        cdf1_interp = np.interp(common_support, support1, cdf1)
        cdf2_interp = np.interp(common_support, support2, cdf2)
        
        # Wasserstein distance
        distance = np.trapz(np.abs(cdf1_interp - cdf2_interp), common_support)
        
        return float(abs(distance))
    
    def compute_risk_decomposition(self, returns: np.ndarray,
                                  positions: np.ndarray,
                                  alpha: float = 0.05) -> Dict[str, float]:
        """
        Compute additive risk decomposition
        
        Decomposes total risk into component contributions.
        """
        # Total CVaR
        total_cvar = self.compute_cvar(returns, alpha).value
        
        # Component contributions (simplified)
        n_components = len(positions)
        component_risks = {}
        
        for i in range(n_components):
            # Marginal contribution approximation
            if np.sum(positions) != 0:
                weight = positions[i] / np.sum(positions)
                component_risk = weight * total_cvar
            else:
                component_risk = 0.0
            
            component_risks[f"asset_{i}"] = float(component_risk)
        
        # Check additivity
        sum_components = sum(component_risks.values())
        
        return {
            'total_risk': float(total_cvar),
            'component_risks': component_risks,
            'additivity_error': abs(sum_components - total_cvar)
        }
    
    def analyze(self, returns: np.ndarray,
               alpha: float = 0.05) -> Dict[str, Any]:
        """
        Complete measure theory analysis
        
        Args:
            returns: Return series
            alpha: Confidence level for risk measures
            
        Returns:
            Analysis results
        """
        # Create empirical measure
        measure = self.create_empirical_measure(returns)
        
        # Compute various risk measures
        var = self.compute_var(returns, alpha)
        cvar = self.compute_cvar(returns, alpha)
        srm = self.compute_spectral_risk_measure(returns)
        erm = self.compute_entropic_risk_measure(returns)
        
        # Compute tail probability
        tail_prob = np.mean(returns <= var.value)
        
        # Kurtosis (tail heaviness)
        kurtosis = float(np.mean((returns - np.mean(returns))**4) / (np.std(returns)**4 + 1e-10) - 3)
        
        # Measure concentration
        concentration = np.max(measure.measure.values()) if measure.measure else 0.0
        
        return {
            'empirical_measure': {
                'n_bins': len(measure.sigma_algebra),
                'total_measure': measure.total_measure
            },
            'risk_measures': {
                'VaR': var.value,
                'CVaR': cvar.value,
                'spectral_risk': srm,
                'entropic_risk': erm
            },
            'tail_probability': tail_prob,
            'kurtosis': kurtosis,
            'measure_concentration': concentration,
            'risk_regime': self._classify_risk_regime(cvar.value, kurtosis)
        }
    
    def _classify_risk_regime(self, cvar: float, kurtosis: float) -> str:
        """Classify risk regime based on measures"""
        if cvar < -0.02 and kurtosis > 3:
            return "EXTREME_RISK"
        elif cvar < -0.01:
            return "HIGH_RISK"
        elif kurtosis > 3:
            return "TAIL_HEAVY"
        else:
            return "NORMAL"
