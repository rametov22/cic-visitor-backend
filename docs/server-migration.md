# Перенос CIC Visitor на новый сервер

Этот runbook переносит код, PostgreSQL и media с возможностью отката. Он рассчитан
на перенос из локального Docker volume старого сервера в локальный Docker volume
нового сервера. Объектное хранилище не используется.

## 1. Подготовка

1. Уменьшить DNS TTL заранее.
2. Проверить свободное место на обоих серверах: архив временно занимает объём БД
   плюс весь media.
3. Установить Docker Engine и Docker Compose v2 на новом сервере.
4. Зафиксировать текущий домен, edge proxy, имя Compose-проекта и имена volumes:

   ```bash
   docker compose -f docker-compose.prod.yml ps
   docker volume ls | grep iccu-visitor
   ```

5. Собрать и отправить образ с точным тегом commit SHA. Для production не
   использовать только плавающий `latest`.

## 2. Совместимый деплой на старом сервере

Сохранить старое имя проекта, чтобы новый Compose подключил существующие volumes:

```dotenv
ENVIRONMENT=prod
PROJECT_NAME=iccu-visitor
BACKEND_IMAGE=registry-test.glob.uz/iccu/visitor-backend:sha-<full-sha>
DJANGO_SECRET_KEY=<текущее значение SECRET_KEY>
```

Также заполнить точные `DJANGO_ALLOWED_HOSTS`,
`DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_CORS_ALLOWED_ORIGINS`, PostgreSQL и Redis.
Не копировать `.env` в Git.

Развернуть без удаления volumes:

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
curl -fsS http://127.0.0.1:${APP_PORT}/healthcheck/
```

Запрещено выполнять `down -v`: эта команда удалит production БД и media.

Создать пробный полный архив:

```bash
make prod dump media
ls -lah dumps/<timestamp>/
gzip -t dumps/<timestamp>/database.sql.gz
tar -tzf dumps/<timestamp>/media.tar.gz >/dev/null
```

Скопировать архив за пределы старого сервера и провести тестовое восстановление
до окна переключения.

## 3. Подготовка нового сервера

Клонировать репозиторий на точный проверенный commit и создать новый `.env`:

```dotenv
ENVIRONMENT=prod
PROJECT_NAME=iccu-visitor
BACKEND_IMAGE=registry-test.glob.uz/iccu/visitor-backend:sha-<full-sha>
DJANGO_SECRET_KEY=<тот же ключ, что на старом сервере>
DJANGO_ALLOWED_HOSTS=<production-domain>
DJANGO_CSRF_TRUSTED_ORIGINS=https://<production-domain>
DJANGO_CORS_ALLOWED_ORIGINS=https://<frontend-domain>
```

Указать новые PostgreSQL credentials. База должна быть недоступна извне; наружу
публикуется только порт внутреннего Nginx, и то через edge proxy/firewall. Compose
сам создаст volumes `postgres-data`, `redis-data`, `django-static` и
`django-media`.

Запустить пустой стек:

```bash
make prod deploy
docker compose -f docker-compose.prod.yml ps
```

Передать тестовый архив:

```bash
rsync -av --progress \
  old-server:/path/to/cic_visitor/dumps/<timestamp>/ \
  /path/to/cic_visitor/dumps/<timestamp>/
```

Восстановить и проверить:

```bash
make prod restore dumps/<timestamp>
docker compose -f docker-compose.prod.yml exec backend \
  python manage.py showmigrations
docker compose -f docker-compose.prod.yml exec backend \
  python manage.py check --deploy
curl -fsS http://127.0.0.1:${APP_PORT}/healthcheck/
```

Проверить вход в админку, количество записей, расписание, rules/FAQ/map API и
открытие всех картинок по URL `/media/...`.

## 4. Финальное переключение

1. Закрыть запись на старом сервере через maintenance mode edge proxy.
2. Убедиться, что пользователи больше не меняют данные через admin.
3. Создать финальный архив `make prod dump media`.
4. Скопировать его на новый сервер и повторить `make prod restore`.
5. Выполнить smoke-проверки.
6. Переключить upstream edge proxy или DNS на новый сервер.
7. Наблюдать healthcheck, HTTP 5xx, Gunicorn, PostgreSQL и media не менее одного
   полного рабочего цикла.

Старый сервер не удалять сразу. Оставить его выключенным для записи, но готовым к
откату.

## 5. Откат

Если новый сервер неисправен до появления новых production-записей, вернуть
edge/DNS на старый сервер. Если записи уже появились на новом сервере, простой
переключатель создаст расхождение баз: сначала снова включить maintenance mode,
снять dump с актуального источника и восстановить его на выбранной стороне.

После стабильного периода включить профиль автоматического backup БД:

```dotenv
COMPOSE_PROFILES=backup
DB_BACKUP_FS_PATH=/srv/backups/cic-visitor
```

Media сохранять вместе с базой командой `make prod dump media` и регулярно
копировать каталог `dumps/` за пределы сервера. Резервная копия считается рабочей
только после успешной проверки восстановления.
