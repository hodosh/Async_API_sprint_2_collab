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

# Описание
1. Данные формируются для каждой сущности в папках `tests/functional/testdata` (создание индекса в ElasticSearch, 
наполнение тестового индекса данными).
2. Тесты сформированы как классы, в классах есть методы setup_class и teardown_class, 
которые соответственно осуществляют загрузку и удаление данных и индексов.
3. Основные методы для работы реализованы как фикстуры, располагаются тут `tests/functional/conftest.py`.
4. Перед работой тестов запускаются функции ожидания поднятия сервисов Redis и ElasticSearch,
описанные в `tests/functional/utils`.
