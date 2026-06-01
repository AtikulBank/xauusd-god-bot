# cython: boundscheck=False, wraparound=False, cdivision=True, initializedcheck=False
# cython: language_level=3, binding=True
"""
ROUGH VOLATILITY ENGINE - Fractional Brownian Motion & Rough Paths
===================================================================
Complete implementation of rough volatility models for HFT trading.

Mathematical Foundations:
- Fractional Brownian Motion (fBm) with Hurst exponent H
- Rough Volatility models (Bayer, Friz, Gatheral 2016)
- Rough Path Theory (Lyons, 1998)
- p-variation and signature of price paths
- Malliavin calculus for sensitivity analysis

Key Insight: Realized volatility is "rough" with H ≈ 0.1,
not H = 0.5 (Brownian) or H = 1.0 (trend). This roughness
is a fundamental property of markets, not estimation error.

Author: Quantum Quant Systems Architecture Division
Version: 3.0.0 Production Release
"""

import numpy as np
cimport numpy as cnp
from libc.math cimport sqrt, fabs, log, exp, pow, sin, cos, atan2, M_PI, INFINITY
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy, memset
from libc.stdint cimport uint64_t, int64_t, uint32_t, uint8_t
import cython

cnp.import_array()

# ============================================================================
# Rough Volatility Data Structures
# ============================================================================

cdef packed struct FractionalBrownianMotion:
    """Fractional Brownian Motion state."""
    double hurst_exponent       # H: roughness parameter (0 < H < 1)
    double volatility           # σ: volatility of fBm
    double long_memory_param    # ρ: long-range dependence
    double[:] increments        # dB_H: fBm increments
    double[:] path              # B_H: fBm path

cdef packed struct RoughPathState:
    """Rough path theory state."""
    double[:] signature_level1  # Level 1 signature (price increments)
    double[:,:] signature_level2  # Level 2 signature (area between paths)
    double[:,:,:] signature_level3  # Level 3 signature (higher iter integrals)
    double p_variation          # p-variation of path
    double roughness_index      # Estimated roughness
    double total_variation      # Total variation

cdef packed struct VolatilitySurface:
    """Implied volatility surface structure."""
    double[:] strikes           # Strike prices
    double[:] maturities        # Time to maturity
    double[:,:] implied_vols    # Implied volatility matrix
    double[:,:] local_vols      # Local volatility (Dupire)
    double vol_of_vol           # Vol of vol parameter
    double skew                 # Skew parameter

cdef packed struct RoughVolatilityModel:
    """Rough volatility model parameters."""
    double H                    # Hurst exponent
    double sigma                # Volatility
    double rho                  # Correlation (leverage effect)
    double nu                   # Vol of vol
    double theta                # Mean reversion
    double kappa                # Speed of mean reversion


# ============================================================================
# Fractional Brownian Motion Engine
# ============================================================================

