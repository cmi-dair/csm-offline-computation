"""Entrypoint for the CSM Offline application."""
import json
import logging
import pathlib
import tempfile

import numpy as np

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

    logger.info("Running surface to volume.")
    surfaces = [
        io.SurfaceFiles[f"{args.species.upper()}_LEFT"].value,
        io.SurfaceFiles[f"{args.species.upper()}_RIGHT"].value,
    ]
    with tempfile.NamedTemporaryFile(suffix=".nii.gz") as volume_file:
        temp_volume_path = pathlib.Path(volume_file.name)
        workbench.multi_surface_to_volume(
            [similarity.human_left, similarity.human_right],
            surfaces,
            io.VolumeFiles.MNI152.value,
            temp_volume_path,
        )

        logger.info("Running NeuroQuery.")
        neuroquery = image_search.search(temp_volume_path, args.n_query_results)

    logger.info("Saving output.")
    np.save(
        OUTPUT_DIR / f"{args.output}_similarity_human.npy",
        similarity.human,
    )
    np.save(OUTPUT_DIR / f"{args.output}_similarity_macaque.npy", similarity.macaque)
    with (OUTPUT_DIR / f"{args.output}_neuroquery.json").open("w") as file_buffer:
        json.dump(neuroquery, file_buffer)
