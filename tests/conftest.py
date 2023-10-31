"""Configurations for pytest."""
import os


def pytest_configure() -> None:
    """Configure pytest."""
    os.environ["CSM_WORKBENCH_PATH"] = "/path/to/workbench"
