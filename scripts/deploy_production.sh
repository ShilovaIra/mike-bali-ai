#!/usr/bin/env bash
# Deploy this app on the production Droplet from the master branch only.
#
# Hand deploy on the Droplet, from a master checkout:
#   ./scripts/deploy_production.sh
#
# GitHub Actions builds the images on the runner and runs:
#   SKIP_GIT_PULL=1 SKIP_IMAGE_BUILD=1 ./scripts/deploy_production.sh
#
# Exit 1: stopped before containers were recreated.
# Exit 2: containers were recreated and the release is not healthy.
# The workflow restores the previous images on a non-zero exit. Exit 2
# also recreates the containers from those images. Image rollback does
# not restore the database.
#
# The Droplet .env must be the production one. Never reuse the staging bot token.
# Keep schema.sql bootable by the previous image.
set -euo pipefail

PRODUCTION_BRANCH="master"
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$APP_DIR"

if [[ "${SKIP_GIT_PULL:-}" != "1" ]]; then
  git config --global --add safe.directory "$APP_DIR" || true
  current="$(git rev-parse --abbrev-ref HEAD)"
  if [[ "$current" != "$PRODUCTION_BRANCH" ]]; then
    echo "Refusing to deploy: current branch is '$current', expected '$PRODUCTION_BRANCH'."
    echo "Run: git fetch origin && git checkout $PRODUCTION_BRANCH"
    exit 1
  fi

  echo "→ Fetching origin/$PRODUCTION_BRANCH"
  git fetch origin "$PRODUCTION_BRANCH"
  git merge --ff-only "origin/$PRODUCTION_BRANCH"
fi

if [[ ! -f .env ]]; then
  echo "Missing .env — copy from template first:"
  echo "  cp .env.example .env && nano .env"
  exit 1
fi

require_env() {
  local key="$1"
  if ! grep -qE "^${key}=.+" .env; then
    echo "Missing ${key} in .env."
    exit 1
  fi
}

require_env TELEGRAM_BOT_TOKEN
require_env OPENAI_API_KEY
require_env POSTGRES_PASSWORD
require_env ADMIN_JWT_SECRET

if ! grep -qE '^GOOGLE_PLACES_API_KEY=.+' .env; then
  echo "→ GOOGLE_PLACES_API_KEY is empty. Empty partner buttons will not open a precise Maps place."
fi

if [[ "${SKIP_IMAGE_BUILD:-}" != "1" ]]; then
  # One image at a time: a small Droplet runs out of memory if these build together.
  echo "→ Building images"
  docker compose build bot
  docker compose build admin-web
  docker compose build partner-web
fi

service_running() {
  docker compose ps --status running --format '{{.Service}}' 2>/dev/null | grep -qx "$1"
}

admin_api_healthy() {
  local cid status
  cid="$(docker compose ps -q --status running admin-api 2>/dev/null || true)"
  cid="${cid%%$'\n'*}"
  [[ -n "$cid" ]] || return 1
  status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "$cid")"
  [[ "$status" == "healthy" ]]
}

bot_logged_ready() {
  local logs
  logs="$(docker compose logs bot 2>/dev/null || true)"
  [[ "$logs" == *"Mike Bali AI запущен"* ]]
}

release_ready() {
  service_running bot || return 1
  service_running admin-api || return 1
  service_running admin-web || return 1
  service_running partner-web || return 1
  admin_api_healthy || return 1
  bot_logged_ready
}

echo "→ Starting containers"
if ! docker compose up -d --remove-orphans --force-recreate; then
  echo "docker compose up failed."
  docker compose ps || true
  exit 2
fi

echo "→ Waiting for bot, admin API, and both panels"
ready=0
for _ in $(seq 1 36); do
  if release_ready; then
    ready=1
    break
  fi
  sleep 5
done

if [[ "$ready" != 1 ]]; then
  echo "Release did not become ready."
  docker compose ps || true
  docker compose logs --tail=80 bot || true
  docker compose logs --tail=40 admin-api || true
  exit 2
fi

if [[ "${SKIP_GIT_PULL:-}" != "1" ]]; then
  echo "→ Branch: $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD)"
else
  echo "→ CI pack deploy (git skipped)"
fi
docker compose ps
echo "Done."
echo "  Bot logs: docker compose logs -f bot"