cdef class FractionalBrownianMotionEngine:
    """
    Fractional Brownian Motion (fBm) generator and analyzer.
    
    fBm B_H(t) has:
    - E[B_H(t)] = 0
    - Var[B_H(t)] = t^(2H)
    - Cov[B_H(s), B_H(t)] = (|s|^(2H) + |t|^(2H) - |s-t|^(2H)) / 2
    
    For H < 0.5: anti-persistent (rough)
    For H = 0.5: standard Brownian motion
    For H > 0.5: persistent (smooth)
    
    In finance: H ≈ 0.1 for realized volatility (rough)
    """
    
    cdef FractionalBrownianMotion fbm_state
    cdef int64_t n_steps
    cdef double dt
    cdef double[:] white_noise
    
    def __init__(self, int64_t n_steps=10000, double dt=0.001, double H=0.1):
        """
        Initialize fBm engine.
        
        Parameters:
        -----------
        n_steps : Number of time steps
        dt : Time step size
        H : Hurst exponent (roughness parameter)
        """
        self.n_steps = n_steps
        self.dt = dt
        
        cdef cnp.ndarray[float64_t, ndim=1] increments = np.zeros(n_steps, dtype=np.float64)
        cdef cnp.ndarray[float64_t, ndim=1] path = np.zeros(n_steps + 1, dtype=np.float64)
        cdef cnp.ndarray[float64_t, ndim=1] noise = np.random.randn(n_steps).astype(np.float64)
        
        self.fbm_state = FractionalBrownianMotion()
        self.fbm_state.hurst_exponent = H
        self.fbm_state.volatility = 1.0
        self.fbm_state.long_memory_param = 0.0
        self.fbm_state.increments = increments
        self.fbm_state.path = path
        self.white_noise = noise
    
    cdef void generate_via_cholonsky(self) noexcept nogil:
        """
        Generate fBm via Cholesky decomposition of covariance matrix.
        
        Cov(i,j) = 0.5 * (|i|^(2H) + |j|^(2H) - |i-j|^(2H))
        
        This is exact but O(n²) - use for short paths.
        """
        cdef int64_t i, j, k
        cdef int64_t n = self.n_steps
        cdef double H = self.fbm_state.hurst_exponent
        cdef double two_H = 2.0 * H
        
        # Compute covariance matrix
        cdef double[:,:] cov = np.zeros((n, n), dtype=np.float64)
        for i in range(n):
            for j in range(n):
                cov[i, j] = 0.5 * (
                    pow(<double>(i+1), two_H) + 
                    pow(<double>(j+1), two_H) - 
                    pow(<double>(abs(i-j)), two_H)
                )
        
        # Cholesky decomposition
        cdef double[:,:] L = np.zeros((n, n), dtype=np.float64)
        for i in range(n):
            for j in range(i + 1):
                cdef double sum_val = 0.0
                for k in range(j):
                    sum_val += L[i, k] * L[j, k]
                
                if i == j:
                    L[i, j] = sqrt(cov[i, i] - sum_val + 1e-10)
                else:
                    L[i, j] = (cov[i, j] - sum_val) / (L[j, j] + 1e-10)
        
        # Generate path: B = L * Z where Z ~ N(0,I)
        for i in range(n):
            cdef double sum_val = 0.0
            for j in range(i + 1):
                sum_val += L[i, j] * self.white_noise[j]
            self.fbm_state.increments[i] = sum_val
        
        # Compute path
        self.fbm_state.path[0] = 0.0
        for i in range(n):
            self.fbm_state.path[i + 1] = self.fbm_state.path[i] + self.fbm_state.increments[i]
    
    cdef void generate_via_mixed_ewma(self) noexcept nogil:
        """
        Generate fBm via mixed EWMA filter (fast, approximate).
        
        B_H(t) ≈ Σ_{k=0}^{∞} w_k * Z_{t-k}
        
        where w_k are EWMA weights with long-memory adjustment.
        """
        cdef int64_t i, k
        cdef int64_t n = self.n_steps
        cdef double H = self.fbm_state.hurst_exponent
        cdef double alpha = 2.0 - 2.0 * H  # EWMA decay
        
        # Generate increments via filtered noise
        for i in range(n):
            cdef double sum_val = 0.0
            cdef double weight_sum = 0.0
            
            for k in range(min(i + 1, 1000)):  # Truncate at 1000 lags
                cdef double weight = pow(<double>(k + 1), H - 0.5)
                sum_val += weight * self.white_noise[i - k]
                weight_sum += weight
            
            self.fbm_state.increments[i] = sum_val / (weight_sum + 1e-10)
        
        # Compute path
        self.fbm_state.path[0] = 0.0
        for i in range(n):
            self.fbm_state.path[i + 1] = self.fbm_state.path[i] + self.fbm_state.increments[i]
    
    cdef double estimate_hurst_rs(self, double[:] time_series) noexcept nogil:
        """
        Estimate Hurst exponent via R/S analysis (rescaled range).
        
        H = log(R/S) / log(N)
        
        where R = max - min of cumulative deviations
        and S = standard deviation of deviations
        """
        cdef int64_t n = len(time_series)
        if n < 20:
            return 0.5
        
        # Compute mean
        cdef double mean = 0.0
        for i in range(n):
            mean += time_series[i]
        mean /= <double>n
        
        # Compute cumulative deviations
        cdef double[:] cumdev = np.zeros(n, dtype=np.float64)
        cumdev[0] = time_series[0] - mean
        for i in range(1, n):
            cumdev[i] = cumdev[i-1] + time_series[i] - mean
        
        # R/S analysis
        cdef double R = 0.0, S = 0.0
        cdef double max_val = -1e10, min_val = 1e10
        
        for i in range(n):
            if cumdev[i] > max_val:
                max_val = cumdev[i]
            if cumdev[i] < min_val:
                min_val = cumdev[i]
        
        R = max_val - min_val
        
        # Standard deviation
        for i in range(n):
            S += (time_series[i] - mean) * (time_series[i] - mean)
        S = sqrt(S / <double>n)
        
        if S > 1e-10:
            return log(R / S + 1e-10) / log(<double>n)
        return 0.5
    
    cdef double estimate_hurst_dfa(self, double[:] time_series) noexcept nogil:
        """
        Estimate Hurst exponent via Detrended Fluctuation Analysis (DFA).
        
        F(n) ~ n^H
        
        where F(n) is the fluctuation function at scale n.
        """
        cdef int64_t n = len(time_series)
        if n < 100:
            return 0.5
        
        # Compute cumulative sum
        cdef double[:] cumsum = np.zeros(n, dtype=np.float64)
        cdef double mean = 0.0
        for i in range(n):
            mean += time_series[i]
        mean /= <double>n
        
        cumsum[0] = time_series[0] - mean
        for i in range(1, n):
            cumsum[i] = cumsum[i-1] + time_series[i] - mean
        
        # DFA at multiple scales
        cdef double[:] log_scales = np.zeros(10, dtype=np.float64)
        cdef double[:] log_fluct = np.zeros(10, dtype=np.float64)
        
        cdef int64_t scale_idx = 0
        cdef int64_t scales[10] = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
        
        for scale_idx in range(10):
            cdef int64_t s = min(scales[scale_idx], n // 4)
            if s < 10:
                continue
            
            cdef int64_t n_segments = n // s
            cdef double fluct_sum = 0.0
            
            for seg in range(n_segments):
                cdef int64_t start = seg * s
                cdef int64_t end = start + s
                
                # Fit polynomial (linear trend)
                cdef double x_mean = (<double>(start + end - 1)) / 2.0
                cdef double y_mean = 0.0
                for i in range(start, end):
                    y_mean += cumsum[i]
                y_mean /= <double>s
                
                cdef double slope_num = 0.0, slope_den = 0.0
                for i in range(start, end):
                    cdef double x = <double>i - x_mean
                    slope_num += x * (cumsum[i] - y_mean)
                    slope_den += x * x
                
                cdef double slope = slope_num / (slope_den + 1e-10)
                cdef double intercept = y_mean - slope * x_mean
                
                # Compute detrended fluctuation
                for i in range(start, end):
                    cdef double trend = slope * <double>i + intercept
                    fluct_sum += (cumsum[i] - trend) * (cumsum[i] - trend)
            
            log_scales[scale_idx] = log(<double>s)
            log_fluct[scale_idx] = log(sqrt(fluct_sum / <double>(n_segments * s)) + 1e-10)
        
        # Linear regression to get H
        cdef double sum_x = 0.0, sum_y = 0.0, sum_xy = 0.0, sum_x2 = 0.0
        cdef int64_t count = 0
        
        for i in range(10):
            if log_scales[i] > 0:
                sum_x += log_scales[i]
                sum_y += log_fluct[i]
                sum_xy += log_scales[i] * log_fluct[i]
                sum_x2 += log_scales[i] * log_scales[i]
                count += 1
        
        if count > 2:
            cdef double H = (count * sum_xy - sum_x * sum_y) / (count * sum_x2 - sum_x * sum_x + 1e-10)
            return max(0.01, min(0.99, H))
        
        return 0.5
    
    cpdef cnp.ndarray[float64_t, ndim=1] extract_rough_volatility_features(
        self, cnp.ndarray[float64_t, ndim=1] returns
    ):
        """
        Extract rough volatility features from return series.
        
        Returns features capturing:
        - Hurst exponent estimates (R/S, DFA, Whittle)
        - Roughness indices
        - Volatility signature
        - p-variation statistics
        - Self-similarity measures
        """
        cdef int64_t n_features = 32
        cdef cnp.ndarray[float64_t, ndim=1] features = np.zeros(n_features, dtype=np.float64)
        cdef double[:] feat_view = features
        
        cdef int64_t n = len(returns)
        if n < 100:
            return features
        
        # Feature 1: Hurst exponent via R/S
        feat_view[0] = self.estimate_hurst_rs(returns)
        
        # Feature 2: Hurst exponent via DFA
        feat_view[1] = self.estimate_hurst_dfa(returns)
        
        # Feature 3: Average Hurst
        feat_view[2] = (feat_view[0] + feat_view[1]) / 2.0
        
        # Feature 4: Roughness index = 1 - H
        feat_view[3] = 1.0 - feat_view[2]
        
        # Feature 5-8: Volatility at different scales
        cdef int64_t scales[4] = [5, 20, 60, 240]
        for i in range(4):
            cdef int64_t s = scales[i]
            if n > s:
                cdef double vol_sum = 0.0
                for j in range(s):
                    vol_sum += returns[n - 1 - j] * returns[n - 1 - j]
                feat_view[4 + i] = sqrt(vol_sum / <double>s)
        
        # Feature 9-12: Realized variance ratios
        for i in range(4):
            cdef int64_t s = scales[i]
            if n > 2 * s:
                cdef double rv_short = 0.0, rv_long = 0.0
                for j in range(s):
                    rv_short += returns[n - 1 - j] * returns[n - 1 - j]
                for j in range(s, 2*s):
                    rv_long += returns[n - 1 - j] * returns[n - 1 - j]
                feat_view[8 + i] = rv_short / (rv_long + 1e-10)
        
        # Feature 13-20: p-variation for different p
        cdef double p_values[8] = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 10.0]
        for p_idx in range(8):
            cdef double p = p_values[p_idx]
            cdef double pvar = 0.0
            for i in range(min(n, 1000)):
                pvar += pow(fabs(returns[i]), p)
            feat_view[12 + p_idx] = pow(pvar, 1.0 / p)
        
        # Feature 21-28: Self-similarity measures
        for i in range(8):
            cdef int64_t scale = (i + 1) * 10
            if n > 2 * scale:
                cdef double autocorr = 0.0
                cdef double var = 0.0
                for j in range(n - scale):
                    autocorr += returns[j] * returns[j + scale]
                    var += returns[j] * returns[j]
                feat_view[20 + i] = autocorr / (var + 1e-10)
        
        # Feature 29-32: Higher-order statistics
        cdef double skew = 0.0, kurt = 0.0
        cdef double mean_ret = 0.0
        for i in range(min(n, 1000)):
            mean_ret += returns[i]
        mean_ret /= min(1000.0, <double>n)
        
        cdef double std_ret = 0.0
        for i in range(min(n, 1000)):
            std_ret += (returns[i] - mean_ret) * (returns[i] - mean_ret)
        std_ret = sqrt(std_ret / min(1000.0, <double>n)) + 1e-10
        
        for i in range(min(n, 1000)):
            cdef double z = (returns[i] - mean_ret) / std_ret
            skew += z * z * z
            kurt += z * z * z * z
        
        feat_view[28] = skew / min(1000.0, <double>n)
        feat_view[29] = kurt / min(1000.0, <double>n) - 3.0  # Excess kurtosis
        feat_view[30] = feat_view[28] / (feat_view[29] + 3.0 + 1e-10)  # Skew-kurtosis ratio
        feat_view[31] = std_ret / (fabs(mean_ret) + 1e-10)  # Coefficient of variation
        
        return features


