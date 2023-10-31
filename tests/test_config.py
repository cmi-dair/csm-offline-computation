"""Test the config module."""
import logging
import pathlib

from csm_offline import config


def test_settings() -> None:
    """Test that the Settings class is initialized with default values."""
    settings = config.Settings()  # type: ignore[call-arg]
    assert settings.LOGGER_NAME == "csm_offline"
    assert pathlib.Path(__file__).parent.parent / "data" == settings.DATA_DIR
    assert isinstance(settings.WORKBENCH_PATH, pathlib.Path)


def test_get_settings() -> None:
    """Test that the get_settings function returns a Settings instance."""
    settings = config.get_settings()
    assert isinstance(settings, config.Settings)


def test_setup_logger_default_verbosity() -> None:
    """Test the logger with the default verbosity."""
    config.setup_logger()
    logger = logging.getLogger(config.get_settings().LOGGER_NAME)
    assert logger.level == 0
    assert logger.handlers


def test_setup_logger_string_verbosity() -> None:
    """Test the logger with a custom verbosity given as a string."""
    config.setup_logger("DEBUG")
    logger = logging.getLogger(config.get_settings().LOGGER_NAME)
    assert logger.level == logging.DEBUG


def test_setup_logger_integer_verbosity() -> None:
    """Test the logger with a custom verbosity given as an integer."""
    config.setup_logger(10)
    logger = logging.getLogger(config.get_settings().LOGGER_NAME)
    assert logger.level == logging.DEBUG
