"""Goal 2 controlled order experiments, separate from the frozen Goal 1 entry.

Only existing mathematical operations are used. Before S the current original
record is deliberately unsplit; computing a common-reference diagnostic never
changes that experimental input. The caller owns registered scope and versions.
"""
from __future__ import annotations

from copy import deepcopy
import math
from numbers import Real

from .evaluation import verify_simplification
from .geometry import (denoise_trajectory, douglas_peucker_indices, filter_segments,
                       select_indices, split_trajectory, validate_trajectory)
from .io import object_hash


ORDERS = ("S-D-P", "S-P-D", "D-S-P", "D-P-S", "P-S-D", "P-D-S")
REFERENCE_PARAMETERS = {"dt": 30, "distance": 400, "min_points": 5,
                        "min_length": 65, "direction": 35, "dp": 5}
PARAMETER_NAMES = set(REFERENCE_PARAMETERS)
DIRECTION_METHOD = "single_pass_simultaneous_keep_undefined"
SCHEMA_VERSION = "G2_PROCESSING_V1"


def validate_parameters(parameters):
    if not isinstance(parameters, dict) or set(parameters) != PARAMETER_NAMES:
        raise ValueError("G2_REQUIRES_EXACTLY_SIX_PARAMETERS")
    for name, value in parameters.items():
        if (isinstance(value, bool) or not isinstance(value, Real)
                or not math.isfinite(value) or value < 0):
            raise ValueError("INVALID_G2_PARAMETER:" + name)
    if type(parameters["min_points"]) is not int or parameters["direction"] > 180:
        raise ValueError("INVALID_G2_PARAMETER_TYPE_OR_RANGE")


def _selection(record, indices, segment_id):
    selected = select_indices(record, indices, time_reliable=True)
    selected["segment_id"] = segment_id
    return selected


def _terminal_rows(record, indices, action, reasons, stage_position):
    chosen = _selection(record, indices, record["segment_id"])
    return [{"record_id": record["record_id"], "original_index": index,
             "timestamp": time, "xy": deepcopy(xy), "action": action,
             "reasons": list(reasons), "stage_position": stage_position,
             "segment_id": record["segment_id"], "parent_hash": object_hash(record)}
            for index, time, xy in zip(chosen["indices"], chosen["timestamps"], chosen["xy"])]


