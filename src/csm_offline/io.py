"""Input/output functionality for the CSM offline package."""
import enum
import logging
import pathlib

import h5py
import nibabel
import numpy as np
from nibabel.gifti import gifti
from numpy import typing as npt

from csm_offline import config

settings = config.get_settings()
logger = logging.getLogger(settings.LOGGER_NAME)
DATA_DIR = settings.DATA_DIR


class VolumeFiles(enum.Enum):
    """A class representing the volume files for the CSM offline application.

    Attributes:
        mni152: The path to the MNI152 volume file.

    """

    MNI152: pathlib.Path = DATA_DIR / "mni152_template.nii.gz"


class FeatureFiles(enum.Enum):
    """A class representing the data files for the CSM Offline application.

    Attributes:
        HUMAN_LEFT: The path to the human left data file.
        HUMAN_RIGHT: The path to the human right data file.
        MACAQUE_LEFT: The path to the macaque left data file.
        MACAQUE_RIGHT: The path to the macaque right data file.
    """

    HUMAN_LEFT: pathlib.Path = DATA_DIR / "human_left_gradient_10k_fs_lr.h5"
    HUMAN_RIGHT: pathlib.Path = DATA_DIR / "human_right_gradient_10k_fs_lr.h5"
    MACAQUE_LEFT: pathlib.Path = DATA_DIR / "macaque_left_gradient_10k_fs_lr.h5"
    MACAQUE_RIGHT: pathlib.Path = DATA_DIR / "macaque_right_gradient_10k_fs_lr.h5"


class SurfaceFiles(enum.Enum):
    """A class representing the surface files for the CSM Offline application.

    Attributes:
        HUMAN_LEFT: The path to the human left surface file.
        HUMAN_RIGHT: The path to the human right surface file.
        MACAQUE_LEFT: The path to the macaque left surface file.
        MACAQUE_RIGHT: The path to the macaque right surface file.

    """

    HUMAN_LEFT: pathlib.Path = DATA_DIR / "human_left_midthickness_10k_fs_lr.surf.gii"
    HUMAN_RIGHT: pathlib.Path = DATA_DIR / "human_right_midthickness_10k_fs_lr.surf.gii"
    MACAQUE_LEFT: pathlib.Path = (
        DATA_DIR / "macaque_left_midthickness_10k_fs_lr.surf.gii"
    )
    MACAQUE_RIGHT: pathlib.Path = (
        DATA_DIR / "macaque_right_midthickness_10k_fs_lr.surf.gii"
    )


class FeatureData:
    """A class representing feature data.

    Attributes:
        human_left (np.ndarray): The feature data for the human left.
        human_right (np.ndarray): The feature data for the human right.
        macaque_left (np.ndarray): The feature data for the macaque left.
        macaque_right (np.ndarray): The feature data for the macaque right.
    """

    def __init__(
        self,
        human_left: npt.ArrayLike,
        human_right: npt.ArrayLike,
        macaque_left: npt.ArrayLike,
        macaque_right: npt.ArrayLike,
    ) -> None:
        """Initialize a FeatureData instance.

        Args:
            human_left: The feature data for the human left.
            human_right: The feature data for the human right.
            macaque_left: The feature data for the macaque left.
            macaque_right: The feature data for the macaque right.
        """
        self.human_left = np.array(human_left)
        self.human_right = np.array(human_right)
        self.macaque_left = np.array(macaque_left)
        self.macaque_right = np.array(macaque_right)

    @classmethod
    def from_data_dir(cls) -> "FeatureData":
        """Load feature data from the data directory.

        Returns:
            FeatureData: The feature data.

        """
        logger.info("Loading feature data from %s.", DATA_DIR)
        human_left = cls.load_from_h5(FeatureFiles.HUMAN_LEFT.value)
        human_right = cls.load_from_h5(FeatureFiles.HUMAN_RIGHT.value)
        macaque_left = cls.load_from_h5(FeatureFiles.MACAQUE_LEFT.value)
        macaque_right = cls.load_from_h5(FeatureFiles.MACAQUE_RIGHT.value)
        return cls(human_left, human_right, macaque_left, macaque_right)

    def feature_similarity(self, weights: npt.ArrayLike, species: str) -> "FeatureData":
        """Calculate the similarity between the feature data the weighted feature map.

        Args:
            weights: The weights to use for the weighted average.
            species: The species of the input files.

        Returns:
            FeatureData: The feature similarity.

        """
        logger.debug("Calculating feature similarity.")
        species_data = getattr(self, species)
        user_feature = np.average(species_data, weights=weights, axis=0)
        similarity = _cosine_similarity(
            np.atleast_2d(user_feature),
            self.all_data,
        ).squeeze()
        return FeatureData(
            similarity[: self.human_left.shape[0]],
            similarity[self.human_left.shape[0] : self.human.shape[0]],
            similarity[
                self.human.shape[0] : (self.human.shape[0] + self.macaque_left.shape[0])
            ],
            similarity[(self.human.shape[0] + self.macaque_left.shape[0]) :],
        )

    @staticmethod
    def load_from_h5(filepath: pathlib.Path) -> np.ndarray:
        """Load feature data from an HDF5 file.

        Args:
            filepath: The path to the HDF5 file.

        Returns:
            np.ndarray: The feature data.

        """
        logger.debug("Loading feature data from %s.", filepath)
        with h5py.File(filepath, "r") as h5:
            return h5["data"][:].squeeze()

    @property
    def human(self) -> np.ndarray:
        """Get the human feature data.

        Returns:
            np.ndarray: The human feature data.

        """
        logger.debug("Getting human feature data.")
        return np.concatenate((self.human_left, self.human_right))

    @property
    def macaque(self) -> np.ndarray:
        """Get the macaque feature data.

        Returns:
            np.ndarray: The macaque feature data.

        """
        logger.debug("Getting macaque feature data.")
        return np.concatenate((self.macaque_left, self.macaque_right))

    @property
    def all_data(self) -> np.ndarray:
        """Get all feature data.

        Returns:
            np.ndarray: All feature data.

        """
        logger.debug("Getting all feature data.")
        return np.concatenate((self.human, self.macaque))


