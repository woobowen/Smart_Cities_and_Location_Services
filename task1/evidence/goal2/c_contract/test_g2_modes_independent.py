"""Independent C boundary tests; ALL provider doubles are ENGINEERING_TEST.

No real model is called. Disposable outputs never enter production run manifests.
The processing and post-lock review functions are real deterministic production
functions operating on explicitly synthetic coordinates.
"""
from copy import deepcopy
from pathlib import Path
import json
import tempfile

import pytest

from task1.workflow import g2_modes as modes
from task1.workflow.g2_memory import FrozenMemory, feature_vector, consumption
from task1.workflow.g2_selection import REFERENCE, compare, select_record, config_id, prediction_result
from task1.workflow.g2_pipeline import run_record
from task1.workflow.io import ROOT, object_hash, write_json, digest


EVIDENCE = ROOT / "task1/evidence/goal2/c_contract"


@pytest.fixture
def work():
    with tempfile.TemporaryDirectory(prefix="engineering_mode_test_", dir=EVIDENCE) as path:
        yield Path(path)


def card(rid):
    return {"record_id": rid, "n_points": 12, "span_work_m": 110.0,
            "duration_seconds": 110, "path_length_work_m": 110.0,
            "zero_dt_edges": 0, "negative_dt_edges": 0, "dt_over_30_edges": 0,
            "distance_over_400_edges": 0, "raw_break_edges": 0,
            "adjacent_duplicate_edges": 0, "direction_unavailable_edges": 0,
            "median_positive_dt": 10, "stratum": "ENGINEERING_TEST",
            "record_content_sha256": object_hash({"fixture": rid})}


class RunDouble:
    """Run I/O boundary fixture, never claims a raw-data experiment."""
    def __init__(self, directory, count=1):
        self.directory = directory
        self.partition = "DEVELOPMENT"
        self.ids = ["ENGINEERING-" + str(i) for i in range(count)]
        self.split = {"raw_sha256": "ENGINEERING_TEST_NO_REAL_RAW", "llm_subsets": {self.partition: self.ids}}
        self.tree_hash = "ENGINEERING_TEST_TREE"
        self.contract_hash = object_hash({"purpose": "ENGINEERING_TEST"})
        self.records = {rid: {"record_id": rid, "indices": list(range(12)),
                             "timestamps": [10 * i for i in range(12)],
                             "xy": [[10 * i, 0] for i in range(12)]} for rid in self.ids}
        self.manifest = {"experiment_model_dispatches": 0, "candidate_evaluations": 0, "deterministic_tool_calls": 0}

    def assert_epoch(self):
        pass

    def provenance(self, ids):
        return {"source_kind": "ENGINEERING_TEST", "partition": self.partition,
                "scope_sha256": object_hash(ids), "code_tree_hash": self.tree_hash}

    def save(self):
        pass


def proposal(parameters=None, candidate_id="fixture-proposal"):
    return {"candidate_id": candidate_id, "parameters": deepcopy(parameters or REFERENCE),
            "metric_id": "n_final", "predicted_sign": "not_predicted",
            "reason": "ENGINEERING_TEST scripted action, not a model response"}


class ProviderDouble:
    provenance = "ENGINEERING_TEST"

    def __init__(self, produce=None, failures=()):
        self.calls = []
        self.produce = produce
        self.failures = list(failures)

    def call(self, prompt, directory, *, request_id, purpose):
        self.calls.append(prompt)
        directory.mkdir(parents=True)
        index = len(self.calls) - 1
        failure = self.failures[index] if index < len(self.failures) else None
        receipt = {"request_id": request_id, "purpose": "ENGINEERING_TEST_ONLY",
                   "classification": "SCRIPTED_FIXTURE_NOT_LIVE", "usage": "unavailable",
                   "completed_turns": 0 if failure else 1,
                   "status": "FAILED" if failure else "VERIFIED_STRUCTURE_ONLY"}
        if failure:
            receipt["error"] = failure
        write_json(directory / "receipt.json", receipt)
        (directory / "visible_events.jsonl").write_text("")
        if failure:
            raise modes.ProviderError(failure)
        return self.produce(prompt) if self.produce else {"records": []}, receipt


