"""One live path: existing ChatGPT-authenticated Codex CLI, independent contexts.

No account files are read here. Only validated visible messages/events are saved.
The CLI has no shell, apps, plugins, child agents, hooks or web search; its sandbox
is read-only. Numeric tools run later in the deterministic parent controller.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import signal
import selectors
import subprocess
import tempfile
import time

import jsonschema

from .io import now, write_json, read_json, digest, object_hash


class ProviderError(RuntimeError):
    pass


# CLI 0.157.1 emits this startup diagnostic when we intentionally remove its
# code executor. It is not a failed model turn: it also returns exit 0 and a
# completed schema response. Preserve the message and require all success events.
# All other errors, missing events, malformed JSON and unexpected tools fail closed.
DISABLED_CODE_HOST = ('Code Mode is unavailable because code-mode host is disabled. '
                     'Code mode will fail closed; enable `features.code_mode_host` '
                     'and install `codex-code-mode-host`.')


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
        if not isinstance(item,dict): raise ProviderError('INVALID_ITEM_SCHEMA')
        if event['type'].startswith('item.') and not isinstance(item.get('type'),str):
            raise ProviderError('INVALID_ITEM_TYPE')
        if item.get('type')=='agent_message' and not isinstance(item.get('text'),str):
            raise ProviderError('INVALID_MESSAGE_TEXT')
        if item.get('type') in ('reasoning','reasoning_summary'):
            continue
        if event['type']=='capability.disabled':
            if event.get('message')!=DISABLED_CODE_HOST: raise ProviderError('INVALID_DISABLED_NOTICE')
            events.append(event)
        elif event['type'] in ('thread.started','turn.started','turn.completed','turn.failed','error'):
            events.append(event)
        elif event['type'].startswith('item.'):
            if item.get('type')=='agent_message':
                if event['type']=='item.completed':events.append(event)
            elif item.get('type')=='error':
                message=item.get('message',item.get('text','CLI error item'))
                kind='capability.disabled' if message==DISABLED_CODE_HOST else 'error'
                events.append({'type':kind,'message':message,'item_id':item.get('id')})
            else:
                # Unexpected CLI tool activity is an execution-boundary failure.
                events.append({'type':'unexpected_tool','item_type':item.get('type'),'item_id':item.get('id')})
        else:
            events.append({'type':'unexpected_event','event_type':event['type']})
    return events


def parse_response(events, schema, returncode):
    if returncode!=0 or any(e['type'] in ('error','turn.failed','unexpected_tool','unexpected_event') for e in events):
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
    text=re.sub(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', '<REDACTED_JWT>',text)
    return text


def stream_problem(events):
    for event in events:
        if event['type'] in ('error','turn.failed','unexpected_tool','unexpected_event'):
            return 'UNEXPECTED_VISIBLE_EVENT:' + event['type']
    return None


def transport_counts(events, stderr):
    return {'reconnect_notifications':sum('reconnect' in json.dumps(e).lower() for e in events),
            'fallback_notifications':sum('falling back' in json.dumps(e).lower() or 'fallback' in json.dumps(e).lower() for e in events),
            'sampling_retry_lines':sum('retry' in line.lower() and 'sampling' in line.lower() for line in stderr.splitlines()),
            'underlying_requests':'unknown'}


def safe_stderr(text):
    # Only this process's errors/transport diagnostics, never arbitrary account logs.
    return '\n'.join(redact(line) for line in text.splitlines()
                     if any(k in line.lower() for k in ('error','warn','retry','reconnect','fallback','falling back','failed','timeout')))


def run_limited(args, prompt, cwd, timeout):
    """Observe JSONL/stderr while running, stop at the first protocol/transport fault."""
    if os.name!='posix':raise ProviderError('PROCESS_GROUP_BOUNDARY_UNAVAILABLE')
    env=os.environ.copy();env.pop('NODE_TLS_REJECT_UNAUTHORIZED',None)
    process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                             cwd=cwd,env=env,start_new_session=True)
    events=[];errors=[];buffers={'out':b'','err':b''};line_number=0
    reason=None;deadline=time.monotonic()+timeout
    def consume(label, line):
        nonlocal reason,line_number
        if label=='err':
            safe=safe_stderr(line)
            if safe: errors.append(safe)
            if any(k in line.lower() for k in ('retry','reconnect','falling back','fallback','error','failed')):
                reason=reason or 'UNEXPECTED_STDERR_DIAGNOSTIC'
        else:
            line_number+=1
            try:
                batch=visible_events(line)
                events.extend(batch)
                reason=reason or stream_problem(batch)
            except ProviderError as exc:
                reason=reason or f'{exc}:stdout_line={line_number}'
    def kill_group():
        try:os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    try:
        # Prompts are bounded, but write via a selectable pipe to include write time in timeout.
        pending=prompt.encode(); offset=0
        with selectors.DefaultSelector() as selector:
            for stream,label in ((process.stdout,'out'),(process.stderr,'err')):
                os.set_blocking(stream.fileno(),False);selector.register(stream,selectors.EVENT_READ,label)
            os.set_blocking(process.stdin.fileno(),False)
            if pending: selector.register(process.stdin,selectors.EVENT_WRITE,'in')
            else: process.stdin.close()
            killed=False; drain_deadline=None
            while selector.get_map():
                if time.monotonic()>=deadline and not reason:reason='MODEL_TIMEOUT'
                if reason and not killed:
                    kill_group();killed=True;drain_deadline=time.monotonic()+3
                    if not process.stdin.closed:
                        try:selector.unregister(process.stdin)
                        except KeyError:pass
                        process.stdin.close()
                if killed and time.monotonic()>drain_deadline:break
                for key,_ in selector.select(.05):
                    label=key.data
                    if label=='in':
                        try: offset+=os.write(key.fileobj.fileno(),pending[offset:offset+4096])
                        except BrokenPipeError: offset=len(pending)
                        if offset==len(pending):selector.unregister(key.fileobj);key.fileobj.close()
                        continue
                    data=os.read(key.fileobj.fileno(),65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        if buffers[label]:consume(label,buffers[label].decode('utf-8',errors='strict'))
                        buffers[label]=b'';continue
                    buffers[label]+=data
                    if len(buffers[label])>1024*1024:
                        reason=reason or 'STREAM_LINE_LIMIT';buffers[label]=b''
                    while b'\n' in buffers[label]:
                        line,buffers[label]=buffers[label].split(b'\n',1)
                        consume(label,line.decode('utf-8',errors='strict'))
            process.wait(timeout=max(.1,deadline-time.monotonic()) if not killed else 3)
    except BaseException as exc:
        kill_group();process.wait(timeout=3)
        if isinstance(exc,subprocess.TimeoutExpired):reason='MODEL_TIMEOUT'
        else:
            error=ProviderError(type(exc).__name__+':'+redact(str(exc)))
            error.stdout=''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events)
            error.stderr='\n'.join(errors);error.returncode=process.returncode;error.process_started=True
            raise error from exc
    finally:
        # Even a parent that exited early must not leave descendants running.
        kill_group()
        for stream in (process.stdin,process.stdout,process.stderr):stream.close()
    stdout=''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events)
    stderr='\n'.join(errors)
    if reason=='MODEL_TIMEOUT':
        exc=subprocess.TimeoutExpired(args,timeout,output=stdout,stderr=stderr)
        exc.returncode=process.returncode;raise exc
    if reason:
        exc=ProviderError(reason);exc.stdout=stdout;exc.stderr=stderr;exc.returncode=process.returncode
        exc.process_started=True;raise exc
    return subprocess.CompletedProcess(args,process.returncode,stdout,stderr)


def verify_saved_call(directory, role, call_id, actions, expected_input_hash):
    """Recover only a dispatched call, verifying the actual visible final event."""
    directory=Path(directory)
    paths=[directory/name for name in ('input.json','receipt.json','response.json','visible_events.jsonl')]
    if any(not p.is_file() or p.is_symlink() for p in paths):
        raise ProviderError('MISSING_OR_UNSAFE_CALL_EVIDENCE')
    saved_input,receipt,value=(read_json(p) for p in paths[:3])
    schema=response_schema(role,call_id,actions)
    if object_hash(saved_input)!=expected_input_hash or saved_input.get('schema')!=schema:
        raise ProviderError('CALL_INPUT_MISMATCH')
    if any(receipt.get(k)!=v for k,v in {'role':role,'call_id':call_id,'classification':'LIVE_CALL_ATTEMPT',
           'status':'VERIFIED_STRUCTURE_ONLY','sandbox':'read-only','shell_tools':'disabled'}.items()):
        raise ProviderError('INVALID_RECOVERY_RECEIPT')
    # These are already filtered visible events, including a deliberately disabled
    # capability notice. Parse directly; never repair or discard recorded errors.
    try:events=[json.loads(line) for line in paths[3].read_text().splitlines() if line.strip()]
    except ValueError as exc:raise ProviderError('INVALID_SAVED_JSONL') from exc
    if any(not isinstance(e,dict) or e.get('type') not in ('thread.started','turn.started','turn.completed',
           'turn.failed','error','item.completed','capability.disabled','unexpected_tool','unexpected_event') for e in events):
        raise ProviderError('INVALID_SAVED_EVENT')
    if any((e['type']=='item.completed' and (not isinstance(e.get('item'),dict) or e['item'].get('type')!='agent_message')) or
           (e['type']=='capability.disabled' and e.get('message')!=DISABLED_CODE_HOST) for e in events):
        raise ProviderError('UNEXPECTED_SAVED_TOOL_OR_DIAGNOSTIC')
    parsed,thread,usage=parse_response(events,schema,receipt.get('exit_code'))
    if parsed!=value or receipt.get('thread_id')!=thread or receipt.get('usage')!=usage:
        raise ProviderError('RESPONSE_EVENT_OR_RECEIPT_MISMATCH')
    return value,receipt,{p.name:digest(p) for p in paths}


class CodexProvider:
    provenance='LIVE'

    def __init__(self, timeout=180, *, executable=None, expected_sha256=None, native_path=None, native_sha256=None):
        self.executable=executable or '/tmp/sc-g1-codex-0.157.1/node_modules/.bin/codex'
        self.expected_sha256=expected_sha256
        self.native_path=native_path;self.native_sha256=native_sha256
        self.timeout=min(timeout,180)

    def call(self, role, call_id, prompt, actions, output_dir):
        schema=response_schema(role,call_id,actions);out=Path(output_dir)
        if out.exists() and any(out.iterdir()):raise ProviderError('PREEXISTING_CALL_DO_NOT_OVERWRITE_OR_RESEND')
        started=now();clock=time.perf_counter();events=[];stderr='';result=None;process_started=False
        receipt={'classification':'LIVE_CALL_ATTEMPT','provider':'Codex CLI / existing ChatGPT login',
                 'role':role,'call_id':call_id,'run_id':out.parent.parent.name,
                 'requested_model':'gpt-6-astra','model_snapshot':'unavailable','request_id':'unavailable',
                 'started_at':started,'sandbox':'read-only','shell_tools':'disabled','reasoning_saved':False,
                 'usage':'unavailable','underlying_requests':'unknown','status':'BLOCKED','exit_code':None,
                 'effective_provider':'openai built-in','retry_control':'FIRST_VISIBLE_FAULT_KILLS_PROCESS_GROUP; hidden requests unknown'}
        try:
            out.mkdir(parents=True,exist_ok=True)
            write_json(out/'input.json',{'role':role,'call_id':call_id,'prompt':prompt,'schema':schema},exclusive=True)
            if not self.executable or not Path(self.executable).is_file():
                raise ProviderError('LIVE_AGENT_BLOCKED: pinned codex missing')
            if self.native_path:
                if digest(self.native_path)!=self.native_sha256:raise ProviderError('NATIVE_EXECUTABLE_HASH_MISMATCH')
                receipt['native_sha256']=self.native_sha256
            receipt['executable_sha256']=digest(self.executable)
            if self.expected_sha256 and receipt['executable_sha256']!=self.expected_sha256:
                raise ProviderError('EXECUTABLE_HASH_MISMATCH')
            with tempfile.TemporaryDirectory(prefix='sc-g1-role-') as tmp:
                p=Path(tmp);write_json(p/'schema.json',schema)
                args=[self.executable,'exec','--ignore-user-config','--strict-config','--ephemeral','--skip-git-repo-check',
                      '--sandbox','read-only','--json','--color','never','--cd',tmp,
                      '--model','gpt-6-astra','-c','model_reasoning_effort="max"',
                      '-c','model_provider="openai"',
                      '-c','analytics.enabled=false','-c','web_search="disabled"','-c','project_doc_max_bytes=0',
                      '--output-schema',str(p/'schema.json')]
                for feature in ('shell_tool','unified_exec','code_mode_host','apps','plugins','multi_agent','hooks','memories','shell_snapshot','browser_use','browser_use_external','computer_use','image_generation'):
                    args.extend(['--disable',feature])
                args.append('-')
                receipt['command']=[x.replace(tmp,'<ephemeral-role-directory>') for x in args]
                result=run_limited(args,prompt,tmp,self.timeout);process_started=True
                receipt['exit_code']=result.returncode;stderr=result.stderr
                # Incremental parsing retains earlier valid events if a later line fails.
                for number,line in enumerate(result.stdout.splitlines(),1):
                    try:events.extend(visible_events(line))
                    except ProviderError as exc:raise ProviderError(f'{exc}:stdout_line={number}') from exc
                value,thread,usage=parse_response(events,schema,result.returncode)
                write_json(out/'response.json',value,exclusive=True)
                receipt.update(thread_id=thread,usage=usage,status='VERIFIED_STRUCTURE_ONLY')
        except (OSError,ValueError,TypeError,ProviderError,subprocess.TimeoutExpired,KeyboardInterrupt) as exc:
            if isinstance(exc,subprocess.TimeoutExpired) or getattr(exc,'process_started',False):
                process_started=True
                stdout=getattr(exc,'stdout',None) or getattr(exc,'output',None) or ''
                if isinstance(stdout,bytes):stdout=stdout.decode('utf-8',errors='replace')
                stderr=getattr(exc,'stderr','') or ''
                if isinstance(stderr,bytes):stderr=stderr.decode('utf-8',errors='replace')
                for number,line in enumerate(stdout.splitlines(),1):
                    try:events.extend(visible_events(line))
                    except ProviderError as parse_exc:
                        receipt['parse_failure']=f'{parse_exc}:stdout_line={number}';break
                receipt['exit_code']=getattr(exc,'returncode',None)
            receipt['error']='MODEL_TIMEOUT' if isinstance(exc,subprocess.TimeoutExpired) else redact(str(exc))
            receipt['error_type']=type(exc).__name__
            receipt['no_automatic_resubmission']=True
        finally:
            receipt.update(ended_at=now(),elapsed_seconds=time.perf_counter()-clock,
                           process_started=process_started,stderr=safe_stderr(stderr),
                           visible_counts=transport_counts(events,stderr),completed_turns=sum(e['type']=='turn.completed' for e in events))
            try:
                (out/'visible_events.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events))
                write_json(out/'receipt.json',receipt,exclusive=True)
            except OSError as save_exc:
                raise ProviderError('EVIDENCE_MISSING: terminal receipt could not be saved; outcome unknown; do not resend') from save_exc
        if receipt['status']!='VERIFIED_STRUCTURE_ONLY':raise ProviderError(receipt['error'])
        return value,receipt
