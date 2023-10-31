"""Tests for the io module."""
import pathlib

import h5py
import nibabel
import numpy as np
import pytest
from pytest_mock import plugin

from csm_offline import io

generator = np.random.default_rng()


@pytest.fixture()
def mock_data() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return mock data."""
    size = (100, 10)
    human_left = generator.random(size)
    human_right = generator.random(size)
    macaque_left = generator.random(size)
    macaque_right = generator.random(size)
    return human_left, human_right, macaque_left, macaque_right


@pytest.fixture()
def feature_data(
    mock_data: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> io.FeatureData:
    """Return an instance of FeatureData."""
    human_left, human_right, macaque_left, macaque_right = mock_data
    return io.FeatureData(human_left, human_right, macaque_left, macaque_right)


def test_from_data_dir_valid(
    mocker: plugin.MockerFixture,
    mock_data: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> None:
    """Test FeatureData.from_data_dir with valid data."""
    mocker.patch("csm_offline.io.FeatureData.load_from_h5", return_value=mock_data)

    result = io.FeatureData.from_data_dir()

    np.testing.assert_array_equal(
        result.human_left,
        mock_data,
        "Data loaded from file should match the original data.",
    )


def test_load_from_h5_valid(tmp_path: pathlib.Path) -> None:
    """Test FeatureData.load_from_h5 with valid HDF5 file."""
    data = generator.random((20, 10))
    file_path = tmp_path / "test_file.h5"
    with h5py.File(file_path, "w") as h5:
        h5.create_dataset("data", data=data)

    result = io.FeatureData.load_from_h5(file_path)

    np.testing.assert_array_equal(
        result,
        data,
        "Data loaded from file should match the original data.",
    )


def test_feature_similarity_valid(feature_data: io.FeatureData) -> None:
    """Test FeatureData.feature_similarity with valid input."""
    weights = generator.random(feature_data.human_left.shape[0] * 2)
    species = "human"

    result = feature_data.feature_similarity(weights, species)

    assert isinstance(
        result,
        io.FeatureData,
    ), "Result should be an instance of FeatureData"


def test_human_property(feature_data: io.FeatureData) -> None:
    """Test FeatureData human property."""
    expected = np.concatenate(
        (feature_data.human_left, feature_data.human_right),
        axis=0,
    )

    result = feature_data.human

    np.testing.assert_array_equal(
        result,
        expected,
        "Human property should return concatenated human left and right",
    )


def test_macaque_property(feature_data: io.FeatureData) -> None:
    """Test FeatureData macaque property."""
    expected = np.concatenate(
        (feature_data.macaque_left, feature_data.macaque_right),
        axis=0,
    )

    result = feature_data.macaque

    np.testing.assert_array_equal(
        result,
        expected,
        "Macaque property should return concatenated macaque left and right",
    )


def test_all_data_property(feature_data: io.FeatureData) -> None:
    """Test FeatureData all_data property."""
    expected = np.concatenate(
        (feature_data.human, feature_data.macaque),
        axis=0,
    )

    result = feature_data.all_data

    np.testing.assert_array_equal(
        result,
        expected,
        "All_data property should return all feature data",
    )


def test_load_user_data_txt(tmp_path: pathlib.Path) -> None:
    """Test load_user_data with valid text file."""
    data = [generator.random((20, 10)), generator.random((20, 10))]
    file_paths = []
    for index, array in enumerate(data):
        file_paths.append(tmp_path / f"test_file_{index}.txt")
        np.savetxt(file_paths[index], array)

    result = io.load_user_data(*file_paths)

    np.testing.assert_array_equal(
        result,
        np.concatenate(data),
        "Data loaded from file should match the original data.",
    )


def test_load_user_data_file_does_not_exist() -> None:
    """Test load_user_data with a file that does not exist."""
    with pytest.raises(FileNotFoundError, match="does not exist."):
        io.load_user_data(pathlib.Path("does_not_exist.txt"))


def test_cosine_similarity_valid() -> None:
    """Test _cosine_similarity with valid input."""
    a = np.array([[1, 0], [0, 1]])
    b = np.array([[1, 0], [0, 1]])
    expected = np.array([[0.9999, 0], [0, 0.9999]])

    result = io._cosine_similarity(a, b)

    np.testing.assert_array_equal(
        result,
        expected,
        "Cosine similarity should be correctly calculated",
    )


def test_array_to_gifti(tmp_path: pathlib.Path) -> None:
    """Test if the function saves a gifti file successfully."""
    array = np.array([[1, 2], [3, 4]], dtype=np.float32)
    file_path = tmp_path / "output.gii"

    io.array_to_gifti(array, file_path)

    assert file_path.is_file()


def test_gifti_file_content(tmp_path: pathlib.Path) -> None:
    """Test if the gifti file contains correct data."""
    array = np.array([[1, 2], [3, 4]], dtype=np.float32)
    file_path = tmp_path / "output.gii"
    io.array_to_gifti(array, file_path)

    gii_img = nibabel.load(file_path)
    loaded_array = gii_img.darrays[0].data  # type: ignore[attr-defined]

    np.testing.assert_array_equal(loaded_array, array, "Data should be the same.")
