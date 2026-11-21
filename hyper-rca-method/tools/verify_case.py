#!/usr/bin/env python3
"""Replay the released BT case using saved judgments; no LLM or telemetry calls."""
from collections import defaultdict
import json
import math
from pathlib import Path


def verify(case_dir: Path) -> dict:
    data = json.loads((case_dir / "result.json").read_text())
    audit = json.loads((case_dir / "ranking_audit.json").read_text())
    truth = json.loads((case_dir / "ground_truth.json").read_text())
    ranking = data["metadata"]["rank_agent"]
    ids = ranking["coarse_order"]
    assert len(ids) == len(set(ids)) == 18
    grouped = defaultdict(list)
    for row in ranking["pairwise_comparisons"]:
        assert row["left_id"] in ids and row["right_id"] in ids
        assert row["winner_id"] in (row["left_id"], row["right_id"], "tie")
        grouped[tuple(sorted((row["left_id"], row["right_id"])))].append(row)
    effective = []
    for rows in grouped.values():
        valid = [row for row in rows if row.get("valid_judgment", True)]
        assert {r["repetition"] for r in valid} == {1, 2}
        assert {r["order_reversed"] for r in valid} == {False, True}
        effective.extend(valid)
    assert len(grouped) == 68 and len(effective) == 136
    parameters = audit["bt_replay_parameters"]
    strengths = dict.fromkeys(ids, 0.0)
    for _ in range(parameters["iterations"]):
        gradient = {c: -2 * parameters["regularization"] * strengths[c] for c in ids}
        for row in effective:
            left, right = row["left_id"], row["right_id"]
            difference = min(30, max(-30, strengths[left] - strengths[right]))
            probability = 1 / (1 + math.exp(-difference))
            outcome = 0.5 if row["winner_id"] == "tie" else float(row["winner_id"] == left)
            gradient[left] += outcome - probability
            gradient[right] -= outcome - probability
        for c in ids:
            strengths[c] += parameters["learning_rate"] * gradient[c] / len(effective)
        center = sum(strengths.values()) / len(ids)
        strengths = {c: value - center for c, value in strengths.items()}
    maximum = max(strengths.values())
    weights = {c: math.exp(value - maximum) for c, value in strengths.items()}
    total = sum(weights.values())
    scores = {c: value / total for c, value in weights.items()}
    order = sorted(ids, key=lambda c: -scores[c])
    saved = ranking["global_ranking"]
    assert order == [row["hypothesis_id"] for row in saved]
    assert all(abs(scores[row["hypothesis_id"]] - row["score"]) <= 0.00000051 for row in saved)
    assert ids[0] != order[0]
    winner = saved[0]
    assert winner["pod"] == truth["metadata"]["injection_info"]["pod"]
    assert winner["fault_type"] == truth["fault_type_catalog_id"]
    assert data["metadata"]["refine_agent"]["round_count"] == 0
    direct_pair = audit["decisive_pairwise_judgments"]
    assert len(direct_pair) == 2 and all(row["winner_id"] == order[0] for row in direct_pair)
    assert ranking["guarded_bt_outcome"] == "challenger_accepted"
    guards = ranking["guarded_bt_judgments"]
    assert len(guards) == 2 and {g["order_reversed"] for g in guards} == {False, True}
    assert all(g["valid_judgment"] and not g["unresolved_evidence_gap"] for g in guards)
    assert all(g[field] == order[0] for g in guards for field in
               ("entity_fit_winner_id", "fault_type_fit_winner_id", "overall_winner_id"))
    calls = data["metadata"]["llm"]
    assert calls["call_count"] == len(calls["calls"]) == 24
    return dict(verified=True, coarse_top1=ids[0], final_top1=order[0],
                fitted_winner_score=scores[order[0]], effective_pairs=len(grouped),
                judgments=len(effective), refinement_rounds=0,
                note="BT scores are ranking strengths, not calibrated causal probabilities.")


if __name__ == "__main__":
    print(json.dumps(verify(Path(__file__).resolve().parents[1] / "case-study"), indent=2))
