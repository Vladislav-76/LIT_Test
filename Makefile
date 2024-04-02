# DEV_CONTAINER = dev_lizaalert
DEV_DB_CONTAINER = dev_db_psql
DEV_DB_VOLUME = dev_db_volume
DEV_DB_NAME = lit
DEV_DB_USER = postgres
DEV_DB_PASSWORD = password

# DEV_USER = Liza
# DEV_USER_MAIL = liza@alert.ru
# DEV_USER_PS = ps

dev-rebuild:
	-docker stop $(DEV_DB_CONTAINER)
	-docker volume rm $(DEV_DB_VOLUME)

	docker run -d --rm\
    --name $(DEV_DB_CONTAINER) \
    -p 5432:5432 \
    --mount type=volume,src=$(DEV_DB_VOLUME),dst=/var/lib/postgresql/data \
    -e POSTGRES_PASSWORD=$(DEV_DB_PASSWORD) \
	-e POSTGRES_DB=$(DEV_DB_NAME) \
    postgres:14-alpine

dev-web:
	# docker network create lit-network

	# docker network connect lit-network dev_db_psql

	docker build -t lit_web ./

	docker run --env-file .env \
               --net lit-network \
               --name lit_web \
               --rm -p 8000:8000 lit_web

# docker-compose up
# docker compose exec backend python manage.py migrate
# docker compose exec backend python manage.py collectstatic
# docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
