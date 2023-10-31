"""Module for interactions with the NeuroQuery Image Search model."""
import logging
import pathlib
from typing import TypedDict

import neuroquery_image_search
import nibabel
import pandas as pd

from csm_offline import config

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class ImageSearchResult(TypedDict):
    """A class representing the results of an image search.

    Attributes:
        image: The image used for the search.
        studies: The studies associated with the search.
        terms: The terms associated with the search.

    Notes:
        If neuroquery_image_search ever includes type hinting, this class
        should be removed and replaced with the neuroquery_image_search
        type hint.

    """

    image: str | pathlib.Path | nibabel.Nifti1Image
    studies: pd.DataFrame
    terms: pd.DataFrame


def search(
    image_path: pathlib.Path,
    n_terms: int = 10,
    n_studies: int = 10,
) -> ImageSearchResult:
    """Search for images similar to the given image.

    Args:
        image_path: The path to the image to search for.
        n_terms: The number of terms to return from the search.
        n_studies: The number of studies to return from the search.


    Returns:
        list[dict]: The results of the search.

    """
    logger.info("Running NeuroQuery Image Search for %s", image_path)
    neuroquery = neuroquery_image_search.NeuroQueryImageSearch()
    return neuroquery(image_path, n_studies=n_studies, n_terms=n_terms)
