FROM python:latest

WORKDIR /app

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock README.md /app/
RUN poetry install --no-root --no-dev --no-interaction --no-ansi
COPY ./pyrepositoryminer /app/pyrepositoryminer
COPY ./executables /app/executables
ENV EXECUTABLES=/app/executables
ENV PYTHONPATH=/app
RUN pip install .