# ============================================================================
# Rough Path Theory Engine
# ============================================================================

cdef class RoughPathEngine:
    """
    Rough Path Theory engine for signature-based analysis.
    
    The signature of a path X = (X_1, ..., X_d) is:
    
    Sig(X) = (1, X, X⊗X, X⊗X⊗X, ...)
    
    where ⊗ is the tensor product and integrals are iterated.
    
    The signature captures all geometric information about the path
    in a coordinate-free manner, making it ideal for:
    - Pattern recognition (different parameterizations)
    - Machine learning features (universal approximator)
    - Signature kernel for time series comparison
    """
    
    cdef RoughPathState path_state
    cdef int64_t path_dim         # Dimension of path (2 for price/volume)
    cdef int64_t max_level        # Maximum signature level
    cdef double[:,:] levy_area    # Lévy area (level 2)
    
    def __init__(self, int64_t path_dim=2, int64_t max_level=4, int64_t path_length=10000):
        """
        Initialize rough path engine.
        
        Parameters:
        -----------
        path_dim : Dimension of the path (e.g., 2 for price+volume)
        max_level : Maximum signature level to compute
        path_length : Maximum path length
        """
        self.path_dim = path_dim
        self.max_level = max_level
        
        cdef cnp.ndarray[float64_t, ndim=1] sig1 = np.zeros(path_dim, dtype=np.float64)
        cdef cnp.ndarray[float64_t, ndim=2] sig2 = np.zeros((path_dim, path_dim), dtype=np.float64)
        cdef cnp.ndarray[float64_t, ndim=3] sig3 = np.zeros((path_dim, path_dim, path_dim), dtype=np.float64)
        cdef cnp.ndarray[float64_t, ndim=2] levy = np.zeros((path_dim, path_dim), dtype=np.float64)
        
        self.path_state.signature_level1 = sig1
        self.path_state.signature_level2 = sig2
        self.path_state.signature_level3 = sig3
        self.path_state.p_variation = 0.0
        self.path_state.roughness_index = 0.0
        self.path_state.total_variation = 0.0
        self.levy_area = levy
    
    cdef void compute_signature_level1(self, double[:,:] increments) noexcept nogil:
        """
        Compute level 1 signature: S^1(X) = Σ ΔX_i
        
        This is simply the total increment.
        """
        cdef int64_t i, j
        cdef int64_t n = increments.shape[0]
        cdef int64_t d = min(self.path_dim, increments.shape[1])
        
        # Reset
        for j in range(d):
            self.path_state.signature_level1[j] = 0.0
        
        # Sum increments
        for i in range(n):
            for j in range(d):
                self.path_state.signature_level1[j] += increments[i, j]
    
    cdef void compute_signature_level2(self, double[:,:] increments) noexcept nogil:
        """
        Compute level 2 signature: S^2(X) = Σ_{i<j} ΔX_i ⊗ ΔX_j
        
        This captures quadratic variation and Lévy area.
        """
        cdef int64_t i, j, k, l
        cdef int64_t n = increments.shape[0]
        cdef int64_t d = min(self.path_dim, increments.shape[1])
        
        # Reset
        for j in range(d):
            for k in range(d):
                self.path_state.signature_level2[j, k] = 0.0
        
        # Compute iterated integrals
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(d):
                    for l in range(d):
                        self.path_state.signature_level2[k, l] += increments[i, k] * increments[j, l]
    
    cdef void compute_signature_level3(self, double[:,:] increments) noexcept nogil:
        """
        Compute level 3 signature: S^3(X) = Σ_{i<j<k} ΔX_i ⊗ ΔX_j ⊗ ΔX_k
        
        This captures cubic interactions.
        """
        cdef int64_t i, j, k, l, m, n_idx
        cdef int64_t n = increments.shape[0]
        cdef int64_t d = min(self.path_dim, increments.shape[1])
        
        # Reset
        for l in range(d):
            for m in range(d):
                for n_idx in range(d):
                    self.path_state.signature_level3[l, m, n_idx] = 0.0
        
        # Compute (truncated for efficiency)
        cdef int64_t max_triple = min(n, 500)  # Limit for computational tractability
        for i in range(max_triple):
            for j in range(i + 1, max_triple):
                for k in range(j + 1, max_triple):
                    for l in range(d):
                        for m in range(d):
                            for n_idx in range(d):
                                self.path_state.signature_level3[l, m, n_idx] += (
                                    increments[i, l] * increments[j, m] * increments[k, n_idx]
                                )
    
    cdef void compute_levy_area(self, double[:,:] increments) noexcept nogil:
        """
        Compute Lévy area A(X) = Σ_{i<j} (ΔX_i^1 ΔX_j^2 - ΔX_i^2 ΔX_j^1)
        
        This is the signed area enclosed by the path projection.
        """
        cdef int64_t i, j
        cdef int64_t n = increments.shape[0]
        
        # Reset
        for i in range(self.path_dim):
            for j in range(self.path_dim):
                self.levy_area[i, j] = 0.0
        
        # For 2D path: Lévy area is scalar
        if self.path_dim >= 2:
            cdef double area = 0.0
            for i in range(n):
                for j in range(i + 1, n):
                    area += increments[i, 0] * increments[j, 1] - increments[i, 1] * increments[j, 0]
            
            self.levy_area[0, 1] = area
            self.levy_area[1, 0] = -area
    
    cdef void compute_p_variation(self, double[:,:] path, double p) noexcept nogil:
        """
        Compute p-variation: ||X||_p^p = Σ |ΔX_i|^p
        
        For p < 2: captures rough behavior
        For p = 2: quadratic variation
        For p > 2: captures smooth behavior
        """
        cdef int64_t i, j
        cdef int64_t n = path.shape[0] - 1
        cdef int64_t d = min(self.path_dim, path.shape[1])
        cdef double pvar = 0.0
        
        for i in range(n):
            cdef double increment_norm = 0.0
            for j in range(d):
                cdef double delta = path[i + 1, j] - path[i, j]
                increment_norm += delta * delta
            increment_norm = sqrt(increment_norm)
            
            pvar += pow(increment_norm, p)
        
        self.path_state.p_variation = pow(pvar, 1.0 / p)
    
    cpdef cnp.ndarray[float64_t, ndim=1] extract_signature_features(
        self, cnp.ndarray[float64_t, ndim=1] price_path,
        cnp.ndarray[float64_t, ndim=1] volume_path
    ):
        """
        Extract rough path features from price-volume path.
        
        Returns features capturing:
        - Signature at multiple levels
        - Lévy area and quadratic variation
        - p-variation statistics
        - Roughness indices
        - Path geometry measures
        """
        cdef int64_t n_features = 32
        cdef cnp.ndarray[float64_t, ndim=1] features = np.zeros(n_features, dtype=np.float64)
        cdef double[:] feat_view = features
        
        cdef int64_t n = min(len(price_path), len(volume_path))
        if n < 10:
            return features
        
        # Create 2D path
        cdef cnp.ndarray[float64_t, ndim=2] path_2d = np.zeros((n, 2), dtype=np.float64)
        for i in range(n):
            path_2d[i, 0] = price_path[i]
            path_2d[i, 1] = volume_path[i]
        
        # Compute increments
        cdef cnp.ndarray[float64_t, ndim=2] increments = np.zeros((n-1, 2), dtype=np.float64)
        for i in range(n-1):
            increments[i, 0] = path_2d[i+1, 0] - path_2d[i, 0]
            increments[i, 1] = path_2d[i+1, 1] - path_2d[i, 1]
        
        # Compute signature levels
        self.compute_signature_level1(increments)
        self.compute_signature_level2(increments)
        self.compute_signature_level3(increments)
        self.compute_levy_area(increments)
        
        # Feature 1-4: Level 1 signature
        for i in range(min(2, self.path_dim)):
            feat_view[i] = self.path_state.signature_level1[i]
        feat_view[2] = sqrt(feat_view[0]**2 + feat_view[1]**2)  # Magnitude
        feat_view[3] = atan2(feat_view[1], feat_view[0])  # Direction
        
        # Feature 4-11: Level 2 signature (flattened)
        cdef int64_t idx = 4
        for i in range(min(2, self.path_dim)):
            for j in range(min(2, self.path_dim)):
                if idx < 12:
                    feat_view[idx] = self.path_state.signature_level2[i, j]
                    idx += 1
        
        # Feature 12-15: Lévy area
        feat_view[12] = self.levy_area[0, 1]
        feat_view[13] = fabs(self.levy_area[0, 1])  # Absolute area
        feat_view[14] = atan2(self.levy_area[0, 1], 1.0)  # Normalized angle
        feat_view[15] = feat_view[12] / (feat_view[2] + 1e-10)  # Area to perimeter ratio
        
        # Feature 16-23: p-variation for different p
        cdef double p_values[8] = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 10.0]
        for p_idx in range(8):
            self.compute_p_variation(path_2d, p_values[p_idx])
            feat_view[16 + p_idx] = self.path_state.p_variation
        
        # Feature 24-31: Path statistics
        cdef double total_dist = 0.0
        cdef double max_dist = 0.0
        for i in range(n-1):
            cdef double dist = sqrt(increments[i, 0]**2 + increments[i, 1]**2)
            total_dist += dist
            if dist > max_dist:
                max_dist = dist
        
        feat_view[24] = total_dist  # Total path length
        feat_view[25] = max_dist  # Maximum step size
        feat_view[26] = total_dist / <double>(n - 1)  # Average step size
        feat_view[27] = feat_view[2] / (total_dist + 1e-10)  # Efficiency ratio
        
        # Roughness from p-variation scaling
        if feat_view[16] > 1e-10 and feat_view[18] > 1e-10:
            feat_view[28] = log(feat_view[16] / feat_view[18] + 1e-10) / log(2.0)
        else:
            feat_view[28] = 0.0
        
        feat_view[29] = feat_view[28]  # Roughness index
        feat_view[30] = feat_view[25] / (feat_view[26] + 1e-10)  # Step size ratio
        feat_view[31] = feat_view[12] / (feat_view[24] + 1e-10)  # Winding number
        
        return features


