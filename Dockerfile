# ---- Builder Stage ----
FROM python:3.13-slim as builder

# Install System Packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /yours_scently

# install poetry
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir poetry

# Set poetry environment
RUN poetry config virtualenvs.create false

# copy poetry setting files
COPY pyproject.toml poetry.lock ./

# install dependencies
RUN poetry install --no-interaction --no-root


# ---- Final Stage ----
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /yours_scently

RUN addgroup --system app && adduser --system --group app

# static / media 디렉토리 생성 및 권한 부여
RUN mkdir -p /yours_scently/apps/static \
    && mkdir -p /yours_scently/apps/media \
    && mkdir -p /yours_scently/staticfiles \
    && chown -R app:app /yours_scently/apps \
    && chown -R app:app /yours_scently/staticfiles

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/

# Copy project files
COPY --chown=app:app ./ ./

USER app

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]