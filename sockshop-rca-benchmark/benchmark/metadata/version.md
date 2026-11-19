# Benchmark Metadata Version

## Version 1.0.0

**Status:** public artifact metadata

This metadata describes the EnhancedSockShopBench package associated with HYPER-RCA.

## Summary

- Application: enhanced Sock Shop
- Workload generator: Locust
- Fault injection: Chaos Mesh
- Fault cases: 320
- Normal baseline cases: 100
- Experiment days: 5
- Telemetry modalities: metrics, logs, traces
- Reported distinct metric names: 1,337
- Primary metric sampling interval: 5 seconds

## Fault Actions

- network delay
- network loss
- network partition
- CPU stress
- memory stress
- pod failure
- JVM exception injection
- I/O fault injection

## Included Metadata Modules

- `dataset_description.json`
- `services_topology.json`
- metric-name inventories under `benchmark/telemetry/data/metrics/types/`
- Chaos Mesh YAML specifications under `benchmark/chaos/chaosmesh/`

## Dataset Release Notes

Full raw telemetry archives and case-level metadata are distributed through the released dataset folder rather than duplicated directly in this Git repository:

https://drive.google.com/drive/folders/1dBNDc2YUYyjJch_BmhO-Hx-0YvdPHHl_?usp=drive_link

Case labels are derived from structured `fault_metadata.json` files and workload windows are derived from `workload_metadata.json`.

## Documentation and Data Licensing

See [DATASHEET.md](../../DATASHEET.md) for collection and evaluation details and
[LICENSE-DATA](../../LICENSE-DATA) for the CC BY 4.0 dataset license.
Metric-name inventories may contain collection candidates beyond the 1,337
reported distinct names.
