"""Append sourced root/controller decisions, without inventing human dialogue."""
from pathlib import Path
import json
from datetime import datetime, timezone
import hashlib

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT/'task1/evidence/goal3'
DOC = ROOT/'task1/docs/goal3/INTERACTION_HANDOFF.md'


def read(path):
    return json.loads(path.read_text())


def ref(relative):
    path = ROOT/relative
    return {'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'locator': None}


def entry(identifier, topic, trigger, proposal, decision, paths, time, importance):
    return {
        'candidate_id': identifier, 'Topic': topic, 'Trigger': trigger,
        'User_verbatim_and_source': {'status': 'NOT_AVAILABLE', 'quotes': [],
            'limitation': 'Current preauthorization is not a per-decision user utterance.'},
        'GPT_or_Agent_proposal': {'status': 'ACTUAL_SYSTEM_ARTIFACTS', 'text': proposal},
        'Human_Judgment': {'status': 'NOT_AVAILABLE', 'verbatim': None,
            'meaning': None, 'not_per_trial_choice': True},
        'Referenced_materials_and_experiments': [ref(path) for path in paths],
        'Actual_decision': {'type': 'SYSTEM_DECISION_WITHIN_USER_PREAPPROVED_RULES', 'text': decision},
        'Available_message_range': {'root_context': '/root', 'C_context': '/root/c_protocol',
            'artifact_time': time, 'original_human_chat_turns': 'NOT_AVAILABLE'},
        'Potential_importance': importance,
        'Evidence_identity': 'REAL_SYSTEM_FACT_NOT_HUMAN_JUDGMENT_OR_VERBATIM_CHAT',
        'artifact_time_if_known': {'source': 'bound actual artifact', 'at': time},
        'current_authority_ref': {**ref('task1/evidence/goal3/USER_PROMPT.md'),
            'locator': '§4, §7–10, §14–15; current preauthorization only'},
        'formal_evidence_selection': 'NOT_ASSIGNED_BY_THIS_HANDOFF', 'Tier': None,
        'screenshot_spec': None, 'annotation_spec': None, 'report_order': None,
        'Evidence_Lock': 'NOT_ASSIGNED_BY_THIS_HANDOFF'}


def main():
    data = read(EV/'interaction_candidates.json')
    selection = read(EV/'selection_decision.json')
    release = read(EV/'release_decision.json')
    closure = read(EV/'independent_c/G3-C08_closure.json')
    boundary = read(EV/'independent_c/new_coverage_boundary_receipt.json')
    if boundary['status'] != 'VERIFIED':
        raise ValueError('INDEPENDENT_BOUNDARY_RECEIPT_REQUIRED')
    items = [
        entry('IH-G3-C08', '审核必须指向当前分片和源码，不能只相信旧通过回执',
            '独立 C 在首次选择冻结前构造真实执行的篡改夹具，发现辅助门控接受已改变分片、错源码版本和缺失审核目标。',
            '主线程修复 verified_run，逐一核对真实分片、C 回执全部目标、回执/运行/当前源码三方身份；独立 C 重跑五项夹具及三次既有开发运行。',
            '初次 1 项通过、4 项失败；修复后 5 项通过，18 个真实开发分片通过当前性核对。数值实现未改变；这是工程修复，不是数据质量收益。修复关闭后才固定选择阶段。',
            ['task1/evidence/goal3/independent_c/G3-C08_failure.json',
             'task1/evidence/goal3/repairs/C08_impact.json',
             'task1/evidence/goal3/independent_c/G3-C08_closure.json',
             'task1/evidence/goal3/selection_freeze.json'], closure['checked_at_utc'],
            '可说明实际问题、最小修复、独立关闭与父任务恢复，避免把一份旧 PASS 回执用于新产物。'),
        entry('IH-G3-SELECTION', '开发支持的方向组合在选择集出现退化，发布候选回到 S0',
            '四个完整策略和规则已冻结后，实际处理 240 条 G3_SELECTION；G0 和 S0_G0 在 3017、9311、9534 三条共同参考几何退化。',
            '确定性选择器依预登记 R0→S0→G0→S0_G0 顺序消费完整配对；C 独立重算全部三条失败的四个策略，定位为方向保留集合改变后的 DP 交互。',
            'S0 相对 R0 全 240 条保护通过，103 条严格覆盖增加，共新增 6,625 点。G0/S0_G0 即时 P 误差仍低于 5 工作米，但不能抵消三条共同几何退化；保持 S0，未修改分组或阈值。开发 incumbent S0_G0 的支持只属于开发范围。',
            ['task1/evidence/goal3/selection_freeze.json',
             'task1/evidence/goal3/selection_decision.json',
             'task1/evidence/goal3/independent_c/selection_failure_receipt.json',
             'task1/evidence/goal3/independent_c/selection_closure_receipt.json'], selection['at'],
            '可展示组合未被预设为最终赢家，局部保证与共同参考保护不同；负结果被保留而非反复调到获胜。'),
        entry('IH-G3-FINAL-CONFIRM', '一次性最终确认支持冻结 S0，未在最终集选择新方案',
            'S0 主候选、R0 预设回退、600 条完整记录、代码和保护规则在打开最终结果前冻结。',
            'B 按冻结参数运行 R0/S0；C 核查 1,200 份实际 trace、完整配对及 40 条记录的 80 份独立数学重算，再由预登记发布门控裁决。',
            '600 条全部保护通过，349 条严格覆盖增加；共同覆盖 35,868→62,220，显式保留 10,991→12,114。采用 S0，未触发 R0 回退；没有最终集调参或新赢家选择。新增覆盖最大原始偏差 6.087102 工作米，不是噪声准确率。',
            ['task1/evidence/goal3/final_freeze.json',
             'task1/evidence/goal3/runs/g3-final-confirm-01/manifest.json',
             'task1/evidence/goal3/release_decision.json',
             'task1/evidence/goal3/independent_c/confirmation_closure_receipt.json'], release['at'],
            '可说明开发、选择、最终确认的边界，以及系统遵守用户预先规则而非伪造逐次 Human Judgment。'),
        entry('IH-G3-FULL-BOUNDARY', '扩大覆盖后仍公开原始几何偏差很大的边界案例',
            '冻结后全量处理的新增覆盖最大偏差远大于 5 工作米；主线程要求 C 定位并从原始值独立核查，不改变方法。',
            'C 枚举所有 11,386 条记录的新增覆盖集合，并用 Decimal/PROJ 重算最差 record 352/index 105 的参考和最终轨迹，区分 S 过滤、D 删除与 P 即时输入。',
            '新增覆盖共 500,312 点；最差点偏差 266.01675442514176 工作米。原窗口 [104,105,106,107] 被 R0 因点数不足过滤；S0 的 D 删除 105，P 输入/输出均 [104,106,107]。这是实际方法局限，局部 P 没有删点；保留冻结 S0 和负面案例，不把覆盖增长称为噪声识别准确率。此专项回执不代替另行的全量总审。',
            ['task1/evidence/goal3/production_freeze.json',
             'task1/evidence/goal3/runs/g3-full-production-01/manifest.json',
             'task1/evidence/goal3/independent_c/new_coverage_boundary_receipt.json'],
            boundary['checked_at_utc'],
            '可呈现扩大真实范围后仍保留限制、准确追溯阶段责任的过程事实；这不是虚构用户质疑，也不是看过全量后重新调参。')]
    replace = {item['candidate_id'] for item in items}
    data['candidates'] = [item for item in data['candidates'] if item['candidate_id'] not in replace] + items
    data['version'] = 'ROOT_POSTFREEZE_FACT_APPEND'
    data['scope'] = 'Original A-authored historical/development index plus root-authored postfreeze C08, selection, final-confirmation and full-production boundary facts; original A research context did not receive final effects.'
    data['append_author_role'] = 'root/controller; independent C evidence is linked, not authored here'
    data['updated_at_utc'] = datetime.now(timezone.utc).isoformat()
    data['selection_effects_read'] = 'ROOT_ONLY_AFTER_SELECTION_FREEZE'
    data['FINAL_CONFIRM_effects_read'] = 'ROOT_AND_C_ONLY_AFTER_FINAL_FREEZE; NOT_SENT_TO_A'
    data['native_message_limits'] = 'Governance events preserve tool metadata and encrypted-payload hashes where plaintext was unavailable. They are not recovered verbatim human/agent dialogue.'
    (EV/'interaction_candidates.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    original = DOC.read_text().split('\n<!-- ROOT_POSTFREEZE_APPEND -->')[0]
    original = original.replace('**开发阶段事实候选索引；供 Evidence Master 检索与进一步审核。**',
        '**真实事实候选索引；供 Evidence Master 检索与进一步审核。**')
    original = original.replace('没有读取选择集或FINAL_CONFIRM效果。',
        '此前 A 撰写部分没有读取选择集或 FINAL_CONFIRM 效果；下方主线程追加部分只在对应冻结之后依据实际产物整理，不向 A 研究上下文传回最终效果。')
    extra = ['\n<!-- ROOT_POSTFREEZE_APPEND -->\n',
        '\n以下由主线程按真实产物追加。治理工具事件只保存可得元数据；平台加密载荷的哈希不表示已恢复消息原文。\n']
    for item in items:
        extra.extend([f"\n## {item['candidate_id']} · {item['Topic']}\n",
            f"\n**真实 Trigger：** {item['Trigger']}\n",
            '\n**User 原话与真实 Human Judgment：** NOT_AVAILABLE。当前预先授权不替代逐次判断。\n',
            f"\n**GPT/Agent 提议：** {item['GPT_or_Agent_proposal']['text']}\n",
            f"\n**实际决定：** {item['Actual_decision']['text']}\n",
            f"\n**可得范围：** 实际产物时间 {item['Available_message_range']['artifact_time']}；主线程 /root、独立 C /root/c_protocol。原始 Human 聊天消息范围 NOT_AVAILABLE。\n",
            f"\n**为什么可能重要：** {item['Potential_importance']}\n",
            '\n资料/实验：\n\n'])
        for source in item['Referenced_materials_and_experiments']:
            relative = '../../'+source['path'].removeprefix('task1/')
            extra.append(f"- [{Path(source['path']).name}]({relative})\n")
    DOC.write_text(original.rstrip()+'\n'+''.join(extra))
    print({'candidates': len(data['candidates']), 'new_fact_entries': len(items), 'Evidence_Lock': 'NOT_ASSIGNED'})


if __name__ == '__main__':
    main()
