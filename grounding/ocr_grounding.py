from typing import Tuple, Optional, List
from PIL import Image
import numpy as np
import config
from grounding.base_grounding import BaseGrounding

try:
    import easyocr
    import ssl
    # Fix SSL certificate issues
    ssl._create_default_https_context = ssl._create_unverified_context
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class OCRGrounding(BaseGrounding):
    """
    Locate UI elements by detecting text using OCR.
    Good for finding buttons, labels, and icons with text.
    """
    
    def __init__(
        self,
        languages: List[str] = None,
        confidence_threshold: float = None,
        use_gpu: bool = False,
        name: str = "OCR"
    ):
        """
        Initialize OCR grounding.
        
        Args:
            languages: List of language codes (default: ['en'])
            confidence_threshold: Minimum confidence for detections
            use_gpu: Whether to use GPU acceleration
            name: Name for this strategy
        """
        super().__init__(name)
        
        if not OCR_AVAILABLE:
            self.logger.error("EasyOCR not installed. Install with: pip install easyocr")
            raise ImportError("EasyOCR is required for OCR grounding")
        
        self.languages = languages or ['en']
        self.confidence_threshold = confidence_threshold or config.OCR_CONFIDENCE_THRESHOLD
        self.last_confidence = -1
        self.last_detections = []
        
        self.logger.info(f"Initializing EasyOCR reader (languages: {self.languages})...")
        self.reader = easyocr.Reader(self.languages, gpu=use_gpu)
        self.logger.info("EasyOCR reader initialized")
    
    def locate(
        self,
        screenshot: Image.Image,
        target: str,
        case_sensitive: bool = False,
        exact_match: bool = False
    ) -> Optional[Tuple[int, int]]:
        """
        Locate target text using OCR.
        
        Args:
            screenshot: PIL Image of screen
            target: Text to search for
            case_sensitive: Whether to match case
            exact_match: If True, require exact match; otherwise partial match
        
        Returns:
            (x, y) coordinates of text center, or None if not found
        """
        self.logger.debug(f"OCR searching for text: '{target}'")
        
        # Convert PIL Image to numpy array for EasyOCR
        img_np = np.array(screenshot)
        
        try:
            # Perform OCR
            results = self.reader.readtext(img_np)
            self.last_detections = results
            
            self.logger.debug(f"OCR detected {len(results)} text regions")
            
            # Find best match
            best_match = None
            best_confidence = 0.0
            
            for bbox, text, confidence in results:
                # Log all detections for debugging
                self.logger.debug(f"  Detected: '{text}' (confidence: {confidence:.3f})")
                
                # Skip low confidence detections
                if confidence < self.confidence_threshold:
                    continue
                
                # Prepare texts for comparison
                detected_text = text.strip()
                search_text = target.strip()
                
                if not case_sensitive:
                    detected_text = detected_text.lower()
                    search_text = search_text.lower()
                
                # Check for match
                is_match = False
                if exact_match:
                    is_match = (detected_text == search_text)
                else:
                    is_match = (search_text in detected_text)
                
                if is_match and confidence > best_confidence:
                    # Calculate center of bounding box
                    x_coords = [p[0] for p in bbox]
                    y_coords = [p[1] for p in bbox]
                    cx = int(sum(x_coords) / len(x_coords))
                    cy = int(sum(y_coords) / len(y_coords))
                    
                    best_match = (cx, cy)
                    best_confidence = confidence
                    
                    self.logger.debug(
                        f"  Match! '{text}' at ({cx}, {cy}) "
                        f"[confidence: {confidence:.3f}]"
                    )
            
            if best_match:
                self.last_confidence = best_confidence
                self.logger.info(
                    f"✓ OCR found '{target}' at {best_match} "
                    f"[confidence: {best_confidence:.3f}]"
                )
                return best_match
            else:
                self.logger.debug(f"✗ OCR did not find '{target}'")
                self.last_confidence = 0.0
                return None
                
        except Exception as e:
            self.logger.error(f"OCR error: {e}")
            self.last_confidence = -1
            return None
    
    def get_confidence(self) -> float:
        """Get confidence of last match."""
        return self.last_confidence
    
    def get_all_text(self, screenshot: Image.Image) -> List[Tuple[str, float, Tuple[int, int]]]:
        """
        Extract all text from screenshot.
        
        Args:
            screenshot: PIL Image of screen
        
        Returns:
            List of (text, confidence, (x, y)) tuples
        """
        img_np = np.array(screenshot)
        results = self.reader.readtext(img_np)
        
        text_results = []
        for bbox, text, confidence in results:
            x_coords = [p[0] for p in bbox]
            y_coords = [p[1] for p in bbox]
            cx = int(sum(x_coords) / len(x_coords))
            cy = int(sum(y_coords) / len(y_coords))
            
            text_results.append((text, confidence, (cx, cy)))
        
        return text_results
    
    def find_multiple(
        self,
        screenshot: Image.Image,
        target: str,
        max_results: int = None
    ) -> List[Tuple[int, int, float]]:
        """
        Find all instances of target text.
        
        Args:
            screenshot: PIL Image of screen
            target: Text to search for
            max_results: Maximum number of results to return
        
        Returns:
            List of (x, y, confidence) tuples
        """
        img_np = np.array(screenshot)
        results = self.reader.readtext(img_np)
        
        matches = []
        for bbox, text, confidence in results:
            if target.lower() in text.strip().lower() and \
               confidence >= self.confidence_threshold:
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]
                cx = int(sum(x_coords) / len(x_coords))
                cy = int(sum(y_coords) / len(y_coords))
                
                matches.append((cx, cy, confidence))
        
        # Sort by confidence
        matches.sort(key=lambda x: x[2], reverse=True)
        
        if max_results:
            matches = matches[:max_results]
        
        return matches


