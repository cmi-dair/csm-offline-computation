"""Tests for the workbench module."""
import pathlib

import pytest
from pytest_mock import plugin

from csm_offline import workbench


@pytest.fixture()
def mock_subprocess_run(mocker: plugin.MockerFixture) -> plugin.MockerFixture:
    """Return a mock subprocess.run function."""
    return mocker.patch("subprocess.run", autospec=True)


@pytest.fixture()
def workbench_instance(
    mock_subprocess_run: plugin.MockerFixture,
) -> workbench.Workbench:
    """Return an instance of Workbench."""
    return workbench.Workbench()


@pytest.fixture()
def mock_logger_exception(mocker: plugin.MockerFixture) -> plugin.MockerFixture:
    """Return a mock logger.exception function."""
    return mocker.patch("csm_offline.workbench.logger.exception", autospec=True)


@pytest.fixture()
def mock_is_workbench_available(mocker: plugin.MockerFixture) -> plugin.MockerFixture:
    """A mock Workbench._is_workbench_available function that always returns True."""
    return mocker.patch.object(
        workbench.Workbench,
        "_is_workbench_available",
        return_value=True,
    )


def test_multi_surface_to_volume_success(
    tmp_path: pathlib.Path,
    workbench_instance: workbench.Workbench,
    mock_subprocess_run: plugin.MockerFixture,
    mock_logger_exception: plugin.MockerFixture,
) -> None:
    """Test successful run of multi_surface_to_volume."""
    metrics = [tmp_path / "metric1", tmp_path / "metric2"]
    surfaces = [tmp_path / "surface1", tmp_path / "surface2"]
    volume_space = [tmp_path / "volume_space"]
    [test_file.touch() for test_file in metrics + surfaces + volume_space]
    volume_out = pathlib.Path("volume_out")
    distance = 3.0
    mock_subprocess_run.return_value.check_returncode.return_value = None
    expected_workbench_calls = (
        5
    )  # 1 for volume math, 2 for surf2vol, 2 for check if workbench exists

    workbench.multi_surface_to_volume(
        metrics,
        surfaces,
        volume_space[0],
        volume_out,
        distance,
    )

    assert mock_logger_exception.call_count == 0
    assert mock_subprocess_run.call_count == expected_workbench_calls


def test_multi_surface_to_volume_mismatched_lengths(
    mock_logger_exception: plugin.MockerFixture,
) -> None:
    """Test multi_surface_to_volume with mismatched lengths of metrics and surfaces."""
    metrics = [pathlib.Path("metric1")]
    surfaces = [pathlib.Path("surface1"), pathlib.Path("surface2")]
    volume_space = pathlib.Path("volume_space")
    volume_out = pathlib.Path("volume_out")

    with pytest.raises(
        ValueError,
        match="The number of metrics and surfaces must be equal.",
    ):
        workbench.multi_surface_to_volume(metrics, surfaces, volume_space, volume_out)
    assert mock_logger_exception.call_count == 1


def test_workbench_surface_to_volume_file_does_not_exist(
    workbench_instance: workbench.Workbench,
    mock_logger_exception: plugin.MockerFixture,
    mock_subprocess_run: plugin.MockerFixture,
) -> None:
    """Test Workbench.surface_to_volume with a file that does not exist."""
    metric = pathlib.Path("metric")
    surface = pathlib.Path("surface")
    volume_space = pathlib.Path("volume_space")
    volume_out = pathlib.Path("volume_out")
    distance = 3.0

    with pytest.raises(FileNotFoundError):
        workbench_instance.surface_to_volume(
            metric,
            surface,
            volume_space,
            volume_out,
            distance,
        )

    assert mock_logger_exception.call_count == 1
    assert mock_subprocess_run.call_count == 1  # Call to check if Workbench exists.


def test_workbench_volume_math_file_exists(
    tmp_path: pathlib.Path,
    workbench_instance: workbench.Workbench,
    mock_logger_exception: plugin.MockerFixture,
    mock_subprocess_run: plugin.MockerFixture,
) -> None:
    """Test Workbench.volume_math with an output file that already exists."""
    expression = "expression"
    volume_out = tmp_path / "volume_out"
    volume_files = [pathlib.Path("volume1"), pathlib.Path("volume2")]
    volume_out.touch()

    with pytest.raises(FileExistsError):
        workbench_instance.volume_math(expression, volume_out, volume_files)

    assert mock_logger_exception.call_count == 1
    assert mock_subprocess_run.call_count == 1  # Call to check if Workbench exists.


def test_workbench_init_workbench_not_available(mocker: plugin.MockerFixture) -> None:
    """Test initializing Workbench when the workbench toolkit is not available."""
    mocker.patch.object(
        workbench.Workbench,
        "_is_workbench_available",
        return_value=False,
    )
    mock_logger_exception = mocker.patch(
        "csm_offline.workbench.logger.exception",
        autospec=True,
    )

    with pytest.raises(RuntimeError):
        workbench.Workbench()

    mock_logger_exception.assert_called_once_with("Workbench not available.")
