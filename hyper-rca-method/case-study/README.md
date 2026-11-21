# Case study: correcting a coarse memory-fault ranking

Source: `output_csv_v2_gemini_3_8_flash_0318_run1`, case
`pod_memory_hog_catalogue_001` (original directory run1, not a relabeled manuscript run).
This is a retrospective illustrative success case, not an estimate of average improvement.

| Stage | Leading joint hypothesis | What is preserved |
|---|---|---|
| Global listwise | `orders-94d48dc8-prbdt` + `memory_stress` | catalogue is second |
| Pairwise judgments | catalogue beats orders | both forward and reversed presentations |
| Regularized BT | `catalogue-58bdd4d4f9-48jpd` + `memory_stress` | fitted ranking weight 0.252783; orders 0.198682 |
| Guarded comparison | catalogue accepted | both presentations support its entity, fault-type and overall fit |
| Final diagnosis | catalogue + `memory_stress` | matches the recorded injected Pod and catalog fault type |

The saved hypothesis explanations contrast a catalogue memory episode at 10:51–10:53
(reported peak 95.17%) with orders' elevated memory across the entire observation window
(reported peak 105.95%). Thus the largest reported magnitude did not remain the final
leader. These percentages are values recorded by the metric pipeline, not independently
verified physical memory-limit ratios. The ordinary pairwise calls intentionally omitted
explanations; the records do not establish which individual feature caused the model's
preference. Both candidates have the same fault type, so this example primarily illustrates
**entity selection under competing memory observations**, not separation of fault mechanisms.

There were 18 hypotheses, 68 effective pairs and 136 usable pairwise judgments, including
3 pairs with inconsistent orientation outcomes. Two guarded judgments accepted promotion.
**No refinement round executed**; the ranking change is therefore not caused by additional
telemetry retrieval in this execution. It reflects the combined pairwise/BT/guard workflow,
not proof that BT is superior to all other preference aggregators.

Files:

- `result.json`: complete saved structured result; local provenance/telemetry paths shortened (12 fields listed in the audit).
- `report.txt`: original readable report.
- `ranking_audit.json`: candidate identities, coarse/final order, decisive comparisons, guard results and provenance.
- `call_records.json`: all 24 logical calls in recorded **completion order**; two calls retried.
- `ground_truth.json`: injection metadata, used only for this offline evaluation; never an LLM input.

The historical raw requests and raw responses for **this case were not found**. The saved
comparison dictionaries are normalized outputs, not raw model responses. Exact request
start order cannot be reconstructed from completion records. Current templates must not
be described as the historical inputs. A separate genuine legacy I/O sample is provided
in [`../raw-io-example/`](../raw-io-example/).

Replay the aggregation and verify the recorded promotion without an API call:

```sh
python3 hyper-rca-method/tools/verify_case.py
```

The replay checks all fitted scores against the saved six-decimal values, the complete
candidate order, forward/reversed outcomes, guarded acceptance and the offline ground truth.
