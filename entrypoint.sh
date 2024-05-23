#!/bin/bash

set -e

SERVICE_ACCOUNT_KEY_FILE=/app/service-account.json
SERVICE_ACCOUNT_SECRET=/run/secrets/service_account_key

if test -f ${SERVICE_ACCOUNT_SECRET} -a ! -f ${SERVICE_ACCOUNT_KEY_FILE}; then
    ln -s ${SERVICE_ACCOUNT_SECRET} ${SERVICE_ACCOUNT_KEY_FILE}
    echo "Link to service account key file created"
fi

exec "$@"