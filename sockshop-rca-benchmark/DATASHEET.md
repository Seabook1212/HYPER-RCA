# EnhancedSockShopBench Data Sheet

## Purpose and scope

EnhancedSockShopBench supports microservice root cause analysis (RCA) using
metrics, logs, traces, topology, and fault labels. Data were collected from an
enhanced Sock Shop Kubernetes testbed using Locust traffic and Chaos Mesh fault
injection. HYPER-RCA is the associated RCA method.

## Composition

| Item | Description |
| --- | --- |
| Collection dates | March 12, 13, 14, 17, and 18, 2026 |
| Fault cases | 320: 64 per collection day, with one injected root cause per case |
| Normal references | 100 normal runs |
| Baseline deployment | 14 services and 22 Pods |
| Replicas | Two each for front-end, orders, carts, catalogue, user, payment, shipping, and queue-master; one each for orders-db, carts-db, catalogue-db, user-db, session-db, and rabbitmq |
| Telemetry | Prometheus metrics, Loki logs, and Jaeger traces; approximately 210 GB |
| Reported metric coverage | 1,337 distinct metric names; entity instances and label combinations are not counted separately |
| Metric sampling | Predominantly 5 seconds |

Metric-name inventories include collection candidates; availability varies by run.

| Fault action | Cases per day | Total cases |
| --- | ---: | ---: |
| CPU stress | 14 | 70 |
| Memory stress | 8 | 40 |
| Pod failure | 12 | 60 |
| JVM exception injection | 3 | 15 |
| I/O fault injection | 3 | 15 |
| Network delay | 8 | 40 |
| Network loss | 8 | 40 |
| Network partition | 8 | 40 |
| **Total** | **64** | **320** |

## Files, time, and labels

The [dataset download](https://huggingface.co/datasets/Seabook1111/EnhancedSockShopBench/tree/main)
contains fault/normal run directories (e.g., `fault_run_0603`, `normal_run_0603`)
and `telemetry/<date>/`.

- CSV telemetry contains metric values and labels, log messages, and trace spans
  with timing and entity metadata, as available.
- `workload/workload_metadata.json` records workload windows and configuration;
  `fault_info/fault_metadata.json` records injection targets, timing, and parameters.
  Injection timing need not equal symptom onset or recovery.
- Times use UTC, including CSV strings without timezone suffixes. Interpret numeric
  timestamp units using the corresponding collector/parser.
- Labels identify the service, Pod, and injected fault type. Case identifiers and
  fault metadata reveal ground truth: exclude them from diagnostic model inputs
  and use labels only for evaluation.

## Recommended evaluation

Use March 12 (64 fault cases) for development and the other four days (256 cases)
for evaluation. The split is by day; system and fault scenarios are shared across
days. Select the closest normal reference from the same day and workload setting.
Keep cases, windows, topology, and telemetry availability identical across methods.

## Limitations and reuse

The release covers one testbed and single injected faults, not live production
incidents or concurrent faults. Replication may mask user-facing impact; not every
injection is required to cause measurable user-visible degradation. Shared node
measurements alone do not identify a faulty Pod.

See [LICENSE-DATA](LICENSE-DATA) for CC BY 4.0 data terms; code is excluded.
Credit the creators and dataset, identify the release used, and describe changes.
Report corrections or questions through the
[artifact repository](https://github.com/Seabook1212/HYPER-RCA/issues).
