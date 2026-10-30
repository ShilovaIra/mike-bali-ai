#!/usr/bin/env bash
# Point the production :local image tags back at :previous.
#
# Usage (on the Droplet, from anywhere):
#   ./scripts/restore_production_images.sh       # retag only
#   ./scripts/restore_production_images.sh --up  # retag and recreate containers
#
# Image rollback does not restore the Postgres volume.
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"

up=0
if [[ "${1:-}" == "--up" ]]; then
  up=1
elif [[ -n "${1:-}" ]]; then
  echo "Usage: $0 [--up]"
  exit 1
fi

missing=0
for name in mike-bali-app mike-bali-admin-web mike-bali-partner-web; do
  if docker image inspect "${name}:previous" >/dev/null 2>&1; then
    docker tag "${name}:previous" "${name}:local"
    echo "Restored ${name}:local from ${name}:previous"
  else
    echo "No ${name}:previous image to restore."
    missing=1
  fi
done

if docker image inspect "mike-bali-tma-web:previous" >/dev/null 2>&1; then
  docker tag "mike-bali-tma-web:previous" "mike-bali-tma-web:local"
  echo "Restored mike-bali-tma-web:local from mike-bali-tma-web:previous"
else
  echo "No mike-bali-tma-web:previous image to restore. Continuing."
fi

if [[ "$missing" -ne 0 ]]; then
  echo "Could not restore a full previous release."
  exit 1
fi

if [[ "$up" -eq 1 ]]; then
  docker compose up -d --remove-orphans --force-recreate
  echo "Previous release is running again."
fi
