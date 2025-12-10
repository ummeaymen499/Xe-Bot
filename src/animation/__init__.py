"""
Animation package initialization
"""
from src.animation.generator import ManimAnimationGenerator, animation_generator, AnimationResult
from src.animation.templates import AnimationTemplates, templates

__all__ = [
    "ManimAnimationGenerator",
    "animation_generator", 
    "AnimationResult",
    "AnimationTemplates",
    "templates"
]
