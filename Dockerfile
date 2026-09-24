# Stage 1 - builder: install dependencies
FROM python:3.13-slim AS builder

RUN pip install uv

ENV UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
RUN uv sync --frozen --no-dev

# Stage 2 - runtime: lean final image
FROM python:3.13-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv ./.venv
COPY src/ ./src/

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "src.food11.serve:app", "--host", "0.0.0.0", "--port", "8000"]