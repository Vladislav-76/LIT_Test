# LIT_Test

Это проект, который включает в себя создание RESTful API с Django.  
Aутентификацию и авторизацию с дополнительным подтверждением пользователя OTP-кодом. Настройку Celery, Redis для очередей сообщений.

------------

#### Разворачиваем проект.
Проект настроен для простой локальной установки в Docker контейнерах.
После клонирования проекта можно создать .env файл из .env.sample с настройками отличными от дефолтных.  
Команда для сборки и запуска контейнеров.  
`make up`

Запустится пять контейнеров:
1. db (Postgress)
2. nginx
3. backend
4. worker
5. redis

Команда для выполнения миграций, сбора статики и создания суперюзера (email: admin@test.com, пароль: 123).  
`make build`

Проект работает на следующих адресах:  
Админка: http://localhost:8000/admin/  
Документация API: http://localhost:8000/swagger/

------------
#### Описание API для управления пользователями и авторизации.  
Для упрощения использования API в проекте находится Postman-коллекция в которой собраны основные эндпойнты с образцами тел запросов.
 
##### Создание пользователя
Создание пользователя производится POST-запросом по адресу:  
http://localhost:8000/api/v1/auth/user/
Создается неактивный пользователь. На указанную при регистрации почту отправляется письмо с OTP-кодом для подтверждения и активации пользователя.
Отправка письма эмулирована. Письмо сохраняется в папку emails контейнера worker.  
Команда просмотра содержимого папки emails:  
`docker compose exec worker ls emails`  
Команда просмотра письма (название файла заменить на корректное):  
`docker compose exec worker head -n20 emails/20240402-162130-139799482503936.log`
 
##### Активация пользователя
Активация пользователя производится POST-запросом по адресу:  
http://localhost:8000/api/v1/auth/user/activation/  
Время жизни кода полученного в письме ограничено соответствующим параметром в настройках проекта.  
При валидном сочетании почты пользователя, кода и времени происходит активация пользователя. В обратном случае возвращается статус 400, дополнительной информации не сообщается из соображений секьюрности.
 
##### Получение токена
Получение возможно только после активации. Получение токена производится POST-запросом по адресу:  
http://localhost:8000/api/v1/auth/jwt/create/
 
##### Управление пользователем
Управление требует авторизации с использованием JWT-токена. Управление осуществляется по адресу:  
http://localhost:8000/api/v1/auth/user/me/  
Реализованы:
- просмотр данных пользователя (GET-запрос)
- изменение данных пользователя (PATCH-запрос)
- удаление пользователя (DELETE-запрос)
