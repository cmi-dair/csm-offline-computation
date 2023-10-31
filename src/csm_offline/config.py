"""Configurations for the CSM Offline application."""
import functools
import logging
import pathlib

import pydantic
import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    """A class representing the settings for the CSM offline computation.

    Attributes:
        WORKBENCH_PATH (pathlib.Path): The path to the workbench.
        LOGGER_NAME (str): The name of the logger.
        DATA_DIR (pathlib.Path): The path to the data directory.
    """

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="CSM_",
    )

    LOGGER_NAME: str = pydantic.Field("csm_offline")
    WORKBENCH_PATH: pathlib.Path = pydantic.Field(...)
    DATA_DIR: pathlib.Path = pydantic.Field(
        pathlib.Path(__file__).parent.parent.parent / "data",
    )
    INPUT_DIR: pathlib.Path = pydantic.Field("/input")
    OUTPUT_DIR: pathlib.Path = pydantic.Field("/output")


@functools.lru_cache
def get_settings() -> Settings:
    """Cached call to the settings for the CSM Offline application.

    Returns:
        Settings: The settings for the CSM Offline application.

    """
    return Settings()  # type: ignore[call-arg]


def setup_logger(verbosity: str | int | None = None) -> None:
    """Set up a logger with the given verbosity level.

    Args:
        verbosity: The verbosity level for the logger. If None, the
            logger will use the default level.

    """
    settings = get_settings()
    logger = logging.getLogger(settings.LOGGER_NAME)
    if verbosity is not None:
        logger.setLevel(verbosity)

    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug("Logger set up with verbosity %s", verbosity)
