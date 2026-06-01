"""
Quantum Chromodynamics and Navier-Stokes Fluid Dynamics Engine
Implements QCD lattice gauge field and Navier-Stokes turbulence prediction
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import math
import logging

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Order types in the quantum field"""
    BUY_LIMIT = "quark"
    SELL_LIMIT = "antiquark"
    BUY_MARKET = "gluon_buy"
    SELL_MARKET = "gluon_sell"
    
    @classmethod
    def from_string(cls, s: str) -> 'OrderType':
        """Create OrderType from string"""
        mapping = {
            'buy_limit': cls.BUY_LIMIT,
            'sell_limit': cls.SELL_LIMIT,
            'buy_market': cls.BUY_MARKET,
            'sell_market': cls.SELL_MARKET
        }
        return mapping.get(s, cls.BUY_LIMIT)


@dataclass
class QuarkField:
    """Represents an order in the QCD lattice"""
    position: Tuple[int, int]
    order_type: OrderType
    strength: float
    color_charge: complex


@dataclass
class GluonField:
    """Gluon field carrying the strong force between orders"""
    source: Tuple[int, int]
    target: Tuple[int, int]
    force_magnitude: float
    binding_energy: float


@dataclass
class QCDState:
    """Complete QCD lattice state"""
    quarks: List[QuarkField]
    antiquarks: List[QuarkField]
    gluons: List[GluonField]
    total_kinetic_energy: float
    strong_coupling: float
    color_neutrality: float


@dataclass
class FluidState:
    """Navier-Stokes fluid dynamics state"""
    velocity_field: np.ndarray
    pressure_field: np.ndarray
    density_field: np.ndarray
    vorticity: float
    reynolds_number: float
    turbulence_intensity: float


@dataclass
class Singularity:
    """Navier-Stokes singularity point"""
    position: Tuple[int, int]
    intensity: float
    time_to_event: float
    severity: str


