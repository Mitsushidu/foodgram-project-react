# FOODGRAM

## Описание
**Foodgram - сервис, позволяющий создавать и делиться рецептами, а также подписываться на других пользователей и следить за их рецептами**

Реализованный функционал: регистрация и авторизация на сайте, создание и редактирование рецепта, добавление его в избранное и список покупок, фильтрация по тегам и подписка на другого пользователя.

## Как запустить проект:
1. **Устанавливаем Docker и Docker Compose:**
    ```bash
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt install docker-compose-plugin 
    ```

2. **Клонируем репозиторий и переходим в папку с файлом docker-compose.yml:**
    ```bash
    git clone git@github.com:Mitsushidu/foodgram-project-react.git
    cd infra
    ```

3. **Создаем файл .env в папке infra:**
    ```bash
    sudo nano .env
    ```
    **Заполняем его следующими данными:**
    ```
    POSTGRES_DB=название_базы_данных
    POSTGRES_USER=имя_пользователя
    POSTGRES_PASSWORD=пароль

    DB_HOST=db
    DB_PORT=5432

    SECRET_KEY=сгенерированный_секретный_ключ
    DEBUG=False/True
    ALLOWED_HOSTS=разрешенные_хосты 
    ```
    Разрешенные хосты: '127.0.0.1 localhost'

4. **Запускаем контейнеры и сеть, связывающую их:**
    ```bash
    sudo docker compose up
    ```

5. **Создаем миграции, собираем статику бэкенда и копируем ее:**
    ```bash
    sudo docker compose exec backend python manage.py migrate
    sudo docker compose exec backend python manage.py collectstatic
    sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
    ```

6. **Заполняем базу данных ингредиентами:**
    ```bash
    sudo docker compose exec backend python manage.py load_data
    ```

7. **Переходим по ссылке https://localhost:5000/**



## Технический стек:
* Django = 3.2.3
* djangorestframework = 3.12.4
* djoser = 2.1.0
* Pillow = 10.0.1
* gunicorn = 20.1.0
* Postgres
* Docker


## Автор: mitsushidu

