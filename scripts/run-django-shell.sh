#!/usr/bin/env bash
set -euo pipefail

docker compose exec -it backend python manage.py shell -v 2
