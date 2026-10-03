"""Small deterministic task/issue journal. Model role contexts are registered."""
from pathlib import Path
from task1.workflow.io import ROOT, now, digest, object_hash, read_json, write_json, bound_path
from .data import EV, GOAL

TASKS = {
    'handoff': [], 'contract_split': ['handoff'], 'implementation': ['contract_split'],
    'development': ['implementation'], 'selection_freeze': ['development'],
    'selection': ['selection_freeze'], 'final_freeze': ['selection'],
    'confirmation': ['final_freeze'], 'production': ['confirmation'],
    'figures': ['production'], 'notebooks': ['production'], 'experiment_report': ['figures'],
    'process_report': ['development'], 'handoffs': ['production'],
    'package': ['notebooks', 'experiment_report', 'process_report'],
    'internal_acceptance': ['figures', 'notebooks', 'experiment_report', 'process_report', 'handoffs', 'package'],
    'publication': ['internal_acceptance']}


class Journal:
    def __init__(self, directory=EV):
        self.directory = Path(directory)
        self.path = self.directory/'goal_state.json'
        self.state = read_json(self.path) if self.path.exists() else {
            'goal_id': GOAL, 'status': 'IMPLEMENTING', 'tasks': {
                name: {'status': 'PENDING', 'depends_on': deps, 'targets': []} for name, deps in TASKS.items()},
            'issues': {}, 'role_dispatches': [], 'events': [], 'inflight': None,
            'GPT_SECOND_REVIEW': 'PENDING', 'Submission': 'NOT_READY', 'Understanding': 'USER_DETERMINED'}
        if set(self.state['tasks']) != set(TASKS):
            raise ValueError('TASK_CHECKPOINT_MISMATCH')

    def event(self, kind, **fields):
        events = self.state['events']
        row = {'at': now(), 'kind': kind, 'previous_hash': events[-1]['hash'] if events else 'ROOT', **fields}
        row['hash'] = object_hash(row); events.append(row)
        write_json(self.path, self.state)

    def attach(self, path):
        path = Path(path).resolve()
        if not path.is_relative_to(ROOT) or path.is_symlink() or not path.is_file():
            raise ValueError('REAL_REPOSITORY_TARGET_REQUIRED')
        return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path)}

    def check(self, targets):
        for target in targets:
            if digest(bound_path(ROOT, target['path'])) != target['sha256']:
                raise ValueError('STALE_TARGET:' + target['path'])

    def register_role(self, role, context, task, source):
        if role not in ('A', 'B', 'C'):
            raise ValueError('UNREGISTERED_ROLE')
        self.state['role_dispatches'].append({'role': role, 'context': context, 'task': task,
                                             'source': source, 'requests_and_cost': 'unknown'})
        self.event('ACTUAL_NATIVE_ROLE_DISPATCH_RECORDED', role=role, context=context, task=task)

    def ready(self, task, allow_external=False):
        allowed = {'VERIFIED', 'BLOCKED_EXTERNAL'} if allow_external else {'VERIFIED'}
        return all(self.state['tasks'][dep]['status'] in allowed and self.current(self.state['tasks'][dep])
                   for dep in TASKS[task])

    def current(self, row):
        try:
            self.check(row.get('targets', []))
            if row.get('receipt'):
                self.check([row['receipt']])
            self.check([{'path': p, 'sha256': h} for p, h in row.get('source_hashes', {}).items()])
        except (OSError, ValueError):
            return False
        return True

    def submit(self, task, paths, sources, *, author='B:root'):
        if not self.ready(task, allow_external=task in ('package', 'internal_acceptance', 'publication')):
            raise ValueError('DEPENDENCY_NOT_CLOSED')
        targets = [self.attach(path) for path in paths]
        if not targets:
            raise ValueError('EMPTY_REVIEW_TARGETS')
        self.state['tasks'][task].update(status='REVIEW_PENDING', targets=targets, source_hashes=sources, author=author)
        self.event('TASK_SUBMITTED', task=task, targets=targets)

    def accept(self, task, receipt_path, verifier):
        receipt = read_json(receipt_path)
        row = self.state['tasks'][task]
        registered = {r['context'] for r in self.state['role_dispatches'] if r['role'] == 'C'}
        if verifier not in registered or verifier == row.get('author') or receipt.get('role_context') != verifier:
            raise ValueError('INDEPENDENT_REGISTERED_C_REQUIRED')
        part = receipt.get('tasks', {}).get(task, receipt)
        if not self.ready(task, allow_external=task in ('package', 'internal_acceptance', 'publication')):
            raise ValueError('DEPENDENCY_NO_LONGER_VERIFIED')
        if row['status'] != 'REVIEW_PENDING' or part.get('status') not in ('VERIFIED', 'BLOCKED_EXTERNAL'):
            raise ValueError('C_RECEIPT_NOT_ACCEPTABLE')
        if not part.get('checked_components') or part.get('source_hashes') != row['source_hashes']:
            raise ValueError('CHECKS_OR_SOURCE_BINDING_MISSING')
        self.check(row['targets']); self.check(part.get('targets', []))
        self.check([{'path': p, 'sha256': h} for p, h in row['source_hashes'].items()])
        if not set(map(object_hash, row['targets'])) <= set(map(object_hash, part.get('targets', []))):
            raise ValueError('ACTUAL_ARTIFACT_NOT_REVIEWED')
        if any(i['parent_task'] == task and i['status'] != 'VERIFIED' for i in self.state['issues'].values()):
            raise ValueError('OPEN_BLOCKING_ISSUE')
        if part['status'] == 'BLOCKED_EXTERNAL' and not part.get('external_dependencies'):
            raise ValueError('EXTERNAL_DEPENDENCY_EVIDENCE_REQUIRED')
        row.update(status=part['status'], receipt=self.attach(receipt_path), verifier=verifier)
        self.event('C_TASK_CLOSED', task=task, status=row['status'])

    def issue(self, issue_id, parent_task, fact, affected, repairer='B:root'):
        if issue_id in self.state['issues']:
            raise ValueError('ISSUE_ALREADY_REGISTERED')
        self.state['issues'][issue_id] = {'issue_id': issue_id, 'parent_task': parent_task,
            'fact': fact, 'affected': affected, 'repairer': repairer, 'status': 'NEEDS_REPAIR', 'attempts': 0}
        self.state['tasks'][parent_task]['status'] = 'NEEDS_REPAIR'
        self.event('ISSUE_OPENED_PARENT_PAUSED', issue_id=issue_id)

    def repair(self, issue_id, paths):
        issue = self.state['issues'][issue_id]
        if issue['status'] not in ('NEEDS_REPAIR', 'REGRESSION_PENDING') or issue['attempts'] >= 3:
            raise ValueError('REPAIR_STATE_OR_ATTEMPT_LIMIT')
        issue['repair_targets'] = [self.attach(p) for p in paths]
        if not issue['repair_targets']:
            raise ValueError('ACTUAL_PATCH_AND_TEST_REQUIRED')
        issue['attempts'] += 1; issue['status'] = 'REGRESSION_PENDING'
        self.event('ACTUAL_B_REPAIR_SUBMITTED', issue_id=issue_id)

    def close_issue(self, issue_id, receipt_path, verifier):
        issue = self.state['issues'][issue_id]; receipt = read_json(receipt_path)
        registered = {r['context'] for r in self.state['role_dispatches'] if r['role'] == 'C'}
        if (issue['status'] != 'REGRESSION_PENDING' or verifier not in registered
                or verifier == issue['repairer'] or receipt.get('role_context') != verifier
                or receipt.get('issue_id') != issue_id or receipt.get('status') != 'VERIFIED'):
            raise ValueError('INDEPENDENT_ISSUE_REVIEW_REQUIRED')
        self.check(issue['repair_targets']); self.check(receipt.get('targets', []))
        if (not set(map(object_hash, issue['repair_targets'])) <= set(map(object_hash, receipt.get('targets', [])))
                or not receipt.get('checked_components')):
            raise ValueError('REPAIRED_TARGET_NOT_REVIEWED')
        issue.update(status='VERIFIED', verifier=verifier, receipt=self.attach(receipt_path))
        others = any(i['parent_task'] == issue['parent_task'] and i['status'] != 'VERIFIED'
                     for i in self.state['issues'].values())
        self.state['tasks'][issue['parent_task']]['status'] = 'NEEDS_REPAIR' if others else 'PENDING'
        self.event('INDEPENDENT_REPAIR_CLOSED_PARENT_STILL_BLOCKED' if others else
                   'INDEPENDENT_REPAIR_CLOSED_PARENT_RESUMED', issue_id=issue_id, task=issue['parent_task'])

    def invalidate_changed(self):
        changed = []
        for name, row in self.state['tasks'].items():
            if row['status'] not in ('VERIFIED', 'BLOCKED_EXTERNAL', 'REVIEW_PENDING'):
                continue
            if not self.current(row):
                row['status'] = 'STALE_REBUILD_REQUIRED'; changed.append(name)
        for _ in TASKS:
            for name, row in self.state['tasks'].items():
                if row['status'] in ('VERIFIED', 'BLOCKED_EXTERNAL', 'REVIEW_PENDING') and not self.ready(name, True):
                    row['status'] = 'STALE_REBUILD_REQUIRED'; changed.append(name)
        self.event('SOURCE_INVALIDATION_PROPAGATED', tasks=sorted(set(changed)))
        return changed

    def checkpoint(self):
        self.invalidate_changed()
        if self.state['inflight']:
            status = 'INTERRUPTED_CHECKPOINT'
        elif any(i['status'] != 'VERIFIED' for i in self.state['issues'].values()):
            status = 'IMPLEMENTING'
        else:
            states = [r['status'] for r in self.state['tasks'].values()]
            status = ('READY_FOR_GPT_REVIEW' if all(s == 'VERIFIED' for s in states) else
                      'PARTIAL_BLOCKED' if all(s in ('VERIFIED', 'BLOCKED_EXTERNAL') for s in states) else 'IMPLEMENTING')
        self.state['status'] = status; self.event('CHECKPOINT', status=status)
        return status