class QCDEngine:
    """
    Quantum Chromodynamics Lattice Gluon Gauge Field Simulator
    
    Treats buy limit orders as Quarks and sell limit orders as Anti-Quarks.
    Models order flow interactions via Lattice Gauge Field where the market's
    "Strong Force" is carried by simulated Gluons.
    """
    
    def __init__(self, lattice_size: int = 50, coupling_constant: float = 0.1):
        self.lattice_size = lattice_size
        self.coupling_constant = coupling_constant
        self.quarks: List[QuarkField] = []
        self.anti_quarks: List[QuarkField] = []
        self.gluons: List[GluonField] = []
        self.energy_history: List[float] = []
        
    def initialize_lattice(self) -> None:
        """Initialize the QCD lattice with vacuum state"""
        self.quarks = []
        self.anti_quarks = []
        self.gluons = []
        logger.info("QCD lattice initialized to vacuum state")
    
    def add_order(self, order_type: OrderType, position: Tuple[int, int], 
                  strength: float) -> None:
        """
        Add an order to the QCD lattice
        
        Args:
            order_type: Type of order (quark or antiquark)
            position: (x, y) position on lattice
            strength: Order strength (volume * price_impact)
        """
        color_charge = complex(np.random.randn(), np.random.randn())
        color_charge = color_charge / abs(color_charge) if abs(color_charge) > 0 else 1+0j
        
        field = QuarkField(
            position=position,
            order_type=order_type,
            strength=strength,
            color_charge=color_charge
        )
        
        if order_type == OrderType.BUY_LIMIT:
            self.quarks.append(field)
        else:
            self.anti_quarks.append(field)
        
        # Update gluon field
        self._update_gluon_field()
    
    def _update_gluon_field(self) -> None:
        """Update gluon interactions between all quark pairs"""
        self.gluons = []
        
        all_orders = self.quarks + self.anti_quarks
        
        for i, q1 in enumerate(all_orders):
            for j, q2 in enumerate(all_orders):
                if i >= j:
                    continue
                
                # Calculate distance
                dx = q1.position[0] - q2.position[0]
                dy = q1.position[1] - q2.position[1]
                distance = math.sqrt(dx*dx + dy*dy) + 1e-10
                
                # Gluon force (strong force decreases with distance)
                force_magnitude = self.coupling_constant * q1.strength * q2.strength / distance
                
                # Binding energy from color charge interaction
                binding = abs(q1.color_charge * np.conj(q2.color_charge)) * force_magnitude
                
                self.gluons.append(GluonField(
                    source=q1.position,
                    target=q2.position,
                    force_magnitude=force_magnitude,
                    binding_energy=binding
                ))
    
    def compute_kinetic_energy(self) -> float:
        """
        Compute total kinetic energy of the QCD system
        
        High kinetic energy spikes indicate impending liquidity vacuums.
        
        Returns:
            Total kinetic energy value
        """
        kinetic = 0.0
        
        # Quark kinetic energy
        for q in self.quarks + self.anti_quarks:
            kinetic += 0.5 * q.strength ** 2
        
        # Gluon interaction energy
        for g in self.gluons:
            kinetic += g.binding_energy
        
        self.energy_history.append(kinetic)
        
        # Keep last 1000 energy values
        if len(self.energy_history) > 1000:
            self.energy_history = self.energy_history[-1000:]
        
        return kinetic
    
    def compute_color_neutrality(self) -> float:
        """
        Compute color charge neutrality of the system
        
        Returns value close to 0 for balanced market, high values for imbalanced.
        
        Returns:
            Color neutrality measure (0 = balanced, high = imbalanced)
        """
        total_buy_charge = sum(abs(q.color_charge) * q.strength for q in self.quarks)
        total_sell_charge = sum(abs(q.color_charge) * q.strength for q in self.anti_quarks)
        
        total = total_buy_charge + total_sell_charge
        if total == 0:
            return 0.0
        
        return abs(total_buy_charge - total_sell_charge) / total
    
    def detect_liquidity_vacuum(self, threshold: float = 2.0) -> bool:
        """
        Detect impending liquidity vacuum based on kinetic energy spikes
        
        Args:
            threshold: Number of standard deviations for spike detection
            
        Returns:
            True if liquidity vacuum is imminent
        """
        if len(self.energy_history) < 50:
            return False
        
        recent = np.array(self.energy_history[-50:])
        current = recent[-1]
        mean = np.mean(recent[:-1])
        std = np.std(recent[:-1]) + 1e-10
        
        return (current - mean) / std > threshold
    
    def get_qcd_state(self) -> QCDState:
        """Get complete QCD state"""
        kinetic = self.compute_kinetic_energy()
        color_neut = self.compute_color_neutrality()
        
        return QCDState(
            quarks=self.quarks.copy(),
            antiquarks=self.anti_quarks.copy(),
            gluons=self.gluons.copy(),
            total_kinetic_energy=kinetic,
            strong_coupling=self.coupling_constant,
            color_neutrality=color_neut
        )


