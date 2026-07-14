#!/usr/bin/env bash
set -euo pipefail

# Expected environment variables:
# - APP_DIR: absolute path of the project on VPS
# - BRANCH: branch to deploy (defaults to main)
# - COMPOSE_FILE: compose file path relative to APP_DIR (defaults to docker-compose.yml)

APP_DIR="${APP_DIR:?APP_DIR is required}"
BRANCH="${BRANCH:-main}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

if [ ! -d "$APP_DIR/.git" ]; then
  echo "ERROR: $APP_DIR is not a git repository. Clone your repo there first."
  exit 1
fi

cd "$APP_DIR"

echo "Deploying branch: $BRANCH"

git fetch --all --prune
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

docker compose -f "$COMPOSE_FILE" up -d --build --force-recreate --remove-orphans

echo "Deployment finished successfully."
