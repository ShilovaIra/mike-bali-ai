# Production deploy

Production does not deploy on push. Merge `staging` into `master` through a pull request, wait until the **pytest** check is green, then run [`.github/workflows/deploy-production.yml`](../.github/workflows/deploy-production.yml) by hand from the `master` branch.

The workflow runs the test suite again, builds the images on the GitHub runner, copies them to the production Droplet, and starts `/opt/mike-bali-ai`. A second click waits until the first run finishes. The run refuses any ref other than `refs/heads/master`.

If the new bot does not log `Mike Bali AI запущен`, or `admin-api`, `admin-web`, or `partner-web` is not up, the Droplet points the image tags back at the previous release and starts that release again. The GitHub job stays red. Image rollback does not restore the database.

Keep `db/schema.sql` additive. A `DROP`, a `NOT NULL` column with no default, or a rewrite of existing rows can make the previous image crash after the new one has already applied the schema. Deploy that kind of change by hand on the Droplet and do not rely on the automatic retag.

Every deploy recreates the containers, so the Telegram bot restarts for a short time.

## GitHub Actions secrets

Do this whole section on your Mac. The production Droplet only receives the public half of a key that your Mac creates. GitHub later receives the private half. A new key for this Droplet: leave the staging host, `STAGING_SSH_KEY`, and the staging bot token as they are.

You need the production address and user you already use to log in, for example `ssh root@203.0.113.10`. In the commands below, replace `USER` and `HOST` with those two values.

If the Terminal prompt already looks like `root@...#`, you are on the Droplet. Type `exit` and press Return until the prompt is your Mac again.

### 1. Create the key on the Mac

```bash
cd ~
ssh-keygen -t ed25519 -f production_deploy -C "github-actions-production" -N ""
```

`-N ""` means the key has no passphrase. GitHub Actions cannot type a passphrase. When it finishes, list the two files:

```bash
ls -l ~/production_deploy ~/production_deploy.pub
```

`production_deploy` is private. `production_deploy.pub` is public. Both stay in your home folder, outside this repo.

### 2. Install the public key on the Droplet, still from the Mac

This uses the login you already have. It will ask for that password or key. It appends one line to the Droplet's `~/.ssh/authorized_keys`.

```bash
ssh-copy-id -i ~/production_deploy.pub USER@HOST
```

A successful run ends with `Number of key(s) added: 1`.

### 3. Prove the new key opens the Droplet

```bash
ssh -i ~/production_deploy -o IdentitiesOnly=yes USER@HOST
```

You should get a shell on the Droplet. Type `exit` to return to the Mac. If this command asks for a password, the public key was not installed. Repeat step 2.

### 4. Save four repository secrets

Open [the Actions secrets page](https://github.com/ShilovaIra/mike-bali-ai/settings/secrets/actions) while logged in as someone who can administer `ShilovaIra/mike-bali-ai`. Choose **New repository secret** each time. These are repository secrets. Environment secrets are invisible to the workflow.

| Name | Value |
|---|---|
| `PRODUCTION_HOST` | The Droplet IP or hostname only, such as `203.0.113.10`. No `ssh://` and no `user@`. |
| `PRODUCTION_SSH_USER` | The same `USER` you just logged in as, such as `root`. |
| `PRODUCTION_SSH_KEY` | The whole private file. On the Mac run `pbcopy < ~/production_deploy`, then paste into the secret. The text starts with `-----BEGIN OPENSSH PRIVATE KEY-----` and ends with `-----END OPENSSH PRIVATE KEY-----`. |
| `PRODUCTION_SSH_PORT` | Only if SSH is not on port 22. Otherwise skip this secret. |

After the private key is saved, clear it from the clipboard with `pbcopy < /dev/null`. Keep `~/production_deploy` somewhere safe, or delete it once GitHub has it. Never commit it and never paste it into chat.

GitHub's own runners also have to reach port 22 on the Droplet. A cloud firewall that allows SSH only from your home IP will accept step 3 and still reject the workflow. Allow SSH from the internet, limited to key login.

## Branch protection

The workflow file does not block a direct push. After this workflow has run once on a pull request into `master`, the check name `pytest` shows up in GitHub. Then:

1. Settings → Branches → Add classic branch protection rule (or a ruleset) for `master`.
2. Require a pull request before merging.
3. Require status checks to pass, and select `pytest`.
4. Do not allow force pushes.
5. Do not allow administrators to bypass the rule.

Turn that on after the first green `pytest` run. Requiring a check that has never run blocks every merge.

## First-time server setup

The Droplet `.env` must already be the production one. The workflow preserves it and refuses to start when it is missing.

```bash
mkdir -p /opt/mike-bali-ai
cp /opt/mike-bali-ai/.env.example /opt/mike-bali-ai/.env
nano /opt/mike-bali-ai/.env
```

Required keys: `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, `POSTGRES_PASSWORD`, `ADMIN_JWT_SECRET`. Never copy the staging `.env`.

The first successful image deploy has no `:previous` tags, so a failed first boot cannot roll back.

## Run a deploy

Actions → **Deploy production** → **Run workflow** → Branch: **master**.

## Hand deploy

On the Droplet, from a `master` checkout, for a schema change the previous image cannot boot:

```bash
cd /opt/mike-bali-ai
./scripts/deploy_production.sh
```

That path builds on the Droplet, one image at a time, and does not retag `:previous`. Exit code 2 means the containers were recreated and the release did not become healthy.

## Check a deploy

```bash
ssh USER@PRODUCTION_HOST
cd /opt/mike-bali-ai
docker compose ps
docker compose logs -f bot
```

You should see `Mike Bali AI запущен...`. Then `/start` the **production** Telegram bot.