class NavierStokesEngine:
    """
    Navier-Stokes Global Smoothness Singularity Predictor
    
    Models post-news order flow as fluid dynamics and tracks
    emergence of singularities (infinite energy points).
    """
    
    def __init__(self, grid_size: int = 50, viscosity: float = 0.01, 
                 time_step: float = 0.01):
        self.grid_size = grid_size
        self.viscosity = viscosity
        self.time_step = time_step
        
        # Initialize velocity fields
        self.u = np.zeros((grid_size, grid_size))  # x-velocity
        self.v = np.zeros((grid_size, grid_size))  # y-velocity
        self.p = np.zeros((grid_size, grid_size))  # pressure
        self.rho = np.ones((grid_size, grid_size))  # density
        
        self.reynolds_history: List[float] = []
        self.singularity_history: List[Singularity] = []
        
    def initialize_fluid(self, buy_pressure: np.ndarray, sell_pressure: np.ndarray) -> None:
        """
        Initialize fluid state from order pressure
        
        Args:
            buy_pressure: 2D array of buy order pressure
            sell_pressure: 2D array of sell order pressure
        """
        # Net pressure drives initial velocity
        net_pressure = buy_pressure - sell_pressure
        
        # Convert to velocity components
        self.u = np.gradient(net_pressure, axis=1)
        self.v = np.gradient(net_pressure, axis=0)
        
        # Normalize
        max_vel = max(np.max(np.abs(self.u)), np.max(np.abs(self.v)), 1e-10)
        self.u = self.u / max_vel
        self.v = self.v / max_vel
        
        # Density from total pressure magnitude
        self.rho = np.abs(net_pressure) / (np.max(np.abs(net_pressure)) + 1e-10)
        
        logger.info("Navier-Stokes fluid initialized from order pressure")
    
    def step(self) -> None:
        """
        Advance the Navier-Stokes simulation by one time step
        
        Uses simplified projection method for incompressible flow.
        """
        # Diffusion step (viscosity)
        self.u = self._diffuse(self.u)
        self.v = self._diffuse(self.v)
        
        # Advection step
        self.u = self._advect(self.u, self.u, self.v)
        self.v = self._advect(self.v, self.u, self.v)
        
        # Pressure projection (enforce incompressibility)
        self._project()
        
        # Update density
        self.rho = self._advect(self.rho, self.u, self.v)
    
    def _diffuse(self, field: np.ndarray) -> np.ndarray:
        """Apply diffusion (viscosity) to a field"""
        alpha = self.time_step * self.viscosity * self.grid_size * self.grid_size
        
        # Simple Jacobi iteration
        for _ in range(5):
            laplacian = np.zeros_like(field)
            laplacian[1:-1, 1:-1] = (
                field[:-2, 1:-1] + field[2:, 1:-1] +
                field[1:-1, :-2] + field[1:-1, 2:] -
                4 * field[1:-1, 1:-1]
            )
            field = field + alpha * laplacian
        
        return field
    
    def _advect(self, field: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Advect a field through the velocity field"""
        new_field = np.zeros_like(field)
        
        for i in range(1, self.grid_size - 1):
            for j in range(1, self.grid_size - 1):
                # Backtrace
                x = i - self.time_step * u[i, j] * self.grid_size
                y = j - self.time_step * v[i, j] * self.grid_size
                
                # Clamp to grid
                x = max(0, min(self.grid_size - 1.01, x))
                y = max(0, min(self.grid_size - 1.01, y))
                
                # Bilinear interpolation
                i0, j0 = int(x), int(y)
                i1, j1 = min(i0 + 1, self.grid_size - 1), min(j0 + 1, self.grid_size - 1)
                fx, fy = x - i0, y - j0
                
                new_field[i, j] = (
                    field[i0, j0] * (1-fx) * (1-fy) +
                    field[i1, j0] * fx * (1-fy) +
                    field[i0, j1] * (1-fx) * fy +
                    field[i1, j1] * fx * fy
                )
        
        return new_field
    
    def _project(self) -> None:
        """Project velocity field to enforce incompressibility"""
        div = np.zeros((self.grid_size, self.grid_size))
        
        div[1:-1, 1:-1] = 0.5 * (
            (self.u[2:, 1:-1] - self.u[:-2, 1:-1]) +
            (self.v[1:-1, 2:] - self.v[1:-1, :-2])
        )
        
        # Solve pressure Poisson equation (simplified)
        for _ in range(20):
            p_new = np.zeros_like(self.p)
            p_new[1:-1, 1:-1] = 0.25 * (
                self.p[:-2, 1:-1] + self.p[2:, 1:-1] +
                self.p[1:-1, :-2] + self.p[1:-1, 2:] -
                div[1:-1, 1:-1]
            )
            self.p = p_new
        
        # Subtract pressure gradient from velocity
        self.u[1:-1, 1:-1] -= 0.5 * (self.p[2:, 1:-1] - self.p[:-2, 1:-1])
        self.v[1:-1, 1:-1] -= 0.5 * (self.p[1:-1, 2:] - self.p[1:-1, :-2])
    
    def compute_vorticity(self) -> float:
        """
        Compute flow vorticity (curl of velocity)
        
        High vorticity indicates turbulent rotation.
        """
        vort_x = np.gradient(self.v, axis=1)
        vort_y = np.gradient(self.u, axis=0)
        vorticity = vort_x - vort_y
        
        return float(np.mean(np.abs(vorticity)))
    
    def compute_reynolds_number(self) -> float:
        """
        Compute effective Reynolds number
        
        Re = (velocity * length) / viscosity
        """
        velocity_scale = np.sqrt(np.mean(self.u**2 + self.v**2))
        length_scale = 1.0 / self.grid_size
        
        re = velocity_scale * length_scale / (self.viscosity + 1e-10)
        
        self.reynolds_history.append(re)
        if len(self.reynolds_history) > 1000:
            self.reynolds_history = self.reynolds_history[-1000:]
        
        return float(re)
    
    def detect_singularities(self, velocity_magnitude: np.ndarray = None) -> List[Singularity]:
        """
        Detect Navier-Stokes singularities (infinite energy points)
        
        These indicate where liquidity drains out instantly.
        
        Args:
            velocity_magnitude: Optional pre-computed velocity magnitude
            
        Returns:
            List of detected singularities
        """
        if velocity_magnitude is None:
            velocity_magnitude = np.sqrt(self.u**2 + self.v**2)
        
        singularities = []
        
        # Find local maxima that exceed threshold
        threshold = np.mean(velocity_magnitude) + 3 * np.std(velocity_magnitude)
        
        for i in range(1, self.grid_size - 1):
            for j in range(1, self.grid_size - 1):
                val = velocity_magnitude[i, j]
                
                # Check if local maximum
                neighborhood = velocity_magnitude[i-1:i+2, j-1:j+2]
                if val == np.max(neighborhood) and val > threshold:
                    # Estimate time to singularity
                    intensity = (val - threshold) / (np.std(velocity_magnitude) + 1e-10)
                    time_to_event = max(0.1, 10.0 / (intensity + 1))
                    
                    severity = "critical" if intensity > 3 else "high" if intensity > 2 else "moderate"
                    
                    singularities.append(Singularity(
                        position=(i, j),
                        intensity=float(intensity),
                        time_to_event=float(time_to_event),
                        severity=severity
                    ))
        
        self.singularity_history.extend(singularities)
        
        return singularities
    
    def compute_turbulence_intensity(self) -> float:
        """
        Compute turbulence intensity
        
        Returns value between 0 (laminar) and 1 (fully turbulent)
        """
        re = self.compute_reynolds_number()
        
        # Turbulence intensity increases with Reynolds number
        # Sigmoid-like mapping
        intensity = 1.0 / (1.0 + np.exp(-(re - 1000) / 500))
        
        return float(intensity)
    
    def get_fluid_state(self) -> FluidState:
        """Get complete fluid dynamics state"""
        vorticity = self.compute_vorticity()
        reynolds = self.compute_reynolds_number()
        turbulence = self.compute_turbulence_intensity()
        
        return FluidState(
            velocity_field=np.sqrt(self.u**2 + self.v**2),
            pressure_field=self.p.copy(),
            density_field=self.rho.copy(),
            vorticity=vorticity,
            reynolds_number=reynolds,
            turbulence_intensity=turbulence
        )
    
    def predict_exit_point(self) -> Tuple[int, int]:
        """
        Predict the calmest exit point from turbulent flow
        
        Returns position of minimum turbulence.
        """
        velocity_mag = np.sqrt(self.u**2 + self.v**2)
        
        # Find minimum velocity magnitude (calmest point)
        min_idx = np.unravel_index(np.argmin(velocity_mag[1:-1, 1:-1]), 
                                   (self.grid_size - 2, self.grid_size - 2))
        
        return (min_idx[0] + 1, min_idx[1] + 1)


class QuantumFluidEngine:
    """
    Unified Quantum Chromodynamics and Navier-Stokes Engine
    Combines QCD lattice gauge field with fluid dynamics for
    flash crash prediction and turbulence trading.
    """
    
    def __init__(self, lattice_size: int = 50):
        self.qcd = QCDEngine(lattice_size=lattice_size)
        self.navier_stokes = NavierStokesEngine(grid_size=lattice_size)
        self.order_buffer: List[Tuple[OrderType, Tuple[int, int], float]] = []
        
    def process_order_flow(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process incoming order flow through both engines
        
        Args:
            orders: List of order dictionaries with type, position, strength
            
        Returns:
            Combined analysis result
        """
        results = {
            'qcd_kinetic_energy': 0.0,
            'qcd_vacuum_detected': False,
            'ns_turbulence': 0.0,
            'ns_singularities': [],
            'exit_point': (25, 25),
            'combined_signal': 0.0
        }
        
        # Process through QCD engine
        buy_pressure = np.zeros((self.qcd.lattice_size, self.qcd.lattice_size))
        sell_pressure = np.zeros((self.qcd.lattice_size, self.qcd.lattice_size))
        
        for order in orders:
            order_type = OrderType.from_string(order.get('type', 'buy_limit'))
            position = order.get('position', (25, 25))
            strength = order.get('strength', 1.0)
            
            self.qcd.add_order(order_type, position, strength)
            
            # Accumulate pressure for Navier-Stokes
            x, y = position
            x = min(max(0, x), self.qcd.lattice_size - 1)
            y = min(max(0, y), self.qcd.lattice_size - 1)
            
            if order_type == OrderType.BUY_LIMIT:
                buy_pressure[x, y] += strength
            else:
                sell_pressure[x, y] += strength
        
        # QCD analysis
        qcd_state = self.qcd.get_qcd_state()
        results['qcd_kinetic_energy'] = qcd_state.total_kinetic_energy
        results['qcd_vacuum_detected'] = self.qcd.detect_liquidity_vacuum()
        results['qcd_color_neutrality'] = qcd_state.color_neutrality
        
        # Initialize and step Navier-Stokes
        if np.max(buy_pressure) > 0 or np.max(sell_pressure) > 0:
            self.navier_stokes.initialize_fluid(buy_pressure, sell_pressure)
            
            # Run several time steps
            for _ in range(10):
                self.navier_stokes.step()
            
            # NS analysis
            ns_state = self.navier_stokes.get_fluid_state()
            results['ns_turbulence'] = ns_state.turbulence_intensity
            results['ns_vorticity'] = ns_state.vorticity
            results['ns_reynolds'] = ns_state.reynolds_number
            
            # Detect singularities
            singularities = self.navier_stokes.detect_singularities()
            results['ns_singularities'] = [
                {'position': s.position, 'intensity': s.intensity, 
                 'severity': s.severity, 'time_to_event': s.time_to_event}
                for s in singularities
            ]
            
            # Predict exit point
            results['exit_point'] = self.navier_stokes.predict_exit_point()
        
        # Combined signal
        vacuum_penalty = 2.0 if results['qcd_vacuum_detected'] else 1.0
        singularity_penalty = 1.0 + 0.5 * len(results['ns_singularities'])
        
        turbulence_signal = 1.0 - results['ns_turbulence']
        energy_signal = min(1.0, results['qcd_kinetic_energy'] / 1000.0)
        
        results['combined_signal'] = turbulence_signal * energy_signal / (vacuum_penalty * singularity_penalty)
        
        return results


if __name__ == "__main__":
    # Test the quantum fluid engine
    engine = QuantumFluidEngine(lattice_size=30)
    
    # Simulate order flow
    orders = [
        {'type': 'buy_limit', 'position': (10, 10), 'strength': 5.0},
        {'type': 'sell_limit', 'position': (20, 20), 'strength': 3.0},
        {'type': 'buy_limit', 'position': (15, 15), 'strength': 4.0},
        {'type': 'sell_limit', 'position': (25, 25), 'strength': 6.0},
    ]
    
    results = engine.process_order_flow(orders)
    
    print("QCD Analysis:")
    print(f"  Kinetic Energy: {results['qcd_kinetic_energy']:.4f}")
    print(f"  Vacuum Detected: {results['qcd_vacuum_detected']}")
    print(f"  Color Neutrality: {results['qcd_color_neutrality']:.4f}")
    
    print("\nNavier-Stokes Analysis:")
    print(f"  Turbulence Intensity: {results['ns_turbulence']:.4f}")
    print(f"  Vorticity: {results.get('ns_vorticity', 0):.4f}")
    print(f"  Reynolds Number: {results.get('ns_reynolds', 0):.4f}")
    print(f"  Singularities Detected: {len(results['ns_singularities'])}")
    print(f"  Exit Point: {results['exit_point']}")
    
    print(f"\nCombined Signal: {results['combined_signal']:.4f}")
