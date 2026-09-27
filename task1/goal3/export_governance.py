"""Export only public collaboration event metadata from the current task session.

The platform stores message arguments encrypted. Preserve their stored-payload
hashes, not ciphertext or invented plaintext. Never export reasoning or auth.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from task1.workflow.io import now, read_json, write_json, digest
from .data import EV

ALLOWED = {'spawn_agent', 'followup_task', 'send_message', 'interrupt_agent'}
SESSION_ID = '01a0e0ef-ee23-7ca0-91b2-10eb9f4fc925'


def sha(value):
    return hashlib.sha256(value.encode('utf8')).hexdigest()


def export(session):
    if not Path(session).name.endswith('-'+SESSION_ID+'.jsonl'):
        raise ValueError('CURRENT_AUTHORIZED_TASK_SESSION_ONLY')
    calls, events, counts = {}, [], Counter()
    for line in Path(session).read_text().splitlines():
        row = json.loads(line)
        if row.get('type') != 'response_item':
            continue
        payload = row.get('payload', {})
        kind = payload.get('type')
        name = payload.get('name', '').split('.')[-1]
        if kind == 'function_call' and name in ALLOWED:
            arguments = json.loads(payload['arguments'])
            call_id = payload['call_id']; calls[call_id] = name
            event = {'at': row['timestamp'], 'event': kind, 'tool': name, 'call_id': call_id,
                     'source_event_sha256': sha(line),
                     'arguments_metadata': {k: arguments[k] for k in ('task_name', 'target', 'fork_turns',
                         'model', 'reasoning_effort') if k in arguments}}
            if 'message' in arguments:
                message = arguments['message']
                encrypted = message.startswith('gAAAA')
                event['message_availability'] = ('PLATFORM_ENCRYPTED_AT_REST; plaintext not recovered'
                    if encrypted else 'CLEAR_TEXT_TOOL_ARGUMENT')
                event['stored_message_payload_sha256'] = sha(message)
                event['stored_message_payload_bytes'] = len(message.encode('utf8'))
                if not encrypted:
                    event['message'] = message
                counts['encrypted_message_fields' if encrypted else 'clear_message_fields'] += 1
            events.append(event); counts[name] += 1
        elif kind == 'function_call_output' and payload.get('call_id') in calls:
            output = payload.get('output', '')
            event = {'at': row['timestamp'], 'event': kind, 'tool': calls[payload['call_id']],
                     'call_id': payload['call_id'], 'source_event_sha256': sha(line),
                     'stored_output_payload_sha256': sha(output), 'stored_output_payload_bytes': len(output.encode('utf8'))}
            if not output:
                event['availability'] = 'EMPTY_TOOL_RETURN'
            elif output.startswith('gAAAA'):
                event['availability'] = 'PLATFORM_ENCRYPTED_AT_REST; plaintext not recovered'
            else:
                event['availability'] = 'CLEAR_TOOL_RETURN'
                try:
                    event['output'] = json.loads(output)
                except ValueError:
                    event['output'] = output
            counts[event['availability']] += 1; events.append(event)
    result = {'at': now(), 'scope': 'Only actual collaboration tool events from this task session; '
              'no reasoning, auth, unrelated history, ciphertext dumps, or invented dialogue.',
              'session_id': SESSION_ID,
              'cutoff': events[-1]['at'] if events else None, 'counts': dict(counts), 'events': events,
              'message_text_limit': 'Native message fields were platform-encrypted in the local session; '
                  'stored payload hashes are not hashes of known plaintext. Role TaskPlans and review artifacts '
                  'provide separately sourced readable decisions, not reconstructed message quotes.',
              'native_model_identity': 'inherited Codex environment; provider/hidden backend requests and billing unknown',
              'record_level_new_model_calls': 0, 'source_sha256': digest(__file__)}
    target = EV/'governance_tool_events.json'
    prior = digest(target) if target.exists() else None
    write_json(target, result)
    write_json(EV/'governance_export_receipt.json', {'at': now(), 'previous_export_sha256': prior,
               'export_sha256': digest(target), 'source_sha256': digest(__file__),
               'events': len(events), 'counts': dict(counts),
               'transformation': 'retain event identity and available metadata; replace opaque stored message payloads with hashes; no decryption'})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=Path, required=True)
    args = parser.parse_args(); result = export(args.session)
    print({'events': len(result['events']), 'counts': result['counts'], 'cutoff': result['cutoff']})
