#!/usr/bin/env bash
set -euo pipefail

# Provision DigitalOcean Managed Postgres and App Platform (staging)
# Requirements:
# - doctl installed: https://docs.digitalocean.com/reference/doctl/how-to/install/
# - export DO_API_TOKEN=... before running

if [[ -z "${DO_API_TOKEN:-}" ]]; then
  echo "ERROR: DO_API_TOKEN is not set" >&2
  exit 1
fi

APP_NAME="cars-trends-staging"
REGION="sfo3"  # Closest to Tijuana
DB_NAME="${APP_NAME}"

echo "==> Authenticating doctl"
doctl auth init -t "$DO_API_TOKEN" >/dev/null

echo "==> Creating Managed PostgreSQL: $DB_NAME"
doctl databases create "$DB_NAME" \
  --engine pg \
  --num-nodes 1 \
  --size db-s-1vcpu-1gb \
  --region "$REGION" >/dev/null

echo "==> Waiting for database to be ready (this can take ~2-3 minutes)"
sleep 120 || true

echo "==> Fetching DATABASE_URL"
DB_URI=$(doctl databases connection "$DB_NAME" --format URI --no-header)
if [[ -z "$DB_URI" ]]; then
  echo "ERROR: Failed to retrieve database URI" >&2
  exit 1
fi

echo "==> Generating SECRET_KEY"
SECRET_KEY=$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)

APP_SPEC="$(dirname "$0")/app.staging.yaml"
TMP_SPEC="$(dirname "$0")/.app.staging.filled.yaml"

echo "==> Preparing App Spec with secrets"
sed -e "s|__TO_FILL_AFTER_DB_CREATED__|$DB_URI|g" \
    -e "s|__TO_FILL_AFTER_GENERATION__|$SECRET_KEY|g" \
    "$APP_SPEC" > "$TMP_SPEC"

echo "==> Creating App Platform app: $APP_NAME"
APP_ID=$(doctl apps create --spec "$TMP_SPEC" --format ID --no-header)

echo "\nSUCCESS! Staging environment provisioning kicked off."
echo "App ID: $APP_ID"
echo "Database URI stored in spec (RUN_TIME)."
echo "
Next steps:
1) Monitor build/deploy: doctl apps get $APP_ID
2) Set FACEBOOK_COOKIES_JSON in App -> Settings -> Environment Variables (paste your cookies JSON)
3) Visit the live URL when status is Active.
"