def scripted(rows_parameters=None, stop=False):
    def produce(prompt):
        context = json.loads(prompt.split("\n")[-1])
        return {"records": [{"record_id": row["card"]["record_id"],
                             "proposals": [proposal(rows_parameters)], "stop": stop,
                             "memory_ids_used": []} for row in context["records"]]}
    return produce


@pytest.mark.parametrize("fault", ["INVALID_STRUCTURED_RESPONSE", "MISSING_OR_AMBIGUOUS_FINAL_EVENT"])
def test_semantic_response_failure_is_not_given_hidden_revision(work, fault):
    provider = ProviderDouble(failures=[fault])
    response, receipts = modes.dispatch(provider, "fixture", work / "call", "fixture", "ENGINEERING_TEST")
    assert response is None
    assert len(provider.calls) == len(receipts) == 1


@pytest.mark.parametrize("fault", ["authentication failed", "billing required", "401 Unauthorized", "permission denied",
                                   "UNEXPECTED_TOOL", "INVALID_JSONL", "UNEXPECTED_VISIBLE_EVENT", "unknown permanent fault"])
def test_auth_tool_protocol_and_unknown_failure_no_retry(work, fault):
    provider = ProviderDouble(failures=[fault])
    with pytest.raises(modes.ProviderError):
        modes.dispatch(provider, "fixture", work / "call", "fixture", "ENGINEERING_TEST")
    assert len(provider.calls) == 1


def test_transient_retry_budget_and_retry_after_are_observed(work, monkeypatch):
    delays = []
    monkeypatch.setattr(modes.time, "sleep", delays.append)
    provider = ProviderDouble(failures=["429 rate_limit Retry-After: 7", "503 temporarily unavailable"])
    response, receipts = modes.dispatch(provider, "fixture", work / "call", "fixture", "ENGINEERING_TEST")
    assert response == {"records": []} and len(receipts) == len(provider.calls) == 3
    assert delays == [7, 4]


def test_transient_failure_stops_after_two_retries(work, monkeypatch):
    delays = []
    monkeypatch.setattr(modes.time, "sleep", delays.append)
    provider = ProviderDouble(failures=["connection reset"] * 4)
    with pytest.raises(modes.ProviderError, match="AFTER_TWO_RETRIES"):
        modes.dispatch(provider, "fixture", work / "call", "fixture", "ENGINEERING_TEST")
    assert len(provider.calls) == 3 and delays == [2, 4]


def test_long_retry_after_saves_failure_without_blocking_sleep(work, monkeypatch):
    delays = []
    monkeypatch.setattr(modes.time, "sleep", delays.append)
    provider = ProviderDouble(failures=["429 rate limit Retry-After: 120"])
    with pytest.raises(modes.ProviderError, match="LATER_RESUME"):
        modes.dispatch(provider, "fixture", work / "call", "fixture", "ENGINEERING_TEST")
    assert len(provider.calls) == 1 and not delays


def test_numeric_substrings_in_request_identity_do_not_become_auth_failures(work, monkeypatch):
    delays = []
    monkeypatch.setattr(modes.time, "sleep", delays.append)
    provider = ProviderDouble(failures=["timeout"])
    result, receipts = modes.dispatch(provider, "fixture", work / "call", "hash401403fixture", "ENGINEERING_TEST")
    assert result == {"records": []} and len(receipts) == 2 and delays == [2]


def test_interrupt_is_preserved_without_retry_or_false_auth_classification(work):
    provider = ProviderDouble(failures=["KeyboardInterrupt"])
    with pytest.raises(modes.ProviderError, match="INTERRUPTED") as caught:
        modes.dispatch(provider, "fixture", work / "call", "hash401403fixture", "ENGINEERING_TEST")
    assert "AUTH" not in str(caught.value) and len(provider.calls) == 1


