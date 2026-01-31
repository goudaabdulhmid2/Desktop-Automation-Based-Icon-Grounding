from .base_grounding import BaseGrounding, MultiStrategyGrounding
from .screenshot import ScreenCapture
from .template_grounding import TemplateGrounding, AdaptiveTemplateGrounding
from .ocr_grounding import OCRGrounding, FuzzyOCRGrounding

# Vision model is optional (requires transformers + torch)
try:
    from .vision_grounding import VisionModelGrounding
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    VisionModelGrounding = None

__all__ = [
    'BaseGrounding',
    'MultiStrategyGrounding',
    'ScreenCapture',
    'TemplateGrounding',
    'AdaptiveTemplateGrounding',
    'OCRGrounding',
    'FuzzyOCRGrounding',
    'VisionModelGrounding',
    'VISION_AVAILABLE',
]