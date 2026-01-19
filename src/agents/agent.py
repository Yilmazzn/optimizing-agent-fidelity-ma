import abc
import base64
from io import BytesIO
from PIL import Image
from typing import Any, Sequence

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

    def resize_coords_to_original(self, coords: Sequence[float]) -> tuple[int, int]:
        """
        Resize coordinates from the agent's image size back to the original viewport size
        :param coords: (x, y) coordinates in the agent's image space
        :return: [x, y] coordinates in the original viewport space (JSON-friendly array)
        """
        if VIEWPORT_SIZE == self.image_size:
            if not isinstance(coords, (list, tuple)) or len(coords) != 2:
                raise ValueError("coords must be a (x, y) pair")
            return (int(round(float(coords[0]))), int(round(float(coords[1]))))

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
    def predict(self, screenshot: str, task, python_output: dict = None, terminal_output: dict = None) -> AgentPredictionResponse:
        pass

    def reset(self):
        self.history = []

    def get_config(self):
        # Return a JSON-friendly snapshot of the agent's attributes.
        # Keeps only: None/bool/int/float/str, dict, list (recursively).
        # Drops any other objects (clients, locks, classes, etc.).
        config = vars(self).copy()
        config.pop("history", None)
        return _json_friendly(config)


_SKIP = object()


def _json_friendly_scalar(value: Any):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return _SKIP


def _json_friendly_dict(value: dict, *, _depth: int, _max_depth: int):
    out: dict[str, Any] = {}
    for k, v in value.items():
        if not isinstance(k, str):
            continue
        sanitized = _json_friendly(v, _depth=_depth + 1, _max_depth=_max_depth)
        if sanitized is not _SKIP:
            out[k] = sanitized
    return out


def _json_friendly_seq(value, *, _depth: int, _max_depth: int):
    out_list = []
    for item in value:
        sanitized = _json_friendly(item, _depth=_depth + 1, _max_depth=_max_depth)
        if sanitized is not _SKIP:
            out_list.append(sanitized)
    return out_list


def _json_friendly(value: Any, *, _depth: int = 0, _max_depth: int = 6):
    if _depth > _max_depth:
        return _SKIP

    scalar = _json_friendly_scalar(value)
    if scalar is not _SKIP:
        return scalar

    if isinstance(value, dict):
        return _json_friendly_dict(value, _depth=_depth, _max_depth=_max_depth)

    if isinstance(value, (list, tuple)):
        return _json_friendly_seq(value, _depth=_depth, _max_depth=_max_depth)

    return _SKIP