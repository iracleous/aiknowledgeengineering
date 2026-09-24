FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv pip install --system --no-cache -r pyproject.toml

COPY . .

RUN uv pip install --system --no-cache .

EXPOSE 8000

CMD ["uvicorn", "dataapi.app:app", "--host", "0.0.0.0", "--port", "8000"]
