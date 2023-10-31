"""Command line interface for the CSM Offline tool."""
import argparse
import logging

from csm_offline import config

settings = config.get_settings()
logger = logging.getLogger(settings.LOGGER_NAME)
INPUT_DIR = settings.INPUT_DIR


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for CSM Offline.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    logger.info("Parsing Arguments")
    parser = argparse.ArgumentParser(
        description="CSM Offline: A tool for processing Cross Species Mapper data.",
        epilog="To report a bug, please raise an issue at https://github.com/cmi-dair/csm-offline-computation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input_left",
        type=lambda filename: INPUT_DIR / filename,
        help="Name of the left hemispheric input file.",
    )
    parser.add_argument(
        "input_right",
        type=lambda filename: INPUT_DIR / filename,
        help="Name of the right hemispheric input file.",
    )
    parser.add_argument(
        "-s",
        "--species",
        default="human",
        type=str.lower,
        help="The species of the input files.",
        choices=["human", "macaque"],
    )
    parser.add_argument(
        "-o",
        "--output",
        default="csm_offline_output",
        type=str,
        help="Basename of the output files.",
    )
    parser.add_argument(
        "-t",
        "--n_terms",
        default=100,
        type=int,
        help="The number of terms to return from the NeuroQuery image search.",
    )
    parser.add_argument(
        "-u",
        "--n_studies",
        default=100,
        type=int,
        help="The number of studies to return from the NeuroQuery image search.",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        default=None,
        type=lambda x: logging.getLevelName(x.upper()),
        help="Change output verbosity. Follows the same format as the Python logging "
        "module. Values may also be supplied as 'debug', 'info', 'warning', 'error', "
        "or 'critical'. This primarily intended for developer usage.",
        choices=[10, 20, 30, 40, 50],
    )
    args = parser.parse_args()
    logger.debug("Arguments parsed: %s", args)
    return args
