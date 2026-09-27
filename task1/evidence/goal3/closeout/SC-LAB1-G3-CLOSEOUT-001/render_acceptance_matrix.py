"""Render the task's one CL01–CL16 checklist; statuses are supported by linked actual evidence."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[4]


def main():
    data = json.loads((BASE / 'ACCEPTANCE_MATRIX.json').read_text())
    lines = ['# SC-LAB1-G3-CLOSEOUT-001 收尾验收矩阵', '',
             '此表是当前 Prompt 的 CL 验收记录；父要求仍由 `task1/evidence/goal3/requirements.json` 统一登记。'
             'PASS 只限所写工程范围，不代表用户理解、Evidence Lock、网页 GPT 最终验收或作业提交。', '',
             '| ID | 对象 | 状态 | 实际范围、命令/动作和结果 | 证据 | 剩余动作 |',
             '|---|---|---|---|---|---|']
    import os
    for row in data['checks']:
        evidence = '<br>'.join(f'[{Path(p).name}]({os.path.relpath(ROOT / p, BASE)})' for p in row['evidence'])
        text = lambda value: str(value).replace('|', '\\|').replace('\n', '<br>')
        lines.append('| ' + ' | '.join(map(text, [row['id'], row['object'], row['status'],
            row['actual_scope'] + '；' + row['action'] + '；' + row['result'], evidence, row['remaining']])) + ' |')
    lines += ['', '独立状态：', '']
    for key, value in data['independent_states'].items():
        lines.append(f'- {key}：`{value}`。')
    lines += ['', '环境新增：系统包、语言包、工具链、字体及持久环境配置均为 0。', '',
              '本轮新增记录级实验模型调用为 0。治理 A/B/C 为真实上下文协作；底层模型请求数和费用不可观察，保持 unknown。', '']
    (BASE / 'ACCEPTANCE_MATRIX.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
