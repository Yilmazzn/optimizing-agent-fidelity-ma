import os

VIEWPORT_SIZE = (1920, 1080)

def expect_env_var(env_name: str) -> str:
    val = os.getenv(env_name)

    if val is None:
        raise EnvironmentError(f"Environment variable {env_name} not set")

    return val