FROM python:3.10-bullseye

WORKDIR /app

RUN apt update && apt install -y libgit2-dev

#RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
#    cd /usr/local/bin && \
#    ln -s /opt/poetry/bin/poetry && \
RUN pip install poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock README.md /app/
RUN poetry install --no-root --no-dev --no-interaction --no-ansi
COPY ./pyrepositoryminer /app/pyrepositoryminer
ENV PYTHONPATH=/app
RUN pip install .

ENTRYPOINT [ "/usr/bin/env", "python3", "pyrepositoryminer"]