"""Render the ten report figures from the included frozen data, without model calls."""
from pathlib import Path
import runpy


def main() -> None:
    from matplotlib import font_manager
    family = "Noto Sans CJK JP"
    if family not in {font.name for font in font_manager.fontManager.ttflist}:
        raise RuntimeError(f"Matplotlib未找到字体 {family}；请先配置中文字体，不要接受缺字输出。")
    root = Path(__file__).resolve().parents[1]
    (root / "figures").mkdir(exist_ok=True)
    runpy.run_path(str(root / "source/draw_sample_trajectory.py"), run_name="__main__")
    module = runpy.run_path(str(root / "source/draw_report_figures.py"))
    for name in module["run"]():
        print(f"已生成：{name}")
    for script in ("draw_g6_logic.py", "draw_workflow.py"):
        runpy.run_path(str(root / "source" / script), run_name="__main__")


if __name__ == "__main__":
    main()
