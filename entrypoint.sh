#!/bin/bash

set -e

SERVICE_ACCOUNT_KEY_FILE=/app/service-account.json
SERVICE_ACCOUNT_SECRET=/run/secrets/service_account_key

if test -f ${SERVICE_ACCOUNT_SECRET} -a ! -f ${SERVICE_ACCOUNT_KEY_FILE}; then
    ln -s ${SERVICE_ACCOUNT_SECRET} ${SERVICE_ACCOUNT_KEY_FILE}
    echo "Link to service account key file created"
fi

POSTGRES_SECRET_FILE=${POSTGRES_SECRET_FILE:-/tmp/postgres-secret.json}

if [ -n "$POSTGRES_SECRET_JSON_B64" ] && [ ! -f "$POSTGRES_SECRET_FILE" ]; then
    mkdir -p "$(dirname "$POSTGRES_SECRET_FILE")"
    echo "$POSTGRES_SECRET_JSON_B64" | base64 -d > "$POSTGRES_SECRET_FILE"
    echo "Decoded POSTGRES_SECRET_JSON_B64 to $POSTGRES_SECRET_FILE"
elif [ -n "$POSTGRES_SECRET_JSON" ] && [ ! -f "$POSTGRES_SECRET_FILE" ]; then
    mkdir -p "$(dirname "$POSTGRES_SECRET_FILE")"
    echo "$POSTGRES_SECRET_JSON" > "$POSTGRES_SECRET_FILE"
    echo "Wrote POSTGRES_SECRET_JSON to $POSTGRES_SECRET_FILE"
elif test -f /run/secrets/postgres_secret -a ! -f "$POSTGRES_SECRET_FILE"; then
    mkdir -p "$(dirname "$POSTGRES_SECRET_FILE")"
    ln -s /run/secrets/postgres_secret "$POSTGRES_SECRET_FILE"
    echo "Link to postgres secret file created"
fi

exec "$@"
