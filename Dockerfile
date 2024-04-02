FROM python:3.10-slim as builder

WORKDIR /app

RUN pip install poetry

WORKDIR /app/

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-dev

COPY /task_backend_1 ./ 

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "task_backend_1.wsgi"]
