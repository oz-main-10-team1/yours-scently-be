# ---- Builder Stage ----
FROM python:3.13-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /yours_scently

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-root

# ---- Final Stage ----
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /yours_scently

RUN addgroup --system app && adduser --system --group app

RUN mkdir -p /yours_scently/apps/static \
    /yours_scently/apps/media \
    /yours_scently/staticfiles \
    && chown -R app:app /yours_scently

# Builder에서 site-packages + 실행파일 복사
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder --chmod=755 /usr/local/bin/ /usr/local/bin/

COPY --chown=app:app ./ ./

USER app

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
