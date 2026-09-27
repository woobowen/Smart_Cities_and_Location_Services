"""Pre-method partitions and the user-authorized Goal 3 machine contract."""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib

from task1.workflow.g2_data import raw_data
from task1.workflow.io import ROOT, digest, object_hash, read_json, write_json, now

EV = ROOT / 'task1/evidence/goal3'
CFG = ROOT / 'task1/config/goal3'
G2 = ROOT / 'task1/evidence/goal2'
GOAL = 'SC-LAB1-G3-FINAL-001'
EXPLORATION_CONSTRAINTS = {
    'parameter_domain': 'registered G2 grids only; no continuous or six-factor exhaustive search',
    'raw_diagnostic_rule_max': 1, 'raw_diagnostic_groups_max': 3,
    'conservative_direction_protection_max': 1,
    'group_boundaries_and_parameters_fixed_on': 'G3_DEVELOPMENT only',
    'unknown_group_fallback': 'R0 or previously registered incumbent; exact choice fixed in strategy',
    'runtime_features': 'verified original diagnostics only, available at inference time',
    'forbidden': ['record_id answer routing', 'final labels or results in routing', 'new algorithm library',
                  'new training', 'smoothing', 'interpolation', 'time rewriting', 'external data',
                  'map matching', 'datum offset conversion', 'unverified physical speed limits',
                  'treating low displacement as measurement truth', 'coordinate choice by cleaning scores'],
    'final_pre_freeze_forbidden_contexts': ['A', 'memory', 'parameter_selection', 'mode_feedback', 'figure_preview'],
    'full_candidate_execution_requires_confirmation_completed': True}


def ranked(group, salt):
    return hashlib.sha256(('42|' + salt + '|' + group).encode()).hexdigest()


def grouped_take(groups, count, salt, strata=None):
    """Take whole groups; stratify only selection, never final confirmation."""
    buckets = defaultdict(list)
    for group, ids in groups.items():
        names = {strata[rid] for rid in ids} if strata is not None else {'ALL'}
        if len(names) != 1:
            raise ValueError('EXACT_GROUP_DESCRIPTIVE_STRATUM_MISMATCH')
        buckets[next(iter(names))].append(group)
    names = sorted(buckets)
    for name in names:
        buckets[name].sort(key=lambda g: (ranked(g, salt), g))
    quotas = {name: count // len(names) + (i < count % len(names))
              for i, name in enumerate(names)}
    selected, realized = [], Counter()
    for name in names:
        while buckets[name] and realized[name] < quotas[name]:
            group = buckets[name].pop(0)
            selected.extend(groups[group]); realized[name] += len(groups[group])
    while len(selected) < count and any(buckets.values()):
        for name in names:
            if buckets[name]:
                group = buckets[name].pop(0)
                selected.extend(groups[group]); realized[name] += len(groups[group])
            if len(selected) >= count:
                break
    if len(selected) < count:
        raise ValueError('INSUFFICIENT_COMPLETE_GROUPS')
    return selected, {'nominal_records': count, 'actual_records': len(selected),
                      'quota': quotas, 'realized': dict(realized), 'salt': salt}


