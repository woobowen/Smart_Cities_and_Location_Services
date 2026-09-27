"""Generate the exposed-development report text from independently bound results.

This entry reads no selection or FINAL_CONFIRM method output. Final chapters are
separate insertion files and remain pending until the final reporting handoff.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'task1/reports'
EV = ROOT / 'task1/evidence/goal3'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value):
    if not isinstance(value, int):
        raise ValueError('INTEGER_REPORT_VALUE_REQUIRED')
    return format(value, ',')


def label(value):
    return r'\texttt{' + value.replace('_', r'\_') + '}'


def main():
    sources, values, docs, aliases = {}, [], {}, {}

    def read(alias, relative):
        path = ROOT / relative
        sources[relative] = sha(path)
        aliases[alias] = relative
        docs[alias] = json.loads(path.read_text())
        return docs[alias]

    def get(alias, *keys):
        value = docs[alias]
        for key in keys:
            value = value[key]
        values.append({'source': alias, 'keys': list(keys), 'value': value})
        return value

    def number(alias, *keys):
        return integer(get(alias, *keys))

    def verify_mapping(mapping):
        for relative, expected in mapping.items():
            path = ROOT / relative
            if sha(path) != expected:
                raise ValueError('REPORT_SOURCE_HASH_MISMATCH:' + relative)
            sources[relative] = expected

    closure = read('C_development', 'task1/evidence/goal3/independent_c/development_closure_receipt.json')
    if closure['status'] != 'VERIFIED' or closure['errors']:
        raise ValueError('CURRENT_INDEPENDENT_DEVELOPMENT_CLOSURE_REQUIRED')
    verify_mapping({item['path']: item['sha256'] for item in closure['targets']})
    targets = {item['path']: item['sha256'] for item in closure['targets']}
    for alias, name in [('A1', 'A1_RECOMPUTE03_DECISION.json'), ('A2', 'A2_DECISION.json'),
                        ('A3', 'A3_DECISION.json'), ('convergence', 'CONVERGENCE_REVIEW.json')]:
        relative = 'task1/evidence/goal3/' + name
        if relative not in targets:
            raise ValueError('DECISION_NOT_IN_INDEPENDENT_C_SCOPE:' + name)
        value = read(alias, relative)
        verify_mapping(value.get('bindings', {}))
    a3 = docs['A3']
    run_id = a3['target_run_id']
    run_base = 'task1/evidence/goal3/runs/' + run_id + '/'
    manifest = read('manifest', run_base + 'manifest.json')
    summary = read('development', run_base + 'analysis/summary.json')
    if (summary['partition'] != 'G3_DEVELOPMENT'
            or manifest['partition'] != 'G3_DEVELOPMENT'
            or manifest['status'] != 'MACHINE_VERIFIED_PENDING_C'
            or manifest['failed_records']
            or manifest['completed_record_ids'] != manifest['input_ids']
            or summary['manifest_sha256'] != sha(ROOT / (run_base + 'manifest.json'))
            or summary['comparisons'] != manifest['comparisons']
            or summary['P_comparisons'] != manifest['P_comparisons']
            or summary['strategy_summaries'] != manifest['record_metrics']):
        raise ValueError('COMPLETE_BOUND_DEVELOPMENT_RESULT_REQUIRED')
    for name, expected in summary['tables'].items():
        verify_mapping({run_base + 'analysis/' + name: expected})
    convergence = docs['convergence']
    if (convergence['status'] != 'CONVERGED_WITHIN_REGISTERED_SCOPE'
            or convergence['previous_incumbent_sequence'] != ['R0', 'S0', 'S0', 'S0_G0']
            or a3['next_incumbent'] != 'S0_G0'):
        raise ValueError('DEVELOPMENT_NARRATIVE_NEEDS_REVIEW_FOR_NEW_DECISIONS')
    for item in docs['A1']['engineering_rebuild']:
        receipt = read(item['issue_id'], item['independent_closure']['path'])
        if receipt['status'] != 'VERIFIED' or sha(ROOT / item['independent_closure']['path']) != item['independent_closure']['sha256']:
            raise ValueError('CURRENT_REPAIR_CLOSURE_REQUIRED')
        verify_mapping({item['impact']['path']: item['impact']['sha256']})

    metric = lambda cid, key: number('development', 'strategy_summaries', cid, key)
    pair = lambda key, field: get('development', 'comparisons', key, field)
    p_pair = lambda key, field: get('development', 'P_comparisons', key, field)
    n = number('development', 'actual_records')
    points = metric('R0', 'n_input')
    status_names = {'NO_DEMONSTRATED_GAIN': '未证实收益', 'SUPPORTED_WITHIN_SCOPE': '范围内支持',
                    'TRADEOFF': '权衡', 'REJECTED_BY_CONSTRAINT': '约束拒绝'}
    table = [r'\begin{table}[H]\centering\small',
             r'\caption{G3 开发结果。每行均含全部 ' + n + r' 条记录；保护失败与严格改善均相对 R0，二者不是互补计数。P 行的研究状态按专项规则另判。}',
             r'\begin{tabularx}{\linewidth}{@{}lrrrrrY@{}}\toprule 候选 & 共同覆盖 & 保留点 & D 删除 & 保护失败 & 严格改善 & 整链状态 \\ \midrule']
    for cid in manifest['strategy_ids']:
        ref = cid + '|R0'
        failure = get('development', 'comparisons', ref, 'n_records') - pair(ref, 'protected_records')
        whole = pair(ref, 'status')
        table.append(' & '.join([label(cid), metric(cid, 'common_covered_points'), metric(cid, 'n_final'),
                                  metric(cid, 'n_direction_removed'), integer(failure),
                                  integer(pair(ref, 'strict_gain_records')), status_names[whole]]) + r' \\')
    table.append(r'\bottomrule\end{tabularx}\end{table}')
    ptable = [r'\begin{table}[H]\centering\small',
              r'\caption{相同完整 P 输入上的 DP 专项比较。正的输出点差表示存储点更多；实际误差仍以共同 5 工作米预算检验。}',
              r'\begin{tabularx}{\linewidth}{@{}lrrY@{}}\toprule 比较 & P 输出点差 & 超预算记录 & P 专项结论 \\ \midrule']
    for key in ('P2|R0', 'P10|R0', 'S0_P2|S0', 'S0_P10|S0'):
        failures = p_pair(key, 'failures_by_reason').get('COMMON_DP_BUDGET_EXCEEDED', 0)
        delta = p_pair(key, 'P_output_delta')
        ptable.append(' & '.join([label(key.replace('|', '/')), ('+' if delta > 0 else '') + integer(delta),
                                  integer(failures), status_names[p_pair(key, 'status')]]) + r' \\')
    ptable.append(r'\bottomrule\end{tabularx}\end{table}')

    exp = r'''% Generated from current independently reviewed exposed-development artifacts.
\subsection{开发范围与可解释候选}
G3 开发使用已有 DEVELOPMENT 与已经暴露的 G2\_EVAL，共 __N__ 条、__POINTS__ 个原始点。旧 G2 评估的历史身份保留；这批新比较不宣称独立最终检验。全部候选使用同一工作坐标、完整记录与原始窗口，以 R0 和当时保留的方案分别核对固定保护。

S0 同时将最小点数从 5 改为 2、最短长度从 65 改为 0；\texttt{S\_POINTS2} 与 \texttt{S\_LENGTH0} 分别只改其中一项。D60 只改方向阈值为 $60^\circ$。P2、P10 分别使用 2、10 工作米，作为有限诊断；发布的共同 P 预算仍为 5 工作米。

G0 是本轮唯一新增的轻量单项规则。只读取本记录完整原始时间：至少两个时间值且所有相邻差满足 $0<\Delta t\le30$ 秒时使用 $60^\circ$；零/负时间差、长间隔、缺失或不可用诊断均回到 $35^\circ$。阈值来自已登记原始诊断，没有按记录 ID 记忆答案。单独 G0 使用 R0 分段；组合 \texttt{S0\_G0} 使用 S0 分段。开发集中两组各 __GROUP__ 条，未知组保留对应基线规则。

__MAIN_TABLE__

\subsection{单项先行，再检查组合与移除}
S0 对 R0 的全部 __N__ 条保护通过；__S_GAIN__ 条增加共同覆盖，覆盖从 __R_COVER__ 增至 __S_COVER__，无输出记录由 __R_EMPTY__ 降至 __S_EMPTY__。在 R0 原已覆盖集合上未观察到严格几何改善，故其支持来自覆盖恢复。仅降低点数或仅取消长度下限都不能保留 S0 的全部新增覆盖：移去长度调整损失 __REMOVE_LENGTH__ 点，移去点数调整损失 __REMOVE_POINTS__ 点。

统一 D60 有 __D_FAIL__ 条共同几何保护失败，不能自动替代 R0。预先登记的 G0 在全部记录满足 R0 保护，并在 __G_GAIN__ 条上严格降低共同最大误差，但它仍丢失 S0 新增的 __S_DELTA__ 个覆盖点。因此 A2 保留 S0 为当时方案，同时允许两个有独立作用的父项进入组合；没有用语言打分在互不包含的收益间选胜者。

\texttt{S0\_G0} 对 R0、S0 和 G0 的全部保护均通过。相对 S0，覆盖不变，__SG_S_GAIN__ 条几何改善，实际存储点增加 __SG_S_POINTS__；相对 G0，__SG_G_GAIN__ 条恢复覆盖。相对 R0 的 __SG_R_GAIN__ 条严格改善由 __COVER_GAIN__ 条覆盖改善与 __GEOM_GAIN__ 条几何改善的并集形成，二者交叠 __OVERLAP__ 条。这些读数属于各参考原已覆盖集合上的最大误差保护，不表示每个原始点都逐点改善。

移除组合的 G0 后，__REMOVE_G_FAILURES__ 条失去已经接受的几何保护；移除 S0 后，__REMOVE_S_RECORDS__ 条丢失 __S_DELTA__ 个覆盖点，并使 __REMOVE_S_EMPTY__ 条重新无输出。这支持保留这次组合的两部分。点数与长度的拆分核验只在原 S0 父项上完成，没有把它扩写成所有 G0 上游组合都已穷尽消融。

\subsection{DP 交互的负结果与停止理由}
__P_TABLE__
\texttt{S0\_P2} 的 P 自身误差较小，但相对相同上游、DP 5 的 S0 多存 __P2_EXTRA__ 点，没有省点收益；整链仍有 __P2_CHAIN_FAIL__ 条相对 S0 的共同几何保护失败，相对更新后的 \texttt{S0\_G0} 为 __P2_INC_FAIL__ 条。\texttt{S0\_P10} 在 __P10_BUDGET_FAIL__ 条记录上实际超出共同 5 工作米预算。S 的覆盖增益不能遮盖 P 组件的无收益或预算失败，故没有采用这些 P 变体。

新增覆盖也单独检查。\texttt{S0\_G0} 新增的 __S_DELTA__ 个覆盖身份全部来自触发参考短段过滤条件（点数不足或长度不足）的片段，不能把这一并集解释为全部长度小于 65。其中 __ZERO_ENDPOINTS__ 个是与原始完全零位移相邻边相接的端点身份；这不是停留点或真实噪声标签。新增覆盖点到最终折线的最大偏差为 __NEW_MAX__ 工作米、均值为 __NEW_MEAN__ 工作米。最大值可超过 5，因为 P 的 5 工作米限制适用于 D 后完整输入，而非所有原始点的统一保证。

实际有限探索新增 __NEW_SINGLE__ 个轻量单项、__NEW_COMB__ 个组合定义，低于批准的 __SINGLE_LIMIT__/__COMB_LIMIT__ 上限。必要父项、组合、P 专项和移除检查已经完成；没有有据可检验的新假设，因此停止扩展。第二类删除保护缺少可靠的位移/物理阈值依据，未纳入；危险顺序与新增在线 LLM/记忆模式也没有新的支持机制。开发结论是保留 \texttt{S0\_G0} 并登记 R0、S0、G0、\texttt{S0\_G0} 四个短名单方案，之后才进入选择与最终确认。保留点增加与未知的可比逐策略耗时限制了“全面支配”表述；本节不声称全局最优。
'''
    regular = next(row['records'] for row in summary['runtime_groups'] if row['strategy'] == 'G0' and row['group'] == 'TIME_REGULAR')
    fallback = next(row['records'] for row in summary['runtime_groups'] if row['strategy'] == 'G0' and row['group'] == 'TIME_FLAGGED_OR_UNAVAILABLE')
    if regular != fallback:
        raise ValueError('GROUP_SIZE_PROSE_NEEDS_REVISION')
    values.append({'source': 'development', 'keys': ['runtime_groups', 'G0/TIME_REGULAR', 'records'], 'value': regular})
    replacements = {
        '__N__': n, '__POINTS__': points, '__GROUP__': integer(regular), '__MAIN_TABLE__': '\n'.join(table),
        '__S_GAIN__': integer(pair('S0|R0', 'strict_gain_records')), '__R_COVER__': metric('R0', 'common_covered_points'),
        '__S_COVER__': metric('S0', 'common_covered_points'), '__R_EMPTY__': metric('R0', 'n_no_output_records'),
        '__S_EMPTY__': metric('S0', 'n_no_output_records'), '__S_DELTA__': integer(pair('S0|R0', 'coverage_delta')),
        '__REMOVE_LENGTH__': integer(-pair('S_POINTS2|S0', 'coverage_delta')),
        '__REMOVE_POINTS__': integer(-pair('S_LENGTH0|S0', 'coverage_delta')),
        '__D_FAIL__': integer(pair('D60|R0', 'n_records') - pair('D60|R0', 'protected_records')),
        '__G_GAIN__': integer(pair('G0|R0', 'strict_gain_records')),
        '__SG_S_GAIN__': integer(pair('S0_G0|S0', 'strict_gain_records')),
        '__SG_S_POINTS__': integer(pair('S0_G0|S0', 'final_point_delta')),
        '__SG_G_GAIN__': integer(pair('S0_G0|G0', 'strict_gain_records')),
        '__SG_R_GAIN__': integer(pair('S0_G0|R0', 'strict_gain_records')),
        '__COVER_GAIN__': number('A3', 'candidate_status', 'S0_G0', 'strict_gain_interpretation', 'vs_R0', 'coverage_gain_records'),
        '__GEOM_GAIN__': number('A3', 'candidate_status', 'S0_G0', 'strict_gain_interpretation', 'vs_R0', 'geometry_gain_records'),
        '__OVERLAP__': number('A3', 'candidate_status', 'S0_G0', 'strict_gain_interpretation', 'vs_R0', 'overlap_records'),
        '__REMOVE_G_FAILURES__': integer(pair('S0|S0_G0', 'n_records') - pair('S0|S0_G0', 'protected_records')),
        '__REMOVE_S_RECORDS__': integer(pair('G0|S0_G0', 'n_records') - pair('G0|S0_G0', 'protected_records')),
        '__REMOVE_S_EMPTY__': integer(pair('G0|S0_G0', 'failures_by_reason')['RECORD_COVERAGE_LOST']),
        '__P_TABLE__': '\n'.join(ptable), '__P2_EXTRA__': integer(p_pair('S0_P2|S0', 'P_output_delta')),
        '__P2_CHAIN_FAIL__': integer(pair('S0_P2|S0', 'n_records') - pair('S0_P2|S0', 'protected_records')),
        '__P2_INC_FAIL__': integer(pair('S0_P2|S0_G0', 'n_records') - pair('S0_P2|S0_G0', 'protected_records')),
        '__P10_BUDGET_FAIL__': integer(p_pair('S0_P10|S0', 'failures_by_reason')['COMMON_DP_BUDGET_EXCEEDED']),
        '__ZERO_ENDPOINTS__': number('development', 'new_coverage', 'S0_G0|R0', 'raw_exact_zero_displacement_adjacent_endpoints'),
        '__NEW_MAX__': format(get('development', 'new_coverage', 'S0_G0|R0', 'max_error_work_m'), '.6f'),
        '__NEW_MEAN__': format(get('development', 'new_coverage', 'S0_G0|R0', 'mean_error_work_m'), '.6f'),
        '__NEW_SINGLE__': number('convergence', 'new_candidate_definitions', 'single'),
        '__NEW_COMB__': number('convergence', 'new_candidate_definitions', 'combination'),
        '__SINGLE_LIMIT__': number('convergence', 'new_candidate_definitions', 'limits', 'single'),
        '__COMB_LIMIT__': number('convergence', 'new_candidate_definitions', 'limits', 'combination'),
    }
    for key, value in replacements.items():
        exp = exp.replace(key, value)
    if '__' in exp:
        raise ValueError('UNRESOLVED_DEVELOPMENT_TEXT_FIELD')

    process = r'''% Decision process, separate from the workflow construction layer.
\subsection{A1：先分开短段策略、方向与 DP 的作用}
A 读取同一 __N__ 条开发记录的已核验对照后，将当时方案从 R0 更新为 S0，触发的是 __S_GAIN__ 条覆盖改善与全部保护通过。点数、长度两项各自具有作用，但单独保留任一项都会损失组合恢复的一部分覆盖，因此没有为了更少参数把必要调整删去。

统一方向 $60^\circ$ 的 __D_FAIL__ 条几何退化被保留为真实负结果。A 没有反复试到统一方向胜出，而是核对事先登记的原始时间分组机制：时间规则组有局部收益，异常/不可计算组回到基线。这只支持下一项真实检查，不提前证明未见记录安全。

\subsection{A2：有用父项不等于立即替换}
G0 相对 R0 的保护通过，__G_GAIN__ 条具有几何改善；与 S0 比较时，它会丢失 __S_DELTA__ 个新增覆盖点，S0 又不能保留 G0 的全部几何收益。按预先批准的保守规则，当时方案仍是 S0。两部分作用机制不同且已独立核验，才允许进入 \texttt{R0/S0/G0/S0\_G0} 四种完整对照。

\subsection{A3：接受实际组合，拒绝无贡献的附加项}
实际组合 \texttt{S0\_G0} 同时通过对固定 R0 和当时 S0 的全部保护，相对 S0 在 __SG_S_GAIN__ 条上改善共同几何误差，开发中的保留方案才更新为组合。移去 G0 会损失这些已接受性质；移去 S0 会损失 __S_DELTA__ 个覆盖身份。这个决定来自父项与移除比较，不来自预设 S0 必胜或“组件越多越好”。

S 与 DP 的两个组合也真实执行：DP 2 在相同上游多存 __P2_EXTRA__ 点，整链相对 S0 有 __P2_CHAIN_FAIL__ 条几何退化；DP 10 在 __P10_BUDGET_FAIL__ 条超过发布预算。A 保留这些负结果，未把覆盖增长解释成 P 改进，最终开发短名单仍使用 DP 5。

剩余机会复盘认为，有依据的父项、主要交互与必要移除已经完成。未采用第二类删除保护，因为没有可靠的位移/物理真值阈值；未重跑完整四模式矩阵，因为历史材料尚不支持增加记录级模型或记忆依赖。实际只新增 __NEW_SINGLE__ 个轻量单项与 __NEW_COMB__ 个组合，没有为了耗尽配额补空实验。开发中的路径为 R0 $\rightarrow$ S0 $\rightarrow$ S0 $\rightarrow$ \texttt{S0\_G0}；短名单进入下一阶段，尚不能代替最终确认。

这些都是在用户事先批准规则内的系统决定。独立 C 已对本轮开发产物与裁决闭合检查，但内部核验不是新的用户批准，也不是 Evidence Master 的互动证据 Lock。没有可用的用户逐次判断原话，因此不补写“用户选中了组合”。
'''
    for key, value in replacements.items():
        process = process.replace(key, value)
    if '__' in process:
        raise ValueError('UNRESOLVED_PROCESS_TEXT_FIELD')
    workflow = r'''% Workflow facts only; technical choice and numerical effects belong in Part II.
\subsection{G3 的可移植复算缺陷触发了真实重建}
离线包没有 Git 目录时，原处理身份代码无法取得 HEAD；相对缓存父目录又在生成仓库内出处时失败。两项实际接口问题分别登记为 G3-C06、G3-C07。B 修复了冻结源码身份的离线校验和路径规范化，没有改变几何、参数或指标定义；C 对新产物独立复验，主线程使受影响的旧版本运行失效并重建。

已有 A 提议和旧结果继续作为历史记录保存；当前决定明确标为在新源码版本下复算，不冒称新的在线模型提议。父任务恢复后才继续条件规则与组合执行。绑定文件、缓存源和审核目标一旦不匹配就拒绝复用，不能只修汇总表而保留失效的决定身份。具体方法裁决与数值在第二层说明。
\input{governance_generated.tex}
\input{workflow_figure_generated.tex}
'''
    outputs = {
        REPORTS / 'experiment1/development_generated.tex': exp,
        REPORTS / 'process1/development_generated.tex': process,
        REPORTS / 'process1/workflow_generated.tex': workflow,
    }
    for path, content in outputs.items():
        path.write_text(content)
    receipt = {'at_utc': datetime.now(timezone.utc).isoformat(),
               'classification': 'REPORT_DEVELOPMENT_BINDING_NOT_NEW_METHOD_RUN',
               'stage': 'G3_DEVELOPMENT_ONLY', 'source_sha256': sha(Path(__file__)),
               'source_aliases': aliases,
               'source_bindings': sources, 'generated_values': values,
               'outputs': {str(p.relative_to(ROOT)): sha(p) for p in outputs},
               'new_model_calls': 0, 'new_method_runs': 0,
               'selection_or_final_effects_read': False,
               'review_status': 'GENERATED_PENDING_INDEPENDENT_DOCUMENT_REVIEW'}
    path = EV / 'report_build/goal3_development_bindings.json'
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': 'GENERATED_BOUND_DEVELOPMENT_CHAPTERS', 'source_files': len(sources),
                      'value_reads': len(values), 'development_run': run_id,
                      'new_model_calls': 0, 'selection_or_final_effects_read': False}))


if __name__ == '__main__':
    main()
