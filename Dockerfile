FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root

COPY . .

EXPOSE 50081
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "50081"]
