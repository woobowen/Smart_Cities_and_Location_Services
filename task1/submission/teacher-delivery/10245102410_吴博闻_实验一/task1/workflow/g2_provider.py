"""Bounded live experiment calls through the existing authenticated Codex CLI.

Only diagnostic cards and explicit feedback are passed. No repository access,
shell, browser, memory service, plugins, or child agents are exposed to a model.
Visible request attempts and replies are retained; hidden provider calls unknown.
"""
import json
import subprocess
import tempfile
import time
from pathlib import Path

from .io import write_json, now, digest, object_hash
from .provider import (run_limited, visible_events, parse_response, safe_stderr,
                       ProviderError, transport_counts)

EXECUTABLE=Path('/tmp/sc-g1-codex-0.157.1/node_modules/.bin/codex')
MODEL='gpt-6-astra'
EFFORT='medium'


def schema():
    def obj(properties):
        return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
    proposal=obj({'candidate_id':{'type':'string'},
        'parameters':obj({p:{'type':'number'} for p in ('dt','distance','min_points','min_length','direction','dp')}),
        'metric_id':{'type':'string'},'predicted_sign':{'type':'string','enum':['increase','decrease','unchanged','not_predicted']},
        'reason':{'type':'string'}})
    item=obj({'record_id':{'type':'string'},'proposals':{'type':'array','items':proposal},
        'stop':{'type':'boolean'},'memory_ids_used':{'type':'array','items':{'type':'string'}}})
    return obj({'records':{'type':'array','items':item}})


class ExperimentProvider:
    provenance='LIVE'

    def __init__(self, executable=EXECUTABLE, timeout=180):
        self.executable=Path(executable);self.timeout=timeout

    def call(self, prompt, output_dir, *, request_id, purpose):
        out=Path(output_dir)
        if out.exists():raise ProviderError('CALL_PATH_EXISTS_NO_RESUBMIT')
        out.mkdir(parents=True)
        started=time.perf_counter();events=[];stderr='';returncode=None
        receipt={'request_id':request_id,'purpose':purpose,'classification':'LIVE_CALL_ATTEMPT',
                 'started_at':now(),'provider':'existing ChatGPT-authenticated Codex CLI',
                 'requested_model':MODEL,'reasoning_effort':EFFORT,'model_snapshot':'unavailable',
                 'provider_request_ids':'unavailable','seed':'unavailable','underlying_requests':'unknown',
                 'status':'DISPATCHED','reasoning_saved':False,'sandbox':'read-only','model_tools':[],
                 'retry_policy':'parent records at most two retries for transient faults; no auth/billing retries'}
        write_json(out/'input.json',{'prompt':prompt,'schema':schema()},exclusive=True)
        write_json(out/'dispatch.json',receipt,exclusive=True)
        try:
            receipt['executable_sha256']=digest(self.executable)
            receipt['cli_version']=subprocess.check_output([str(self.executable),'--version'],text=True).strip()
            with tempfile.TemporaryDirectory(prefix='sc-g2-episode-') as temporary:
                p=Path(temporary);write_json(p/'response_schema.json',schema())
                args=[str(self.executable),'exec','--ignore-user-config','--strict-config',
                      '--ephemeral','--skip-git-repo-check','--sandbox','read-only','--json',
                      '--color','never','--cd',temporary,'--model',MODEL,
                      '-c','model_reasoning_effort="'+EFFORT+'"','-c','model_provider="openai"',
                      '-c','analytics.enabled=false','-c','web_search="disabled"',
                      '-c','project_doc_max_bytes=0','--output-schema',str(p/'response_schema.json')]
                for feature in ('shell_tool','unified_exec','code_mode_host','apps','plugins','multi_agent',
                                'hooks','memories','shell_snapshot','browser_use','browser_use_external',
                                'computer_use','image_generation','unbounded_connection_retries'):
                    args.extend(['--disable',feature])
                args.append('-')
                receipt['command']=[a.replace(temporary,'<ephemeral-episode-directory>') for a in args]
                result=run_limited(args,prompt,temporary,self.timeout)
                events=visible_events(result.stdout);stderr=result.stderr;returncode=result.returncode
                response,thread,usage=parse_response(events,schema(),returncode)
                write_json(out/'response.json',response,exclusive=True)
                receipt.update(status='VERIFIED_STRUCTURE_ONLY',thread_id=thread,usage=usage,
                               response_sha256=digest(out/'response.json'))
        except (OSError,ValueError,ProviderError,subprocess.TimeoutExpired) as exc:
            stdout=getattr(exc,'stdout',None) or getattr(exc,'output',None) or ''
            if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
            if stdout:
                try:events=visible_events(stdout)
                except ProviderError:receipt['visible_stream_parse_failure']=True
            stderr=getattr(exc,'stderr','') or ''
            if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
            returncode=getattr(exc,'returncode',returncode)
            receipt.update(status='FAILED',error=str(exc),error_type=type(exc).__name__)
        finally:
            (out/'visible_events.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events))
            receipt.update(ended_at=now(),elapsed_seconds=time.perf_counter()-started,
                           exit_code=returncode,stderr=safe_stderr(stderr),
                           visible_counts=transport_counts(events,stderr),
                           input_sha256=digest(out/'input.json'),
                           events_sha256=digest(out/'visible_events.jsonl'))
            receipt['completed_turns']=sum(e['type']=='turn.completed' for e in events)
            write_json(out/'receipt.json',receipt,exclusive=True)
        if receipt['status']!='VERIFIED_STRUCTURE_ONLY':
            raise ProviderError(receipt.get('error','FAILED'))
        return response,receipt
