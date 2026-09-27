"""Bind the completed selection decision and every observed failure to reports."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'task1/reports'
EV = ROOT / 'task1/evidence/goal3'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sources, docs, aliases, values = {}, {}, {}, []

    def read(alias, relative):
        path = ROOT / relative
        sources[relative] = sha(path)
        aliases[alias] = relative
        docs[alias] = json.loads(path.read_text())
        return docs[alias]

    def verify(mapping):
        for path, expected in mapping.items():
            if sha(ROOT / path) != expected:
                raise ValueError('SELECTION_REPORT_HASH_MISMATCH:' + path)
            sources[path] = expected

    def value(alias, *keys):
        result = docs[alias]
        for key in keys:
            result = result[key]
        values.append({'source': alias, 'keys': list(keys), 'value': result})
        return result

    def integer(alias, *keys):
        result = value(alias, *keys)
        if not isinstance(result, int):
            raise ValueError('EXPECTED_INTEGER_REPORT_VALUE')
        return format(result, ',')

    closure = read('C_selection', 'task1/evidence/goal3/independent_c/selection_closure_receipt.json')
    if closure['status'] != 'VERIFIED' or closure['errors']:
        raise ValueError('INDEPENDENT_SELECTION_CLOSURE_REQUIRED')
    targets = {row['path']: row['sha256'] for row in closure['targets']}
    verify(targets)
    decision = read('decision', 'task1/evidence/goal3/selection_decision.json')
    verify(decision['bindings'])
    base = 'task1/evidence/goal3/runs/' + decision['run_id'] + '/'
    manifest = read('manifest', base + 'manifest.json')
    failure = read('failures', 'task1/evidence/goal3/independent_c/selection_failure_receipt.json')
    frozen = read('freeze', 'task1/evidence/goal3/selection_freeze.json')
    for path in (aliases['decision'], aliases['manifest'], aliases['failures']):
        if path not in targets:
            raise ValueError('SELECTION_REPORT_TARGET_NOT_REVIEWED:' + path)
    if (decision['partition'] != 'G3_SELECTION' or decision['final_feedback_used']
            or manifest['partition'] != 'G3_SELECTION' or manifest['failed_records']
            or manifest['input_ids'] != manifest['completed_record_ids']
            or manifest['input_ids'] != frozen['input_ids']
            or manifest['strategy_ids'] != frozen['strategy_ids']
            or failure['status'] != 'VERIFIED' or failure['errors']
            or decision['incumbent'] != 'S0'):
        raise ValueError('SELECTION_PROSE_REQUIRES_CURRENT_COMPLETE_REVIEWED_SCOPE')
    verify({row['path']: row['sha256'] for row in failure['targets']})
    comparisons, metrics = manifest['comparisons'], manifest['record_metrics']
    bad_ids = comparisons['S0_G0|S0']['failure_records']
    if (sorted(bad_ids) != sorted(row['record_id'] for row in failure['records'])
            or sorted(bad_ids) != sorted(comparisons['G0|R0']['failure_records'])
            or len(bad_ids) != 3
            or any(set(row['independent_mathematics']) != {'R0', 'S0', 'G0', 'S0_G0'} for row in failure['records'])):
        raise ValueError('ALL_ACTUAL_SELECTION_FAILURES_REQUIRED')
    metric = lambda cid, key: integer('manifest', 'record_metrics', cid, key)
    pair = lambda key, field: value('manifest', 'comparisons', key, field)
    lab = lambda cid: r'\texttt{' + cid.replace('_', r'\_') + '}'
    n = metric('R0', 'n_records')
    rows = [r'\begin{table}[H]\centering\small',
            r'\caption{冻结短名单的全部选择结果。每行均为 ' + n + r' 条记录；失败/改善均对 R0。保留点与共同覆盖分开统计。}',
            r'\begin{tabularx}{\linewidth}{@{}lrrrrY@{}}\toprule 策略 & 共同覆盖 & 保留点 & 保护失败 & 严格改善 & 冻结规则的决定 \\ \midrule']
    for cid in manifest['strategy_ids']:
        count = pair(cid+'|R0', 'n_records') - pair(cid+'|R0', 'protected_records')
        decision_text = '固定参考' if cid == 'R0' else ('保留为确认主候选' if cid == 'S0' else '权衡，未替换 S0')
        rows.append(' & '.join([lab(cid), metric(cid, 'common_covered_points'), metric(cid, 'n_final'),
                                 str(count), integer('manifest', 'comparisons', cid+'|R0', 'strict_gain_records'), decision_text]) + r' \\')
    rows.append(r'\bottomrule\end{tabularx}\end{table}')
    failure_rows = [r'\begin{table}[H]\centering\small',
                    r'\caption{全部三个选择失败案例：S0 与 S0\_G0 的同一参考原始覆盖集合。距离为工作米；即时 P 误差均不超过 5。}',
                    r'\begin{tabularx}{\linewidth}{@{}lrrrrY@{}}\toprule 原记录 & 原始点 & D 后点数 & P 后点数 & 共同最大误差 & 性质 \\ \midrule']
    selected_diagnoses = {}
    for ri, record in enumerate(failure['records']):
        di = next(i for i, row in enumerate(record['stage_pair_diagnoses']) if row['candidate'] == 'S0_G0' and row['reference'] == 'S0')
        item = record['stage_pair_diagnoses'][di]
        selected_diagnoses[record['record_id']] = item
        if (not item['same_D_input'] or item['same_DP_tolerance_work_m'] != 5
                or item['engineering'] != 'VERIFIED'
                or item['strict_margin_work_m'] <= item['allowed_numeric_margin_work_m']
                or max(item['P_immediate_max_before_work_m_Decimal'], item['P_immediate_max_after_work_m_Decimal']) > 5):
            raise ValueError('FAILURE_EXPLANATION_NO_LONGER_SUPPORTED')
        vals = lambda *keys: value('failures', 'records', ri, 'stage_pair_diagnoses', di, *keys)
        transition = lambda key: str(vals(key, 'before')) + r'$\to$' + str(vals(key, 'after'))
        error = format(vals('common_max_before_work_m_Decimal'), '.4f') + r'$\to$' + format(vals('candidate_max_on_same_raw_set_work_m_Decimal'), '.4f')
        failure_rows.append(' & '.join([value('failures', 'records', ri, 'record_id'),
                                         integer('failures', 'records', ri, 'raw_points'),
                                         transition('D_before_after'), transition('P_before_after'),
                                         error, '共同几何保护退化']) + r' \\')
    failure_rows.append(r'\bottomrule\end{tabularx}\end{table}')
    case = selected_diagnoses['9311']
    if (case['P_before_after']['original_indices_no_longer_retained'] != [27]
            or case['P_before_after']['newly_retained_original_indices'] != [22]):
        raise ValueError('SPECIFIC_INDEX_EXPLANATION_REQUIRES_REVIEW')

    exp = r'''% Completed selection; never a final-test tuning decision.
\subsection{选择集上的保护失败使开发组合退出}
R0、S0、G0、\texttt{S0\_G0} 四个完整策略先于选择结果冻结，再处理全部 __N__ 条、__POINTS__ 个原始点。该集合由保留区事先抽取，使用既有描述性分层、稳定哈希和独立 salt；它用于选择，不能与最终确认混为一谈。按冻结顺序从 R0 开始，S0 在全部记录保护通过，__GAIN__ 条严格增加共同覆盖，共增加 __DELTA__ 点，因此成为确认主候选。

__TABLE__

开发中支持的 \texttt{S0\_G0} 在选择集的 __BAD__ 三条记录上出现真实几何退化。虽然它相对 S0 有 __SG_GAIN__ 条严格几何改善、总体多保留 __SG_EXTRA__ 点，预先固定的“全部记录保护”条件仍不成立。G0 也在同三条记录失败；系统保留 S0，没有改分组、改容差、删除难例或在已暴露选择集上开发新规则。

__FAIL_TABLE__

独立 C 对三个失败记录的四个冻结策略逐一重算，共 12 份 Decimal/PROJ 核验。每个比较的 D 输入相同，较宽方向阈值保留更多点，随后相同 DP 5 在改变后的完整输入上重算，实际替换了部分保留索引。例如记录 9311 原保留索引 27 被删除而索引 22 新增，P 输出点数仍为 10；同集合最大误差却从 __CASE_BEFORE__ 增至 __CASE_AFTER__ 工作米。两边的 P 即时误差都不超过 5，因此没有违反 DP 的自身定义，但已违反发布候选要求的共同原始几何非退化。

这是合法执行后的方法权衡，不是要修到胜出的工程错误。开发支持只在当时范围内成立；本次按规则去掉未通过保护的 G0 部分，使进入最终确认的方案更简单。在选择完成时，S0 尚须与预设参考 R0 在一次性最终确认中核对；本节没有利用最终集选赢家，也没有把 S0 的历史候选身份倒写成预设答案。
'''
    tokens = {'__N__': n, '__POINTS__': metric('R0', 'n_input'),
              '__GAIN__': integer('manifest', 'comparisons', 'S0|R0', 'strict_gain_records'),
              '__DELTA__': integer('manifest', 'comparisons', 'S0|R0', 'coverage_delta'),
              '__TABLE__': '\n'.join(rows), '__BAD__': '、'.join(bad_ids),
              '__SG_GAIN__': integer('manifest', 'comparisons', 'S0_G0|S0', 'strict_gain_records'),
              '__SG_EXTRA__': integer('manifest', 'comparisons', 'S0_G0|S0', 'final_point_delta'),
              '__FAIL_TABLE__': '\n'.join(failure_rows),
              '__CASE_BEFORE__': format(case['common_max_before_work_m_Decimal'], '.6f'),
              '__CASE_AFTER__': format(case['candidate_max_on_same_raw_set_work_m_Decimal'], '.6f')}
    process = r'''% Selection decision belongs in Part II, distinct from engineering repair.
\subsection{选择阶段：开发中有支持的组件仍可退出}
冻结四个短名单策略后，真实选择集的 __N__ 条记录改变了后续决定。S0 的全部保护通过，并在 __GAIN__ 条增加共同覆盖；G0 与 \texttt{S0\_G0} 则在 __BAD__ 三条记录发生共同几何保护退化。即使组合另有 __SG_GAIN__ 条改善，冻结规则仍要求所有保护通过，所以保留 S0 进入最终确认，开发阶段的组合没有继续发布。

主线程要求 C 把全部三个失败逐条核清。独立重算发现，宽方向阈值改变 DP 的实际输入与保留索引，同为 DP 5 并不保证共同原始最大误差单调变小。这属于真实权衡，处理实现没有错误。工程队没有把负结果登记为待修算法，也没有改参数把失败“修成通过”；当场接受更简单的已保护方案。

这段经历说明独立保留数据改变了决定。最初保留 S0、开发中接受组合、选择时退回 S0，都是实际发生的规则内裁决，而非事后把 S0 描述为从一开始就确定的赢家。在当时的选择阶段，最终确认仍是后续独立门控，选择通过不等同最终通过。
'''
    for key, replacement in tokens.items():
        exp = exp.replace(key, replacement)
        process = process.replace(key, replacement)
    if '__' in exp or '__' in process:
        raise ValueError('UNRESOLVED_SELECTION_REPORT_FIELD')
    outputs = {REPORTS/'experiment1/selection_generated.tex': exp,
               REPORTS/'process1/selection_generated.tex': process}
    for path, text in outputs.items():
        path.write_text(text)
    receipt = {'at_utc': datetime.now(timezone.utc).isoformat(), 'stage': 'VERIFIED_SELECTION_ONLY',
               'source_sha256': sha(Path(__file__)), 'source_aliases': aliases,
               'source_bindings': sources, 'generated_values': values,
               'outputs': {str(p.relative_to(ROOT)): sha(p) for p in outputs},
               'final_confirm_effects_read': False, 'new_model_calls': 0, 'new_method_runs': 0,
               'status': 'GENERATED_PENDING_INDEPENDENT_DOCUMENT_REVIEW'}
    (EV/'report_build/goal3_selection_bindings.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'status': 'GENERATED_BOUND_SELECTION_CHAPTERS', 'sources': len(sources),
                      'value_reads': len(values), 'final_confirm_effects_read': False}))


if __name__ == '__main__':
    main()
