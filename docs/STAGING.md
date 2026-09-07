# Staging deploy

Push or merge to the **`staging`** branch runs [`.github/workflows/deploy-staging.yml`](../.github/workflows/deploy-staging.yml). GitHub builds the bot image, copies it to the Droplet, and starts `/opt/mike-bali-ai` with Docker Compose.

Manual fallback on the Droplet:

```bash
cd /opt/mike-bali-ai
./scripts/deploy_staging.sh
```

That script refuses to run unless the checkout is `staging`.

## First-time server setup

1. Install Docker on the Droplet (`curl -fsSL https://get.docker.com | sh`).
2. Create the app dir and a staging `.env` (never reuse production or Phuket tokens):

```bash
mkdir -p /opt/mike-bali-ai
# After the first workflow run, or copy files once:
cp /opt/mike-bali-ai/.env.example /opt/mike-bali-ai/.env
nano /opt/mike-bali-ai/.env
```

The workflow preserves `.env` across deploys. The first run fails until that file exists with real secrets.

## GitHub Actions secrets

Repo → **Settings** → **Secrets and variables** → **Actions**:

| Secret | Value |
|---|---|
| `STAGING_HOST` | Droplet IP or hostname |
| `STAGING_SSH_USER` | `root` or `deploy` |
| `STAGING_SSH_KEY` | Private key whose public half is in the Droplet `authorized_keys` |
| `STAGING_SSH_PORT` | Optional; defaults to `22` |

Use a dedicated deploy key, not a personal laptop key. Firewall SSH must allow GitHub-hosted runners (key-only auth).

You can reuse the Phuket staging Droplet: keep Bali in `/opt/mike-bali-ai` so it does not overwrite `/opt/mike-phuket-ai`.

## Check a deploy

```bash
ssh USER@STAGING_HOST
cd /opt/mike-bali-ai
docker compose ps
docker compose logs -f bot
```

You should see `Mike Bali AI запущен...`. Then `/start` the **staging** Telegram bot.
