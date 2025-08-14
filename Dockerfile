# ---- Builder Stage ----
FROM python:3.13-slim as builder

# Install System Packages (build tools + Postgres headers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리
WORKDIR /yours_scently

# poetry 설치
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir poetry

# poetry 환경 설정 (가상환경 생성 안 함)
RUN poetry config virtualenvs.create false

# pyproject.toml & poetry.lock 복사
COPY pyproject.toml poetry.lock ./

# 의존성 설치
RUN poetry install --no-interaction --no-root

# ---- Final Stage ----
FROM python:3.13-slim

# 런타임 의존성 설치 (libpq5 for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리
WORKDIR /yours_scently

# 앱 전용 유저 생성
RUN addgroup --system app && adduser --system --group app

# static / media 디렉토리 생성 및 권한 부여
RUN mkdir -p /yours_scently/apps/static \
    && mkdir -p /yours_scently/apps/media \
    && mkdir -p /yours_scently/staticfiles \
    && chown -R app:app /yours_scently/apps \
    && chown -R app:app /yours_scently/staticfiles

# Builder에서 설치된 패키지와 실행파일 복사
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# 프로젝트 코드 복사
COPY --chown=app:app ./ ./

# 비root 유저로 실행
USER app

# 기본 실행 명령
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
