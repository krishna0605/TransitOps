# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv

RUN python -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

WORKDIR /build
COPY apps/api/pyproject.toml ./pyproject.toml
COPY apps/api/app ./app
RUN pip install --upgrade pip && pip install .

FROM python:3.12-slim AS runtime

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONPATH=/app/apps/api \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --system transitops && useradd --system --gid transitops --create-home transitops
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY apps/api ./apps/api
COPY scripts ./scripts
RUN chown -R transitops:transitops /app
USER transitops

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--app-dir", "apps/api", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
