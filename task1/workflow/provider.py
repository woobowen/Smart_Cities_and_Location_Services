"""One live path: existing ChatGPT-authenticated Codex CLI, independent contexts.

No account files are read here. Only validated visible messages/events are saved.
The CLI has no shell, apps, plugins, child agents, hooks or web search; its sandbox
is read-only. Numeric tools run later in the deterministic parent controller.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

import jsonschema

from .io import now, write_json


class ProviderError(RuntimeError):
    pass


def response_schema(role, call_id, actions):
    fields={
        'role':{'type':'string','enum':[role]},
        'call_id':{'type':'string','enum':[call_id]},
        'action':{'type':'string','enum':actions},
        'record_ids':{'type':'array','items':{'type':'string'}},
        'feedback_refs':{'type':'array','items':{'type':'string'}},
        'evidence_refs':{'type':'array','items':{'type':'string'}},
        'summary':{'type':'string'},
        'reason':{'type':'string'},
        'request_status':{'type':'string','enum':['PROPOSED','NEEDS_REVIEW','BLOCKED']},
        'candidate_for_future_review':{'type':['string','null']},
    }
    return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}


def visible_events(stdout):
    """Strict JSONL. Never repair malformed output with regex or store reasoning."""
    events=[]
    for line in stdout.splitlines():
        if not line.strip():continue
        try:
            event=json.loads(line)
        except ValueError as exc:
            raise ProviderError('INVALID_JSONL') from exc
        if not isinstance(event,dict) or not isinstance(event.get('type'),str):
            raise ProviderError('INVALID_EVENT_SCHEMA')
        item=event.get('item',{})
        if item.get('type') in ('reasoning','reasoning_summary'):
            continue
        if event['type'] in ('thread.started','turn.started','turn.completed','turn.failed','error'):
            events.append(event)
        elif event['type']=='item.completed':
            if item.get('type')=='agent_message':
                events.append(event)
            else:
                # Unexpected CLI tool activity is an execution-boundary failure.
                events.append({'type':'unexpected_tool','item_type':item.get('type'),'item_id':item.get('id')})
    return events


def parse_response(events, schema, returncode):
    if returncode!=0 or any(e['type'] in ('error','turn.failed','unexpected_tool') for e in events):
        raise ProviderError('CLI_FAILED_OR_UNEXPECTED_TOOL')
    threads=[e for e in events if e['type']=='thread.started']
    completed=[e for e in events if e['type']=='turn.completed']
    messages=[e['item']['text'] for e in events if e['type']=='item.completed' and e['item'].get('type')=='agent_message']
    if len(threads)!=1 or len(completed)!=1 or len(messages)!=1:
        raise ProviderError('MISSING_OR_AMBIGUOUS_FINAL_EVENT')
    try:
        value=json.loads(messages[0])
        jsonschema.validate(value,schema)
    except (ValueError,jsonschema.ValidationError) as exc:
        raise ProviderError('INVALID_STRUCTURED_RESPONSE') from exc
    return value,threads[0].get('thread_id','unavailable'),completed[0].get('usage','unavailable')


def redact(text):
    text=re.sub(r'(https?://)[^/@\s]+:[^/@\s]+@',r'\1<REDACTED>@',text)
    text=re.sub(r'\bsk-[A-Za-z0-9_-]{12,}', '<REDACTED_KEY>',text)
    text=re.sub(r'(?i)(authorization:\s*bearer\s+)\S+',r'\1<REDACTED>',text)
    return text


class CodexProvider:
    provenance='LIVE'

    def __init__(self, timeout=180):
        self.executable=shutil.which('codex')
        self.timeout=timeout

    def call(self, role, call_id, prompt, actions, output_dir):
        if not self.executable:
            raise ProviderError('LIVE_AGENT_BLOCKED: codex not found')
        schema=response_schema(role,call_id,actions)
        out=Path(output_dir)
        out.mkdir(parents=True,exist_ok=True)
        write_json(out/'input.json',{'role':role,'call_id':call_id,'prompt':prompt,'schema':schema},exclusive=True)
        started=now();clock=time.perf_counter()
        with tempfile.TemporaryDirectory(prefix='sc-g1-role-') as tmp:
            p=Path(tmp);write_json(p/'schema.json',schema)
            args=[self.executable,'exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
                  '--sandbox','read-only','--json','--color','never','--cd',tmp,
                  '--model','gpt-6-astra','-c','model_reasoning_effort="max"',
                  '-c','web_search="disabled"','-c','project_doc_max_bytes=0',
                  '--output-schema',str(p/'schema.json')]
            for feature in ('shell_tool','unified_exec','code_mode_host','apps','plugins','multi_agent','hooks','memories','shell_snapshot','browser_use','browser_use_external','computer_use','image_generation'):
                args.extend(['--disable',feature])
            args.append('-')
            try:
                result=subprocess.run(args,input=prompt,cwd=tmp,capture_output=True,text=True,timeout=self.timeout)
            except subprocess.TimeoutExpired as exc:
                write_json(out/'receipt.json',{'classification':'LIVE_CALL_ATTEMPT','role':role,'call_id':call_id,
                           'started_at':started,'ended_at':now(),'elapsed_seconds':time.perf_counter()-clock,
                           'status':'BLOCKED','error':'MODEL_TIMEOUT; no automatic resubmission','usage':'unavailable'},exclusive=True)
                raise ProviderError('MODEL_TIMEOUT') from exc
            events=visible_events(result.stdout)
            (out/'visible_events.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events))
            receipt={'classification':'LIVE_CALL_ATTEMPT','provider':'Codex CLI / existing ChatGPT login',
                     'role':role,'call_id':call_id,'requested_model':'gpt-6-astra',
                     'model_snapshot':'unavailable','request_id':'unavailable',
                     'started_at':started,'ended_at':now(),'elapsed_seconds':time.perf_counter()-clock,
                     'exit_code':result.returncode,'sandbox':'read-only','shell_tools':'disabled',
                     'command':[x.replace(tmp,'<ephemeral-role-directory>') for x in args],
                     'stderr':redact(result.stderr), 'reasoning_saved':False,'status':'EXECUTED'}
            try:
                value,thread,usage=parse_response(events,schema,result.returncode)
            except ProviderError as exc:
                receipt.update(status='BLOCKED',error=str(exc))
                write_json(out/'receipt.json',receipt,exclusive=True)
                raise
            receipt.update(thread_id=thread,usage=usage,status='VERIFIED_STRUCTURE_ONLY')
            write_json(out/'receipt.json',receipt,exclusive=True)
            write_json(out/'response.json',value,exclusive=True)
            return value,receipt
