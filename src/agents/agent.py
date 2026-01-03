import abc
import base64
from io import BytesIO
from PIL import Image

from domain.request import AgentPredictionResponse
from utils import VIEWPORT_SIZE


class Agent(abc.ABC):

    def __init__(
            self,
            name: str,
            max_images_in_history: int = 3,
            image_size: tuple[int, int] = (1920, 1080),
            screen_size: tuple[int, int] = VIEWPORT_SIZE,
    ):
        self.name = name
        self.max_images_in_history = max_images_in_history
        self.image_size = image_size
        self.screen_size = screen_size

        self.history = []

    def resize_screenshot(self, screenshot: str):
        """
        Resize the screenshot to fit the agent's defined size
        :param screenshot: base64 encoded screenshot
        :return: resized base64 encoded screenshot given self.image_size
        """
        if VIEWPORT_SIZE == self.image_size:
            return screenshot

        img_bytes = base64.b64decode(screenshot)
        img = Image.open(BytesIO(img_bytes))


        img = img.resize(self.image_size, Image.Resampling.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="PNG")

        resized_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return resized_b64

    def resize_coords_to_original(self, coords: tuple[int, int]):
        """
        Resize coordinates from the agent's image size back to the original viewport size
        :param coords: (x, y) coordinates in the agent's image space
        :return: (x, y) coordinates in the original viewport space
        """
        if VIEWPORT_SIZE == self.image_size:
            return coords

        x, y = coords
        src_w, src_h = self.image_size
        dst_w, dst_h = VIEWPORT_SIZE

        scale_x = dst_w / src_w
        scale_y = dst_h / src_h

        orig_x = int(round(x * scale_x))
        orig_y = int(round(y * scale_y))

        return orig_x, orig_y

    def map_cords_to_orig_cords(self, cords: tuple[int, int]):
        """
        Map coordinates from the agent image space (self.image_size)
        back to the original viewport space (VIEWPORT_SIZE).
        """
        # If sizes are equal, no mapping is necessary
        if self.image_size == VIEWPORT_SIZE:
            return cords

        if not cords or len(cords) != 2:
            raise ValueError("cords must be a tuple of (x, y)")

        x, y = cords
        src_w, src_h = self.image_size
        dst_w, dst_h = VIEWPORT_SIZE

        if src_w == 0 or src_h == 0:
            raise ValueError("self.image_size must have non-zero dimensions")

        scale_x = dst_w / src_w
        scale_y = dst_h / src_h

        mapped_x = int(round(x * scale_x))
        mapped_y = int(round(y * scale_y))

        # Clamp to viewport bounds just in case
        mapped_x = max(0, min(dst_w - 1, mapped_x))
        mapped_y = max(0, min(dst_h - 1, mapped_y))

        return mapped_x, mapped_y

    @abc.abstractmethod
    def predict(self, screenshot: str, task) -> AgentPredictionResponse:
        pass

    def reset(self):
        self.history = []

    def get_config(self):
       return vars(self)