def run_record(record, parameters, order="S-D-P", *, contract_hash, provenance=None):
    """Run all three registered stages and retain an auditable complete trace.

`parameters` has exactly dt/distance/min_points/min_length/direction/dp. The
provided trajectory is already in the frozen conditional work plane. This
function does not choose candidates, read model output, or modify the contract.
    """
    validate_trajectory(record)
    validate_parameters(parameters)
    if order not in ORDERS:
        raise ValueError("UNREGISTERED_G2_ORDER")
    if (not isinstance(contract_hash, str) or len(contract_hash) != 64
            or any(c not in "0123456789abcdef" for c in contract_hash)):
        raise ValueError("G2_CONTRACT_HASH_REQUIRED")
    if any(t is None for t in record["timestamps"]):
        raise ValueError("MISSING_TIMESTAMP: registered G2 temporal processing is blocked")
    source = deepcopy(record)
    current = ([_selection(record, record["indices"], "record:" + record["record_id"])]
               if record["indices"] else [])
    stages, ledger = [], []
    for stage_position, stage_name in enumerate(order.split("-"), 1):
        inputs, outputs, operations = deepcopy(current), [], []
        for segment in inputs:
            parent_hash = object_hash(segment)
            if stage_name == "S":
                split = split_trajectory(segment, parameters["dt"], parameters["distance"],
                                         time_reliable=True)
                for i, part in enumerate(split["segments"]):
                    part["segment_id"] = segment["segment_id"] + "/S" + str(i)
                filtered = filter_segments(split["segments"], parameters["min_points"],
                                           parameters["min_length"], time_reliable=True)
                all_parts = sorted(filtered["kept"] + filtered["dropped"],
                                   key=lambda part: part["segment_index"])
                operations.append({"input_segment_id": segment["segment_id"],
                                   "parent_hash": parent_hash, "boundaries": split["boundaries"],
                                   "segments": deepcopy(all_parts)})
                outputs.extend(filtered["kept"])
                for part in filtered["dropped"]:
                    ledger.extend(_terminal_rows(part, part["indices"], "filtered",
                                                 part["filter_reasons"], stage_position))
            elif stage_name == "D":
                denoised = denoise_trajectory(segment, parameters["direction"],
                                             method=DIRECTION_METHOD, time_reliable=True)
                selected = denoised["record"]
                selected["segment_id"] = segment["segment_id"]
                outputs.append(selected)
                operations.append({"input_segment_id": segment["segment_id"],
                                   "parent_hash": parent_hash, "method": DIRECTION_METHOD,
                                   "passes": 1, "decisions": denoised["decisions"],
                                   "deleted_indices": denoised["deleted_indices"]})
                ledger.extend(_terminal_rows(segment, denoised["deleted_indices"], "denoised",
                                             ["DIRECTION_RULE"], stage_position))
            else:
                kept = douglas_peucker_indices(segment["xy"], parameters["dp"], segment["indices"])
                selected = _selection(segment, kept, segment["segment_id"])
                outputs.append(selected)
                review = verify_simplification(segment, selected, parameters["dp"])
                if review["status"] != "VERIFIED":
                    raise ValueError("G2_DP_RUNTIME_INVARIANT_FAILED:" + object_hash(review))
                operations.append({"input_segment_id": segment["segment_id"],
                                   "parent_hash": parent_hash, "tolerance": parameters["dp"],
                                   "input_points": len(segment["indices"]),
                                   "output_points": len(selected["indices"]),
                                   "dp_reference_hash": parent_hash,
                                   "dp_output_hash": object_hash(selected),
                                   "runtime_dp_check": review})
                ledger.extend(_terminal_rows(segment, [i for i in segment["indices"] if i not in kept],
                                             "simplified", ["DP_WITHIN_TOLERANCE"], stage_position))
        stages.append({"name": stage_name, "position": stage_position,
                       "input": inputs, "output": deepcopy(outputs), "operations": operations})
        current = outputs
    for segment in current:
        ledger.extend(_terminal_rows(segment, segment["indices"], "retained", ["FINAL_OUTPUT"], 4))
    ledger.sort(key=lambda row: row["original_index"])
    if [row["original_index"] for row in ledger] != record["indices"]:
        raise ValueError("G2_POINT_CONSERVATION_FAILED")
    source_kind = (provenance or {}).get("source_kind")
    classification = (source_kind if source_kind in {"SYNTHETIC_COUNTEREXAMPLE", "ENGINEERING_TEST"}
                      else "CURRENT_RUN_CONDITIONAL_ANALYSIS")
    result = {"schema_version": SCHEMA_VERSION, "status": "EXECUTED",
              "classification": classification,
              "record_id": record["record_id"], "source_record": source,
              "source_record_hash": object_hash(source), "parameters": deepcopy(parameters),
              "order": order, "contract_hash": contract_hash,
              "provenance": deepcopy(provenance or {}), "stages": stages,
              "final_segments": deepcopy(current), "point_actions": ledger,
              "terminal_status": ("EMPTY_INPUT" if not record["indices"] else
                                  "ALL_FILTERED" if all(row["action"] == "filtered" for row in ledger) else
                                  "NO_OUTPUT_AFTER_STAGE_FILTERING" if not current else "PROCESSED"),
              "source_crs": "UNVERIFIED", "working_unit": "conditional_working_metre",
              "modified_values": 0}
    from .g2_metrics import record_metrics
    result["metrics"] = record_metrics(source, result)
    return result


def run_batch(records, parameters, order="S-D-P", *, contract_hash, provenance=None):
    """Complete explicit record scope; duplicate input IDs are never accepted."""
    if not isinstance(records, list):
        raise ValueError("COMPLETE_RECORD_LIST_REQUIRED")
    ids = [record.get("record_id") for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("DUPLICATE_INPUT_RECORD")
    results = [run_record(record, parameters, order, contract_hash=contract_hash,
                          provenance=provenance) for record in records]
    from .g2_metrics import summarize
    return {"schema_version": SCHEMA_VERSION, "status": "EXECUTED",
            "parameters": deepcopy(parameters), "order": order, "contract_hash": contract_hash,
            "provenance": deepcopy(provenance or {}), "input_hash": object_hash(records),
            "record_scope": ids, "records": results, "summary": summarize(results)}
