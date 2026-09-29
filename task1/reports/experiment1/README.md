# 当前 Experiment 1 章节源

本目录 `Experiment_Report.tex` + `chapters/` 是25页已验收Experiment的唯一当前章节源。`experiment1.tex`仅为兼容入口；旧`*_generated.tex`不再参与正常构建。源ZIP原README保存在[README_SUPPLIED.md](README_SUPPLIED.md)，其中“尚未集成”的话属于输入交付时的历史说明。

当前原件、构建入口、隔离依赖与回归边界统一见[报告工程README](../README.md)。源包的普通 `build.sh`真实编译两次；仓库构建器在干净临时副本执行该脚本，保护当前批准阅读版 `experiment1.pdf`。`Experiment_Report.pdf`若由用户直接运行脚本生成，是新编译产物，不替代不可变canonical参考。

`source/p2_cloud_sorbet_colors.tex`只适配到公共配色源，其余主文件、章节、图形与绘图源码保持输入字节。`checks/`是源包原作者历史检查，不冒充本轮独立C核验。
