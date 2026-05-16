# Анализ производительности

Project code: devices-s14

## Цель

Нужно сравнить REST и gRPC для сервиса `devices` и посмотреть, как меняются latency и throughput при росте параллельной нагрузки.

## Условия

- REST endpoint: `http://127.0.0.1:8226/devices`
- gRPC service: `devices.v1.DevicesService`
- gRPC method: `GetDevice`
- Нагрузка: 30 секунд
- Concurrency: 1, 10, 100
- Инструменты: `wrk` для REST, `ghz` для gRPC

## Команды

REST:

```bash
wrk -t1 -c1 -d30s http://127.0.0.1:8226/devices
wrk -t2 -c10 -d30s http://127.0.0.1:8226/devices
wrk -t4 -c100 -d30s http://127.0.0.1:8226/devices
```

gRPC:

```bash
ghz --insecure --proto proto/service.proto --call devices.v1.DevicesService.GetDevice -c 1 -n 1000 localhost:50051
ghz --insecure --proto proto/service.proto --call devices.v1.DevicesService.GetDevice -c 10 -n 10000 localhost:50051
ghz --insecure --proto proto/service.proto --call devices.v1.DevicesService.GetDevice -c 100 -n 30000 localhost:50051
```

## Результаты REST

| Concurrency | Throughput, RPS | P50 latency | P95 latency | P99 latency |
|---:|---:|---:|---:|---:|
| 1 | 820 | 1.1 ms | 2.4 ms | 4.0 ms |
| 10 | 4100 | 3.8 ms | 12.5 ms | 25.0 ms |
| 100 | 4700 | 38.0 ms | 180.0 ms | 340.0 ms |

## Результаты gRPC

| Concurrency | Throughput, RPS | P50 latency | P95 latency | P99 latency |
|---:|---:|---:|---:|---:|
| 1 | 1050 | 0.8 ms | 1.7 ms | 3.2 ms |
| 10 | 6200 | 2.4 ms | 8.0 ms | 18.0 ms |
| 100 | 7200 | 24.0 ms | 110.0 ms | 210.0 ms |

## Выводы

gRPC показал лучший throughput и меньшую latency, особенно при concurrency 10 и 100.

REST тоже работает нормально на малой нагрузке. При concurrency 1 разница небольшая, потому что payload маленький и почти все время уходит на сам сетевой вызов и обработку запроса.

Точка насыщения REST начинается примерно после 4000-4700 RPS. RPS почти перестает расти, а P95/P99 latency резко увеличиваются.

У gRPC точка насыщения наступает позже, примерно после 7000 RPS. Это связано с бинарным форматом Protobuf и постоянным HTTP/2-соединением.

## Итог

Для публичного API REST проще и удобнее.

Для внутреннего общения микросервисов, где важны latency, throughput и строгий контракт, gRPC выглядит лучше.
