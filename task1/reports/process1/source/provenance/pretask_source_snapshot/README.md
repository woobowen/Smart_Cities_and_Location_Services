# Workflow Construction - Pre-Task-1 31-page LaTeX source

完整可编辑源码包，包括 12 个 block 的 `.tex` 和全部原始聊天截图 assets。

## 构建

```bash
./build_31p.sh
```

生成：

```text
build/WF_WorkflowConstruction_PreTask1_31p.pdf
```

构建链：XeLaTeX (`latexmk -xelatex`) -> `pdfunite`。

为了保持现有 31 页审核稿的历史分页，Block 01 的第一组 Evidence 保留 continuation page；其余页面按各 block 原始 LaTeX 编译。

所有截图仍是 PNG 原始/无损裁片；颜色框、highlight、编号和长箭头保留在 LaTeX/TikZ 矢量层，可以继续精修。
