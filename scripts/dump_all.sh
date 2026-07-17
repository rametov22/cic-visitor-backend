#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

COMPOSE="${COMPOSE:-docker compose}"
EXEC="${EXEC:-}"
WITH_MEDIA=0
for argument in "$@"; do
    case "$argument" in
        media | --media) WITH_MEDIA=1 ;;
    esac
done

timestamp="$(date +%Y-%m-%d_%H-%M-%S)"
directory="dumps/${timestamp}"
mkdir -p "$directory"
chmod 700 "$directory"

echo "Backing up to ${directory}"
echo "  database"
$COMPOSE exec -T db sh -c \
    'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges' \
    | gzip >"${directory}/database.sql.gz"
gzip -t "${directory}/database.sql.gz"

echo "  media manifest"
$COMPOSE exec -T $EXEC backend python manage.py media_info \
    >"${directory}/manifest.json"

if [ "$WITH_MEDIA" -eq 1 ]; then
    echo "  media files"
    $COMPOSE exec -T $EXEC backend python manage.py media_dump \
        >"${directory}/media.tar.gz"
    tar -tzf "${directory}/media.tar.gz" >/dev/null
fi

echo "Backup complete:"
du -sh "$directory"/* 2>/dev/null || true
