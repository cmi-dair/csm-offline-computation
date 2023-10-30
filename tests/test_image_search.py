"""Test the image_search module."""
import pathlib

import pandas as pd
import pytest
from pytest_mock import plugin

from csm_offline import image_search

template_output = {
    "image": "my_path",
    "studies": pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}),
    "terms": pd.DataFrame({"col1": [5, 6], "col2": [7, 8]}),
}


@pytest.fixture()
def mock_neuroquery(mocker: plugin.MockerFixture) -> plugin.MockerFixture:
    """Return a mock NeuroQueryImageSearch class."""
    return mocker.patch(
        "csm_offline.image_search.neuroquery_image_search.NeuroQueryImageSearch",
        autospec=True,
        return_value=lambda image_path, results: template_output,
    )


def test_search_valid_input(mock_neuroquery: plugin.MockerFixture) -> None:
    """Test the search function with valid input."""
    image_path = pathlib.Path("/path/to/image")
    n_results = 1
    expected = template_output

    result = image_search.search(image_path, n_results)

    assert result == expected