def test_nonerror_model_payload_does_not_override_parser_rejection(work):
    class ErrorPayloadProvider(ProviderDouble):
        def call(self, prompt, directory, *, request_id, purpose):
            try:
                return super().call(prompt, directory, request_id=request_id, purpose=purpose)
            except modes.ProviderError:
                (directory / "visible_events.jsonl").write_text(json.dumps({"type": "item.completed", "item": {
                    "type": "agent_message", "text": "ENGINEERING_TEST arbitrary answer text: authentication billing 401 403"}}) + "\n")
                raise
    provider = ErrorPayloadProvider(failures=["INVALID_STRUCTURED_RESPONSE"])
    result, receipts = modes.dispatch(provider, "fixture", work / "call", "fixture", "ENGINEERING_TEST")
    assert result is None and len(receipts) == len(provider.calls) == 1


def test_hash_and_usage_digits_do_not_make_an_unknown_failure_retryable(work, monkeypatch):
    class IrrelevantDigitsProvider(ProviderDouble):
        def call(self, prompt, directory, *, request_id, purpose):
            try:
                return super().call(prompt, directory, request_id=request_id, purpose=purpose)
            except modes.ProviderError:
                path = directory / "receipt.json"
                receipt = json.loads(path.read_text())
                receipt.update(usage={"input_tokens": 429, "output_tokens": 503},
                               source_sha256="a401403429502503504b")
                write_json(path, receipt)
                raise
    delays = []
    monkeypatch.setattr(modes.time, "sleep", delays.append)
    provider = IrrelevantDigitsProvider(failures=["unknown permanent fault"])
    with pytest.raises(modes.ProviderError, match="UNCLASSIFIED_PROVIDER_FAILURE_NO_RETRY"):
        modes.dispatch(provider, "fixture", work / "call", "a401403429502503504b", "ENGINEERING_TEST")
    assert len(provider.calls) == 1 and delays == []


def test_actual_archived_keyboard_interrupt_receipt_is_classified_without_new_call(work):
    archived = ROOT / ("task1/evidence/goal2/runs/g2-development-modes-01/modes/"
                       "DEVELOPMENT-llm+memory+search-e1-b0/round3_call/attempt01")
    before = {p.name: digest(p) for p in archived.iterdir() if p.is_file()}
    actual_receipt = json.loads((archived / "receipt.json").read_text())
    assert actual_receipt["error"] == "KeyboardInterrupt:"
    class ArchivedReceiptReader:
        calls = 0
        provenance = "ENGINEERING_TEST_ARCHIVED_DIAGNOSTIC_NO_MODEL"
        def call(self, prompt, directory, **kwargs):
            self.calls += 1
            directory.mkdir(parents=True)
            (directory / "receipt.json").write_bytes((archived / "receipt.json").read_bytes())
            (directory / "visible_events.jsonl").write_bytes((archived / "visible_events.jsonl").read_bytes())
            raise modes.ProviderError("archived diagnostic fixture")
    reader = ArchivedReceiptReader()
    with pytest.raises(modes.ProviderError, match="INTERRUPTED_CHECKPOINT"):
        modes.dispatch(reader, "ENGINEERING_TEST_NO_REQUEST", work / "call", "fixture", "ENGINEERING_TEST")
    assert reader.calls == 1
    assert before == {p.name: digest(p) for p in archived.iterdir() if p.is_file()}


def test_search_only_never_instantiates_a_model_or_reads_memory(work):
    run = RunDouble(work)
    def forbidden_model():
        pytest.fail("search-only instantiated an experiment model")
    class ForbiddenMemory:
        def __getattribute__(self, key):
            pytest.fail("search-only touched memory: " + key)
    summary = modes.run_batch_episode(run, "search-only", 0, run.ids, {rid: card(rid) for rid in run.ids},
                                     provider_factory=forbidden_model, memory=ForbiddenMemory())
    assert summary["resources"]["experiment_model_dispatches"] == 0
    assert summary["resources"]["candidate_evaluations"] == 20
    assert summary["records"][0]["candidate_ids"][0] == config_id(REFERENCE)
    assert summary["records"][0]["resources"]["unique_candidate_evaluations"] == 20


