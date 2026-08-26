# Sanitized portfolio artifact. It illustrates the private service-image
# structure; the public edition is intentionally not a standalone build.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

ARG RUNTIME_REQUIREMENTS=requirements-runtime.txt
COPY requirements-runtime.txt requirements-api.txt requirements-streamlit-min.txt requirements-mcp.txt ./
RUN pip install --no-cache-dir -r "${RUNTIME_REQUIREMENTS}"

COPY app ./app
COPY scripts ./scripts
COPY streamlit_app.py README.md .env.example ./

RUN mkdir -p /app/data/cache /app/data/raw

EXPOSE 8000 8001 8501

CMD ["python", "-m", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
