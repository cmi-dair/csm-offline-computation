"""Entrypoint for the CSM Offline application."""
import logging
import pathlib
import tempfile

from csm_offline import cli, config, image_search, io, workbench

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME
WORKBENCH_PATH = settings.WORKBENCH_PATH
OUTPUT_DIR = settings.OUTPUT_DIR


def main() -> None:
    """Run the CSM Offline application."""
    args = cli.parse_arguments()
    config.setup_logger(args.verbosity)

    logger = logging.getLogger(LOGGER_NAME)
    logger.info(
        "Running CSM Offline with input file %s and %s.",
        args.input_left,
        args.input_right,
    )

    logger.info("Loading data.")
    user_data = io.load_user_data(args.input_left, args.input_right)

    logger.info("Calculating feature similarity.")
    features = io.FeatureData.from_data_dir()
    similarity = features.feature_similarity(weights=user_data, species=args.species)

    logger.info("Computing Neuroquery terms and studies.")
    neuroquery = run_neuroquery(similarity, args.species, args.n_terms, args.n_studies)

    logger.info("Saving output.")
    save_output(similarity, neuroquery, args.output)


def run_neuroquery(
    similarity: io.FeatureData,
    species: str,
    n_terms: int,
    n_studies: int,
) -> image_search.ImageSearchResult:
    """Run a neuroquery search using the given similarity data from the given species.

    Args:
        similarity: The similarity data to use for the search.
        species: The species to use for the search.
        n_terms: The number of terms to return in the search results.
        n_studies: The number of studies to return in the search results.

    Returns:
        image_search.ImageSearchResult: The result of the neuroquery search.
    """
    surfaces = [
        io.SurfaceFiles[f"{species.upper()}_LEFT"].value,
        io.SurfaceFiles[f"{species.upper()}_RIGHT"].value,
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_volume_path = pathlib.Path(temp_dir) / "volume.nii.gz"
        temp_surface_left_path = pathlib.Path(temp_dir) / "surface_left.surf.gii"
        temp_surface_right_path = pathlib.Path(temp_dir) / "surface_right.surf.gii"

        io.array_to_gifti(similarity.human_left, temp_surface_left_path)
        io.array_to_gifti(similarity.human_right, temp_surface_right_path)

        workbench.multi_surface_to_volume(
            [temp_surface_left_path, temp_surface_right_path],
            surfaces,
            io.VolumeFiles.MNI152.value,
            temp_volume_path,
        )

        return image_search.search(temp_volume_path, n_terms, n_studies)


def save_output(
    similarity: io.FeatureData,
    neuroquery: image_search.ImageSearchResult,
    output_prefix: str,
) -> None:
    """Save the output of the CSM offline computation to disk.

    Args:
        similarity: The similarity data to save.
        neuroquery: The neuroquery data to save.
        output_prefix: The prefix to use for the output filenames.
    """
    for species in ("human", "macaque"):
        for side in ("left", "right"):
            io.array_to_gifti(
                getattr(similarity, f"{species}_{side}"),
                OUTPUT_DIR / f"{output_prefix}_{species}_{side}.func.gii",
            )
    for dataframe_name in ("terms", "studies"):
        neuroquery[dataframe_name].to_json(  # type: ignore[literal-required]
            OUTPUT_DIR / f"{output_prefix}_neuroquery_{dataframe_name}.json",
            orient="records",
            indent=4,
        )
