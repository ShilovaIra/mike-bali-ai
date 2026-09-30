#!/usr/bin/env bash
# Deploy this app on the staging Droplet from the staging branch only.
#
# Usage (on the Droplet, from the repo root):
#   ./scripts/deploy_staging.sh
#
set -euo pipefail

STAGING_BRANCH="staging"
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$APP_DIR"

if [[ "${SKIP_GIT_PULL:-}" != "1" ]]; then
  git config --global --add safe.directory "$APP_DIR" || true
  current="$(git rev-parse --abbrev-ref HEAD)"
  if [[ "$current" != "$STAGING_BRANCH" ]]; then
    echo "Refusing to deploy: current branch is '$current', expected '$STAGING_BRANCH'."
    echo "Run: git fetch origin && git checkout $STAGING_BRANCH"
    exit 1
  fi
  echo "→ Fetching origin/$STAGING_BRANCH"
  git fetch origin "$STAGING_BRANCH"
  git merge --ff-only "origin/$STAGING_BRANCH"
fi

if [[ ! -f .env ]]; then
  echo "Missing .env — copy from template first:"
  echo "  cp .env.example .env && nano .env"
  exit 1
fi

if [[ "${SKIP_IMAGE_BUILD:-}" != "1" ]]; then
  echo "→ Building images"
  docker compose build bot admin-web
fi

echo "→ Starting containers"
docker compose up -d --remove-orphans

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

if [[ "${SKIP_GIT_PULL:-}" != "1" ]]; then
  echo "→ Branch: $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD)"
else
  echo "→ CI pack deploy (git skipped)"
fi
docker compose ps
echo "Done."
echo "  Bot logs: docker compose logs -f bot"
