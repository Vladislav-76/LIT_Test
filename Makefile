ADMIN_USER = admin
ADMIN_USER_MAIL = admin@test.com
ADMIN_USER_PS = 123
ADMIN_FIRST_NAME = admin
ADMIN_LAST_NAME = admin

up:
	docker compose up --build

build:
	docker compose exec backend python manage.py migrate
	docker compose exec backend python manage.py collectstatic
	docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
	docker compose exec -it \
		-e DJANGO_SUPERUSER_PASSWORD=$(ADMIN_USER_PS) \
		-e DJANGO_SUPERUSER_USERNAME=$(ADMIN_USER) \
		-e DJANGO_SUPERUSER_EMAIL=$(ADMIN_USER_MAIL) \
		-e DJANGO_SUPERUSER_FIRST_NAME=$(ADMIN_FIRST_NAME) \
		-e DJANGO_SUPERUSER_LAST_NAME=$(ADMIN_LAST_NAME) \
		backend python manage.py createsuperuser --no-input
