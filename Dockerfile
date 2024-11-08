FROM python:3.11-slim

RUN pip install poetry

WORKDIR /app
COPY . .
RUN poetry install --only main
ENTRYPOINT ["poetry", "run", "tfm"]