def load_user_data(*args: pathlib.Path) -> np.ndarray:
    """Load user data from the given files.

    Args:
        *args: The paths to the user data files. Can be provided as
            gifti or text files.

    Returns:
        np.ndarray: The user data.

    """
    logger.info("Loading user data.")
    data_arrays = []
    for filepath in args:
        if not filepath.exists():
            message = f"File {filepath} does not exist."
            logger.exception(message)
            raise FileNotFoundError(message)
        if filepath.suffix == ".gii":
            image = nibabel.load(filepath)
            if not isinstance(image, gifti.GiftiImage):
                message = f"File {filepath} is not a gifti file."
                logger.exception(message)
                raise ValueError(message)
            data_arrays.append(image.darrays[0].data)
        else:
            # Fallback to loading as .txt file.
            data_arrays.append(np.loadtxt(filepath))
    return np.concatenate(data_arrays)


def _cosine_similarity(
    seed_features: npt.ArrayLike,
    target_features: npt.ArrayLike,
) -> np.ndarray:
    """Computes the cosine similarity between two sets of features.

    Args:
        seed_features: The features on the seed surface.
        target_features: The features on the target surface.

    Returns:
        A vector of similarities per vertex.

    Notes:
        The similarity is thresholded as the online Cross Species Mapper
        uses a Fisher Z transformation to normalize the data. This would
        result in an infinite result for a cosine similarity of 1.

    """
    threshold = 0.9999
    cosine_similarity = np.dot(seed_features, np.transpose(target_features)) / (
        np.linalg.norm(seed_features, axis=1)[:, np.newaxis]
        * np.linalg.norm(target_features, axis=1)[np.newaxis, :]
    )
    cosine_similarity[cosine_similarity > threshold] = threshold
    cosine_similarity[cosine_similarity < -threshold] = -threshold
    cosine_similarity[np.isnan(cosine_similarity)] = 0
    return cosine_similarity


def array_to_gifti(
    array: np.ndarray,
    filepath: pathlib.Path,
    *,
    allow_cast: bool = True,
) -> None:
    """Save an array as a gifti file.

    Args:
        array: The array to save.
        filepath: The path to the output file.
        allow_cast: Whether to allow casting the array to a type compatible with
            gifti files.

    """
    logger.info("Saving array to %s.", filepath)
    image = nibabel.gifti.GiftiImage()
    if not allow_cast:
        data_array = nibabel.gifti.GiftiDataArray(data=array)
    elif np.issubdtype(array.dtype, np.integer):
        data_array = nibabel.gifti.GiftiDataArray(
            data=np.array(array),
            datatype="NIFTI_TYPE_INT32",
        )
    elif np.issubdtype(array.dtype, np.floating):
        data_array = nibabel.gifti.GiftiDataArray(
            data=np.array(array),
            datatype="NIFTI_TYPE_FLOAT32",
        )
    else:
        message = f"Array of type {array.dtype} cannot be saved as a gifti file."
        logger.exception(message)
        raise TypeError(message)

    image.add_gifti_data_array(data_array)
    nibabel.save(image, filepath)
