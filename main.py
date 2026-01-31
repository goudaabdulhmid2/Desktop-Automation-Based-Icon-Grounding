import sys
import time
from pathlib import Path

import config
from utils import setup_file_logger
from utils.retry import retry_on_exception
from data import PostAPIClient
from automation import NotepadController
from grounding import (
    MultiStrategyGrounding,
    AdaptiveTemplateGrounding,
    FuzzyOCRGrounding,
    ScreenCapture
)

# Set up logging
logger = setup_file_logger(__name__, level=config.LOG_LEVEL)


class DesktopAutomationWorkflow:
    """
    Main workflow orchestrator for desktop automation.
    Coordinates grounding, data fetching, and Notepad automation.
    """
    
    def __init__(self):
        """Initialize workflow with all necessary components."""
        logger.info("=" * 70)
        logger.info("INITIALIZING DESKTOP AUTOMATION WORKFLOW")
        logger.info("=" * 70)
        
        # Ensure directories exist
        config.ensure_directories()
        
        # Validate configuration
        errors = config.validate_config()
        if errors:
            for error in errors:
                logger.warning(error)
        
        # Initialize components
        logger.info("Initializing components...")
        
        # 1. API Client
        self.api_client = PostAPIClient()
        
        # 2. Notepad Controller
        self.notepad_controller = NotepadController()
        
        # 3. Screen Capture
        self.screen_capture = ScreenCapture()
        
        # 4. Grounding System - Multi-strategy with fallbacks
        self.grounding_system = self._setup_grounding()
        
        logger.info("✓ All components initialized")
        logger.info("=" * 70)
    
    def _setup_grounding(self) -> MultiStrategyGrounding:
        """
        Set up multi-strategy grounding system.
        Prioritizes vision model for maximum flexibility.
        
        Returns:
            Configured MultiStrategyGrounding instance
        """
        logger.info("Setting up grounding strategies...")
        
        grounding = MultiStrategyGrounding()
        
        # Strategy 1: Adaptive Template Matching (Primary - fast and reliable)
        try:
            template_strategy = AdaptiveTemplateGrounding(
                template_path=config.TEMPLATE_PATH,
                thresholds=[0.9, 0.8, 0.7, 0.6],
                name="AdaptiveTemplate"
            )
            grounding.add_strategy(template_strategy)
            logger.info("  ✓ Added AdaptiveTemplate strategy (Primary)")
        except Exception as e:
            logger.warning(f"  ⚠ Could not add template strategy: {e}")
            logger.info("    (Ensure resources/notepad_icon.png exists)")
        
        # Strategy 2: Fuzzy OCR (Fallback - for text-based icons)
        try:
            ocr_strategy = FuzzyOCRGrounding(
                languages=['en'],
                confidence_threshold=0.5,
                fuzzy_threshold=0.7,
                name="FuzzyOCR"
            )
            grounding.add_strategy(ocr_strategy)
            logger.info("  ✓ Added FuzzyOCR strategy (Fallback)")
        except Exception as e:
            logger.warning(f"  ⚠ Could not add OCR strategy: {e}")
        
        if len(grounding.strategies) == 0:
            raise RuntimeError(
                "No grounding strategies available! Please fix configuration:\n"
                "  Template: Create resources/notepad_icon.png\n"
                "  OCR: pip install easyocr --break-system-packages"
            )
        
        logger.info(f"Grounding system ready with {len(grounding.strategies)} strategies")
        logger.info("=" * 70)
        return grounding
    
    @retry_on_exception(max_attempts=config.MAX_GROUNDING_ATTEMPTS, delay=config.GROUNDING_RETRY_DELAY)
    def locate_notepad_icon(self) -> tuple:
        """
        Locate Notepad icon on desktop with retry logic.
        
        Returns:
            Tuple of (coordinates, screenshot)
        
        Raises:
            RuntimeError: If icon cannot be located after all retries
        """
        logger.info("Capturing desktop screenshot...")
        screenshot = self.screen_capture.capture_screen()
        
        logger.info("Searching for Notepad icon...")
        coords = self.grounding_system.locate(screenshot, "Notepad")
        
        if not coords:
            raise RuntimeError("Could not locate Notepad icon")
        
        logger.info(f"✓ Notepad icon located at {coords}")
        
        # Save debug screenshot if enabled
        if config.SAVE_DEBUG_SCREENSHOTS:
            self.screen_capture.save_debug_screenshot(
                screenshot,
                coords,
                label="Notepad Icon",
                prefix="notepad_grounding"
            )
        
        return coords, screenshot
    
    def process_posts(self, posts: list, target_name: str = "Notepad") -> dict:
        """
        Process all posts - main automation loop.
        
        Args:
            posts: List of post dictionaries
            target_name: Name of target application (for grounding)
        
        Returns:
            Dictionary with processing statistics
        """
        logger.info("=" * 70)
        logger.info(f"PROCESSING {len(posts)} POSTS")
        logger.info("=" * 70)
        
        stats = {
            'total': len(posts),
            'successful': 0,
            'failed': 0,
            'failed_posts': []
        }
        
        for i, post in enumerate(posts, 1):
            post_id = post['id']
            filename = f"post_{post_id}.txt"
            filepath = config.OUTPUT_DIR / filename
            
            logger.info("")
            logger.info(f"[{i}/{len(posts)}] Processing Post ID: {post_id}")
            logger.info(f"  Title: {post['title']}")
            logger.info(f"  Filename: {filename}")
            
            # Check if file already exists
            if filepath.exists():
                logger.info(f"  File exists, removing: {filepath}")
                filepath.unlink()
            
            try:
                # 1. Locate Notepad icon (fresh screenshot each time)
                logger.info("  Step 1: Locating Notepad icon...")
                coords, screenshot = self.locate_notepad_icon()
                
                # 2. Prepare content
                content = self.api_client.format_post_content(post)
                
                # 3. Execute Notepad workflow
                logger.info("  Step 2: Executing Notepad workflow...")
                success = self.notepad_controller.write_post_to_file(
                    content=content,
                    filepath=filepath,
                    coords=coords
                )
                
                if success:
                    stats['successful'] += 1
                    logger.info(f"  ✓ Post {post_id} completed successfully")
                else:
                    stats['failed'] += 1
                    stats['failed_posts'].append(post_id)
                    logger.error(f"  ✗ Post {post_id} failed")
                
                # Small delay between posts
                time.sleep(0.5)
                
            except Exception as e:
                stats['failed'] += 1
                stats['failed_posts'].append(post_id)
                logger.error(f"  ✗ Post {post_id} failed with exception: {e}")
                
                # Cleanup on error
                self.notepad_controller.cleanup_all_notepad_windows()
        
        return stats
    
    def run(self, posts_count: int = None):
        """
        Main execution method.
        
        Args:
            posts_count: Number of posts to process (None = use config default)
        """
        posts_count = posts_count or config.POSTS_COUNT
        
        logger.info(f"Starting automation workflow in {config.STARTUP_DELAY} seconds...")
        logger.info("Please ensure Notepad shortcut is on desktop!")
        time.sleep(config.STARTUP_DELAY)
        
        try:
            # 1. Fetch posts
            logger.info("Fetching blog posts...")
            posts = self.api_client.fetch_posts_with_fallback(count=posts_count)
            logger.info(f"✓ Retrieved {len(posts)} posts")
            
            # 2. Validate posts
            posts = self.api_client.validate_posts(posts)
            logger.info(f"✓ Validated {len(posts)} posts")
            
            if not posts:
                logger.error("No valid posts to process!")
                return
            
            # 3. Process posts
            stats = self.process_posts(posts)
            
            # 4. Print summary
            logger.info("")
            logger.info("=" * 70)
            logger.info("WORKFLOW COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Total posts:      {stats['total']}")
            logger.info(f"Successful:       {stats['successful']}")
            logger.info(f"Failed:           {stats['failed']}")
            
            if stats['failed_posts']:
                logger.info(f"Failed post IDs:  {stats['failed_posts']}")
            
            logger.info(f"Output directory: {config.OUTPUT_DIR}")
            logger.info("=" * 70)
            
        except KeyboardInterrupt:
            logger.warning("\n\nWorkflow interrupted by user")
            self.notepad_controller.cleanup_all_notepad_windows()
            
        except Exception as e:
            logger.exception("Workflow failed with unexpected error")
            self.notepad_controller.cleanup_all_notepad_windows()
            raise


def main():
    """Entry point for the application."""
    try:
        # Create and run workflow
        workflow = DesktopAutomationWorkflow()
        workflow.run()
        
        logger.info("\n✓ Automation completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"\n✗ Automation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())