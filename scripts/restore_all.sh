#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

COMPOSE="${COMPOSE:-docker compose}"
EXEC="${EXEC:-}"
directory="${1:-}"

if [ -z "$directory" ] || [ ! -d "$directory" ]; then
    echo "Usage: ./scripts/restore_all.sh dumps/<timestamp>" >&2
    exit 1
fi
if [ ! -f "$directory/database.sql.gz" ]; then
    echo "Error: ${directory}/database.sql.gz is missing." >&2
    exit 1
fi
gzip -t "$directory/database.sql.gz"
if [ -f "$directory/media.tar.gz" ]; then
    tar -tzf "$directory/media.tar.gz" >/dev/null
fi

echo "Restoring from ${directory}"
echo "  database"
gunzip -c "$directory/database.sql.gz" \
    | $COMPOSE exec -T db sh -c \
        'exec psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -q -v ON_ERROR_STOP=1'

echo "  migrations"
$COMPOSE exec -T $EXEC backend python manage.py migrate --no-input

if [ -f "$directory/media.tar.gz" ]; then
    echo "  media files"
    $COMPOSE exec -T $EXEC backend python manage.py media_load \
        <"$directory/media.tar.gz"
fi

if [ -f "$directory/manifest.json" ]; then
    old_base="$(
        python3 -c \
            'import json, sys; print(json.load(open(sys.argv[1]))["media_base_url"])' \
            "$directory/manifest.json"
    )"
    case "$old_base" in
        http://* | https://*)
            echo "  embedded media URLs"
            $COMPOSE exec -T $EXEC backend \
                python manage.py rewrite_media_urls --from "$old_base"
            ;;
        *)
            echo "  embedded media URLs skipped (old base is relative: ${old_base})"
            ;;
    esac
fi

echo "Restore complete."