@pytest.mark.parametrize("count", [0, 9])
def test_batch_scope_limit_is_enforced_before_model(work, count):
    run = RunDouble(work, count)
    with pytest.raises(ValueError, match="INVALID_BATCH"):
        modes.run_batch_episode(run, "llm-only", 0, run.ids, {}, provider_factory=lambda: pytest.fail("model started"))


def test_llm_only_preserves_illegal_original_without_clamping_or_revision(work):
    run = RunDouble(work)
    invalid = {**REFERENCE, "dp": 999}
    provider = ProviderDouble(scripted(invalid))
    summary = modes.run_batch_episode(run, "llm-only", 0, run.ids, {rid: card(rid) for rid in run.ids},
                                     provider_factory=lambda: provider)
    record = summary["records"][0]
    assert len(provider.calls) == 1
    context = json.loads(provider.calls[0].split("\n")[-1])
    assert context["evaluations_already_consumed"] == {run.ids[0]: 0}
    assert "own_candidate_feedback" not in context["records"][0]
    assert "demonstration_memory" not in context["records"][0]
    assert record["proposal_records"][0]["original"]["parameters"]["dp"] == 999
    assert record["proposal_records"][0]["legal"] is False
    assert record["proposal_records"][0]["executed"] is False
    assert record["fallback"] is True and record["selected_parameters"] == REFERENCE
    assert record["resources"]["unique_candidate_evaluations"] == 1


def test_llm_only_unparseable_batch_records_rejection_and_single_reference(work):
    run = RunDouble(work, 2)
    provider = ProviderDouble(failures=["INVALID_STRUCTURED_RESPONSE"])
    summary = modes.run_batch_episode(run, "llm-only", 0, run.ids, {rid: card(rid) for rid in run.ids},
                                     provider_factory=lambda: provider)
    assert len(provider.calls) == 1
    assert all(r["fallback"] and r["proposal_records"][0]["reason"] == "INVALID_RECORD_ACTION_STRUCTURE" for r in summary["records"])
    assert summary["resources"]["candidate_evaluations"] == 2


def test_scripted_test_provider_is_not_labelled_live(work):
    run = RunDouble(work)
    provider = ProviderDouble(scripted())
    result = modes.run_batch_episode(run, "llm-only", 0, run.ids, {rid: card(rid) for rid in run.ids},
                                    provider_factory=lambda: provider)
    assert result["classification"] == "ENGINEERING_TEST_SCRIPTED_PROVIDER_NOT_LIVE"


def test_formal_run_rejects_scripted_provider_before_any_call(work):
    run = RunDouble(work)
    run.manifest["classification"] = "CURRENT_RUN_CONDITIONAL_ANALYSIS"
    provider = ProviderDouble(scripted())
    with pytest.raises(ValueError, match="REGISTERED_LIVE_PROVIDER"):
        modes.run_batch_episode(run, "llm-only", 0, run.ids, {rid: card(rid) for rid in run.ids},
                                provider_factory=lambda: provider)
    assert len(provider.calls) == 0


def test_search_feedback_is_sequential_own_record_only_and_ephemeral(work):
    run = RunDouble(work, 2)
    cards = {rid: card(rid) for rid in run.ids}
    provider = ProviderDouble(scripted({**REFERENCE, "dp": 0}))
    for episode in (0, 1):
        before = len(provider.calls)
        summary = modes.run_batch_episode(run, "llm+search", episode, run.ids, cards, provider_factory=lambda: provider)
        assert len(provider.calls) - before == 3
        contexts = [json.loads(p.split("\n")[-1]) for p in provider.calls[before:]]
        assert contexts[0]["evaluations_already_consumed"] == {rid: 0 for rid in run.ids}
        assert contexts[1]["evaluations_already_consumed"] == {rid: 8 for rid in run.ids}
        assert contexts[2]["evaluations_already_consumed"] == {rid: 14 for rid in run.ids}
        assert all("own_candidate_feedback" not in x for x in contexts[0]["records"])
        for context in contexts[1:]:
            assert all(len(x["own_candidate_feedback"]) == (8 if context["decision_round"] == 2 else 14) for x in context["records"])
            assert "post_lock_review" not in json.dumps(context)
        for row in summary["records"]:
            for rd in row["rounds"]:
                actual_context = contexts[rd["round"] - 1]
                assert rd["context_hash"] == object_hash(actual_context)
        assert summary["resources"]["candidate_evaluations"] == 40
        assert all(r["resources"]["unique_candidate_evaluations"] == 20 for r in summary["records"])
        assert summary["working_memory_reset_at_episode_start"] is True
        assert summary["working_memory_persisted_for_next_episode"] is False


