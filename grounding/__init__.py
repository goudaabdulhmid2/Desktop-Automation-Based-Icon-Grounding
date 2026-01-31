from .base_grounding import BaseGrounding, MultiStrategyGrounding
from .screenshot import ScreenCapture
from .template_grounding import TemplateGrounding, AdaptiveTemplateGrounding
from .ocr_grounding import OCRGrounding, FuzzyOCRGrounding


__all__ = [
    'BaseGrounding',
    'MultiStrategyGrounding',
    'ScreenCapture',
    'TemplateGrounding',
    'AdaptiveTemplateGrounding',
    'OCRGrounding',
    'FuzzyOCRGrounding',
]