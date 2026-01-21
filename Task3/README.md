# Task 3.1: MVP с OpenTelemetry и Jaeger

Демонстрация distributed tracing с двумя сервисами.

## Архитектура

```
[Service A: Order Service] --HTTP--> [Service B: Calculation Service]
         |                                    |
         |                                    |
         +---------> [Jaeger] <---------------+
                   (OTLP gRPC)
```

- **Service A** (port 8080): Сервис заказов - принимает запросы и вызывает Service B
- **Service B** (port 8081): Сервис расчетов - имитирует расчет стоимости (как MES)
- **Jaeger**: Собирает и визуализирует трейсы

## Требования

- Docker
- Kubernetes (minikube, kind, или Docker Desktop с Kubernetes)
- kubectl

## Запуск

### 1. Запустите minikube (если используете minikube)

```bash
minikube start
eval $(minikube docker-env)  # Для использования локальных образов
```

### 2. Соберите Docker образы

```bash
# Из корня Task3
cd service-a
docker build -t service-a:latest .

cd ../service-b
docker build -t service-b:latest .
```

### 3. Разверните в Kubernetes

```bash
# Из папки k8s
kubectl apply -f jaeger.yaml
kubectl apply -f service-a.yaml
kubectl apply -f service-b.yaml

# Проверьте статус
kubectl get pods
kubectl get services
```

### 4. Дождитесь запуска всех pod'ов

```bash
kubectl wait --for=condition=ready pod -l app=jaeger --timeout=120s
kubectl wait --for=condition=ready pod -l app=service-a --timeout=120s
kubectl wait --for=condition=ready pod -l app=service-b --timeout=120s
```

### 5. Сделайте тестовый вызов

```bash
# Вызов service-a, который вызывает service-b
kubectl exec -it $(kubectl get pods -l app=service-a -o jsonpath='{.items[0].metadata.name}') -- wget -qO- http://service-a:8080
```

Ожидаемый результат:
```json
{
  "service": "service-a (Order Service)",
  "order_id": "ORD-12345",
  "price": 847.23,
  "status": "Order created and price calculated",
  "trace_info": "Check Jaeger UI for distributed trace"
}
```

### 6. Откройте Jaeger UI

```bash
kubectl port-forward svc/simplest-query 16686:16686
```

Откройте в браузере: http://localhost:16686

### 7. Найдите трейс

1. В Jaeger UI выберите сервис `service-a-orders`
2. Нажмите "Find Traces"
3. Кликните на трейс чтобы увидеть полную цепочку вызовов

## Структура трейса

```
service-a-orders: GET /
  └── create-order
      └── call-calculation-service
          └── service-b-calculation: GET /calculate
              └── calculate-price
                  ├── fetch-model-data
                  ├── compute-materials-cost
                  └── compute-labor-cost
```

## Скриншот

После выполнения шагов выше, сделайте скриншот трейса в Jaeger UI и сохраните его в папку Task3.

## Очистка

```bash
kubectl delete -f service-a.yaml
kubectl delete -f service-b.yaml
kubectl delete -f jaeger.yaml
```

## Атрибуты в трейсах

Каждый span содержит бизнес-атрибуты:

| Span | Атрибуты |
|------|----------|
| create-order | order.id, order.status, order.price |
| calculate-price | order.id, price.total, price.materials, price.labor |
| fetch-model-data | model.complexity |

Эти атрибуты позволяют искать трейсы по бизнес-данным (например, по order_id).
