# Project name

[![Build](https://github.com/cmi-dair/csm-offline-computation/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/cmi-dair/csm-offline-computation/actions/workflows/test.yaml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/cmi-dair/csm-offline-computation/branch/main/graph/badge.svg?token=22HWWFWPW5)](https://codecov.io/gh/cmi-dair/csm-offline-computation)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![stability-wip](https://img.shields.io/badge/stability-work_in_progress-lightgrey.svg)
[![L-GPL License](https://img.shields.io/badge/license-L--GPL_2.1-blue.svg)](https://github.com/cmi-dair/csm-offline-computation/blob/main/LICENSE)
# CSM Offline Computation

CSM Offline is a command-line tool designed for processing data in a manner similar to the [Cross Species Mapper](https://interspeciesmap.childmind.org/). It allows users to load data, calculate feature similarity, run NeuroQuery image searches, and save the output to disk.

## Getting Started

### Prerequisites

- Docker
- Command Line Interface

### Running with Docker

You can run CSM Offline using the Docker image `cmidair/interspeciesmap`. To do this, you need to mount the `/input` and `/output` directories using the `--volume` option in Docker.

Here is an example of how to run the tool:

```bash
docker run \
  --volume /path/to/your/input:/input \
  --volume /path/to/your/output:/output \
  cmidair/interspeciesmap \
  left_hemispheric_filename.gii \
  right_hemispheric_filename.gii
```

Replace /path/to/your/input and /path/to/your/output with the paths to your input and output directories, respectively. For an up-to-date usage, including all possible parameters, see `docker run cmidair/interspeciesmap -h`. 


