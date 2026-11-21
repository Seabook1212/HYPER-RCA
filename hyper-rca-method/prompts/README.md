# Prompt templates

Six JSON files cover single-Pod/batched Hypothesis, global listwise, batched pairwise (including anchor and recovery calls), guarded BT, and Refine planning. `system_instruction` is copied verbatim from the current method source; `payload_template` is a readable scaffold. Strings in angle brackets are runtime placeholders, not actual observations or sent requests. Optional fields and instructions depend on the evidence and configuration; the JSON is not directly executable.

The fault descriptions and differential guidance are in `fault_catalog.yaml`. Evidence is referenced once and retains its entity ownership. Listwise returns ordinal IDs; pairwise returns winners or ties; guarded BT assesses entity, fault-type, and overall fit; Refine proposes non-executable query sketches.

This is a source snapshot from 2026-11-21, not proof of the exact prompt text used in an earlier experiment. The case-study result and legacy I/O example below have separate provenance. Other workflow calls (e.g., request parsing and the monolithic ablation) are outside this compact release.

Before transport, `LLMClient` also applies the configured context-redaction policy (e.g., removing calibration diagnostics). These are source prompt scaffolds, not a byte-for-byte reconstruction of any historical provider request.