def memory_fixture(work, count=4, edits=None):
    demo_ids = ["DEMO-" + str(i) for i in range(count)]
    split = {"raw_sha256": "raw-fixture", "splits": {"DEMO_MEMORY": demo_ids}}
    chash = "contract-fixture"
    entries = [{"memory_id": "MEMORY-" + rid, "record_id": rid, "partition": "DEMO_MEMORY",
                "record_content_sha256": card(rid)["record_content_sha256"], "stratum": "ENGINEERING_TEST",
                "features": feature_vector(card(rid)), "contract_sha256": chash, "raw_sha256": "raw-fixture",
                "engineering_status": "VERIFIED", "selected_parameters": deepcopy(REFERENCE),
                "selected_metrics": {}, "research_status": "NO_DEMONSTRATED_GAIN"} for rid in demo_ids]
    if edits:
        edits(entries)
    snapshot = {"contract_sha256": chash, "raw_sha256": split["raw_sha256"], "split_sha256": object_hash(split),
                "entries": entries, "feature_scales": [{"min": 0, "max": 1}] * 6, "procedural_memory": {}}
    path = work / "memory.json"
    write_json(path, snapshot)
    return FrozenMemory(path, digest(path), chash, split)


def test_memory_public_snapshot_mutation_cannot_affect_retrieval(work):
    memory = memory_fixture(work)
    memory.snapshot["entries"][0]["selected_parameters"]["dp"] = 999
    result = memory.retrieve(card("QUERY"))
    assert all(e["selected_parameters"]["dp"] == 5 for e in result["delivered"])
    assert memory.verify_unchanged() == memory.expected_hash


def test_memory_private_in_process_tamper_detected(work):
    memory = memory_fixture(work)
    memory._snapshot["entries"][0]["selected_parameters"]["dp"] = 999
    with pytest.raises(ValueError, match="CONTENT_CHANGED"):
        memory.retrieve(card("QUERY"))


def test_memory_disk_write_detected_and_write_api_denied(work):
    memory = memory_fixture(work)
    with pytest.raises(PermissionError, match="READ_ONLY"):
        memory.write({"fake": "evaluation example"})
    memory.path.write_text("{}")
    with pytest.raises(ValueError, match="MEMORY_CHANGED"):
        memory.retrieve(card("QUERY"))


@pytest.mark.parametrize("field,value,reason", [
    ("record_id", "QUERY", "SAME_PARENT_RECORD_OR_EXACT_DUPLICATE"),
    ("record_content_sha256", card("QUERY")["record_content_sha256"], "SAME_PARENT_RECORD_OR_EXACT_DUPLICATE"),
    ("partition", "G2_EVAL", "NOT_DEMO_MEMORY"),
    ("contract_sha256", "wrong", "WRONG_DATA_OR_CONTRACT"),
    ("raw_sha256", "wrong", "WRONG_DATA_OR_CONTRACT"),
    ("engineering_status", "PENDING", "NOT_VERIFIED"),
    ("stratum", "different", "STRATUM_NOT_APPLICABLE"),
    ("features", None, "DIAGNOSTIC_FEATURE_UNAVAILABLE"),
])
def test_memory_ineligible_cases_are_not_delivered(work, field, value, reason):
    memory = memory_fixture(work, count=1, edits=lambda entries: entries[0].update({field: value}))
    result = memory.retrieve(card("QUERY"))
    assert result["delivered"] == [] and reason in result["filtered"][0]["reasons"]
    assert result["empty_reason"] == "NO_APPLICABLE_VERIFIED_DEMONSTRATION"