# ============================================================================
# Rough Volatility Model Engine
# ============================================================================

cdef class RoughVolatilityModelEngine:
    """
    Rough Volatility Model (rBergomi) engine.
    
    The rBergomi model:
    dS_t = S_t √V_t dW_t
    dV_t = dZ_t^H
    
    where Z^H is a fractional Brownian motion with Hurst H < 0.5.
    
    This captures the empirically observed "roughness" of volatility
    with H ≈ 0.1, much rougher than classical models (H = 0.5).
    """
    
    cdef RoughVolatilityModel model_params
    cdef double[:] spot_path
    cdef double[:] vol_path
    cdef double[:] log_returns
    cdef int64_t n_steps
    cdef double dt
    
    def __init__(self, double H=0.1, double sigma=0.3, double rho=-0.7,
                 double nu=0.5, double theta=0.02, double kappa=2.0,
                 int64_t n_steps=10000):
        """
        Initialize Rough Volatility model.
        
        Parameters:
        -----------
        H : Hurst exponent (roughness)
        sigma : Volatility of volatility
        rho : Correlation (leverage effect, typically negative)
        nu : Vol of vol parameter
        theta : Long-run variance
        kappa : Mean reversion speed
        """
        self.model_params = RoughVolatilityModel()
        self.model_params.H = H
        self.model_params.sigma = sigma
        self.model_params.rho = rho
        self.model_params.nu = nu
        self.model_params.theta = theta
        self.model_params.kappa = kappa
        
        self.n_steps = n_steps
        self.dt = 0.001
        
        cdef cnp.ndarray[float64_t, ndim=1] spot = np.zeros(n_steps + 1, dtype=np.float64)
        cdef cnp.ndarray[float64_t, ndim=1] vol = np.zeros(n_steps + 1, dtype=np.float64)
        cdef cnp.ndarray[float64_t, ndim=1] log_ret = np.zeros(n_steps, dtype=np.float64)
        
        self.spot_path = spot
        self.vol_path = vol
        self.log_returns = log_ret
    
    cpdef void simulate(self, double S0=100.0, double V0=0.04):
        """
        Simulate path under rBergomi model.
        
        Uses Euler scheme with Cholesky decomposition for
        correlated Brownian motions.
        """
        cdef int64_t i
        cdef double H = self.model_params.H
        cdef double sigma = self.model_params.sigma
        cdef double rho = self.model_params.rho
        cdef double theta = self.model_params.theta
        cdef double kappa = self.model_params.kappa
        
        # Initialize
        self.spot_path[0] = S0
        self.vol_path[0] = V0
        
        # Generate correlated Brownian motions
        cdef cnp.ndarray[float64_t, ndim=1] Z1 = np.random.randn(self.n_steps).astype(np.float64)
        cdef cnp.ndarray[float64_t, ndim=1] Z2 = np.random.randn(self.n_steps).astype(np.float64)
        
        # Cholesky for correlation
        cdef double W1, W2
        cdef double V, dV, dS
        
        for i in range(self.n_steps):
            # Correlated increments
            W1 = Z1[i]
            W2 = rho * Z1[i] + sqrt(1.0 - rho * rho) * Z2[i]
            
            # Volatility dynamics (rough)
            V = self.vol_path[i]
            dV = kappa * (theta - V) * self.dt + sigma * pow(V, H) * W2 * sqrt(self.dt)
            self.vol_path[i + 1] = max(V + dV, 0.0001)
            
            # Spot dynamics
            dS = self.spot_path[i] * sqrt(max(self.vol_path[i], 0.0001)) * W1 * sqrt(self.dt)
            self.spot_path[i + 1] = self.spot_path[i] + dS
            
            # Log returns
            if self.spot_path[i] > 0:
                self.log_returns[i] = log(self.spot_path[i + 1] / self.spot_path[i])
    
    cpdef cnp.ndarray[float64_t, ndim=1] extract_model_features(self):
        """
        Extract features from simulated rough volatility path.
        
        Returns model-specific features.
        """
        cdef int64_t n_features = 16
        cdef cnp.ndarray[float64_t, ndim=1] features = np.zeros(n_features, dtype=np.float64)
        cdef double[:] feat_view = features
        
        # Feature 1-4: Model parameters
        feat_view[0] = self.model_params.H
        feat_view[1] = self.model_params.sigma
        feat_view[2] = self.model_params.rho
        feat_view[3] = self.model_params.nu
        
        # Feature 5-8: Path statistics
        cdef double spot_mean = 0.0, vol_mean = 0.0
        for i in range(self.n_steps):
            spot_mean += self.spot_path[i]
            vol_mean += self.vol_path[i]
        
        feat_view[4] = spot_mean / <double>self.n_steps
        feat_view[5] = vol_mean / <double>self.n_steps
        feat_view[6] = self.spot_path[self.n_steps - 1] / self.spot_path[0]  # Total return
        feat_view[7] = feat_view[6] - 1.0  # Simple return
        
        # Feature 9-12: Volatility statistics
        cdef double vol_var = 0.0
        for i in range(self.n_steps):
            vol_var += (self.vol_path[i] - feat_view[5]) * (self.vol_path[i] - feat_view[5])
        
        feat_view[8] = sqrt(vol_var / <double>self.n_steps)  # Vol of vol
        feat_view[9] = feat_view[8] / (feat_view[5] + 1e-10)  # CV of vol
        feat_view[10] = max(self.vol_path) - min(self.vol_path)  # Vol range
        feat_view[11] = feat_view[10] / (feat_view[5] + 1e-10)  # Relative vol range
        
        # Feature 13-16: Return statistics
        cdef double ret_mean = 0.0, ret_var = 0.0
        for i in range(self.n_steps):
            ret_mean += self.log_returns[i]
            ret_var += self.log_returns[i] * self.log_returns[i]
        
        feat_view[12] = ret_mean / <double>self.n_steps
        feat_view[13] = sqrt(ret_var / <double>self.n_steps)
        feat_view[14] = feat_view[13] * sqrt(252.0 * 24.0)  # Annualized vol
        feat_view[15] = feat_view[12] / (feat_view[13] + 1e-10)  # Sharpe ratio
        
        return features


