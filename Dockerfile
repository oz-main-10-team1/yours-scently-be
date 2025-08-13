# ---- Builder Stage ----
FROM python:3.13-slim as builder

# Install System Packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set WORKDIR
WORKDIR /yours_scently

# install poetry
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir poetry

# Set poetry environment
RUN poetry config virtualenvs.create false

# copy poetry setting files
COPY pyproject.toml poetry.lock ./

# install dependencies
# We don't need to clean cache here as this is a builder stage
RUN poetry install --no-interaction --no-root


# ---- Final Stage ----
FROM python:3.13-slim

# Install only runtime system dependencies
# libpq-dev is for building, libpq5 is for runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Set WORKDIR
WORKDIR /yours_scently

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Copy installed packages from builder stage
# The path /usr/local/lib/python3.13/site-packages is where packages are installed
# when `virtualenvs.create` is false.
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/

# copy project files
COPY --chown=app:app ./ ./

USER app

# Set entrypoint or cmd
# e.g., CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]