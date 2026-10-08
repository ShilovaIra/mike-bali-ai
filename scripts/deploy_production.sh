#!/usr/bin/env bash
# Deploy this app on the production Droplet from the master branch only.
#
# Promote staging by merging it into master and pushing origin/master, then
# on the production Droplet:
#   ./scripts/deploy_production.sh
#
# The Droplet .env must be the production one. Never reuse the staging bot token.
#
set -euo pipefail

PRODUCTION_BRANCH="master"
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$APP_DIR"

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

# One image at a time: a small Droplet runs out of memory if these build together.
echo "→ Building images"
docker compose build bot
docker compose build admin-web
docker compose build partner-web

echo "→ Starting containers"
docker compose up -d --remove-orphans --force-recreate

echo "→ Waiting for bot"
ready=0
for _ in $(seq 1 30); do
  if docker compose ps --status running --format '{{.Service}}' 2>/dev/null | grep -qx bot; then
    if docker compose logs bot 2>/dev/null | grep -q 'Mike Bali AI запущен'; then
      ready=1
      break
    fi
  fi
  sleep 2
done

if [[ "$ready" != 1 ]]; then
  echo "Bot did not become ready."
  docker compose ps
  docker compose logs --tail=80 bot
  exit 1
fi

echo "→ Branch: $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD)"
docker compose ps
echo "Done."
echo "  Bot logs: docker compose logs -f bot"