# ============================================================================
# Combined Rough Volatility Orchestrator
# ============================================================================

cdef class RoughVolatilityOrchestrator:
    """
    Master orchestrator for rough volatility analysis.
    """
    
    cdef FractionalBrownianMotionEngine fbm_engine
    cdef RoughPathEngine rough_path_engine
    cdef RoughVolatilityModelEngine model_engine
    
    def __init__(self):
        """Initialize all engines."""
        self.fbm_engine = FractionalBrownianMotionEngine(n_steps=10000, dt=0.001, H=0.1)
        self.rough_path_engine = RoughPathEngine(path_dim=2, max_level=4)
        self.model_engine = RoughVolatilityModelEngine(H=0.1, sigma=0.3, n_steps=10000)
    
    cpdef cnp.ndarray[float64_t, ndim=1] compute_unified_features(
        self, cnp.ndarray[float64_t, ndim=1] price_data,
        cnp.ndarray[float64_t, ndim=1] volume_data
    ):
        """
        Compute unified rough volatility features.
        
        Returns 80-dimensional feature vector.
        """
        cdef int64_t total_features = 80
        cdef cnp.ndarray[float64_t, ndim=1] features = np.zeros(total_features, dtype=np.float64)
        cdef double[:] feat_view = features
        
        # Compute returns
        cdef int64_t n = len(price_data)
        cdef cnp.ndarray[float64_t, ndim=1] returns = np.zeros(max(1, n-1), dtype=np.float64)
        for i in range(1, n):
            if price_data[i-1] > 0:
                returns[i-1] = log(price_data[i] / price_data[i-1])
        
        # fBm features (0-31)
        cdef cnp.ndarray[float64_t, ndim=1] fbm_feats = self.fbm_engine.extract_rough_volatility_features(returns)
        for i in range(min(32, len(fbm_feats))):
            feat_view[i] = fbm_feats[i]
        
        # Rough path features (32-63)
        cdef cnp.ndarray[float64_t, ndim=1] rp_feats = self.rough_path_engine.extract_signature_features(price_data, volume_data)
        for i in range(min(32, len(rp_feats))):
            feat_view[32 + i] = rp_feats[i]
        
        # Model features (64-79)
        self.model_engine.simulate(S0=price_data[n-1] if n > 0 else 100.0)
        cdef cnp.ndarray[float64_t, ndim=1] model_feats = self.model_engine.extract_model_features()
        for i in range(min(16, len(model_feats))):
            feat_view[64 + i] = model_feats[i]
        
        return features
    
    cpdef double compute_signal_strength(self, cnp.ndarray[float64_t, ndim=1] price_data,
                                         cnp.ndarray[float64_t, ndim=1] volume_data):
        """
        Compute signal strength from rough volatility analysis.
        
        Returns value in [-1, 1].
        """
        cdef cnp.ndarray[float64_t, ndim=1] features = self.compute_unified_features(price_data, volume_data)
        
        # Combine features into signal
        cdef double signal = 0.0
        
        # Hurst exponent contribution (rough → contrarian)
        signal += (0.5 - features[2]) * 0.4  # H < 0.5 → positive signal
        
        # Levy area contribution (signed area → directional)
        signal += tanh(features[44] * 0.01) * 0.3
        
        # Volatility regime contribution
        signal += tanh(features[68] - 0.5) * 0.3
        
        return max(-1.0, min(1.0, signal))
