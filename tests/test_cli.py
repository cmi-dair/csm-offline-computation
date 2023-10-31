"""Test the command-line interface."""
import logging
import pathlib
import sys

import pytest
from pytest_mock import plugin

from csm_offline import cli


@pytest.fixture()
def basic_arguments() -> list[str]:
    """Return a list of basic arguments."""
    return [
        "app-csm",
        "/path/to/left",
        "/path/to/right",
        "-o",
        "output_basename",
    ]


def test_parse_valid_arguments(
    mocker: plugin.MockerFixture,
    basic_arguments: list[str],
) -> None:
    """Test that the arguments are parsed correctly."""
    mocker.patch.object(sys, "argv", basic_arguments)

    args = cli.parse_arguments()

    assert args.input_left == pathlib.Path("/path/to/left")
    assert args.input_right == pathlib.Path("/path/to/right")
    assert args.output == "output_basename"
    assert args.species == "human"
    assert args.n_terms == 100  # noqa: PLR2004
    assert args.n_studies == 100  # noqa: PLR2004
    assert args.verbosity is None


def test_parse_missing_required_arguments() -> None:
    """Test that the parser exits when required arguments are missing."""
    with pytest.raises(SystemExit):
        cli.parse_arguments()


def test_parse_custom_verbosity_level(
    mocker: plugin.MockerFixture,
    basic_arguments: list[str],
) -> None:
    """Test that the parser accepts a custom verbosity level."""
    arguments = [*basic_arguments, "-v", "debug"]
    mocker.patch.object(sys, "argv", arguments)

    args = cli.parse_arguments()

    assert args.verbosity == logging.DEBUG


def test_parse_valid_species_choice(
    mocker: plugin.MockerFixture,
    basic_arguments: list[str],
) -> None:
    """Test that the parser accepts a valid species choice."""
    arguments = [*basic_arguments, "-s", "macaque"]
    mocker.patch.object(sys, "argv", arguments)

    args = cli.parse_arguments()

    assert args.species == "macaque"


def test_parse_invalid_species_choice(
    mocker: plugin.MockerFixture,
    basic_arguments: list[str],
) -> None:
    """Test that the parser exits when an invalid species choice is given."""
    arguments = [*basic_arguments, "-s", "unknown_species"]
    mocker.patch.object(sys, "argv", arguments)

    with pytest.raises(SystemExit):
        cli.parse_arguments()
