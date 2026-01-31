from abc import ABC, abstractmethod
from typing import Tuple, Optional
from PIL import Image
from utils.logger import LoggerMixin


class BaseGrounding(ABC, LoggerMixin):
    """
    Abstract base class for all grounding strategies.
    
    A grounding strategy locates UI elements on screen and returns their coordinates.
    """
    
    def __init__(self, name: str = None):
        """
        Initialize grounding strategy.
        
        Args:
            name: Optional name for this strategy
        """
        self.name = name or self.__class__.__name__
        self.logger.info(f"Initialized {self.name} grounding strategy")
    
    @abstractmethod
    def locate(
        self,
        screenshot: Image.Image,
        target: str,
        **kwargs
    ) -> Optional[Tuple[int, int]]:
        """
        Locate a target element on the screenshot.
        
        Args:
            screenshot: PIL Image of the screen
            target: Target to locate (interpretation depends on strategy)
            **kwargs: Additional strategy-specific parameters
        
        Returns:
            Tuple of (x, y) coordinates if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_confidence(self) -> float:
        """
        Get confidence score of last detection.
        
        Returns:
            Float between 0 and 1, or -1 if no detection was made
        """
        pass
    
    def validate_result(
        self,
        coords: Tuple[int, int],
        screenshot: Image.Image
    ) -> bool:
        """
        Validate that coordinates are within screenshot bounds.
        
        Args:
            coords: (x, y) coordinates
            screenshot: Screenshot image
        
        Returns:
            True if coordinates are valid
        """
        if coords is None:
            return False
        
        x, y = coords
        width, height = screenshot.size
        
        if not (0 <= x < width and 0 <= y < height):
            self.logger.warning(
                f"Coordinates ({x}, {y}) out of bounds for {width}x{height} screen"
            )
            return False
        
        return True
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


class MultiStrategyGrounding(LoggerMixin):
    """
    Combines multiple grounding strategies with fallback logic.
    Tries strategies in order until one succeeds.
    """
    
    def __init__(self, strategies: list = None):
        """
        Initialize with list of grounding strategies.
        
        Args:
            strategies: List of BaseGrounding instances
        """
        self.strategies = strategies or []
        self.last_successful_strategy = None
        self.logger.info(f"Initialized MultiStrategy with {len(self.strategies)} strategies")
    
    def add_strategy(self, strategy: BaseGrounding):
        """Add a grounding strategy to the list."""
        if not isinstance(strategy, BaseGrounding):
            raise TypeError("Strategy must inherit from BaseGrounding")
        
        self.strategies.append(strategy)
        self.logger.debug(f"Added strategy: {strategy.name}")
    
    def locate(
        self,
        screenshot: Image.Image,
        target: str,
        **kwargs
    ) -> Optional[Tuple[int, int]]:
        """
        Try each strategy in order until one succeeds.
        
        Args:
            screenshot: PIL Image of screen
            target: Target to locate
            **kwargs: Parameters passed to each strategy
        
        Returns:
            Coordinates if any strategy succeeds, None otherwise
        """
        self.logger.info(f"Attempting to locate '{target}' using {len(self.strategies)} strategies")
        
        for i, strategy in enumerate(self.strategies, 1):
            self.logger.debug(f"Trying strategy {i}/{len(self.strategies)}: {strategy.name}")
            
            try:
                coords = strategy.locate(screenshot, target, **kwargs)
                
                if coords and strategy.validate_result(coords, screenshot):
                    confidence = strategy.get_confidence()
                    self.logger.info(
                        f"✓ Strategy '{strategy.name}' succeeded at {coords} "
                        f"(confidence: {confidence:.2f})"
                    )
                    self.last_successful_strategy = strategy
                    return coords
                else:
                    self.logger.debug(f"Strategy '{strategy.name}' found no match")
                    
            except Exception as e:
                self.logger.warning(f"Strategy '{strategy.name}' failed: {e}")
                continue
        
        self.logger.warning(f"✗ All {len(self.strategies)} strategies failed to locate '{target}'")
        return None
    
    def get_last_strategy(self) -> Optional[BaseGrounding]:
        """Get the last successful strategy."""
        return self.last_successful_strategy


if __name__ == "__main__":
    # Example usage (won't run without concrete implementations)
    print("BaseGrounding is an abstract class")
    print("Create concrete implementations like TemplateGrounding, OCRGrounding, etc.")
