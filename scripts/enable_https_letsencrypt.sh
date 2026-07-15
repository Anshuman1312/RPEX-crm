#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   DOMAIN=srv1829331.hstgr.cloud EMAIL=you@example.com ./scripts/enable_https_letsencrypt.sh

DOMAIN="${DOMAIN:?DOMAIN is required, e.g. srv1829331.hstgr.cloud}"
EMAIL="${EMAIL:?EMAIL is required for Let's Encrypt notices}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "ERROR: docker compose file '$COMPOSE_FILE' not found"
  exit 1
fi

if [ "$DOMAIN" != "srv1829331.hstgr.cloud" ]; then
  echo "WARNING: nginx SSL template is currently configured for srv1829331.hstgr.cloud"
  echo "Update infra/nginx/nginx.ssl.conf before proceeding for domain: $DOMAIN"
  exit 1
fi

echo "Starting nginx and services for ACME challenge..."
docker compose -f "$COMPOSE_FILE" up -d nginx backend frontend

echo "Requesting certificate for $DOMAIN ..."
docker compose -f "$COMPOSE_FILE" run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  --email "$EMAIL" \
  -d "$DOMAIN" \
  --agree-tos --no-eff-email --non-interactive

echo "Switching nginx to SSL configuration..."
cp infra/nginx/nginx.ssl.conf infra/nginx/nginx.conf

docker compose -f "$COMPOSE_FILE" up -d nginx

echo "HTTPS enabled. Visit: https://$DOMAIN"
