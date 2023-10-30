FROM python:3.11-bullseye

WORKDIR /app

COPY . .

RUN apt-get update -y && \
    apt-get install -y libgl1 libglu1 && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main && \
    curl https://www.humanconnectome.org/storage/app/media/workbench/workbench-linux64-v1.5.0.zip -o workbench.zip && \
    unzip workbench.zip && \
    rm workbench.zip && \
    chmod +x ./workbench/bin_linux64/wb_command && \
    export PATH=$PATH:/app/workbench/bin_linux64 && \
    python -c "from neuroquery_image_search import _datasets; _datasets._download_data(_datasets.get_neuroquery_data_dir())"

ENV CSM_WORKBENCH_PATH=/app/workbench/bin_linux64/wb_command

ENTRYPOINT [ "poetry", "run", "csm_offline" ]

