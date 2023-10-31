"""Interactions with the Workbench Toolkit."""
import logging
import pathlib
import subprocess
import tempfile
from collections.abc import Sequence

from csm_offline import config

settings = config.get_settings()
logger = logging.getLogger(settings.LOGGER_NAME)

WORKBENCH_PATH = settings.WORKBENCH_PATH


def multi_surface_to_volume(
    metrics: Sequence[pathlib.Path],
    surfaces: Sequence[pathlib.Path],
    volume_space: pathlib.Path,
    volume_out: pathlib.Path,
    distance: float = 3.0,
) -> None:
    """Convert multiple surface data to volume data.

    Args:
        metrics: The metric files.
        surfaces: The surface files.
        volume_space: The volume space file.
        volume_out: The output volume file.
        distance: The distance to use for the surface to volume conversion.

    """
    if len(metrics) != len(surfaces):
        message = "The number of metrics and surfaces must be equal."
        logger.exception(message)
        raise ValueError(message)

    volume_files = []
    wb = Workbench()
    with tempfile.TemporaryDirectory() as temp_dir:
        for index in range(len(metrics)):
            metric = metrics[index]
            surface = surfaces[index]
            volume_file = pathlib.Path(temp_dir) / f"volume_{index}.nii.gz"
            wb.surface_to_volume(
                metric,
                surface,
                volume_space,
                volume_file,
                distance,
            )
            volume_files.append(volume_file)

        average_expression = "({}) / {}".format(
            " + ".join(f"x{i}" for i in range(len(volume_files))),
            len(volume_files),
        )
        wb.volume_math(average_expression, volume_out, volume_files)


class Workbench:
    """A class for interacting with the Workbench Toolkit.

    Attributes:
        executable: The path to the Workbench executable.
    """

    def __init__(self, executable: pathlib.Path | str = WORKBENCH_PATH) -> None:
        """Initialize a Workbench instance.

        Args:
            executable: The path to the Workbench executable.
        """
        self.executable = str(executable)
        if not self._is_workbench_available():
            message = "Workbench not available."
            logger.exception(message)
            raise RuntimeError(message)

    def volume_math(
        self,
        expression: str,
        volume_out: pathlib.Path,
        volume_files: Sequence[pathlib.Path],
    ) -> None:
        """Perform math on nifti volumes.

        Args:
            expression: The expression to use for the math. Note that the volume
                names are x0, x1, x2, etc.
            volume_out: The output volume file.
            volume_files: The volume files to use for the math.

        """
        logger.info("Performing math on volumes %s.", volume_files)
        _raise_error_if_file_exists(volume_out)

        volume_files_arg = [
            f"-var x{i} {volume_file}" for i, volume_file in enumerate(volume_files)
        ]
        volume_files_arg_list = " ".join(volume_files_arg).split()
        _logged_subprocess_run(
            [
                self.executable,
                "-volume-math",
                expression,
                str(volume_out),
                *volume_files_arg_list,
            ],
        )

    def surface_to_volume(  # noqa: PLR0913
        self,
        metric: pathlib.Path,
        surface: pathlib.Path,
        volume_space: pathlib.Path,
        volume_out: pathlib.Path,
        distance: float = 3.0,
    ) -> None:
        """Convert surface data to volume data.

        Args:
            metric: The metric file.
            surface: The surface file.
            volume_space: The volume space file.
            volume_out: The output volume file.
            distance: The distance to use for the surface to volume conversion.

        """
        logger.info("Converting surface %s to volume %s.", surface, volume_out)
        _raise_error_if_file_does_not_exist(metric)
        _raise_error_if_file_does_not_exist(surface)
        _raise_error_if_file_does_not_exist(volume_space)
        _raise_error_if_file_exists(volume_out)

        _logged_subprocess_run(
            [
                self.executable,
                "-metric-to-volume-mapping",
                str(metric),
                str(surface),
                str(volume_space),
                str(volume_out),
                "-nearest-vertex",
                str(distance),
            ],
        )

    def _is_workbench_available(self) -> bool:
        """Check if the Workbench Toolkit is available.

        Returns:
            bool: True if the Workbench Toolkit is available, False otherwise.
        """
        try:
            _logged_subprocess_run([self.executable, "-version"])
        except subprocess.CalledProcessError:
            return False
        return True


def _raise_error_if_file_exists(file: pathlib.Path) -> None:
    """Raise an exception if the given file exists.

    Args:
        file: The file to check.

    Raises:
        FileExistsError: If the file exists.

    """
    if file.exists():
        message = f"File {file} already exists."
        logger.exception(message)
        raise FileExistsError(message)


def _raise_error_if_file_does_not_exist(file: pathlib.Path) -> None:
    """Raise an exception if the given file does not exist.

    Args:
        file: The file to check.

    Raises:
        FileNotFoundError: If the file does not exist.

    """
    if not file.exists():
        message = f"File {file} does not exist."
        logger.exception(message)
        raise FileNotFoundError(message)


def _logged_subprocess_run(command: list[str]) -> None:
    """Run a command and log the input."""
    logger.info("Running command: %s", " ".join(command))
    subprocess.run(command, check=True)  # noqa: S603
