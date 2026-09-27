"""Generate verified confirmation, native-event boundaries and optional full output.

Full production text is admitted only when the independently verified reporting
summary and all formal figures exist. Missing production is not replaced by zero.
"""
from collections import defaultdict
from datetime import datetime, timezone
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'task1/reports'
EV = ROOT / 'task1/evidence/goal3'
sys.path.insert(0, str(ROOT))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tex(value):
    return str(value).replace('_', r'\_').replace('%', r'\%').replace('&', r'\&')


def number(value):
    if not isinstance(value, int):
        raise ValueError('INTEGER_REPORT_VALUE_REQUIRED')
    return format(value, ',')


def figure(name, caption, width='.98'):
    return (r'\begin{figure}[H]\centering\includegraphics[width=' + width
            + r'\linewidth]{../../figures/goal3/' + name + '.pdf}\n'
            + r'\caption{' + caption + r'}\end{figure}' + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scope', choices=['auto', 'confirmation', 'full'], default='auto')
    args = parser.parse_args()
    full = args.scope == 'full' or (args.scope == 'auto' and (EV/'result_summary.json').exists())
    sources, aliases, docs, values = {}, {}, {}, []

    def read(alias, path):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT/path
        data = path.read_bytes()
        rel = str(path.relative_to(ROOT))
        sources[rel] = hashlib.sha256(data).hexdigest()
        aliases[alias] = rel
        docs[alias] = json.loads(data)
        return docs[alias]

    def verify(mapping):
        for relative, expected in mapping.items():
            if sha(ROOT/relative) != expected:
                raise ValueError('FINAL_REPORT_BINDING_MISMATCH:' + relative)
            sources[relative] = expected

    def value(alias, *keys):
        result = docs[alias]
        for key in keys:
            result = result[key]
        values.append({'source': alias, 'keys': list(keys), 'value': result})
        return result

    def independent(alias, path):
        receipt = read(alias, path)
        if receipt['status'] != 'VERIFIED' or receipt.get('errors'):
            raise ValueError('INDEPENDENT_REPORT_CLOSURE_REQUIRED:' + str(path))
        verify({row['path']: row['sha256'] for row in receipt['targets']})
        return {row['path'] for row in receipt['targets']}

    targets = independent('C_confirmation', EV/'independent_c/confirmation_closure_receipt.json')
    release = read('release', EV/'release_decision.json')
    freeze = read('final_freeze', EV/'final_freeze.json')
    split = read('split', EV/'split_manifest.json')
    base = EV/'runs'/release['run_id']
    manifest = read('confirmation', base/'manifest.json')
    if not {aliases['release'], aliases['confirmation']} <= targets:
        raise ValueError('CONFIRMATION_TARGET_NOT_REVIEWED')
    verify(release['bindings']); verify(freeze['bindings']); verify(manifest['bindings'])
    primary = freeze['primary_strategy']
    pair_key = primary+'|R0'
    pair = manifest['comparisons'][pair_key]
    if (manifest['partition'] != 'FINAL_CONFIRM' or manifest['status'] != 'MACHINE_VERIFIED_PENDING_C'
            or manifest['failed_records'] or manifest['input_ids'] != manifest['completed_record_ids']
            or manifest['input_ids'] != freeze['input_ids']
            or manifest['input_ids'] != split['partitions']['FINAL_CONFIRM']
            or manifest['strategy_ids'] != freeze['strategy_ids']
            or release['trigger'] != pair or release['retuning_or_new_winner_selection_on_final']
            or freeze['final_results_read_before_freeze'] or not freeze['no_final_parameter_selection']
            or not (freeze['frozen_at'] < manifest['started_at'] < manifest['ended_at'] < release['at'])):
        raise ValueError('CONFIRMATION_PROTOCOL_IDENTITY_MISMATCH')
    if primary != 'S0' or release['final_strategy'] != 'S0' or not pair['all_guards_pass'] or not pair['replacement_supported']:
        raise ValueError('CURRENT_CONFIRMATION_NARRATIVE_REQUIRES_REVIEW')

    # Reduce the actual C-bound per-record outputs; do not trust a free-standing
    # hand-edited stratum CSV or replace null geometric values by zero.
    strata, observed, comparable, geometric_gain = defaultdict(lambda: {'n': 0, 'protected': 0, 'gain': 0, 'coverage': 0}), [], 0, 0
    additions, added_error = 0, 0.0
    for shard in manifest['shards']:
        path = base/shard['path']; rel = str(path.relative_to(ROOT))
        verify({rel: shard['sha256']})
        ids = []
        with gzip.open(path, 'rt', encoding='utf8') as stream:
            for line in stream:
                row = json.loads(line); ids.append(row['record_id']); p = row['comparisons'][pair_key]
                item = strata[p['stratum']]
                item['n'] += 1; item['protected'] += p['feasible']; item['gain'] += p['feasible'] and p['strict_gain']
                item['coverage'] += p['coverage_delta']
                if p['baseline_common_max'] is not None and p['candidate_max_on_baseline_covered'] is not None:
                    comparable += 1
                    geometric_gain += p['candidate_max_on_baseline_covered'] < p['baseline_common_max']-p['numerical_allowance']
                additions += p['newly_covered_count']; added_error += p['newly_covered_error_sum']
        if ids != shard['input_ids']:
            raise ValueError('CONFIRMATION_SHARD_SCOPE_MISMATCH')
        observed += ids
    if (observed != manifest['input_ids'] or sum(v['gain'] for v in strata.values()) != pair['strict_gain_records']
            or sum(v['protected'] for v in strata.values()) != pair['protected_records']
            or sum(v['coverage'] for v in strata.values()) != pair['coverage_delta']
            or additions != pair['coverage_delta']):
        raise ValueError('CONFIRMATION_REPORT_REDUCTION_MISMATCH')
    n = number(value('confirmation', 'record_metrics', 'R0', 'n_records'))
    metric = lambda cid, key: value('confirmation', 'record_metrics', cid, key)
    rows = [r'\begin{table}[H]\centering\small',
            r'\caption{一次性最终确认的完整输入、互斥点终态与共同覆盖。各终态之和等于原始点数；覆盖不是存储点数。}',
            r'\begin{tabularx}{\linewidth}{@{}Yrr@{}}\toprule 读数 & R0 & S0 \\ \midrule']
    for title, key in [('原始记录','n_records'), ('原始点','n_input'), ('S 过滤点','n_filtered'),
                       ('D 删除点','n_direction_removed'), ('P 精简点','n_dp_removed'),
                       ('显式保留点','n_final'), ('共同覆盖原始点','common_covered_points'),
                       ('覆盖原始窗口','raw_windows_covered'), ('无输出记录','n_no_output_records'),
                       ('跨原始断点边','raw_break_crossings')]:
        rows.append(title+' & '+number(metric('R0',key))+' & '+number(metric('S0',key))+r' \\')
    rows.append(r'\bottomrule\end{tabularx}\end{table}')
    strat_rows = [r'\begin{table}[H]\centering\small',
                  r'\caption{最终确认的实际描述性分层。全部记录入分母，层样本不均；小层不单独支持总体推断。}',
                  r'\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule 原始诊断层 & 记录 & 保护通过 & 严格改善 & 新增覆盖点 \\ \midrule']
    for key, item in sorted(strata.items()):
        if item['n'] != split['stratum_distributions']['FINAL_CONFIRM'][key]:
            raise ValueError('FROZEN_STRATUM_DISTRIBUTION_MISMATCH')
        strat_rows.append(tex(key)+' & '+' & '.join(number(item[k]) for k in ['n','protected','gain','coverage'])+r' \\')
    strat_rows.append(r'\bottomrule\end{tabularx}\end{table}')
    frozen_time = freeze['frozen_at'].replace('T',' ').replace('+00:00',' UTC')
    params = freeze['strategies']['S0']['parameters']
    if params != {'dt':30,'distance':400,'min_points':2,'min_length':0,'direction':35,'dp':5}:
        raise ValueError('CONFIRMED_PARAMETER_PROSE_MISMATCH')
    confirmation = r'''% Actual independent confirmation after strategy/rule freeze.
\subsection{先冻结，再执行一次性最终确认}
数据划分先于本轮方法比较保存，seed 固定为 __SEED__。完整相同原始记录按同一组处理，未发现完全重复组；没有可信的更高层用户或行程关联，因此推断单位仍是记录。开发区使用已经暴露的历史记录，选择区按既有描述性分层抽取；最终确认从剩余完整组的单一池按独立 salt 稳定等概率抽取，不设分层配额。此前存在全量原始结构盘点，故这里只称“没有已记录的方法效果暴露”，不称从未接触原始数据。

确认样本预先固定为 __N__ 条，实际含 __POINTS__ 点。主候选 S0、参考及失败回退 R0、工作坐标、代码、指标和发布规则于 __FREEZE_TIME__ 冻结；冻结文件 SHA256 前缀为 \texttt{__FREEZE_HASH__}，处理代码为 \texttt{__CODE__}。只有全部保护通过并出现登记的严格改善才支持 S0，否则使用预设 R0；不在确认集上调参或生成新规则。

\begin{finding}
完整确认集上，S0 的 __N__ 条保护全部通过；__GAINS__ 条获得严格覆盖改善，新增共同覆盖 __COVER_DELTA__ 点，显式存储点增加 __STORED_DELTA__。原有覆盖身份和窗口未丢失，跨原始断点为 0。发布门控据此支持 S0，预设 R0 回退未触发。
\end{finding}
__SUMMARY_TABLE__

几何可比较的 __COMPARABLE__ 条记录没有严格几何改善；其余 __NULL__ 条因 R0 无覆盖而不能用于几何改善判断，但继续计入覆盖和保护分母。两方案的最大 P 即时误差均为 __PMAX__ 工作米，共同原始最大误差均为 __RAWMAX__ 工作米。新增覆盖点的最大 raw-to-final 偏差为 __NEWMAX__ 工作米，再次说明 P 的 5 工作米即时约束不覆盖 D 之前的所有原始点。提高覆盖没有证明新增点干净。

__STRATA_TABLE__
层名称沿用原始 ENU 包围盒对角线三分位 LOW/MID/HIGH；T 表示是否存在 $\Delta t\le0$ 或 $\Delta t>30$，D 表示是否存在相邻坐标完全重复。最终集的实际分布由抽样实现，未为结果重新平衡。只有极少记录的层保留在表中，不据此宣称稳定的层间差异；没有独立用户/行程假设，也不把记录级支持外推为普遍清洗准确率。

冻结后真实完成 __EVALUATIONS__ 次记录--策略处理，新增记录级模型调用为 0。完整逐记录配对、原始分区和冻结哈希保存在工程中。确认的结论是 \texttt{SUPPORTED\_WITHIN\_SCOPE}；S0 的方案仍为 S--D--P，$(30,400,2,0,35,5)$，使用统一确定性参数，不保留 G0 分组或新增在线模型依赖。
'''
    replacements = {'__SEED__':number(value('split','seed')), '__N__':n, '__POINTS__':number(metric('R0','n_input')),
        '__FREEZE_TIME__':frozen_time, '__FREEZE_HASH__':sources[aliases['final_freeze']][:16], '__CODE__':freeze['processing_code_sha'][:12],
        '__GAINS__':number(value('confirmation','comparisons',pair_key,'strict_gain_records')),
        '__COVER_DELTA__':number(value('confirmation','comparisons',pair_key,'coverage_delta')),
        '__STORED_DELTA__':number(value('confirmation','comparisons',pair_key,'final_point_delta')),
        '__SUMMARY_TABLE__':'\n'.join(rows), '__COMPARABLE__':number(comparable), '__NULL__':number(len(observed)-comparable),
        '__PMAX__':format(metric('S0','dp_max_error'),'.6f'), '__RAWMAX__':format(metric('S0','common_max_error'),'.6f'),
        '__NEWMAX__':format(value('confirmation','comparisons',pair_key,'new_coverage_max_error'),'.6f'),
        '__STRATA_TABLE__':'\n'.join(strat_rows), '__EVALUATIONS__':number(value('confirmation','processing_evaluations'))}
    if geometric_gain != 0 or metric('R0','dp_max_error') != metric('S0','dp_max_error') or metric('R0','common_max_error') != metric('S0','common_max_error'):
        raise ValueError('GEOMETRY_COMPARISON_PROSE_REQUIRES_REVIEW')
    for token, text in replacements.items():
        confirmation = confirmation.replace(token,text)
    process_confirmation = r'''\subsection{最终确认：执行预设门控，不再选参数}
选择之后先冻结 S0 与 R0，再执行预先保留的 __N__ 条记录。全部保护通过，__GAINS__ 条获得严格覆盖改善，R0 的预设失败回退没有触发，系统依既定规则继续使用 S0。这个结论来自实际一次性确认；没有根据确认反馈重新分组、换参数或写入记忆。

两方案的几何可比记录没有严格几何改善，支持来自覆盖恢复。报告因此只保留范围内覆盖支持，不把“最后通过”改写成噪声识别正确或全局最优。技术范围与剩余身份/互动证据缺项分别登记；确认通过也不会替 Evidence Master 锁定证据，或替用户宣布理解与最终提交通过。
'''
    for token,text in replacements.items():
        process_confirmation = process_confirmation.replace(token,text)

    governance = read('governance', EV/'governance_report_snapshot.json')
    governance_receipt = read('governance_snapshot_receipt', EV/'governance_report_snapshot_receipt.json')
    if (governance_receipt['snapshot'] != aliases['governance']
            or governance_receipt['snapshot_sha256'] != sources[aliases['governance']]
            or governance_receipt['cutoff'] != governance['cutoff']
            or governance_receipt['events'] != len(governance['events'])):
        raise ValueError('GOVERNANCE_REPORT_SNAPSHOT_MISMATCH')
    dispatch = sum(governance['counts'].get(key,0) for key in ('spawn_agent','followup_task','send_message'))
    governance_text = r'''\subsection{Native 协作证据只按实际可读范围保存}
本轮原生子代理实际参与 A 提案、B 执行与交付、C 独立核验。仅从当前任务 session 导出的工具事件快照截至 __CUTOFF__，包含 __EVENTS__ 个事件、__DISPATCH__ 次派发或通信调用；后者含 __SPAWN__ 次 spawn、__FOLLOWUP__ 次 followup 和 __SEND__ 次 send。这些是工具事件数量，不是底层模型请求数，也不是独立实验次数。本报告绑定此固定时点快照，后续交付与审核事件另存于持续更新的事件索引，不倒写本报告当时的读数。

本地 native message 字段以平台加密值保存，未取得可读逐字原文。工程只导出时间、工具、call ID、可见角色元数据与加密载荷哈希，移除密文正文；没有解密或重建消息。这些哈希不是已知明文的哈希。可读决定另由真实 TaskPlan、执行产物和 C 回执提供，不能称已恢复完整 native 逐字对话。G2 保存的真实 Provider response 与 G1 用户授权原话有各自原始来源，不受这个限制替代或扩充。底层请求和费用仍未知。
'''
    gov_values = {'__CUTOFF__':governance['cutoff'].replace('T',' ').replace('Z',' UTC'),
                  '__EVENTS__':number(len(governance['events'])), '__DISPATCH__':number(dispatch),
                  '__SPAWN__':number(governance['counts'].get('spawn_agent',0)),
                  '__FOLLOWUP__':number(governance['counts'].get('followup_task',0)),
                  '__SEND__':number(governance['counts'].get('send_message',0))}
    for token,text in gov_values.items():
        governance_text = governance_text.replace(token,text)

    outputs = {REPORTS/'experiment1/confirmation_generated.tex':confirmation,
               REPORTS/'process1/confirmation_generated.tex':process_confirmation,
               REPORTS/'process1/governance_generated.tex':governance_text}
    full_receipt = None
    if full:
        # The root REPORT_BUILD entry also checks this gate. Keeping the report
        # gate here prevents a direct LaTeX build from accepting an unchecked run.
        from task1.goal3.freezes import verified_task
        production_receipt = verified_task('production')
        independent('C_production', production_receipt)
        summary = read('result_summary', EV/'result_summary.json')
        verify(summary['source_bindings'])
        current = read('current_runs', EV/'current_runs.json')
        full_manifest = read('production', EV/'runs'/current['production']/'manifest.json')
        production_freeze = read('production_freeze', EV/'production_freeze.json')
        verify(production_freeze['bindings'])
        final = summary['final_strategy']
        if (full_manifest['status'] != 'MACHINE_VERIFIED_PENDING_C' or full_manifest['failed_records']
                or full_manifest['input_ids'] != full_manifest['completed_record_ids']
                or full_manifest['record_metrics'] != summary['production']['summaries']
                or final != release['final_strategy'] or final != current['final_strategy']
                or summary['data']['records'] != split['raw_records']
                or summary['data']['points'] != split['raw_points']
                or summary['production']['records_attempted'] != summary['data']['records']
                or summary['production']['records_with_terminal_state'] != summary['data']['records']
                or summary['production']['processing_failures']):
            raise ValueError('FULL_REPORT_SCOPE_OR_DEPLOYMENT_MISMATCH')
        fig_manifest = read('figure_manifest', ROOT/'task1/figures/goal3/figure_manifest.json')
        verify(fig_manifest['sources'])
        figure_data = ROOT/'task1/figures/goal3/figure_data.json'
        verify({str(figure_data.relative_to(ROOT)):fig_manifest['figure_data_sha256']})
        expected = {'development_candidates','selection_tradeoffs','point_fates_and_coverage','final_confirmation_pairs',
                    'production_trajectory_cases','goal3_actual_workflow','incumbent_decision_path'}
        if {f['name'] for f in fig_manifest['figures']} != expected:
            raise ValueError('ALL_SEVEN_FORMAL_FIGURES_REQUIRED')
        for item in fig_manifest['figures']:
            for fmt in item['formats'].values():
                verify({'task1/figures/goal3/'+fmt['file']:fmt['sha256']})
        metrics = full_manifest['record_metrics']; deployed = metrics[final]
        production_rows = [r'\begin{table}[H]\centering\small',r'\caption{全部原始记录的生产终态。分母包含开发、选择、确认和其余记录；同一输入的参考与发布策略分别处理。}',
                           r'\begin{tabularx}{\linewidth}{@{}Yrr@{}}\toprule 读数 & R0 & '+tex(final)+r' \\ \midrule']
        for title,key in [('原始记录','n_records'),('原始点','n_input'),('S 过滤点','n_filtered'),('D 删除点','n_direction_removed'),
                          ('P 精简点','n_dp_removed'),('显式保留点','n_final'),('共同覆盖原始点','common_covered_points'),
                          ('覆盖原始窗口','raw_windows_covered'),('无输出记录','n_no_output_records'),('跨原始断点边','raw_break_crossings')]:
            production_rows.append(title+' & '+number(metrics['R0'][key])+' & '+number(deployed[key])+r' \\')
        production_rows.append(r'\bottomrule\end{tabularx}\end{table}')
        for m in metrics.values():
            if sum(m[k] for k in ['n_filtered','n_direction_removed','n_dp_removed','n_final']) != m['n_input']:
                raise ValueError('FULL_POINT_FATE_DENOMINATOR_MISMATCH')
        c = summary['coordinate_check']; ext = c['extrema']; counts = c['counts']
        if c['implementation_status'] != 'VERIFIED' or counts['points_checked'] != summary['data']['points'] or counts['records_checked'] != summary['data']['records']:
            raise ValueError('FULL_COORDINATE_SCOPE_MISMATCH')
        independent('C_categories', EV/'independent_c'/(full_manifest['run_id']+'_categories_receipt.json'))
        independent('C_coordinates', EV/'independent_c'/(full_manifest['run_id']+'_coordinates_receipt.json'))
        categories, coordinates_c = docs['C_categories'], docs['C_coordinates']
        if categories['whole_dataset_records_categorized'] != summary['data']['records']:
            raise ValueError('FULL_CATEGORY_SCOPE_MISMATCH')
        differences = c['difference_counts']
        difference_note = ('登记的替代模型阶段检查未观察到动作差异。' if not sum(differences.values()) else
                           '替代模型出现 '+number(sum(differences.values()))+' 项阈值或保留索引差异，完整对象保留在敏感性记录中；这些差异不被隐藏，也不用于按效果重新选择坐标模型。')
        production = r'\subsection{冻结策略下的全部原始记录生产}'+'\n'
        production += ('全量实际尝试并形成终态 '+number(summary['data']['records'])+' 条、'+number(summary['data']['points'])+' 点，处理失败 '+number(len(summary['production']['processing_failures']))+' 条。所有分区都包含在生产中；这些汇总描述本数据集输出，不是新的独立最终测试。发布策略为 '+tex(final)+'，运行不需要逐记录模型或在线记忆，未加入逐记录候选拒绝后回退机制。原坐标、时间和记录身份保持可追踪。\n\n')
        production += '\n'.join(production_rows)+'\n\n'
        production += ('全部点以互斥终态记账，共同覆盖另算。发布策略的最大 P 即时误差为 '+format(deployed['dp_max_error'],'.6f')+' 工作米；共同 raw-to-final 最大误差为 '+format(deployed['common_max_error'],'.6f')+' 工作米，两者参考集合不同。未因合法空输出而删去原始记录，也未将参考空记录记作处理异常。\n\n')
        boundary_path = EV/'independent_c/new_coverage_boundary_receipt.json'
        independent('C_new_coverage_boundary', boundary_path)
        boundary = docs['C_new_coverage_boundary']; witness = boundary['witness']
        additional_pair = summary['production']['final_vs_R0']
        original_index = witness['original_index']
        segment = next(s for s in witness['final_S_output_original_indices'] if original_index in s)
        immediate = next(s for s in witness['final_P_input_original_indices'] if segment[0] in s)
        final_segment = next(s for s in witness['final_P_output_original_indices'] if segment[0] in s)
        if (boundary['whole_dataset_records_enumerated'] != summary['data']['records']
                or boundary['added_covered_original_points'] != additional_pair['coverage_delta']
                or witness['maximum_new_raw_to_final_error_work_m'] != additional_pair['new_coverage_max_error']
                or witness['maximum_new_raw_to_final_error_work_m'] != witness['independent_Decimal_same_point_error_work_m']
                or witness['R0_point_action']['reasons'] != ['TOO_FEW_POINTS']
                or witness['final_point_action']['reasons'] != ['DIRECTION_RULE']
                or immediate != final_segment or original_index in immediate
                or boundary['methods_or_parameters_changed']):
            raise ValueError('NEW_COVERAGE_WITNESS_NARRATIVE_MISMATCH')
        values.append({'source':'C_new_coverage_boundary','keys':['witness'],'value':witness})
        values.append({'source':'result_summary','keys':['production','final_vs_R0'],'value':additional_pair})
        attribution_path = EV/'full_filter_attribution.json'
        attribution_targets = independent('C_filter_attribution', EV/'independent_c/full_filter_attribution_receipt.json')
        attribution = read('filter_attribution', attribution_path)
        verify(attribution['source_bindings'])
        reasons = attribution['mutually_exclusive_reference_reason_counts']
        fates = attribution['new_point_final_ledger_actions']
        if (str(attribution_path.relative_to(ROOT)) not in attribution_targets
                or attribution['records'] != summary['data']['records']
                or attribution['newly_covered_points'] != additional_pair['coverage_delta']
                or sum(reasons.values()) != attribution['newly_covered_points']
                or sum(fates.values()) != attribution['newly_covered_points']
                or reasons != docs['C_filter_attribution']['mutually_exclusive_reference_reason_counts']
                or fates != docs['C_filter_attribution']['new_point_final_ledger_actions']
                or attribution['method_or_parameter_change']
                or attribution['legacy_analysis_field']['historical_artifacts_rewritten']):
            raise ValueError('FILTER_ATTRIBUTION_REPORT_BINDING_MISMATCH')
        values.append({'source':'filter_attribution','keys':['mutually_exclusive_reference_reason_counts'],'value':reasons})
        values.append({'source':'filter_attribution','keys':['new_point_final_ledger_actions'],'value':fates})
        production += (r'\subsection{新增覆盖的边界案例：不能解释为新增干净点}'+'\n'
            +'逐记录保护在全部 '+number(additional_pair['protected_records'])+' 条上满足，'+number(additional_pair['strict_gain_records'])+' 条严格改善，共同覆盖增加 '+number(additional_pair['coverage_delta'])+' 个原始身份。这个读数只说明固定定义下的覆盖恢复；全量新增覆盖最大偏差为 '+format(witness['maximum_new_raw_to_final_error_work_m'],'.6f')+' 工作米，明显大于确认样本中的新增覆盖最大值。\n\n'
            +'按 R0 的真实过滤原因，将新增覆盖互斥分解为：仅长度不足 '+number(reasons['TOO_SHORT_LENGTH'])+' 点、仅点数不足 '+number(reasons['TOO_FEW_POINTS'])+' 点、同时满足两项 '+number(reasons['TOO_FEW_POINTS+TOO_SHORT_LENGTH'])+' 点。这三项之和才是全部新增覆盖；不能把它们统一解释为长度小于 65。新增覆盖身份最终有 '+number(fates['retained'])+' 点被显式保留、'+number(fates['simplified'])+' 点由 P 精简、'+number(fates['denoised'])+' 点由 D 删除。后两类仍可能被最终折线的相邻保留索引夹持，所以共同覆盖增长远大于存储点增长。\n\n'
            +'实际最差点位于记录 '+tex(witness['record_id'])+' 的原始索引 '+str(original_index)+'。完整局部原始窗口为 '+tex(str(segment))+'，共 '+number(len(segment))+' 点；R0 因点数不足过滤该段，原因是 '+r'\texttt{TOO\_FEW\_POINTS}'+'，并非长度小于 65。S0 保留该段后，D 以方向规则删除索引 '+str(original_index)+'，P 的完整输入与输出同为 '+tex(str(immediate))+'，这个局部没有 P 删除。该原始点到最终夹持边 '+tex(str(witness['bracketing_final_original_indices']))+' 的偏差由独立 Decimal 原值重算确认；整条记录的 P 即时最大误差仍只有 '+format(witness['final_P_immediate_max_work_m'],'.6f')+' 工作米。\n\n'
            +'因此，新增覆盖不意味着新增点已被识别为干净，DP 自身的 5 工作米保证也没有覆盖此前被 D 删除的点。参考短段过滤条件是“点数不足或长度不足”的并集；开发中的观察不能替代全量过滤原因。本案例保留为发布局限，没有在看过全量之后更换策略或修改保护定义。\n\n')
        production += r'\subsection{扩大范围的工作坐标核验与限制}'+'\n'
        production += ('全部 '+number(counts['points_checked'])+' 点和 '+number(counts['records_checked'])+' 条记录完成指定 ENU 与独立 PROJ 路径核对，最大实现差为 '+r'\texttt{'+format(ext['PROJ_implementation_error_work_m']['value'],'.6g')+'} 工作米。原始相邻边 '+number(counts['raw_adjacent_edges'])+' 条全部核查；与同假设椭球测地距离的最大绝对差 '+format(ext['raw_adjacent_geod_absolute_difference_work_m']['value'],'.6f')+' 工作米，最大相对差 '+format(ext['raw_adjacent_geod_relative_difference']['value']*100,'.6f')+r'\%。'+'\n\n')
        production += ('实际处理的 S 邻边 '+number(counts['S_distance_edges'])+'、段长 '+number(counts['S_actual_segments_length'])+'、D 窗口 '+number(counts['D_windows'])+' 与 P 完整输入点 '+number(counts['P_complete_input_points'])+' 均进入登记的阈值/误差/保留集合敏感性核验。'+difference_note+'没有进行全域所有点的两两距离；公式核对和模型近似比较不能证明源 datum。\n\n')
        production += ('独立 C 对完整原始范围、身份、阶段操作、点账本和汇总逐记录核验；另外从预登记随机组与所有实际存在类别中抽取数学复算记录。随机部分 '+number(len(categories['random_records']))+' 条，加上每个类别至多两个完整组代表后共 '+number(categories['unique_math_records'])+' 条、'+number(categories['distinct_configuration_math_checks'])+' 份策略轨迹接受独立 Decimal/PROJ 重算。这是明确的数学抽查，不是所有同类记录都用第二套数学实现重跑。\n\n')
        production += ('替代坐标的独立阶段敏感性复算覆盖 '+number(len(coordinates_c['independent_sensitivity_record_ids']))+' 条、'+number(coordinates_c['independent_sensitivity_trace_checks'])+' 份策略轨迹，包含预登记随机/类别代表、全部已报告差异及极值记录。它在真实各阶段固定输入上比较动作；没有把这种检查写成另一坐标模型下的全链重跑，也没有声称全部未抽中记录的敏感性均被独立重算。\n\n')
        values.append({'source':'C_categories','keys':['unique_math_records'],'value':categories['unique_math_records']})
        values.append({'source':'C_coordinates','keys':['independent_sensitivity_trace_checks'],'value':coordinates_c['independent_sensitivity_trace_checks']})
        production += figure('point_fates_and_coverage','最终确认与全量生产的互斥点终态、共同覆盖和显式存储点，分别使用各自完整分母。')
        production += figure('production_trajectory_cases','同案例的原始、R0 与发布策略。前两行分别选取最大覆盖增益和最大原始几何误差的完整记录；第三行为新增覆盖最差点所在的四点局部窗口，图中显示点数不是整条记录的存储总数。粉红叉号表示 S 过滤，紫色加号表示 D 删除；蓝色与橙色折线分别表示 R0 与 S0 的存储输出。同一行原点与尺度一致，断段不重连，无道路底图。')
        cost_rows = [r'\begin{table}[H]\centering\small',
                     r'\caption{当前有效运行的计算账本。观察数可以复用相同配置或已经存在的真实产物，不等于实际重新处理次数。}',
                     r'\begin{tabularx}{\linewidth}{@{}Yrrrr@{\hspace{1.4em}}r@{}}\toprule 运行范围 & 实际处理 & 缓存复核 & 同配置复用 & 策略观察 & 秒 \\ \midrule']
        for scope, title in [('development','最终开发对照'),('selection','选择'),('confirmation','最终确认'),('production','全量生产')]:
            cost = summary['run_costs'][scope]
            if (cost['new_record_model_calls'] != 0 or cost['processing_evaluations']+cost['cached_trace_rechecks']
                    +cost['reused_identical_configuration_observations'] != cost['strategy_record_observations']):
                raise ValueError('CURRENT_RUN_COST_PROSE_MISMATCH')
            cost_rows.append(title+' & '+' & '.join(number(cost[k]) for k in ['processing_evaluations','cached_trace_rechecks',
                             'reused_identical_configuration_observations','strategy_record_observations'])
                             +' & '+format(cost['elapsed_seconds'],'.1f')+r' \\')
        cost_rows.append(r'\bottomrule\end{tabularx}\end{table}')
        production += (r'\subsection{执行成本与复现身份}'+'\n'+'\n'.join(cost_rows)+'\n\n'
            +'表中只列当前四个有效运行，不把早期开发、失效后重建、独立核验或 Notebook 离线复算的成本塞入同一分母。各次耗时包含其实际执行环境，不作为硬件无关基准。四次运行新增记录级模型调用均为 0；原生治理角色的工具事件另记，底层请求与费用未知。历史真实提议在默认离线复算中原样重用，不能计作新的 LIVE 提议。\n')
        outputs[REPORTS/'experiment1/production_generated.tex'] = production
        outputs[REPORTS/'process1/production_generated.tex'] = (r'\subsection{生产与交付继续按冻结策略执行}'+'\n'
            +'确认门控之后，全部 '+number(summary['data']['records'])+' 条记录实际处理并形成可追踪终态。生产沿用确认后的 '+tex(final)+'，没有根据全量效果临时增加组件、修改指标或补入逐记录回退。\n\n'
            +'全量输出还暴露了新增覆盖的边界：最差局部在 S0 中先通过点数过滤，再由 D 删除一个点，P 对剩余局部点没有再删除，但该原始点偏离最终线段 '+format(witness['maximum_new_raw_to_final_error_work_m'],'.2f')+' 工作米。C 从原值与实际动作独立核验后，正文保留这一局限；没有将它改称 DP 实现错误，也没有在确认后“修到更好”。进一步按原过滤原因核对，点数不足与长度不足是并集，新增覆盖与显式保留也是不同读数。\n\n'
            +'全量统计与独立确认分开；报告、Notebook、提交包和真实互动证据分别验收，不能用计算完成替代文档或外部证据闭合。\n')
        outputs[REPORTS/'experiment1/generated.tex'] = (r'\input{development_generated.tex}'+'\n'+figure('development_candidates','完整开发比较保留支持、无收益、权衡和约束拒绝；所有候选相对固定 R0。')
            +r'\input{selection_generated.tex}'+'\n'+figure('selection_tradeoffs','选择阶段所有实际几何保护失败均保留；其他记录上的改善不能抵消固定保护失败。')
            +r'\input{confirmation_generated.tex}'+'\n'+figure('final_confirmation_pairs','冻结后的全部确认配对与分层读数；缺失几何只从散点图剔除，仍计入完整分母。')+r'\input{production_generated.tex}'+'\n')
        outputs[REPORTS/'process1/generated.tex'] = (r'\input{development_generated.tex}'+'\n'+r'\input{selection_generated.tex}'+'\n'
            +r'\input{confirmation_generated.tex}'+'\n'+r'\input{production_generated.tex}'+'\n'
            +figure('incumbent_decision_path','实际规则内方法决定的路径。它是实验决策记录，不是重建的用户对话或已锁定的 Human Judgment 证据。'))
        outputs[REPORTS/'process1/workflow_figure_generated.tex'] = figure('goal3_actual_workflow','本轮实际 A/B/C、确定性控制器、修复返回与外部依赖。角色事件与产物有真实记录；图不代替互动原图或 Evidence Lock。')
        full_receipt = {'final_strategy':final,'raw_records':summary['data']['records'],'raw_points':summary['data']['points'],
                        'production_C_receipt':str(production_receipt.relative_to(ROOT)), 'formal_figures':sorted(expected)}
    else:
        outputs[REPORTS/'experiment1/generated.tex'] = (r'\input{development_generated.tex}'+'\n'+r'\input{selection_generated.tex}'+'\n'
            +r'\input{confirmation_generated.tex}'+'\n'+r'\begin{noteBox}全量生产尚未接入完整核验结果；不填写推测数值，不将确认样本冒称全量。\end{noteBox}'+'\n'
            +r'\subsection{全量生产与条件化坐标核验}'+'\n'+'待接入：全部原始记录与点的终态、完整扩大范围核验、正式图及全量独立 C 范围。\n')
        outputs[REPORTS/'process1/generated.tex'] = (r'\input{development_generated.tex}'+'\n'+r'\input{selection_generated.tex}'+'\n'
            +r'\input{confirmation_generated.tex}'+'\n'+r'\begin{decisionbox}全量处理与正式交付待完整核验产物接入。确认通过不会自动关闭报告、复现、身份与互动证据缺项。\end{decisionbox}'+'\n')
        outputs[REPORTS/'process1/workflow_figure_generated.tex'] = '% Actual formal system figure awaits complete production reporting inputs.\n'
    outputs[REPORTS/'experiment1/conclusion_generated.tex'] = ('G3 开发曾支持加入时间分组规则；选择记录中的真实几何退化使这项组件退出。S0 随后在全部 '+n+' 条最终确认记录上通过保护，并按预设发布门控保留。结论支持固定 S0 在本次条件化范围内恢复覆盖，不支持真实噪声准确率或普遍最优性。最终记录级策略采用确定性参数，实际 A/B/C 治理的作用体现于候选、拒绝、核验和修复，不等同记录级 LLM 带来的质量收益。\n')
    for path, content in outputs.items():
        if '__' in content:
            raise ValueError('UNRESOLVED_FINAL_REPORT_TOKEN:' + str(path))
        path.write_text(content)
    receipt = {'at_utc':datetime.now(timezone.utc).isoformat(), 'scope':'CONFIRMATION_AND_FULL' if full else 'CONFIRMATION_ONLY',
               'source_sha256':sha(Path(__file__)), 'source_aliases':aliases, 'source_bindings':sources,
               'generated_values':values, 'confirmation_actual_shard_reduction':{'records':len(observed),'comparable_geometry':comparable,
                   'strict_geometric_gain_records':geometric_gain,'strata':dict(strata),'new_covered_points':additions,
                   'new_covered_mean_error_work_m':added_error/additions if additions else None},
               'governance_snapshot':{'cutoff':governance['cutoff'],'events':len(governance['events']),'dispatches':dispatch,
                   'native_plaintext_available':False,'underlying_model_requests_and_cost':'UNKNOWN'},
               'outputs':{str(p.relative_to(ROOT)):sha(p) for p in outputs},'full':full_receipt,
               'new_model_calls':0,'new_method_runs':0,'status':'GENERATED_PENDING_INDEPENDENT_DOCUMENT_REVIEW'}
    (EV/'report_build/goal3_final_bindings.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'GENERATED_BOUND_FINAL_CHAPTERS','scope':receipt['scope'], 'sources':len(sources),
                      'confirmation_records':len(observed),'new_model_calls':0}))


if __name__ == '__main__':
    main()
