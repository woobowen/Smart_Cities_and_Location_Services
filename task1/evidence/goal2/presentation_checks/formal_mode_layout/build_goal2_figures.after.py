"""P2 scientific figures from hash-verified current Goal 2 experiment artifacts.

No synthetic substitute is accepted for a missing real experiment. Every output
has SVG/PDF, 300-dpi PNG, and a 200-dpi PDF render for actual visual inspection.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch
from matplotlib.path import Path as DrawingPath
from matplotlib.ticker import MaxNLocator
import numpy as np
from PIL import Image

from task1.workflow.g2_experiments import read_gzip
from task1.workflow.g2_selection import REFERENCE
from task1.workflow.io import ROOT, digest, object_hash, read_json, write_json, now


EV = ROOT / "task1/evidence/goal2"
MODES = ("llm-only", "search-only", "llm+search", "llm+memory+search")
MODE_LABELS = ("LLM only", "Search only", "LLM + search", "LLM + memory\n+ search")
PARAM_LABELS = {"dt": "Time threshold (s)", "distance": "Distance threshold (working m)",
                "min_points": "Minimum segment points", "min_length": "Minimum segment length (working m)",
                "direction": "Direction threshold (degrees)", "dp": "DP tolerance (working m)"}


def palette():
    path = ROOT / "templates/latex/common/p2_cloud_sorbet_colors.tex"
    return {name: "#" + value for name, value in re.findall(r"\\definecolor\{([^}]+)\}\{HTML\}\{([A-Fa-f0-9]+)\}", path.read_text())}


def theme():
    p = palette()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 12,
                         "axes.labelsize": 10, "legend.fontsize": 9, "xtick.labelsize": 9, "ytick.labelsize": 9,
                         "figure.facecolor": p["Paper"], "axes.facecolor": p["Panel"],
                         "text.color": p["Ink"], "axes.labelcolor": p["Ink"], "xtick.color": p["Ink"],
                         "ytick.color": p["Ink"], "axes.edgecolor": p["Muted"], "grid.color": p["Rule"],
                         "axes.spines.top": False, "axes.spines.right": False, "grid.linewidth": .6,
                         "lines.linewidth": 1.7, "lines.markersize": 5, "pdf.fonttype": 42,
                         "svg.fonttype": "none", "savefig.facecolor": p["Paper"]})
    return p


def _path_label(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name


class FigureSet:
    def __init__(self, current_runs_path, output_directory, topic):
        self.output = Path(output_directory)
        self.output.mkdir(parents=True, exist_ok=True)
        self.current_path = Path(current_runs_path)
        self.current = read_json(self.current_path)
        self.p = theme()
        self.sources = {_path_label(self.current_path): digest(self.current_path)}
        self.figures, self.data = [], {}
        self.topic = topic

    def source(self, path):
        path = Path(path)
        self.sources[_path_label(path)] = digest(path)
        return path

    def run(self, key):
        directory = EV / "runs" / self.current[key]
        manifest = read_json(self.source(directory / "manifest.json"))
        if manifest["status"] in ("RUNNING", "STALE", "SUPERSEDED", "FAILED"):
            raise ValueError("INCOMPLETE_OR_STALE_FIGURE_SOURCE:" + key)
        return directory, manifest

    def trace(self, directory, entry):
        path = directory / entry["file"]
        if digest(path) != entry["sha256"] or entry["engineering_status"] != "VERIFIED":
            raise ValueError("UNVERIFIED_OR_CHANGED_PLOT_SOURCE")
        return read_gzip(self.source(path))

    def table(self, directory, manifest, name):
        path = directory / name
        if digest(path) != manifest.get("tables", {}).get(name):
            raise ValueError("UNBOUND_OR_CHANGED_PLOT_TABLE:" + name)
        return read_json(self.source(path))

    def save(self, fig, name, data, description):
        self.data[name] = data
        paths = {}
        for extension in ("svg", "pdf", "png"):
            path = self.output / (name + "." + extension)
            fig.savefig(path, dpi=300 if extension == "png" else None)
            paths[extension] = {"file": path.name, "sha256": digest(path)}
        plt.close(fig)
        render = self.output / "pdf-render-200dpi" / name
        render.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["pdftoppm", "-r", "200", "-singlefile", "-png", str(self.output / (name + ".pdf")), str(render)],
                       check=True, capture_output=True)
        rendered_path = render.with_suffix(".png")
        with Image.open(self.output / (name + ".png")) as image:
            size = list(image.size)
        self.figures.append({"name": name, "description": description, "formats": paths,
                             "png_size_pixels": size, "png_dpi": 300,
                             "pdf_render": {"file": str(rendered_path.relative_to(self.output)),
                                            "dpi": 200, "sha256": digest(rendered_path)},
                             "visual_inspection": "PENDING_ACTUAL_IMAGE_REVIEW"})


def _oat(entries, parameter):
    return sorted([entry for entry in entries if all(entry["parameters"][key] == REFERENCE[key]
                                                    for key in REFERENCE if key != parameter)],
                  key=lambda entry: entry["parameters"][parameter])


def parameters_figures(writer):
    directory, manifest = writer.run("parameter_development")
    entries = writer.table(directory, manifest, "parameter_table.json")
    p = writer.p
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.3), layout="constrained")
    data = {}
    for ax, parameter in zip(axes.flat, ("dt", "distance", "min_points", "min_length")):
        rows = _oat(entries, parameter)
        x = [r["parameters"][parameter] for r in rows]
        retained = [r["summary"]["point_retention"] for r in rows]
        missing = [r["summary"]["no_output_record_fraction"] for r in rows]
        ax.plot(x, retained, "o-", color=p["C1"], label="Retained / raw points")
        ax.plot(x, missing, "s--", color=p["C3"], label="No-output / input records")
        ax.axvline(REFERENCE[parameter], color=p["Muted"], ls=":", lw=1)
        ax.set(xlabel=PARAM_LABELS[parameter], ylabel="Fraction", ylim=(-.03, 1.03), xticks=x)
        ax.grid(axis="y")
        ax.set_title(parameter.replace("_", " ").capitalize(), loc="left")
        data[parameter] = [{"value": r["parameters"][parameter], "config_id": r["config_id"],
                            "retained_fraction": a, "no_output_record_fraction": b,
                            "raw_points": r["summary"]["n_input"], "records": r["summary"]["n_records"]}
                           for r, a, b in zip(rows, retained, missing)]
    axes[0, 0].legend(loc="best")
    fig.suptitle(f"Segmentation and filtering · {len(manifest['input_ids'])} records / {entries[0]['summary']['n_input']:,} raw points", fontsize=14)
    writer.save(fig, "segmentation_filter_response", data, "Four one-factor sweeps; dashed vertical lines mark the reference configuration.")

    fig, axes = plt.subplots(2, 2, figsize=(11, 8), layout="constrained")
    heat_data = []
    for row_number, (x_key, y_key) in enumerate((("dt", "distance"), ("min_points", "min_length"))):
        rows = [entry for entry in entries if all(entry["parameters"][key] == REFERENCE[key]
                                                for key in REFERENCE if key not in (x_key, y_key))]
        xs, ys = sorted({r["parameters"][x_key] for r in rows}), sorted({r["parameters"][y_key] for r in rows})
        for column, (metric, label, color) in enumerate((("point_retention", "Retained / raw points", "C1"),
                                                        ("no_output_record_fraction", "No-output / input records", "C3"))):
            z = np.full((len(ys), len(xs)), np.nan)
            for entry in rows:
                x, y = entry["parameters"][x_key], entry["parameters"][y_key]
                z[ys.index(y), xs.index(x)] = entry["summary"][metric]
            ax = axes[row_number, column]
            # Native flat cells avoid interpolation artifacts in PDF backends.
            image = ax.pcolormesh(np.arange(len(xs) + 1) - .5, np.arange(len(ys) + 1) - .5, z,
                                  vmin=0, vmax=1, shading="flat", antialiased=False,
                                  cmap=LinearSegmentedColormap.from_list(metric, [p["Paper"], p[color]]))
            ax.set(xticks=range(len(xs)), xticklabels=xs, yticks=range(len(ys)), yticklabels=ys,
                   xlabel=PARAM_LABELS[x_key], ylabel=PARAM_LABELS[y_key])
            ax.set_title(label, loc="left")
            for j in range(len(ys)):
                for i in range(len(xs)):
                    ax.text(i, j, f"{z[j, i]:.2f}", ha="center", va="center", fontsize=8)
            fig.colorbar(image, ax=ax, label="Fraction", shrink=.85)
            heat_data.append({"x": x_key, "y": y_key, "x_values": xs, "y_values": ys,
                              "metric": metric, "matrix": z.tolist(), "config_ids": [r["config_id"] for r in rows]})
    fig.suptitle("Two registered 5 × 5 grids · no four-factor Cartesian expansion", fontsize=14)
    writer.save(fig, "segmentation_filter_grids", heat_data, "Same fractions and 0–1 color range in both registered two-factor grids.")

    rows = _oat(entries, "direction")
    baseline_entry = next(entry for entry in entries if entry["parameters"] == REFERENCE)
    baseline = writer.trace(directory, baseline_entry)
    direction_case = None
    for record in sorted(baseline["records"], key=lambda row: row["record_id"]):
        stage = next(stage for stage in record["stages"] if stage["name"] == "D")
        for before, after, operation in zip(stage["input"], stage["output"], stage["operations"]):
            if operation["deleted_indices"]:
                index = operation["deleted_indices"][0]
                position = before["indices"].index(index)
                direction_case = (record["record_id"], index, before, after, position)
                break
        if direction_case:
            break
    selection = {"rule": "first original-index deletion in stable record-ID order from reference DEVELOPMENT",
                 "selected": {"record_id": direction_case[0], "index": direction_case[1]} if direction_case else None}
    write_json(writer.output / "DIRECTION_CASE_SELECTION.json", selection)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), layout="constrained")
    x = [entry["parameters"]["direction"] for entry in rows]
    for ax, metric, label, color in ((axes[0], "n_direction_removed", "Deleted by D (points)", "C3"),
                                     (axes[1], "direction_undefined_points", "Protected undefined / boundary points", "C4")):
        ax.plot(x, [entry["summary"][metric] for entry in rows], "o-", color=p[color])
        ax.set(xlabel=PARAM_LABELS["direction"], ylabel=label, xticks=x, ylim=(0, None))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis="y")
    if direction_case:
        rid, index, before, after, position = direction_case
        window = before["indices"][max(0, position - 2):position + 4]
        local = [point for idx, point in zip(before["indices"], before["xy"]) if idx in window]
        after_local = [point for idx, point in zip(after["indices"], after["xy"]) if window[0] <= idx <= window[-1]]
        axes[2].plot(*np.asarray(local).T, "o--", color=p["Muted"], label="D input")
        if after_local:
            axes[2].plot(*np.asarray(after_local).T, "s-", color=p["C1"], label="After one D pass")
        point = before["xy"][position]
        axes[2].scatter(*point, marker="x", s=80, color=p["C3"], zorder=5)
        axes[2].annotate(str(index), point, xytext=(6, 6), textcoords="offset points")
        axes[2].set_title(f"Record {rid} · deleted index {index}", loc="left")
        axes[2].legend(loc="upper left", fontsize=8)
    else:
        axes[2].text(.5, .5, "No direction deletion in reference scope", ha="center", transform=axes[2].transAxes)
    axes[2].set(xlabel="East (working m)", ylabel="North (working m)")
    axes[2].set_aspect("equal", adjustable="datalim")
    fig.suptitle("Direction threshold: deletion, protected windows, and changed adjacency", fontsize=14)
    writer.save(fig, "direction_threshold_and_neighborhood", {"rows": rows, "case_selection": selection},
                "Undefined-window protection is not a noise truth label; the local edge is recomputed after simultaneous deletion.")

    rows = _oat(entries, "dp")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")
    x = [entry["parameters"]["dp"] for entry in rows]
    axes[0].plot(x, [entry["summary"]["dp_saving"] for entry in rows], "o-", color=p["C1"])
    axes[0].set(xlabel=PARAM_LABELS["dp"], ylabel="1 − P immediate output / P input", ylim=(-.03, 1.03))
    axes[0].grid(axis="y")
    for entry in rows:
        error, saving = entry["summary"]["dp_max_error"], entry["summary"]["dp_saving"]
        if error is not None and saving is not None:
            axes[1].scatter(error, saving, color=p["C1"], s=40)
            axes[1].annotate(str(entry["parameters"]["dp"]), (error, saving), xytext=(5, 5), textcoords="offset points")
    axes[1].axvline(5, color=p["C3"], ls="--", label="Common P budget: 5 working m")
    axes[1].set(xlabel="Actual maximum P interval error (working m)", ylabel="P-stage saving", ylim=(-.03, 1.03))
    axes[1].grid(axis="y")
    axes[1].legend(loc="lower right", fontsize=8)
    fig.suptitle("DP geometric error and compression · identical S/D input", fontsize=14)
    writer.save(fig, "dp_error_compression", rows, "Labels are registered tolerances; P-stage guarantees do not certify cross-method quality.")

    directory, manifest = writer.run("order_development")
    rows = writer.table(directory, manifest, "order_table.json")
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7), layout="constrained")
    labels = [entry["order"] for entry in rows]
    readings = [("common_coverage", "Covered / raw points"), (None, "Records failing common protection"),
                ("raw_break_crossings", "Final edges crossing raw breaks"),
                ("direction_windows_across_raw_breaks", "D windows across raw breaks")]
    for ax, (metric, label) in zip(axes.flat, readings):
        values = [len(entry["safety_failures"]) if metric is None else entry["summary"][metric] for entry in rows]
        colors = [p["C3"] if entry["research_status"] == "REJECTED_BY_CONSTRAINT" else p["C1"] for entry in rows]
        ax.bar(range(len(rows)), values, color=colors, edgecolor=p["Ink"], linewidth=.5)
        ax.set(xticks=range(len(rows)), xticklabels=labels, ylabel=label)
        if metric == "common_coverage":
            ax.set_ylim(0, 1)
        else:
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis="x", rotation=25)
        ax.grid(axis="y")
        for i, value in enumerate(values):
            ax.annotate(f"{value:.3f}" if metric == "common_coverage" else str(value), (i, value),
                        xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8)
        ax.margins(y=.18)
    fig.suptitle(f"Six executed stage orders · {len(manifest['input_ids'])} development records", fontsize=14)
    axes[0, 0].legend(handles=[Patch(facecolor=p["C1"], edgecolor=p["Ink"], label="Passes common protection"),
                               Patch(facecolor=p["C3"], edgecolor=p["Ink"], label="Rejected by common protection")],
                      loc="upper right", fontsize=8)
    writer.save(fig, "order_protection_and_neighborhoods", rows,
                "Rose denotes a constraint-rejected order; geometric execution remains a valid negative experiment.")


def mode_figures(writer):
    directory, manifest = writer.run("mode_evaluation")
    episodes = []
    for entry in manifest["mode_episodes"]:
        path = directory / entry["path"]
        if digest(path) != entry["sha256"]:
            raise ValueError("MODE_EPISODE_HASH_MISMATCH")
        episodes.append(read_json(writer.source(path)))
    records = [row for episode in episodes for row in episode["records"]]
    if set(row["mode"] for row in records) != set(MODES):
        raise ValueError("ALL_FOUR_REAL_MODES_REQUIRED_FOR_FIGURE")
    p = writer.p
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.8), layout="constrained")
    paired_data = []
    for ax, metric, label in zip(axes, ("common_coverage", "common_max_error", "n_final"),
                                 ("Δ raw coverage fraction", "Δ error on baseline-covered points (working m)", "Δ retained point count")):
        for i, mode in enumerate(MODES):
            rows = [row for row in records if row["mode"] == mode]
            grouped, values = defaultdict(list), []
            for row in rows:
                if metric == "common_max_error":
                    a = row["research_assessment"].get("candidate_max_on_baseline_covered")
                    b = row["research_assessment"].get("baseline_common_max")
                else:
                    a, b = row["selected_metrics"].get(metric), row["reference_metrics"].get(metric)
                if a is None or b is None:
                    continue
                delta = a - b
                grouped[row["record_id"]].append(delta)
                values.append(delta)
                paired_data.append({"metric": metric, "mode": mode, "record_id": row["record_id"],
                                    "episode": row["episode"], "delta": delta})
            jitter = np.linspace(-.16, .16, len(values)) if values else []
            ax.scatter(np.asarray(jitter) + i, values, s=13, alpha=.23, color=p["C" + str(i + 1)], marker="o")
            means = [np.mean(v) for _, v in sorted(grouped.items())]
            ax.scatter(np.linspace(-.10, .10, len(means)) + i, means, s=24, facecolors="none", edgecolors=p["Ink"], marker="D")
            n_records = len({row["record_id"] for row in rows})
            ax.annotate(f"{len(grouped)}/{n_records} records\n{len(values)}/{len(rows)} pairs", (i, .97), xycoords=("data", "axes fraction"),
                        ha="center", va="top", fontsize=7)
        ax.axhline(0, color=p["Muted"], ls=":", lw=1)
        ax.set(xticks=range(4), xticklabels=MODE_LABELS, ylabel=label)
        ax.tick_params(axis="x", rotation=23)
        ax.grid(axis="y")
        ax.margins(y=.2)
    fig.suptitle("Four modes: paired differences from each record's reference · 3 episodes", fontsize=14)
    fig.get_layout_engine().set(rect=(0, .075, 1, .925))
    fig.text(.5, .018, "Circles: record-episode pairs · Outlined diamonds: per-record means across episodes · Labels: available / total",
             ha="center", va="bottom", fontsize=9)
    writer.save(fig, "four_mode_paired_results", paired_data,
                "Circles: record-episode pairs; outlined diamonds: per-record episode means. Labels give available / total records and pairs; no quality or significance claim.")

    resources = {}
    for mode in MODES:
        subset = [e for e in episodes if e["mode"] == mode]
        rows = [r for r in records if r["mode"] == mode]
        proposals = [pr for row in rows for pr in row["proposal_records"]]
        resources[mode] = {"model_dispatches": sum(e["resources"]["experiment_model_dispatches"] for e in subset),
                           "candidate_evaluations": sum(e["resources"]["candidate_evaluations"] for e in subset),
                           "elapsed_seconds": sum(e["elapsed_seconds"] for e in subset),
                           "raw_proposal_slots": len(proposals), "illegal_proposals": sum(not pr["legal"] for pr in proposals),
                           "executed_proposals": sum(pr["executed"] for pr in proposals),
                           "fallback_records": sum(row["fallback"] for row in rows),
                           "selected_break_violations": sum(row["selected_metrics"]["raw_break_crossings"] > 0 for row in rows),
                           "record_episodes": len(rows)}
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7), layout="constrained")
    for ax, key, label in ((axes[0, 0], "model_dispatches", "Actual experiment model dispatches"),
                            (axes[0, 1], "candidate_evaluations", "Actual candidate evaluations"),
                            (axes[1, 0], "elapsed_seconds", "Observed wall time summed by batches (s)")):
        values = [resources[mode][key] for mode in MODES]
        ax.bar(range(4), values, color=[p["C" + str(i + 1)] for i in range(4)], edgecolor=p["Ink"], linewidth=.4)
        ax.set(xticks=range(4), xticklabels=MODE_LABELS, ylabel=label)
        ax.tick_params(axis="x", rotation=20)
        for i, value in enumerate(values):
            ax.annotate(f"{value:.1f}" if key == "elapsed_seconds" else str(value), (i, value),
                        xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8)
        ax.margins(y=.17)
        ax.grid(axis="y")
    ax = axes[1, 1]
    count_max = 0
    for offset, key, label, color in ((-.23, "illegal_proposals", "Rejected raw proposals", "C3"),
                                     (0, "fallback_records", "Fallback record-episodes", "C2"),
                                     (.23, "selected_break_violations", "Selected constraint violations", "C4")):
        values = [resources[mode][key] for mode in MODES]
        count_max = max(count_max, *values)
        ax.bar(np.arange(4) + offset, values, width=.23, label=label, color=p[color])
        for i, value in enumerate(values):
            ax.annotate(str(value), (i + offset, value), xytext=(0, 3), textcoords="offset points",
                        ha="center", fontsize=8)
    ax.set(xticks=range(4), xticklabels=MODE_LABELS, ylabel="Count", ylim=(0, max(1, count_max * 1.25)))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis="x", rotation=20)
    ax.legend(fontsize=7, loc="upper left")
    ax.grid(axis="y")
    fig.suptitle("Mode costs, rejected actions, and fallback · actual counts", fontsize=14)
    writer.save(fig, "four_mode_failures_and_cost", resources,
                "Model batches are counted once; governance calls are excluded. LLM-only has a smaller decision evaluation budget by design.")

    rows = [row for row in records if row["mode"] == "llm+memory+search"]
    counts = Counter()
    by_stratum = defaultdict(Counter)
    for row in rows:
        consumption = [rd["memory_consumption"] for rd in row["rounds"] if "memory_consumption" in rd]
        flags = {"Eligible": any(c["retrieved_eligible"] > 0 for c in consumption),
                 "Delivered": any(c["delivered_ids"] for c in consumption),
                 "Model cited": any(c["model_cited_valid"] for c in consumption),
                 "Action consistent": any(c["action_consistent"] for c in consumption)}
        for name, flag in flags.items():
            counts[name] += flag
            by_stratum[row["stratum"]][name] += flag
        by_stratum[row["stratum"]]["denominator"] += 1
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.8), layout="constrained")
    labels = list(counts)
    axes[0].barh(labels[::-1], [counts[label] for label in labels[::-1]], color=p["C4"])
    axes[0].set(xlabel=f"Record-episodes out of {len(rows)}", xlim=(0, max(1, len(rows)) * 1.10))
    for i, label in enumerate(labels[::-1]):
        axes[0].text(counts[label] + .5, i, str(counts[label]), va="center")
    strata = sorted(by_stratum)
    y = np.arange(len(strata))
    axes[1].barh(y - .17, [by_stratum[s]["Delivered"] / by_stratum[s]["denominator"] for s in strata], height=.34,
                 color=p["C1"], label="Delivered")
    axes[1].barh(y + .17, [by_stratum[s]["Action consistent"] / by_stratum[s]["denominator"] for s in strata], height=.34,
                 color=p["C4"], label="Cited + matching action")
    axes[1].set(yticks=y, yticklabels=[f"{s} (n={by_stratum[s]['denominator']})" for s in strata],
                xlabel="Fraction of stratum record-episodes", xlim=(0, 1.05))
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(.5, .005), ncol=2, fontsize=9)
    fig.get_layout_engine().set(rect=(0, .075, 1, .925))
    fig.suptitle("Frozen demonstration memory: eligibility, delivery, and observable consumption", fontsize=13)
    writer.save(fig, "memory_coverage_and_consumption", {"counts": dict(counts), "denominator": len(rows),
                                                         "by_stratum": {s: dict(v) for s, v in by_stratum.items()}},
                "Retrieval, citation, and matching parameters are distinct observations; none alone proves causal memory benefit.")


def _draw_trajectory(ax, record, p, title):
    raw = np.asarray(record["source_record"]["xy"])
    if raw.size:
        ax.scatter(raw[:, 0], raw[:, 1], s=10, color=p["Muted"], alpha=.45, label="Raw points")
    for i, segment in enumerate(record["final_segments"]):
        xy = np.asarray(segment["xy"])
        if xy.size:
            ax.plot(xy[:, 0], xy[:, 1], "o-", ms=3, color=p["C1"], label="Final segments" if i == 0 else None)
    ax.set_title(title, loc="left", fontsize=10)
    ax.set(xlabel="East (working m)", ylabel="North (working m)")
    # Keep one working metre equal on both axes without collapsing a narrow
    # or exactly horizontal trajectory into an unreadable axes box.
    ax.set_aspect("equal", adjustable="datalim")
    ax.xaxis.set_major_locator(MaxNLocator(nbins=4))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.tick_params(labelsize=7)
    if not record["final_segments"]:
        ax.text(.03, .97, "No final output", transform=ax.transAxes, va="top", color=p["C3"], fontsize=8)


def case_figures(writer):
    directory, manifest = writer.run("evaluation_parameters")
    entries = list(manifest["artifacts"].values())
    baseline_entry = next(entry for entry in entries if entry["parameters"] == REFERENCE and entry["order"] == "S-D-P")
    base_result = writer.trace(directory, baseline_entry)
    baseline = {row["record_id"]: row for row in base_result["records"]}
    cards_path = EV / "data/raw_diagnostics.json"
    cards = read_json(writer.source(cards_path))
    chosen = []
    for level in ("LOW", "MID", "HIGH"):
        ids = [rid for rid in baseline if cards[rid]["stratum"].startswith(level + "_")]
        median = float(np.median([cards[rid]["span_work_m"] for rid in ids]))
        rid = min(ids, key=lambda candidate: (abs(cards[candidate]["span_work_m"] - median), candidate))
        chosen.append({"role": "Representative " + level, "record_id": rid, "config_id": baseline_entry["config_id"],
                       "record": baseline[rid], "criterion_value": cards[rid]["span_work_m"],
                       "rule": "closest raw span to within-span-stratum median; stable ID tie"})
    worst_coverage, worst_error, near = None, None, None
    for entry in entries:
        result = writer.trace(directory, entry)
        for row in result["records"]:
            rid = row["record_id"]
            loss = baseline[rid]["metrics"]["common_covered_points"] - row["metrics"]["common_covered_points"]
            candidate = (loss, rid, entry["config_id"], row)
            if worst_coverage is None or (-loss, rid, entry["config_id"]) < (-worst_coverage[0], worst_coverage[1], worst_coverage[2]):
                worst_coverage = candidate
            error = row["metrics"]["common_max_error"]
            if error is not None and (worst_error is None or (-error, rid, entry["config_id"]) < (-worst_error[0], worst_error[1], worst_error[2])):
                worst_error = (error, rid, entry["config_id"], row)
            for stage in row["stages"]:
                if stage["name"] != "P":
                    continue
                for operation in stage["operations"]:
                    for point in operation["runtime_dp_check"]["error_by_original_index"]:
                        gap = abs(entry["parameters"]["dp"] - point["error"])
                        if point["error"] > 0 and gap > 0:
                            item = (gap, rid, entry["config_id"], row, point["index"])
                            if near is None or item[:3] < near[:3]:
                                near = item
    for role, candidate, rule in (("Largest covered-point loss", worst_coverage, "largest raw coverage-count loss versus same-record reference"),
                                   ("Largest available raw error", worst_error, "largest available common raw error among predeclared evaluation configurations"),
                                   ("Nearest positive P residual gap", near, "smallest positive |P tolerance - actual P residual|; stable ID/config tie")):
        if candidate:
            chosen.append({"role": role, "criterion_value": candidate[0], "record_id": candidate[1],
                           "config_id": candidate[2], "record": candidate[3], "rule": rule,
                           "original_index": candidate[4] if len(candidate) > 4 else None})
    selection = [{k: v for k, v in case.items() if k != "record"} for case in chosen]
    write_json(writer.output / "CASE_SELECTION.json", {"selection_recorded_before_render": True,
                "scope": manifest["input_ids"], "source_run": manifest["run_id"], "cases": selection,
                "selection_changes_candidates": False})
    parameter_text = {"dt": ("dt", "s"), "distance": ("distance", "working m"),
                      "min_points": ("min points", ""), "min_length": ("min length", "working m"),
                      "direction": ("direction", "deg"), "dp": ("DP", "working m")}

    def parameter_label(key, value):
        label, unit = parameter_text[key]
        return f"{label} = {value:g}" + (" " + unit if unit else "")

    fig, axes = plt.subplots(2, 3, figsize=(13, 8), layout="constrained")
    for ax, case in zip(axes.flat, chosen):
        row = case["record"]
        changed = [parameter_label(key, row["parameters"][key]) for key in REFERENCE
                   if row["parameters"][key] != REFERENCE[key]]
        configuration = "; ".join(changed) if changed else "Reference"
        _draw_trajectory(ax, row, writer.p, f"{case['role']}\nrecord {row['record_id']} · {row['metrics']['n_input']} → {row['metrics']['n_final']} points\n{configuration}")
        if case.get("original_index") is not None:
            index = case["original_index"]
            position = row["source_record"]["indices"].index(index)
            xy = row["source_record"]["xy"][position]
            residual = next(point["error"] for stage in row["stages"] if stage["name"] == "P"
                            for operation in stage["operations"]
                            for point in operation["runtime_dp_check"]["error_by_original_index"] if point["index"] == index)
            ax.scatter(*xy, s=65, facecolors="none", edgecolors=writer.p["C3"], linewidths=1.2, zorder=5)
            ax.annotate(f"Original index {index}\nP residual = {residual:.6f} working m\nTolerance = {row['parameters']['dp']:g} working m",
                        xy, xytext=(.32, .96), textcoords="axes fraction", va="top", fontsize=7,
                        arrowprops={"arrowstyle": "-", "color": writer.p["C3"], "lw": .8},
                        bbox={"facecolor": writer.p["Paper"], "edgecolor": "none", "alpha": .95})
    for ax in list(axes.flat)[len(chosen):]:
        ax.set_visible(False)
    legend = {}
    for ax in axes.flat:
        handles, labels = ax.get_legend_handles_labels()
        legend.update(zip(labels, handles))
    fig.legend(legend.values(), legend.keys(), loc="lower center", bbox_to_anchor=(.5, .045),
               ncol=2, frameon=False, fontsize=9)
    reference_description = "; ".join(parameter_label(key, value) for key, value in REFERENCE.items())
    fig.text(.5, .018, "Common reference: S-D-P; " + reference_description + ".\n"
             "Changed values are shown per panel; other parameters use the reference. Coordinates use the conditional working plane.",
             ha="center", va="center", fontsize=7)
    fig.get_layout_engine().set(rect=(0, .095, 1, .905))
    fig.suptitle(f"{manifest['partition']} · Real trajectory cases · fixed selection rules", fontsize=14)
    writer.save(fig, "real_trajectory_cases", selection,
                "Raw points are not connected across breaks. Cases include representative, largest loss/error, and near-boundary results; no basemap or ground-truth claim.")

    counter_path = ROOT / writer.current["counterexamples"] / "synthetic_cases.json"
    suite = read_json(writer.source(counter_path))
    selected_cases = [("CE03_ORDER_AND_BREAK_INFORMATION", "hidden_distance_break:P-S-D"),
                      ("CE06_OWN_CLEAN_IS_NOT_COMMON_TRUTH", "direction=35")]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")
    data = []
    for ax, (case_id, key) in zip(axes, selected_cases):
        case = next(case for case in suite["cases"] if case["case_id"] == case_id)
        record = case["executions"][key]["output"]
        title = ("Synthetic: P precedes S\noriginal distance-break information" if case_id == "CE03_ORDER_AND_BREAK_INFORMATION"
                 else "Synthetic: own-clean error\nversus the common raw reference")
        _draw_trajectory(ax, record, writer.p, title)
        for index, xy in zip(record["source_record"]["indices"], record["source_record"]["xy"]):
            ax.annotate(str(index), xy, xytext=(7, 12 if index == 0 or index % 2 else -16),
                        textcoords="offset points", fontsize=8,
                        arrowprops={"arrowstyle": "-", "lw": .5, "color": writer.p["Muted"]})
        metrics = record["metrics"]
        note = (f"Original break crossings: {metrics['raw_break_crossings']}" if case_id == "CE03_ORDER_AND_BREAK_INFORMATION"
                else f"DP input max error: {metrics['dp_max_error']:.3g} working m\nCommon raw max error: {metrics['common_max_error']:.3g} working m")
        ax.text(.03, .95, note, transform=ax.transAxes, va="top", fontsize=8,
                bbox={"facecolor": writer.p["Paper"], "edgecolor": "none", "alpha": .9})
        data.append({"case_id": case_id, "execution": key, "metrics": record["metrics"], "classification": "SYNTHETIC_COUNTEREXAMPLE"})
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, fontsize=9)
    fig.get_layout_engine().set(rect=(0, .07, 1, .93))
    fig.suptitle("Analytic risk tests · authored examples, not real-data accuracy", fontsize=14)
    writer.save(fig, "synthetic_metric_counterexamples", data, "Left: original break hidden by P. Right: zero own-clean DP error coexists with positive common raw error.")


def architecture(writer):
    p = writer.p
    # One native specification drives editable draw.io cells and vector exports.
    nodes = [
        ("human", "User + web GPT\nresearch judgment / remote review", 4.3, 8.0, 4.4, .75, "P2", None),
        ("A", "A · diagnosis / planning\ncontract and bounded proposals", .6, 6.6, 3.1, .9, "Panel", "task1/config/goal2/contract.json"),
        ("root", "Codex main + deterministic GoalJournal\nrequirements · versions · dependencies", 4.3, 6.6, 4.4, .9, "Panel", "task1/workflow/g2_journal.py"),
        ("C", "C · independent read-only review\ntrusted input + target hashes", 9.3, 6.6, 3.1, .9, "Panel", "task1/evidence/goal2/c_contract/independent_numeric.py"),
        ("B", "B-Run\nregistered actions / new artifacts", 4.3, 5.0, 2.5, .85, "Panel", "task1/workflow/g2_experiments.py"),
        ("repair", "B-Repair\nreproduce → fix → rebuild", 8.1, 5.0, 3.1, .85, "Panel", "task1/workflow/g2_journal.py"),
        ("cards", "Fixed raw diagnostic cards\nrecord / split / contract handles", .6, 2.9, 3.1, .85, "Panel", "task1/workflow/g2_data.py"),
        ("modes", "Evaluated decision paths\nLLM only · zero-model search\nLLM + search · LLM + memory + search", 4.3, 2.75, 4.4, 1.15, "P1", "task1/workflow/g2_modes.py"),
        ("tools", "S / D / P deterministic tools\ncomplete point ledger", 9.3, 2.9, 3.1, .85, "Panel", "task1/workflow/g2_pipeline.py"),
        ("memory", "Frozen DEMO memory\nverified examples · read-only eval", .6, .75, 3.1, .9, "Panel", "task1/workflow/g2_memory.py"),
        ("lock", "Lock candidate → post-lock evaluation\nno evaluation feedback to episode", 7.0, .75, 5.4, .9, "Panel", "task1/workflow/g2_metrics.py"),
    ]
    edges = [("human", "root", "authorized scope", False), ("A", "root", "task plan", False),
             ("root", "B", "validated action", False), ("B", "C", "artifact + hash", False),
             ("C", "root", "receipt / issue", True), ("C", "repair", "engineering issue", True),
             ("repair", "B", "new version / parent resumes", True), ("B", "cards", "controlled experiment", False),
             ("cards", "modes", "common observations", False), ("memory", "modes", "memory mode only", True),
             ("modes", "tools", "bounded candidates", False), ("tools", "modes", "actual internal feedback\nsearch LLM modes only", True),
             ("tools", "lock", "final locked output", False)]
    for node in nodes:
        if node[-1] and not (ROOT / node[-1]).is_file():
            raise ValueError("ARCHITECTURE_MODULE_DOES_NOT_EXIST:" + node[-1])
    graph = ET.Element("mxfile", host="app.diagrams.net", version="24.7.17")
    diagram = ET.SubElement(graph, "diagram", name="Goal 2 actual modules", id="g2-actual-modules")
    model = ET.SubElement(diagram, "mxGraphModel", dx="1400", dy="1000", grid="1", gridSize="10", page="1", pageWidth="1400", pageHeight="1000")
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    for ident, label, x, y, width, height, fill, module in nodes:
        style = f"rounded=1;whiteSpace=wrap;html=0;fillColor={p[fill]};strokeColor={p['Muted']};fontColor={p['Ink']};fontSize=13;"
        cell = ET.SubElement(root, "mxCell", id=ident, value=label, style=style, vertex="1", parent="1")
        ET.SubElement(cell, "mxGeometry", x=str(x * 100), y=str((9 - y - height) * 100), width=str(width * 100), height=str(height * 100), **{"as": "geometry"})
    for number, (source, target, label, dashed) in enumerate(edges):
        style = f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;endArrow=block;strokeColor={p['Ink']};fontSize=11;" + ("dashed=1;" if dashed else "")
        cell = ET.SubElement(root, "mxCell", id="edge" + str(number), value=label, edge="1", parent="1", source=source, target=target, style=style)
        ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})
    ET.indent(graph)
    drawio_path = writer.output / "goal2_actual_architecture.drawio"
    ET.ElementTree(graph).write(drawio_path, encoding="utf-8", xml_declaration=True)
    fig, ax = plt.subplots(figsize=(14, 9.6), layout="constrained")
    ax.set(xlim=(0, 13), ylim=(0, 9.3))
    ax.axis("off")
    ax.text(.5, 8.9, "Production and governance · actual roles", fontsize=14, weight="bold")
    ax.text(.5, 4.2, "Evaluated runtime · model calls counted separately", fontsize=14, weight="bold")
    ax.axhline(4.55, xmin=.03, xmax=.97, color=p["Rule"], lw=1)
    lookup = {node[0]: node for node in nodes}
    node_patches = {}
    for ident, label, x, y, width, height, fill, module in nodes:
        patch = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=.025,rounding_size=.06",
                              facecolor=p[fill], edgecolor=p["Muted"], linewidth=.8, zorder=2)
        ax.add_patch(patch)
        node_patches[ident] = patch
        ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=9, zorder=3)
    for source, target, label, dashed in edges:
        a, b = lookup[source], lookup[target]
        start = (a[2] + a[4] / 2, a[3] + a[5] / 2)
        stop = (b[2] + b[4] / 2, b[3] + b[5] / 2)
        reverse = (source, target) == ("tools", "modes")
        rad = -.45 if reverse else .14 if dashed else 0
        if (source, target) == ("B", "cards"):
            route = DrawingPath([(4.27, 5.40), (.32, 5.40), (.32, 3.325), (.57, 3.325)],
                                [DrawingPath.MOVETO, DrawingPath.LINETO, DrawingPath.LINETO, DrawingPath.LINETO])
            arrow = FancyArrowPatch(path=route, arrowstyle="-|>", mutation_scale=12, linewidth=1, color=p["Muted"], zorder=1)
        else:
            arrow = FancyArrowPatch(start, stop, arrowstyle="-|>", mutation_scale=12, linewidth=1,
                                    linestyle="--" if dashed else "-", color=p["Muted"], shrinkA=3, shrinkB=3,
                                    patchA=node_patches[source], patchB=node_patches[target],
                                    connectionstyle=f"arc3,rad={rad}", zorder=1)
        ax.add_patch(arrow)
        x, y = (start[0] + stop[0]) / 2, (start[1] + stop[1]) / 2
        if reverse:
            y -= .95
        elif source == "C" and target == "root":
            y += .65
        elif source == "repair":
            y -= .55
        elif (source, target) == ("B", "cards"):
            x, y = 1.8, 5.4
        elif (source, target) in (("cards", "modes"), ("modes", "tools")):
            y += .70
        elif (source, target) == ("A", "root"):
            y += .23
        ax.text(x, y, label, ha="center", va="center", fontsize=7, color=p["Muted"], zorder=4,
                bbox={"facecolor": p["Paper"], "edgecolor": "none", "pad": 1.2})
    writer.save(fig, "goal2_actual_architecture", {"nodes": nodes, "edges": edges,
                "drawio_file": drawio_path.name, "drawio_sha256": digest(drawio_path)},
                "Native draw.io XML and exports share one node/edge specification. Controller and S/D/P are deterministic tools, not additional agents. Web GPT review remains external.")


def build(current_runs_path=EV / "current_runs.json", output_directory=ROOT / "task1/figures/goal2", topic="all"):
    if topic not in ("all", "parameters", "modes", "candidates"):
        raise ValueError("UNKNOWN_FIGURE_TOPIC")
    writer = FigureSet(current_runs_path, output_directory, topic)
    if topic in ("all", "parameters"):
        parameters_figures(writer)
    if topic in ("all", "modes"):
        mode_figures(writer)
    if topic in ("all", "candidates"):
        case_figures(writer)
        architecture(writer)
    data_path = writer.output / "figure_data.json"
    write_json(data_path, writer.data)
    pngs = [str(writer.output / (figure["name"] + ".png")) for figure in writer.figures]
    command = [sys.executable, str(ROOT / "tools/skills/publication-plots/scripts/check_figure_set.py"), *pngs]
    check = subprocess.run(command, text=True, capture_output=True, check=False)
    (writer.output / "raster_checks.log").write_text(check.stdout + check.stderr)
    if check.returncode:
        raise ValueError("RASTER_FIGURE_CHECK_FAILED:" + check.stdout + check.stderr)
    result = {"created_at": now(), "topic": topic, "source_files": writer.sources,
              "source_binding_hash": object_hash(writer.sources), "generator_sha256": digest(__file__),
              "palette_source": "templates/latex/common/p2_cloud_sorbet_colors.tex",
              "palette_sha256": digest(ROOT / "templates/latex/common/p2_cloud_sorbet_colors.tex"),
              "figure_data_sha256": digest(data_path), "figures": writer.figures,
              "raster_check_status": "PASSED", "pdf_render_dpi": 200,
              "visual_inspection_status": "PENDING_ACTUAL_IMAGE_REVIEW", "independent_C_status": "PENDING",
              "claims": "current run visual readings only; no source datum, ground truth, final-method, or statistical superiority claim"}
    write_json(writer.output / "figure_manifest.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-runs", type=Path, default=EV / "current_runs.json")
    parser.add_argument("--output", type=Path, default=ROOT / "task1/figures/goal2")
    parser.add_argument("--topic", choices=("all", "parameters", "modes", "candidates"), default="all")
    args = parser.parse_args()
    result = build(args.current_runs, args.output, args.topic)
    print(json.dumps({"figures": len(result["figures"]), "raster_check": result["raster_check_status"],
                      "visual_inspection": result["visual_inspection_status"]}))


if __name__ == "__main__":
    main()
