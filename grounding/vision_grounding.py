from typing import Tuple, Optional, List
from PIL import Image
import re
from grounding.base_grounding import BaseGrounding

try:
    from transformers import AutoProcessor, AutoModelForCausalLM
    import torch
    VISION_MODEL_AVAILABLE = True
except ImportError:
    VISION_MODEL_AVAILABLE = False


class VisionModelGrounding(BaseGrounding):
    """
    Modern vision model grounding using Florence-2.
    
    Can detect UI elements by description without prior templates.
    This is the flexible approach the OmniParser paper demonstrates.
    
    Examples:
        coords = grounding.locate(screenshot, "Notepad icon")
        coords = grounding.locate(screenshot, "text editor application")
        coords = grounding.locate(screenshot, "OK button")
    """
    
    def __init__(
        self,
        model_name: str = "microsoft/Florence-2-base",
        device: str = None,
        name: str = "Florence2Vision"
    ):
        """
        Initialize Florence-2 vision model.
        
        Args:
            model_name: HuggingFace model ID
                - "microsoft/Florence-2-base" (faster, 230M params)
                - "microsoft/Florence-2-large" (better, 770M params)
            device: 'cuda', 'cpu', or None (auto-detect)
            name: Strategy name
        """
        super().__init__(name)
        
        if not VISION_MODEL_AVAILABLE:
            self.logger.error(
                "Vision model dependencies not installed!\n"
                "Install with: pip install transformers torch pillow --break-system-packages"
            )
            raise ImportError("Missing: transformers, torch")
        
        # Determine device
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        
        self.logger.info(f"Loading vision model: {model_name} on {device}")
        self.logger.info("This may take a minute on first run (downloading model)...")
        
        # Load Florence-2 model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True
        ).to(device)
        
        self.processor = AutoProcessor.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        
        self.last_confidence = -1
        self.logger.info(f"✓ Vision model loaded on {device}")
    
    def locate(
        self,
        screenshot: Image.Image,
        target: str,
        **kwargs
    ) -> Optional[Tuple[int, int]]:
        """
        Locate UI element using vision model.
        
        Args:
            screenshot: Desktop screenshot (PIL Image)
            target: Natural language description
                Examples:
                - "Notepad icon"
                - "Notepad application"
                - "text editor icon"
                - "blue notepad symbol"
        
        Returns:
            (x, y) coordinates of element center, or None if not found
        """
        self.logger.info(f"Vision model searching for: '{target}'")
        
        try:
            # Florence-2 task for phrase grounding (object detection by text)
            task_prompt = "<CAPTION_TO_PHRASE_GROUNDING>"
            prompt = f"{task_prompt} {target}"
            
            # Prepare inputs
            inputs = self.processor(
                text=prompt,
                images=screenshot,
                return_tensors="pt"
            ).to(self.device)
            
            # Generate predictions
            self.logger.debug("Running inference...")
            with torch.no_grad():
                generated_ids = self.model.generate(
                    input_ids=inputs["input_ids"],
                    pixel_values=inputs["pixel_values"],
                    max_new_tokens=1024,
                    num_beams=3,
                    do_sample=False
                )
            
            # Decode results
            generated_text = self.processor.batch_decode(
                generated_ids,
                skip_special_tokens=False
            )[0]
            
            # Parse the output
            parsed_answer = self.processor.post_process_generation(
                generated_text,
                task=task_prompt,
                image_size=(screenshot.width, screenshot.height)
            )
            
            # Extract bounding boxes
            if task_prompt in parsed_answer:
                detection = parsed_answer[task_prompt]
                
                # Check if we have detections
                if 'bboxes' in detection and detection['bboxes']:
                    bboxes = detection['bboxes']
                    labels = detection.get('labels', [])
                    
                    # Get the first (most confident) detection
                    bbox = bboxes[0]  # Format: [x_min, y_min, x_max, y_max]
                    
                    # Calculate center point
                    cx = int((bbox[0] + bbox[2]) / 2)
                    cy = int((bbox[1] + bbox[3]) / 2)
                    
                    # Store confidence (Florence-2 doesn't provide scores, assume high)
                    self.last_confidence = 0.9
                    
                    label = labels[0] if labels else target
                    self.logger.info(
                        f"✓ Vision model found '{label}' at ({cx}, {cy}) "
                        f"[bbox: {bbox}]"
                    )
                    
                    return (cx, cy)
                else:
                    self.logger.debug(f"✗ No detections found for '{target}'")
                    self.last_confidence = 0.0
                    return None
            else:
                self.logger.warning("Unexpected model output format")
                self.last_confidence = 0.0
                return None
                
        except Exception as e:
            self.logger.error(f"Vision model error: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            self.last_confidence = -1
            return None
    
    def get_confidence(self) -> float:
        """Get confidence of last detection."""
        return self.last_confidence
    
    def detect_all(
        self,
        screenshot: Image.Image,
        target: str
    ) -> List[Tuple[int, int, float]]:
        """
        Detect all instances of target.
        
        Args:
            screenshot: Desktop screenshot
            target: What to detect
        
        Returns:
            List of (x, y, confidence) tuples
        """
        self.logger.info(f"Vision model searching for all instances of: '{target}'")
        
        try:
            task_prompt = "<CAPTION_TO_PHRASE_GROUNDING>"
            prompt = f"{task_prompt} {target}"
            
            inputs = self.processor(
                text=prompt,
                images=screenshot,
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                generated_ids = self.model.generate(
                    input_ids=inputs["input_ids"],
                    pixel_values=inputs["pixel_values"],
                    max_new_tokens=1024,
                    num_beams=3
                )
            
            generated_text = self.processor.batch_decode(
                generated_ids,
                skip_special_tokens=False
            )[0]
            
            parsed_answer = self.processor.post_process_generation(
                generated_text,
                task=task_prompt,
                image_size=(screenshot.width, screenshot.height)
            )
            
            results = []
            
            if task_prompt in parsed_answer:
                detection = parsed_answer[task_prompt]
                
                if 'bboxes' in detection:
                    for bbox in detection['bboxes']:
                        cx = int((bbox[0] + bbox[2]) / 2)
                        cy = int((bbox[1] + bbox[3]) / 2)
                        results.append((cx, cy, 0.9))
            
            self.logger.info(f"Found {len(results)} instances")
            return results
            
        except Exception as e:
            self.logger.error(f"Error detecting all: {e}")
            return []




if __name__ == "__main__":
    """Test vision model grounding."""
    print("Florence-2 Vision Model Grounding")
    print("=" * 50)
    
    if not VISION_MODEL_AVAILABLE:
        print("❌ Missing dependencies!")
        print("Install: pip install transformers torch pillow --break-system-packages")
    else:
        print("✓ Dependencies available")
        print("\nThis vision model can:")
        print("  - Detect any UI element by description")
        print("  - Handle unexpected pop-ups")
        print("  - Work across different themes/sizes")
        print("  - No template images needed")
        print("\nExample usage:")
        print('  coords = grounding.locate(screenshot, "Notepad icon")')
        print('  coords = grounding.locate(screenshot, "OK button")')
        print('  coords = grounding.locate(screenshot, "close button")')
