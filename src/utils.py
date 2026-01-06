import os

VIEWPORT_SIZE = (1920, 1080)

def expect_env_var(env_name: str) -> str:
    val = os.getenv(env_name)

    if val is None:
        raise EnvironmentError(f"Environment variable {env_name} not set")

    return val

def map_coords_to_screen(
        coords: tuple[int, int],
        scr_size: tuple[int, int], 
        target_size: tuple[int, int]
) -> tuple[int, int]:
    """
    Map coordinates from source size to destination size
    :param coords: (x, y) coordinates in the source space
    :param scr_size: (width, height) of the source space
    :param target_size: (width, height) of the destination space
    :return: (x, y) coordinates in the destination space
    """
    x, y = coords
    src_w, src_h = scr_size
    dst_w, dst_h = target_size

    scale_x = dst_w / src_w
    scale_y = dst_h / src_h

    mapped_x = int(round(x * scale_x))
    mapped_y = int(round(y * scale_y))

    return mapped_x, mapped_y