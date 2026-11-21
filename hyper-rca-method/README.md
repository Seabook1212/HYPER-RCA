# HYPER-RCA method artifacts

This folder complements [`../sockshop-rca-benchmark/`](../sockshop-rca-benchmark/)
with prompt documentation, a verifiable pairwise/BT case study, and real historical LLM
I/O. It is a compact inspection artifact, not the complete runnable framework.

| Folder | Contents |
|---|---|
| [`prompts/`](prompts/) | Six source-derived system prompts and payload scaffolds: Hypothesis (single/batch), listwise, pairwise, guarded BT and Refine; fault catalog included |
| [`case-study/`](case-study/) | catalogue memory-fault example: orders leads the coarse order, catalogue wins pairwise/BT/guard; no refinement executed |
| [`raw-io-example/`](raw-io-example/) | One genuine older Hypothesis request and raw response, with original logged timestamps and model name |
| [`tools/`](tools/) | Offline case verification and an opt-in recorder for future full-case LLM traces |

**Availability:** the case study has complete saved structured results, but its historical
raw prompt/response log was not retained in the files found. The raw I/O example is a
different, older execution. It must not be joined to the case study or represented as a
complete end-to-end trace. No missing raw content was reconstructed or invented.
`source_manifest.json` identifies source files and hashes; current prompt snapshots and
historical outputs are explicitly distinguished.

## Verify the case study

```sh
python3 hyper-rca-method/tools/verify_case.py
```

This uses Python's standard library only. It refits BT from saved judgments and checks
the full final order, guard decisions and ground truth; it does not call an LLM.

## Record a future full case

Use the Python environment and local checkout that already run the method. The wrapper
observes its existing transport hook without changing the prompts or RCA decisions:

```sh
python hyper-rca-method/tools/capture_case.py \
  --source-project /path/to/LLM_agent_skills_v2 \
  --trace-file /path/to/new_run/llm_io.jsonl \
  -- baseline --case pod_memory_hog_catalogue_001 \
  --dataset-tag 0318 --provider gemini --model gemini-3.8-flash \
  --output-dir /path/to/new_run/results
```

This command makes normal provider API calls and requires the corresponding CSV dataset
to be unpacked in the source project's expected locations. It produces a **new execution**,
which may have a different ranking; it cannot restore the missing historical transcript.
Do not overwrite the released case study with a rerun while retaining its original claims.

The JSONL records UTC timestamps, an ordered event sequence, logical call IDs, request
attempts, configured decoding settings, actual application-level request payloads, and
the raw model text supplied by the existing client. Parallel request and response order
are recorded separately. Gemini records contain its unmodified `text` plus logged model
version/usage metadata, not a full HTTP/SDK envelope. Known credential dictionary keys are
redacted; prompt content is otherwise preserved. Original report/result outputs continue
to be written by the runner. The trace file must be new to avoid mixing executions.

For a publication bundle, keep `llm_io.jsonl`, the resulting report/result files and the
effective configuration from the **same** execution together. A raw transcript for a
future run is not evidence of the exact prompts used in an earlier experiment.
