# Architecture Pro - Alexandrite

Проектная работа 6 спринта курса по архитектуре.

## О проекте

Компания "Александрит" - ювелирное производство с возможностью создания украшений по индивидуальному дизайну через 3D-конструктор.

## Структура решения

| Папка | Задание | Описание |
|-------|---------|----------|
| Task1 | Анализ и планирование | Идентификация проблем, инициативы, целевая архитектура |
| Task2 | Мониторинг | Выбор метрик (RED/USE), план внедрения Prometheus + Grafana |
| Task3 | Трейсинг | OpenTelemetry + Jaeger, MVP с двумя сервисами |
| Task4 | Логирование | OpenSearch, политики хранения и безопасности |
| Task5 | Кеширование | Redis Cache-Aside, Sequence диаграммы |

## Технологии

- **Мониторинг:** Prometheus, Grafana, Alertmanager
- **Трейсинг:** OpenTelemetry, Jaeger
- **Логирование:** Fluent Bit, OpenSearch
- **Кеширование:** Redis

## Запуск MVP трейсинга (Task3)

```bash
cd Task3
docker-compose up -d --build
# Открыть http://localhost:16686 (Jaeger UI)
# Вызвать http://localhost:8080 для создания трейса
```
