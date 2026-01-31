from pathlib import Path
from typing import Tuple, Optional
from PIL import Image
import numpy as np
import config
from grounding.base_grounding import BaseGrounding

try:
    from botcity.core import DesktopBot
    BOTCITY_AVAILABLE = True
except ImportError:
    BOTCITY_AVAILABLE = False


class TemplateGrounding(BaseGrounding):
    """
    Locate UI elements using template matching.
    Requires a reference image of the target element.
    """
    
    def __init__(
        self,
        template_path: Path = None,
        threshold: float = None,
        name: str = "TemplateMatching"
    ):
        """
        Initialize template grounding.
        
        Args:
            template_path: Path to template image
            threshold: Matching threshold (0-1), lower is more lenient
            name: Name for this strategy
        """
        super().__init__(name)
        
        if not BOTCITY_AVAILABLE:
            self.logger.error("BotCity not installed. Install with: pip install botcity-core")
            raise ImportError("BotCity is required for template matching")
        
        self.template_path = template_path or config.TEMPLATE_PATH
        self.threshold = threshold or config.TEMPLATE_MATCH_THRESHOLD
        self.last_confidence = -1
        
        # Initialize BotCity
        self.bot = DesktopBot()
        
        # Validate and load template
        if not self.template_path.exists():
            self.logger.error(f"Template not found: {self.template_path}")
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        
        # Register template with BotCity
        template_name = "target_icon"
        abs_path = self.template_path.absolute()
        self.bot.add_image(template_name, str(abs_path))
        self.template_name = template_name
        
        self.logger.info(f"Loaded template from: {self.template_path}")
        self.logger.info(f"Matching threshold: {self.threshold}")
    
    def locate(
        self,
        screenshot: Image.Image,
        target: str,
        threshold: float = None
    ) -> Optional[Tuple[int, int]]:
        """
        Locate target using template matching.
        
        Args:
            screenshot: PIL Image of screen (not used, BotCity captures internally)
            target: Target name (not used for template matching)
            threshold: Optional override for matching threshold
        
        Returns:
            (x, y) coordinates of template center, or None if not found
        """
        match_threshold = threshold or self.threshold
        
        self.logger.debug(
            f"Searching for template '{self.template_name}' "
            f"(threshold: {match_threshold})"
        )
        
        try:
            # BotCity's find method returns True/False
            found = self.bot.find(
                self.template_name,
                matching=match_threshold,
                waiting_time=2000  # 2 second timeout
            )
            
            if not found:
                self.logger.debug("Template not found")
                self.last_confidence = 0.0
                return None
            
            # Get the last matched element
            element = self.bot.get_last_element()
            
            # Calculate center coordinates
            x = element.left + (element.width // 2)
            y = element.top + (element.height // 2)
            
            # Store confidence if available
            self.last_confidence = getattr(element, 'score', match_threshold)
            
            self.logger.info(
                f"✓ Template found at ({x}, {y}) "
                f"[confidence: {self.last_confidence:.3f}]"
            )
            
            return (x, y)
            
        except Exception as e:
            self.logger.error(f"Template matching error: {e}")
            self.last_confidence = -1
            return None
    
    def get_confidence(self) -> float:
        """Get confidence of last match."""
        return self.last_confidence
    
    def update_threshold(self, threshold: float):
        """
        Update matching threshold.
        
        Args:
            threshold: New threshold value (0-1)
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        self.threshold = threshold
        self.logger.info(f"Updated matching threshold to {threshold}")
    
    def update_template(self, template_path: Path):
        """
        Update the template image.
        
        Args:
            template_path: Path to new template image
        """
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        self.template_path = template_path
        
        # Re-register with BotCity
        abs_path = template_path.absolute()
        self.bot.add_image(self.template_name, str(abs_path))
        
        self.logger.info(f"Updated template to: {template_path}")


class AdaptiveTemplateGrounding(TemplateGrounding):
    """
    Template matching with adaptive threshold.
    Tries multiple thresholds from strict to lenient.
    """
    
    def __init__(
        self,
        template_path: Path = None,
        thresholds: list = None,
        name: str = "AdaptiveTemplateMatching"
    ):
        """
        Initialize adaptive template grounding.
        
        Args:
            template_path: Path to template image
            thresholds: List of thresholds to try (high to low)
            name: Name for this strategy
        """
        # Initialize with highest threshold
        initial_threshold = thresholds[0] if thresholds else 0.9
        super().__init__(template_path, initial_threshold, name)
        
        # Default thresholds: strict to lenient
        self.thresholds = thresholds or [0.9, 0.8, 0.7, 0.6, 0.5]
        self.logger.info(f"Will try thresholds: {self.thresholds}")
    
    def locate(
        self,
        screenshot: Image.Image,
        target: str,
        **kwargs
    ) -> Optional[Tuple[int, int]]:
        """
        Try multiple thresholds until match is found.
        
        Returns:
            Coordinates of best match, or None
        """
        self.logger.debug(f"Trying {len(self.thresholds)} threshold levels")
        
        for i, threshold in enumerate(self.thresholds, 1):
            self.logger.debug(f"Attempt {i}/{len(self.thresholds)}: threshold={threshold}")
            
            coords = super().locate(screenshot, target, threshold=threshold)
            
            if coords:
                self.logger.info(
                    f"✓ Match found with threshold {threshold} "
                    f"(attempt {i}/{len(self.thresholds)})"
                )
                return coords
        
        self.logger.warning("✗ No match found at any threshold level")
        return None


if __name__ == "__main__":
    # Test template grounding
    print("Testing TemplateGrounding...")
    
    if not BOTCITY_AVAILABLE:
        print("BotCity not available. Install it to test template matching.")
    else:
        # This would need an actual template file to test
        print("Template grounding initialized successfully")
        print("Note: Actual testing requires a template image and desktop environment")
