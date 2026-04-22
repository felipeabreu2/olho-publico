#!/bin/sh
# Daily Postgres backup → Cloudflare R2.
#
# Requires aws-cli (in a custom image) and these env vars:
# - PGUSER, PGPASSWORD, PGHOST, PGDATABASE
# - R2_ACCOUNT_ID, R2_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

set -e

DATE=$(date -u +%Y%m%d-%H%M%S)
DUMP_FILE="/tmp/olho_publico_${DATE}.sql.gz"

pg_dump --no-owner --no-acl | gzip > "${DUMP_FILE}"

aws s3 cp "${DUMP_FILE}" "s3://${R2_BUCKET}/postgres/${DATE}.sql.gz" \
  --endpoint-url "https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

rm "${DUMP_FILE}"
echo "Backup ${DATE} enviado."