def prepare():
    if (CFG / 'contract.json').exists() or (EV / 'split_manifest.json').exists():
        raise ValueError('ALREADY_PREPARED_NO_OVERWRITE')
    old_contract_path = ROOT / 'task1/config/goal2/contract.json'
    old = read_json(old_contract_path)
    old_split_path = G2 / 'data/split_manifest.json'
    old_split = read_json(old_split_path)
    diagnostics_path = G2 / 'data/raw_diagnostics.json'
    if digest(diagnostics_path) != old_split['diagnostics_sha256']:
        raise ValueError('G2_DESCRIPTIVE_DIAGNOSTICS_CHANGED')
    cards = read_json(diagnostics_path)
    raw = raw_data()
    membership, groups = {}, defaultdict(list)
    for rid, record in raw.items():
        content = object_hash(record)
        if cards[rid]['record_content_sha256'] != content:
            raise ValueError('G2_DIAGNOSTIC_RAW_IDENTITY_CHANGED')
        membership[rid] = content; groups[content].append(rid)
    original_membership = {rid: name for name, ids in old_split['splits'].items() for rid in ids}
    if set(original_membership) != set(raw) or sum(map(len, old_split['splits'].values())) != len(raw):
        raise ValueError('G2_PARTITION_INCOMPLETE_OR_OVERLAPPING')
    for ids in groups.values():
        if len({original_membership[rid] for rid in ids}) != 1:
            raise ValueError('INHERITED_ASSOCIATED_GROUP_SPLIT')
    reserved = set(old_split['splits']['G3_RESERVED'])
    available = {g: ids for g, ids in groups.items() if set(ids) <= reserved}
    strata = {rid: c['stratum'] for rid, c in cards.items()}
    selection, selection_info = grouped_take(available, 240, 'SC_LAB1_G3_SELECTION_V1', strata)
    available = {g: ids for g, ids in available.items() if not set(ids).intersection(selection)}
    final, final_info = grouped_take(available, 600, 'SC_LAB1_FINAL_CONFIRM_V1')
    remainder = sorted(reserved - set(selection) - set(final), key=lambda rid: (ranked(membership[rid], 'PRODUCTION'), rid))
    partitions = {
        'PILOT_REGRESSION': old_split['splits']['PILOT_REGRESSION'],
        'DEMO_MEMORY': old_split['splits']['DEMO_MEMORY'],
        'G3_DEVELOPMENT': old_split['splits']['DEVELOPMENT'] + old_split['splits']['G2_EVAL'],
        'G3_SELECTION': selection, 'FINAL_CONFIRM': final, 'PRODUCTION_REMAINDER': remainder}
    flat = [rid for ids in partitions.values() for rid in ids]
    if len(flat) != len(set(flat)) or set(flat) != set(raw):
        raise ValueError('G3_PARTITION_NOT_EXACT')
    split = {'goal_id': GOAL, 'frozen_at': now(), 'seed': 42,
             'raw_sha256': old['raw_sha256'], 'raw_records': len(raw),
             'raw_points': sum(len(r[0]) for r in raw.values()),
             'g2_split_sha256': digest(old_split_path), 'g2_diagnostics_sha256': digest(diagnostics_path),
             'g2_diagnostics_path': str(diagnostics_path.relative_to(ROOT)),
             'group_definition': 'SHA256 canonical complete raw record; no verified higher entity association',
             'group_count': len(groups), 'duplicate_groups': [ids for ids in groups.values() if len(ids) > 1],
             'group_for_record': membership, 'partitions': partitions,
             'selection_algorithm': 'equal extant descriptive strata, whole groups sorted SHA256(42|salt|group), shortage sorted-stratum cycling',
             'final_algorithm': 'all remaining complete groups in one pool, stable SHA256(42|salt|group) order; no stratified quotas',
             'allocation': {'G3_SELECTION': selection_info, 'FINAL_CONFIRM': final_info},
             'stratum_distributions': {p: dict(Counter(strata[rid] for rid in ids)) for p, ids in partitions.items()},
             'development_exposure': 'KNOWN_EXPOSED; inherited DEVELOPMENT and G2_EVAL now used as development; historical G2 identity unchanged',
             'reserved_exposure': 'NO_DOCUMENTED_METHOD_EXPOSURE; prior full-raw descriptive inventory disclosed',
             'inference_unit': 'record; not independently verified person or trip',
             'source_sha256': digest(__file__)}
    write_json(EV / 'split_manifest.json', split, exclusive=True)
    reference = deepcopy(old['reference_parameters'])
    memory_run = read_json(G2 / 'current_runs.json')['memory']
    memory_path = G2 / 'runs' / memory_run / 'memory_snapshot.json'
    contract = {
        'goal_id': GOAL, 'contract_id': 'G3_CONDITIONAL_ENU_V1', 'created_at': now(),
        'status': 'PREPARED_FOR_INDEPENDENT_C_REVIEW',
        'authority': {'type': 'CURRENT_DIRECT_USER_PROMPT', 'path': str((EV / 'USER_PROMPT.md').relative_to(ROOT)),
                      'sha256': digest(EV / 'USER_PROMPT.md'), 'internal_C_is_new_user_approval': False},
        'inherited_contract': {'path': str(old_contract_path.relative_to(ROOT)), 'sha256': digest(old_contract_path)},
        'split_sha256': digest(EV / 'split_manifest.json'),
        'raw_path': old['raw_path'], 'raw_sha256': old['raw_sha256'],
        'expected_raw_records': len(raw), 'expected_raw_points': split['raw_points'],
        **{key: deepcopy(old[key]) for key in ('model', 'units', 'source_crs', 'direction_method', 'stage_rules',
                                              'parameter_grids', 'numeric_audit', 'common_reference', 'metrics')},
        'reference_order': 'S-D-P',
        'references': {'R0': reference, 'S0': {**reference, 'min_points': 2, 'min_length': 0}},
        'budget': {'new_single_definitions_max': 8, 'combination_definitions_max': 12,
                   'enhancement_depth_max': 3, 'selection_shortlist_max': 4, 'final_comparison_max': 4,
                   'prior_configuration_recomputes_count_as_new': False},
        'exploration_constraints': EXPLORATION_CONSTRAINTS,
        'partitions': {'development': 'G3_DEVELOPMENT', 'selection': 'G3_SELECTION', 'confirmation': 'FINAL_CONFIRM',
                       'full_production': 'ALL_PARTITIONS', 'final_method_feedback_to_A_before_freeze': False,
                       'selection_requires_shortlist_freeze': True, 'confirmation_requires_method_and_code_freeze': True,
                       'selection_redevelopment_consumes_existing_budget': True},
        'selection': {
            'initial_incumbent': 'R0', 'predeclared_order': 'A registers before each development round; shortlist order fixed before selection',
            'fixed_and_incumbent_protection': True,
            'all_records_must_pass': True, 'integer_gain_minimum': 1,
            'SD_guards': old['selection']['CS_CD']['per_record_guards'],
            'SD_primary': old['selection']['CS_CD']['primary'],
            'P_guards': old['selection']['CP']['guards'],
            'P_complete_input_equality_required': True, 'P_same_upstream_dp5_parent_required': True,
            'P_shared_actual_error_budget_work_m': 5,
            'P_primary': 'fewer immediate P output points at exactly identical complete P input, actual error <=5',
            'null': 'cannot establish geometric improvement; report coverage gain separately',
            'all_pairwise_and_frontier_saved': True, 'weighted_quality_score': None,
            'incomparable': 'retain already protected incumbent; preserve tradeoffs',
            'equivalent': ['fewer enhancement modules', 'no added online model dependency', 'lower measured cost', 'canonical ID'],
            'new_coverage_reporting': ['identity_set', 'geometry_on_added_points', 'short_segments', 'near_stationary_descriptive_only'],
            'noise_accuracy_available': False},
        'release_gate': {'all_fixed_guards_pass': True, 'strict_predeclared_gain_required': True,
                         'on_no_support_or_tradeoff': 'R0', 'retune_on_confirmation': False,
                         'engineering_error': 'freeze affected runs; repair implementation; new code/run and disclose exposure',
                         'record_fallback': 'NONE_UNLESS_PART_OF_REGISTERED_COMPLETE_CANDIDATE_BEFORE_SHORTLIST'},
        'mode': {'default_candidate_mode': 'DETERMINISTIC_FIXED_OR_RAW_DIAGNOSTIC_RULE',
                 'new_record_level_model_dispatches': 0, 'new_mode_gain_claim': False,
                 'G2_four_modes': 'HISTORICAL_VERIFIED_INPUT; not Goal3 new LIVE',
                 'memory_path': str(memory_path.relative_to(ROOT)), 'memory_sha256': digest(memory_path),
                 'memory_access': 'FROZEN_READONLY; not used by deterministic record processing',
                 'new_provider_or_paid_service': False},
        'full_audit': {
            'all_records': ['raw_hash', 'identity_and_original_values', 'exact_scope', 'stage_and_final_indices',
                            'unique_point_terminal_ledger', 'summary_reduction', 'shard_hashes', 'frozen_parameters',
                            'actual_P_error_budget', 'original_break_crossings', 'machine_review_from_external_raw'],
            'coordinate': 'PROJ cart+topocentric for all points; raw adjacent Geod distances; actual stage thresholds and DP intervals under same-ellipsoid AEQD; no all-pairs requirement',
            'independent_math_sample': {'random_records': 40, 'salt': 'SC_LAB1_G3_C_RAW_RECHECK_V1',
                'random_algorithm': 'SHA256(42|salt|complete_raw_group_hash) ascending; whole groups',
                'categories': ['all_filtered_R0', 'no_output_final', 'fallback', 'failure', 'near_S_threshold',
                               'near_D_threshold', 'near_P_threshold', 'extreme_span', 'new_coverage', 'worst_common_error'],
                'category_selection': {'all_filtered_R0': 'stable random rank', 'no_output_final': 'stable random rank',
                    'fallback': 'stable random rank; all receipts additionally checked',
                    'failure': 'stable random rank; all receipts additionally checked',
                    'near_S_threshold': 'minimum absolute margin of actual adjacent distance to400 or segment length to active min_length, exact equality included; stable rank tie',
                    'near_D_threshold': 'minimum absolute margin of calculable actual direction differences to active threshold; stable rank tie',
                    'near_P_threshold': 'minimum absolute margin of actual interval residuals to5; stable rank tie',
                    'extreme_span': 'descending original ENU bbox diagonal; stable rank tie',
                    'new_coverage': 'descending added common raw point count; stable rank tie',
                    'worst_common_error': 'descending final common max over its covered points; null excluded with reason; stable rank tie'},
                'representatives_per_present_category': 2, 'all_failures_and_fallback_receipts': True,
                'category_representatives_not_all_category_records': True},
            'uncertainty': 'descriptive paired records and strata; no IID-person inference or true-noise accuracy'},
        'resources': {'record_tools': 'serial deterministic; preflight timings on development; bounded finite candidates',
                      'governance': 'native Codex A/B/C contexts, separate from tested modes',
                      'reserve': 'final confirmation + two full production strategies + full Notebook/isolated ZIP recomputation + report/C review',
                      'exact_hidden_requests_and_cost': 'unknown'},
        'external_statuses': {'GPT_SECOND_REVIEW': 'PENDING', 'Understanding': 'USER_DETERMINED',
                              'Submission': 'NOT_READY', 'Evidence_Lock': 'EVIDENCE_MASTER_ONLY'}
    }
    write_json(CFG / 'contract.json', contract, exclusive=True)
    return {'contract_sha256': digest(CFG / 'contract.json'), 'split_sha256': digest(EV / 'split_manifest.json'),
            'partition_counts': {p: len(ids) for p, ids in partitions.items()}}


if __name__ == '__main__':
    print(prepare())
