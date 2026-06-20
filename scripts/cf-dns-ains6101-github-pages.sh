#!/usr/bin/env bash
set -euo pipefail

: "${CLOUDFLARE_API_TOKEN:?Set CLOUDFLARE_API_TOKEN}"
: "${CLOUDFLARE_ZONE_ID:?Set CLOUDFLARE_ZONE_ID}"

curl -sS -X POST "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/dns_records" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"type":"CNAME","name":"ains6101.courses","content":"castaliainstitute.github.io","proxied":true}'
