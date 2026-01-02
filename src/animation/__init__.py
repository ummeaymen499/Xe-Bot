"""
Animation package initialization
Includes quantum physics animation templates for entanglement and related topics
"""
from src.animation.generator import ManimAnimationGenerator, animation_generator, AnimationResult
from src.animation.templates import AnimationTemplates, templates
from src.animation.quantum_templates import QuantumAnimationTemplates, quantum_templates

__all__ = [
    "ManimAnimationGenerator",
    "animation_generator", 
    "AnimationResult",
    "AnimationTemplates",
    "templates",
    "QuantumAnimationTemplates",
    "quantum_templates"
]
