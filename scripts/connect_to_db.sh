#!/usr/bin/env bash
set -euo pipefail

docker compose exec -it db sh -c \
    'exec psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
