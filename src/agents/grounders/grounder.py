import abc
import base64
import io
from typing import Tuple

from PIL import Image
from loguru import logger

from utils import VIEWPORT_SIZE


class GroundingError(Exception):
    """Raised when the grounder cannot extract coordinates from the LLM response."""
    pass


class Grounder(abc.ABC):
    def __init__(self, image_size: Tuple[int, int] = None, action_space_size: Tuple[int, int] = None):
        self.image_size = image_size if image_size else VIEWPORT_SIZE
        self.action_space_size = action_space_size if action_space_size else image_size

    def _resize_image(self, screenshot: str) -> str:
        """Resize base64 encoded image to self.image_size and return resized base64 image."""
        if VIEWPORT_SIZE == self.image_size:
            return screenshot
        image_bytes = base64.b64decode(screenshot)
        
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Resize to target size
        resized_image = image.resize(self.image_size, Image.Resampling.LANCZOS)
        
        # Convert back to base64
        buffer = io.BytesIO()
        resized_image.save(buffer, format=image.format or "PNG")
        resized_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return resized_base64

    def _resize_coords_to_viewport(self, pred_coords: tuple[int, int]) -> tuple[int, int]:
        x, y = pred_coords
        
        # Calculate scale factors
        scale_x = VIEWPORT_SIZE[0] / self.action_space_size[0]
        scale_y = VIEWPORT_SIZE[1] / self.action_space_size[1]
        
        # Scale coordinates back to viewport
        viewport_x = int(x * scale_x)
        viewport_y = int(y * scale_y)
        
        return (viewport_x, viewport_y)
    
    def locate_ui_element_coords(self, screenshot: str, ui_element: str) -> tuple[int, int]:
        resized_image = self._resize_image(screenshot)
        coords, usage = self._locate_ui_element_coords_raw(resized_image, ui_element)
        logger.info(f"Grounder localized {coords} for element '{ui_element}'")
        resized_coords = self._resize_coords_to_viewport(coords)
        logger.info(f"Resized coords to viewport: {resized_coords}")
        return resized_coords, usage
    

    @abc.abstractmethod
    def _locate_ui_element_coords_raw(self, screenshot: str, ui_element: str) -> tuple[int, int]:
        pass    


