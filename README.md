![Github actions](https://github.com/DDanielleinaDD/foodgram-project-react/actions/workflows/main.yml/badge.svg)
##  Продуктовый помощник - foodgram

### Сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «cписок покупок» позволит пользователям создавать список ингредиентов, которые нужно купить для приготовления выбранных блюд. Есть возможность выгрузить файл (.pdf) с перечнем и количеством необходимых ингредиентов для рецептов.
---
Стек технологий проекта:
 - JavaScript
 - Python
 - Django Rest Framework
 - PostgreSQL
 - Nginx
 - Docker
----
#### Сайт доступен по адресу - https://foodgram-prjct.ddnsking.com/
Логин и пароль для Админ-зоны:
- admin 
- 120899Dn
-----
Для локального запуска проекта необходимо:
 - Клонировать проект локально:
 `git clone git@github.com:DDanielleinaDD/foodgram-project-react.git`
 - Перейдите в каталог infra:
 `cd .../foodgram-project-react/infra`
 - Создайте файл .env для корректной работы проекта:
 ```
SECRET_KEY = 'секретный ключ Django проекта'
DB_NAME=postgres # указываем имя созданной базы данных
POSTGRES_USER=postgres # указываем имя своего пользователя для подключения к БД
POSTGRES_PASSWORD=postgres # устанавливаем свой пароль для подключения к БД
DB_HOST=db # указываем название сервиса (контейнера)
DB_PORT=5432 # указываем порт для подключения к БД 
```
-   Запустите docker-compose, развёртывание контейнеров выполниться в «фоновом режиме»:
`docker-compose up`
-   выполните миграции:
`docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate`
-   соберите статику:
`docker-compose exec backend python manage.py collectstatic --no-input`
-   cоздайте суперпользователя:
`docker-compose exec backend python manage.py createsuperuser`
-   загрузите в базу список ингридиентов:
`docker-compose exec backend python manage.py csvimport`

## Проект готов к работе.

Backend разработал Носков Д.С. ([DDanielleinaDD](https://github.com/DDanielleinaDD))