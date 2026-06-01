"""
Engine 9: Category Theory
Functor mappings between market states

Uses categorical structures to model transformations
between different market representations.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any, Callable
from dataclasses import dataclass
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class Morphism:
    """Morphism between objects in category"""
    source: str
    target: str
    name: str
    mapping: Callable[[np.ndarray], np.ndarray]
    preserves_structure: bool


@dataclass
class Functor:
    """Functor between categories"""
    name: str
    object_mapping: Dict[str, str]
    morphism_mapping: Dict[str, Morphism]
    naturality_check: bool


@dataclass
class NaturalTransformation:
    """Natural transformation between functors"""
    name: str
    components: Dict[str, Callable[[np.ndarray], np.ndarray]]
    commutative: bool


class CategoryTheoryEngine:
    """
    Category Theory Engine
    
    Models market transformations using categorical structures.
    
    Key applications:
    - Invariant properties across timeframes
    - Structure-preserving maps between regimes
    - Universal properties for optimal strategies
    """
    
    def __init__(self):
        self.objects: Dict[str, np.ndarray] = {}
        self.morphisms: List[Morphism] = []
        self.functors: List[Functor] = []
        
    def define_market_category(self, prices: np.ndarray,
                              timeframe: str) -> str:
        """
        Define market state as object in category
        
        Returns object identifier
        """
        obj_id = f"market_{timeframe}_{len(self.objects)}"
        
        # Compute features as object representation
        features = self._extract_features(prices)
        
        self.objects[obj_id] = features
        
        return obj_id
    
    def _extract_features(self, prices: np.ndarray) -> np.ndarray:
        """Extract feature vector from prices"""
        if len(prices) < 10:
            return np.zeros(5)
        
        returns = np.diff(np.log(prices + 1e-10))
        
        features = np.array([
            np.mean(returns),
            np.std(returns),
            float(np.mean(returns > 0)),
            float(np.mean((returns - np.mean(returns))**3)) / (np.std(returns)**3 + 1e-10),
            len(returns)
        ])
        
        return features
    
    def define_morphism(self, source_id: str, target_id: str,
                       name: str = "default") -> Morphism:
        """
        Define morphism (transformation) between market states
        
        A morphism preserves structure if it maintains key relationships.
        """
        def default_mapping(x: np.ndarray) -> np.ndarray:
            # Simple normalization morphism
            return (x - np.mean(x)) / (np.std(x) + 1e-10)
        
        # Check structure preservation
        if source_id in self.objects and target_id in self.objects:
            source_features = self.objects[source_id]
            target_features = self.objects[target_id]
            
            # Check if morphism preserves correlation structure
            source_norm = default_mapping(source_features)
            target_norm = default_mapping(target_features)
            
            correlation = np.corrcoef(source_norm, target_norm)[0, 1]
            preserves = abs(correlation) > 0.5
        else:
            preserves = False
        
        morphism = Morphism(
            source=source_id,
            target=target_id,
            name=name,
            mapping=default_mapping,
            preserves_structure=preserves
        )
        
        self.morphisms.append(morphism)
        
        return morphism
    
    def define_functor(self, name: str,
                      source_category: Dict[str, str],
                      target_category: Dict[str, str]) -> Functor:
        """
        Define functor between categories
        
        Functor maps objects and morphisms while preserving structure.
        """
        # Create object mapping
        object_mapping = {}
        for src, tgt in zip(source_category.keys(), target_category.keys()):
            object_mapping[src] = tgt
        
        # Create morphism mappings
        morphism_mapping = {}
        
        functor = Functor(
            name=name,
            object_mapping=object_mapping,
            morphism_mapping=morphism_mapping,
            naturality_check=True
        )
        
        self.functors.append(functor)
        
        return functor
    
    def check_naturality(self, transformation: NaturalTransformation,
                        test_data: np.ndarray) -> bool:
        """
        Check naturality condition for natural transformation
        
        Commutativity: F(f) ∘ α_A = α_B ∘ G(f)
        """
        # Simplified check: transformation should commute with structure
        try:
            # Apply transformation at different points
            results = []
            for component_fn in transformation.components.values():
                result = component_fn(test_data)
                results.append(result)
            
            # Check if results are consistent
            if len(results) >= 2:
                # Compare transformations
                diff = np.mean(np.abs(results[0] - results[-1]))
                return diff < 0.1
            
            return True
        except Exception:
            return False
    
    def compute_universal_property(self, objects: List[np.ndarray]) -> np.ndarray:
        """
        Compute universal property (limit/colimit) of objects
        
        The limit represents the "most general" solution.
        """
        if not objects:
            return np.zeros(5)
        
        # Simple limit: component-wise mean
        stacked = np.array(objects)
        limit = np.mean(stacked, axis=0)
        
        return limit
    
    def find_isomorphism(self, obj1_id: str, obj2_id: str) -> Optional[Morphism]:
        """
        Find isomorphism between two objects
        
        Isomorphism: invertible structure-preserving map
        """
        if obj1_id not in self.objects or obj2_id not in self.objects:
            return None
        
        obj1 = self.objects[obj1_id]
        obj2 = self.objects[obj2_id]
        
        # Check if objects are "isomorphic" (similar structure)
        norm1 = obj1 / (np.linalg.norm(obj1) + 1e-10)
        norm2 = obj2 / (np.linalg.norm(obj2) + 1e-10)
        
        similarity = np.dot(norm1, norm2)
        
        if similarity > 0.8:
            def iso_mapping(x: np.ndarray) -> np.ndarray:
                scale = np.linalg.norm(obj2) / (np.linalg.norm(x) + 1e-10)
                return x * scale
            
            morphism = Morphism(
                source=obj1_id,
                target=obj2_id,
                name="isomorphism",
                mapping=iso_mapping,
                preserves_structure=True
            )
            
            return morphism
        
        return None
    
    def analyze(self, prices_multi: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Complete category theory analysis
        
        Args:
            prices_multi: Dict of timeframe -> prices
            
        Returns:
            Analysis results
        """
        # Define objects for each timeframe
        objects = {}
        for tf, prices in prices_multi.items():
            obj_id = self.define_market_category(prices, tf)
            objects[tf] = obj_id
        
        # Define morphisms between timeframes
        morphisms = []
        tf_list = list(objects.keys())
        for i in range(len(tf_list)):
            for j in range(i + 1, len(tf_list)):
                m = self.define_morphism(objects[tf_list[i]], objects[tf_list[j]], 
                                        f"{tf_list[i]}_to_{tf_list[j]}")
                morphisms.append(m)
        
        # Compute universal property
        all_features = [self.objects[oid] for oid in objects.values() 
                       if oid in self.objects]
        if all_features:
            universal = self.compute_universal_property(all_features)
        else:
            universal = np.zeros(5)
        
        # Check for isomorphisms
        isomorphisms = []
        for i in range(len(tf_list)):
            for j in range(i + 1, len(tf_list)):
                iso = self.find_isomorphism(objects[tf_list[i]], objects[tf_list[j]])
                if iso is not None:
                    isomorphisms.append((tf_list[i], tf_list[j]))
        
        return {
            'n_objects': len(objects),
            'n_morphisms': len(morphisms),
            'n_isomorphisms': len(isomorphisms),
            'isomorphic_pairs': isomorphisms,
            'structure_preserving': sum(1 for m in morphisms if m.preserves_structure),
            'universal_property': universal.tolist(),
            'categorical_complexity': len(morphisms) / max(1, len(objects))
        }
