# Тесты

Для запуска тестов необходимо выполнить следующее:
1. Заполнить файлы переменных окружения .env (примеры в тех же папках .env.example) для:
   - postgres/.env
   - etl/app/etl/.env
   - app/src/core/.env
   - app/src/core/.env.dev
   - tests/functional/.env

2. Запустить докер-компоуз командой `docker-compose --file docker-compose-dev.yml up`
3. Дождаться выполнения тестов в контейнере tests. По итогу в папке `tests/functional/results` сформируется html-отчет
