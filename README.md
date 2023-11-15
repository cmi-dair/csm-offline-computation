# CSM Offline Computation
[![Build](https://github.com/cmi-dair/csm-offline-computation/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/cmi-dair/csm-offline-computation/actions/workflows/test.yaml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/cmi-dair/csm-offline-computation/branch/main/graph/badge.svg?token=22HWWFWPW5)](https://codecov.io/gh/cmi-dair/csm-offline-computation)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![stability-wip](https://img.shields.io/badge/stability-work_in_progress-lightgrey.svg)
[![L-GPL License](https://img.shields.io/badge/license-L--GPL_2.1-blue.svg)](https://github.com/cmi-dair/csm-offline-computation/blob/main/LICENSE)

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

Replace /path/to/your/input and /path/to/your/output with the paths to your input and output directories, respectively. For an up-to-date usage, including all possible parameters, see `docker run cmidair/interspeciesmap -h`. Note that the gifti surfaces have to match the 10k FS-LR surfaces used in the Cross Species Mapper. 

### Decoding from Neuroquery Terms

We can also decode directly from neuroquery terms. To do so, run the following commands. First in Python we create the volumetric neuroquery image.

```python
import nibabel
import neuroquery

model = neuroquery.fetch_neuroquery_model()
encoder = neuroquery.NeuroQueryModel.from_data_dir(model)
query = "default mode"
result = encoder(query)

nibabel.save('my/volume/file.nii.gz', result["brain_map"])
```

Then in Bash we create the surface files and run the rest of the code. Note that you need Workbench tools installed for this.
```bash
wb_command \
  -volume-to-surface-mapping \
  "my/volume/file.nii.gz" \
  "my/left_surface.gii" \
  "my_left_output.gii" \
  -trilinear
wb_command \
  -volume-to-surface-mapping \
  "my/volume/file.nii.gz" \
  "my/right_surface.gii" \
  "my_right_output.gii" \
  -trilinear

docker run \
  --volume /my/volume:/input \
  --volume /path/to/your/output:/output \
  cmidair/interspeciesmap \
  my_left_output.gii \
  my_right_output.gii
```
