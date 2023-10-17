FROM apache/airflow:2.6.2-python3.11

ENV POETRY_VERSION=1.5.0

USER root
RUN apt-get -y update && apt-get -y install git jq
USER airflow

RUN pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"

COPY --chown=airflow:root poetry.lock pyproject.toml /opt/airflow/

RUN poetry build --format=wheel
RUN pip install dist/*.whl
