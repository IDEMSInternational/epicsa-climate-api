#!/bin/bash

set -e

SERVICE_ACCOUNT_KEY_FILE=/app/service-account.json
SERVICE_ACCOUNT_SECRET=/run/secrets/service_account_key
POSTGRES_SECRET_FILE=${POSTGRES_SECRET_FILE:-/tmp/postgres-secret.json}

if test -f ${SERVICE_ACCOUNT_SECRET} -a ! -f ${SERVICE_ACCOUNT_KEY_FILE}; then
    ln -s ${SERVICE_ACCOUNT_SECRET} ${SERVICE_ACCOUNT_KEY_FILE}
    echo "Link to service account key file created"
fi

# Materialize postgres secret file from base64 content when provided via env var.
# This avoids baking DB credentials into the image while keeping file-based loading.
if test -n "${POSTGRES_SECRET_JSON_B64}" -a ! -f "${POSTGRES_SECRET_FILE}"; then
    mkdir -p "$(dirname "${POSTGRES_SECRET_FILE}")"
    printf '%s' "${POSTGRES_SECRET_JSON_B64}" | base64 -d > "${POSTGRES_SECRET_FILE}"
    chmod 600 "${POSTGRES_SECRET_FILE}" || true
    echo "Postgres secret file created from POSTGRES_SECRET_JSON_B64"
fi

exec "$@"