import pyautogui
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
import config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ScreenCapture:
    """Handles screen capture operations."""
    
    @staticmethod
    def capture_screen(region: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
        """
        Capture screenshot of entire screen or specific region.
        
        Args:
            region: Optional tuple (left, top, width, height) for partial capture
        
        Returns:
            PIL Image of screenshot
        """
        try:
            if region:
                logger.debug(f"Capturing screen region: {region}")
                screenshot = pyautogui.screenshot(region=region)
            else:
                logger.debug("Capturing full screen")
                screenshot = pyautogui.screenshot()
            
            return screenshot
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            raise
    
    @staticmethod
    def save_screenshot(
        image: Image.Image,
        filename: str = None,
        directory: Path = None
    ) -> Path:
        """
        Save screenshot to file.
        
        Args:
            image: PIL Image to save
            filename: Optional filename (auto-generated if None)
            directory: Directory to save to (default: screenshots/)
        
        Returns:
            Path where screenshot was saved
        """
        if directory is None:
            directory = config.SCREENSHOTS_DIR
        
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.png"
        
        filepath = directory / filename
        image.save(filepath)
        logger.info(f"Screenshot saved: {filepath}")
        
        return filepath
    
    @staticmethod
    def mark_coordinates(
        image: Image.Image,
        coords: Tuple[int, int],
        label: str = None,
        color: str = "red",
        radius: int = 15
    ) -> Image.Image:
        """
        Draw a marker at specified coordinates on an image.
        
        Args:
            image: PIL Image to mark
            coords: (x, y) coordinates to mark
            label: Optional text label
            color: Marker color
            radius: Marker radius in pixels
        
        Returns:
            New PIL Image with marker drawn
        """
        img_copy = image.copy()
        draw = ImageDraw.Draw(img_copy)
        
        x, y = coords
        
        # Draw circle
        left_up = (x - radius, y - radius)
        right_down = (x + radius, y + radius)
        draw.ellipse([left_up, right_down], outline=color, width=4)
        
        # Draw crosshair
        draw.line([(x - radius - 5, y), (x + radius + 5, y)], fill=color, width=2)
        draw.line([(x, y - radius - 5), (x, y + radius + 5)], fill=color, width=2)
        
        # Add label if provided
        if label:
            try:
                # Try to use a nice font
                font = ImageFont.truetype("arial.ttf", 14)
            except:
                # Fall back to default font
                font = ImageFont.load_default()
            
            # Draw text with background
            text_bbox = draw.textbbox((x + radius + 10, y - 10), label, font=font)
            draw.rectangle(text_bbox, fill="white", outline=color)
            draw.text((x + radius + 10, y - 10), label, fill=color, font=font)
        
        logger.debug(f"Marked coordinates {coords} on image")
        return img_copy
    
    @staticmethod
    def save_debug_screenshot(
        image: Image.Image,
        coords: Tuple[int, int],
        label: str = None,
        prefix: str = "debug"
    ) -> Path:
        """
        Save a debug screenshot with marked coordinates.
        
        Args:
            image: PIL Image to save
            coords: Coordinates to mark
            label: Optional label for marker
            prefix: Filename prefix
        
        Returns:
            Path where debug screenshot was saved
        """
        if not config.SAVE_DEBUG_SCREENSHOTS:
            logger.debug("Debug screenshots disabled in config")
            return None
        
        # Mark the coordinates
        marked_image = ScreenCapture.mark_coordinates(
            image,
            coords,
            label=label,
            color=config.DEBUG_MARKER_COLOR,
            radius=config.DEBUG_MARKER_RADIUS
        )
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.png"
        
        # Save to screenshots directory
        filepath = ScreenCapture.save_screenshot(
            marked_image,
            filename=filename,
            directory=config.SCREENSHOTS_DIR
        )
        
        logger.info(f"Debug screenshot saved: {filepath}")
        return filepath
    
    @staticmethod
    def create_comparison_image(
        images: list,
        labels: list = None,
        layout: str = "horizontal"
    ) -> Image.Image:
        """
        Create a comparison image from multiple screenshots.
        
        Args:
            images: List of PIL Images
            labels: Optional list of labels for each image
            layout: "horizontal" or "vertical"
        
        Returns:
            Combined PIL Image
        """
        if not images:
            raise ValueError("No images provided")
        
        if layout == "horizontal":
            total_width = sum(img.width for img in images)
            max_height = max(img.height for img in images)
            combined = Image.new('RGB', (total_width, max_height), 'white')
            
            x_offset = 0
            for i, img in enumerate(images):
                combined.paste(img, (x_offset, 0))
                
                # Add label if provided
                if labels and i < len(labels):
                    draw = ImageDraw.Draw(combined)
                    draw.text((x_offset + 10, 10), labels[i], fill="red")
                
                x_offset += img.width
        
        else:  # vertical
            max_width = max(img.width for img in images)
            total_height = sum(img.height for img in images)
            combined = Image.new('RGB', (max_width, total_height), 'white')
            
            y_offset = 0
            for i, img in enumerate(images):
                combined.paste(img, (0, y_offset))
                
                # Add label if provided
                if labels and i < len(labels):
                    draw = ImageDraw.Draw(combined)
                    draw.text((10, y_offset + 10), labels[i], fill="red")
                
                y_offset += img.height
        
        return combined


if __name__ == "__main__":
    # Test screen capture
    print("Testing screen capture...")
    
    # Capture full screen
    screenshot = ScreenCapture.capture_screen()
    print(f"Captured screenshot: {screenshot.size}")
    
    # Save it
    path = ScreenCapture.save_screenshot(screenshot, "test_screenshot.png")
    print(f"Saved to: {path}")
    
    # Mark some coordinates
    marked = ScreenCapture.mark_coordinates(
        screenshot,
        (100, 100),
        label="Test Point",
        color="blue"
    )
    
    # Save debug screenshot
    debug_path = ScreenCapture.save_debug_screenshot(
        screenshot,
        (200, 200),
        label="Debug Test"
    )
    print(f"Debug screenshot: {debug_path}")