def test_memory_frozen_maximum_three_cannot_be_expanded(work):
    memory = memory_fixture(work)
    try:
        result = memory.retrieve(card("QUERY"), limit=4)
    except ValueError:
        return
    assert len(result["delivered"]) <= 3


def test_memory_citation_and_matching_parameters_are_distinct_from_gain(work):
    memory = memory_fixture(work)
    retrieval = memory.retrieve(card("QUERY"))
    response = {"proposals": [proposal()], "memory_ids_used": [retrieval["delivered"][0]["memory_id"], "NONEXISTENT"]}
    result = consumption(retrieval, response)
    assert len(result["model_cited_valid"]) == len(result["action_consistent"]) == 1
    assert result["model_cited_invalid"] == ["NONEXISTENT"] and result["causal_benefit_proven"] is False


def actual_result(parameters=None):
    raw = {"record_id": "synthetic-selection", "indices": list(range(12)), "timestamps": list(range(12)),
           "xy": [[10 * i, 0] for i in range(12)]}
    return run_record(raw, parameters or REFERENCE, "S-D-P", contract_hash=object_hash({"purpose": "ENGINEERING_TEST"}),
                      provenance={"source_kind": "ENGINEERING_TEST"})


def test_empty_output_cannot_win_by_zero_error_or_compression():
    baseline = actual_result()
    empty = actual_result({**REFERENCE, "min_length": 130})
    assessed = compare(empty, baseline)
    assert not assessed["feasible"] and not assessed["strict_gain"]
    assert empty["metrics"]["common_max_error"] is None


def test_equal_coverage_count_with_changed_point_identities_is_not_protected():
    baseline = actual_result()
    candidate = deepcopy(baseline)
    candidate["parameters"]["direction"] = 25
    baseline["metrics"]["common_point_errors"][0]["error"] = None
    candidate["metrics"]["common_point_errors"][1]["error"] = None
    assessed = compare(candidate, baseline)
    assert assessed["baseline_covered_count"] == assessed["candidate_covered_count"]
    assert "COMMON_COVERED_IDENTITIES_LOST" in assessed["protection_failures"]


def test_changed_upstream_cannot_claim_dp_error_as_common_quality_gain():
    baseline = actual_result()
    candidate = actual_result({**REFERENCE, "direction": 25})
    candidate["metrics"]["common_point_errors"][5]["error"] = 12
    candidate["metrics"]["dp_max_error"] = 0
    assessed = compare(candidate, baseline)
    assert not assessed["dp_only_comparison"] and not assessed["strict_gain"]
    assert "COMMON_GEOMETRIC_PROTECTION_DEGRADED" in assessed["protection_failures"]


def test_full_frontier_is_retained_even_without_strict_gain():
    baseline = actual_result()
    duplicate = actual_result({**REFERENCE, "dp": 10})
    refid, dupeid = config_id(REFERENCE), config_id(duplicate["parameters"])
    selected, selection = select_record({refid: baseline, dupeid: duplicate}, refid)
    assert selected == refid
    assert "frontier" in selection
    assert set(selection["frontier"]) == {refid, dupeid}


def test_prediction_denominator_excludes_cross_reference_and_unavailable():
    baseline = actual_result()
    changed = actual_result({**REFERENCE, "direction": 25})
    p = {"metric_id": "dp_saving", "predicted_sign": "increase"}
    assert prediction_result(p, changed, baseline)["status"] == "DIFFERENT_DP_REFERENCE"
    assert prediction_result({**p, "predicted_sign": "not_predicted"}, changed, baseline)["status"] == "NOT_PREDICTED"
    unchanged = prediction_result({"metric_id": "n_final", "predicted_sign": "unchanged"}, baseline, baseline)
    assert unchanged["status"] == "NEAR_ZERO_OR_UNCHANGED" and not unchanged["evaluable"]
