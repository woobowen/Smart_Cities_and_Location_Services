"""Check the included frozen figure inputs; this is not a new full experiment."""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

B = Path(__file__).resolve().parents[1]
D = B / "data"


def main() -> dict:
    checks = []

    def check(name: str, ok: bool) -> None:
        checks.append({"check": name, "passed": bool(ok)})
        if not ok:
            raise AssertionError(name)

    raw = json.loads((D / "raw_statistics.json").read_text())
    check("原始记录、点与边的数量关系", raw["n_records"] == 11386 and raw["n_points"] == 1173410 and raw["n_edges"] == raw["n_points"] - raw["n_records"])
    table = pd.read_csv(D / "parameter_results.csv")
    check("59项唯一参数配置，均为完整120条开发记录", len(table) == 59 and table.config_id.nunique() == 59 and (table.n_records == 120).all() and (table.n_input == 11777).all())
    check("全部开发配置点终态相加等于输入", (table.n_filtered + table.n_direction_removed + table.n_dp_removed + table.n_final == table.n_input).all())
    grid = pd.read_csv(D / "parameter_grid.csv")
    check("三维参数网格恰为5乘5实测设置", len(grid) == 25 and grid.min_points.nunique() == 5 and grid.min_length.nunique() == 5 and not grid.duplicated(["min_points", "min_length"]).any())
    check("网格覆盖率与冻结配置逐项一致", all(abs(float(r.coverage_pct) - float(table[(table.min_points == r.min_points) & (table.min_length == r.min_length) & (table.dt == 30) & (table.distance == 400) & (table.direction == 35) & (table.dp == 5)].iloc[0].common_covered_points) / 11777 * 100) < 1e-8 for r in grid.itertuples()))
    M = np.loadtxt(D / "fate_transition_counts.csv", delimiter=",", skiprows=1, dtype=np.int64)
    check("流向矩阵非负，全部点只计入一次", M.shape == (4, 4) and (M >= 0).all() and int(M.sum()) == 1173410)
    check("参考状态边际计数一致", M.sum(axis=1).tolist() == [501511, 36056, 435373, 200470])
    check("最终状态边际计数一致", M.sum(axis=0).tolist() == [1199, 39732, 911330, 221149])
    pair = pd.read_csv(D / "confirmation_coverage_pairs.csv")
    check("确认600个唯一记录，原始点数一致", len(pair) == 600 and pair.record_id.nunique() == 600 and int(pair.n_raw.sum()) == 62284)
    check("确认覆盖总数与严格改善计数", int(pair.r0_cover.sum()) == 35868 and int(pair.s0_cover.sum()) == 62220 and int((pair.new_coverage > 0).sum()) == 349 and int((pair.new_coverage == 0).sum()) == 251)
    check("确认直方图差值是覆盖率百分点", np.allclose(pair.coverage_delta_pp, (pair.s0_cover - pair.r0_cover) / pair.n_raw * 100, atol=1e-12) and pair.coverage_delta_pp.between(0,100).all())
    m = pd.read_csv(D / "mode_results.csv")
    check("模式表实际派发总数84且search-only为0", int(m.dispatches.sum()) == 84 and m[m["mode"] == "仅确定性搜索"].dispatches.eq(0).all())
    check("模式观察数区分24与24乘3", m[m.split == "开发"].observations.eq(24).all() and m[m.split == "阶段评估"].observations.eq(72).all())
    final = json.loads((D / "final_verified_results.json").read_text())
    check("完整结果冻结来源与原始数量一致", final["original_records"] == 11386 and final["original_points"] == 1173410 and final["data_sha256"] == "c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3")
    for tag, idx in [("R0", 0), ("S0", 1)]:
        v = final["full"][tag]
        counts = [v["n_filtered"], v["n_direction_removed"], v["n_dp_removed"], v["n_final"]]
        check(f"{tag}全量点账本与流向图一致", counts == (M.sum(axis=1) if idx == 0 else M.sum(axis=0)).tolist() and sum(counts) == v["n_input"])
        check(f"{tag}DP省点率由其自身完整输入计算", math.isclose(v["dp_saving"], 1-v["n_dp_output"]/v["n_dp_input"], abs_tol=1e-12))
    ex = json.loads((D / "trajectory_examples.json").read_text())["352"]
    p = np.asarray(ex["xy"], dtype=float)
    a, b, q = p[104], p[106], p[105]
    u = np.clip(np.dot(q-a,b-a)/np.dot(b-a,b-a),0,1)
    error = float(np.linalg.norm(q-a-u*(b-a)))
    check("边界例105仅按104—106有限线段计算", math.isclose(error, 266.01675442514176, abs_tol=1e-6))
    check("最终新增覆盖来源三类总数", 492513 + 5434 + 2365 == 500312 == final["full_pairs"]["coverage_delta"])
    for f in (B / "figures").glob("*.drawio"):
        tree = ET.parse(f)
        cells = tree.findall(".//mxCell")
        ids = {c.attrib["id"] for c in cells}
        check(f"{f.name}可解析且连线端点引用有效", len(cells) > 10 and all(c.attrib.get(k) is None or c.attrib[k] in ids for c in cells if c.attrib.get("edge") == "1" for k in ("source", "target")))
    out = {"scope": "Frozen-input and figure-source checks only; no model call or new full processing", "checks": checks, "passed": sum(c["passed"] for c in checks), "total": len(checks), "boundary_error_work_m": error}
    (B / "checks").mkdir(exist_ok=True)
    (B / "checks/input_validation.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"冻结输入检查：{out['passed']}/{out['total']}，未运行新实验。")
    return out


if __name__ == "__main__":
    main()
