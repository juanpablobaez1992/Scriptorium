#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${1:-/srv/scriptorium}"
HEALTHCHECK_URL="${2:-http://127.0.0.1/healthz}"
COMPOSE_FILES="-f docker-compose.yml"

if [[ ! -d "$APP_DIR" ]]; then
  echo "Directorio no encontrado: $APP_DIR" >&2
  exit 1
fi

cd "$APP_DIR"

if [[ ! -f ".env" ]]; then
  echo "Falta el archivo .env en $APP_DIR" >&2
  exit 1
fi

git fetch origin main
git checkout main
git pull --ff-only origin main

if [[ "${DEPLOY_HTTPS:-0}" == "1" ]]; then
  if [[ ! -f "docker-compose.https.yml" ]]; then
    echo "DEPLOY_HTTPS=1 pero no existe docker-compose.https.yml" >&2
    exit 1
  fi
  COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.https.yml"
fi

docker compose $COMPOSE_FILES up -d --build
docker compose $COMPOSE_FILES ps

if command -v curl >/dev/null 2>&1; then
  curl --fail --silent --show-error "$HEALTHCHECK_URL" >/dev/null
elif command -v wget >/dev/null 2>&1; then
  wget --quiet --spider "$HEALTHCHECK_URL"
else
  echo "Ni curl ni wget estan disponibles para verificar healthcheck." >&2
fi