class FuzzyOCRGrounding(OCRGrounding):
    """
    OCR grounding with fuzzy matching for better tolerance.
    Handles slight variations in text.
    """
    
    def __init__(
        self,
        languages: List[str] = None,
        confidence_threshold: float = None,
        fuzzy_threshold: float = 0.8,
        name: str = "FuzzyOCR"
    ):
        """
        Initialize fuzzy OCR grounding.
        
        Args:
            languages: OCR languages
            confidence_threshold: Minimum OCR confidence
            fuzzy_threshold: Minimum string similarity (0-1)
            name: Name for this strategy
        """
        super().__init__(languages, confidence_threshold, False, name)
        self.fuzzy_threshold = fuzzy_threshold
        
        try:
            from difflib import SequenceMatcher
            self.matcher = SequenceMatcher
            self.logger.info(f"Fuzzy matching enabled (threshold: {fuzzy_threshold})")
        except ImportError:
            self.logger.warning("difflib not available, falling back to substring matching")
            self.matcher = None
    
    def _fuzzy_match(self, text1: str, text2: str) -> float:
        """Calculate fuzzy similarity between two strings."""
        if self.matcher:
            return self.matcher(None, text1.lower(), text2.lower()).ratio()
        else:
            # Simple fallback: check if one is substring of other
            t1, t2 = text1.lower(), text2.lower()
            if t1 in t2 or t2 in t1:
                return 0.9
            return 0.0
    
    def locate(
        self,
        screenshot: Image.Image,
        target: str,
        **kwargs
    ) -> Optional[Tuple[int, int]]:
        """
        Locate target text using fuzzy matching.
        
        Args:
            screenshot: PIL Image of screen
            target: Text to search for
        
        Returns:
            Coordinates of best match
        """
        img_np = np.array(screenshot)
        results = self.reader.readtext(img_np)
        
        best_match = None
        best_score = 0.0
        
        for bbox, text, ocr_conf in results:
            if ocr_conf < self.confidence_threshold:
                continue
            
            # Calculate fuzzy similarity
            similarity = self._fuzzy_match(text.strip(), target.strip())
            
            # Combined score: OCR confidence * fuzzy similarity
            combined_score = ocr_conf * similarity
            
            if similarity >= self.fuzzy_threshold and combined_score > best_score:
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]
                cx = int(sum(x_coords) / len(x_coords))
                cy = int(sum(y_coords) / len(y_coords))
                
                best_match = (cx, cy)
                best_score = combined_score
                
                self.logger.debug(
                    f"Fuzzy match: '{text}' vs '{target}' "
                    f"(similarity: {similarity:.3f}, score: {combined_score:.3f})"
                )
        
        if best_match:
            self.last_confidence = best_score
            self.logger.info(f"✓ Fuzzy OCR found match at {best_match} (score: {best_score:.3f})")
        else:
            self.last_confidence = 0.0
            self.logger.debug("✗ No fuzzy match found")
        
        return best_match


if __name__ == "__main__":
    # Test OCR grounding
    print("Testing OCRGrounding...")
    
    if not OCR_AVAILABLE:
        print("EasyOCR not available. Install it to test OCR grounding.")
    else:
        print("OCR grounding would initialize here")
        print("Note: Actual testing requires a screenshot with text")
