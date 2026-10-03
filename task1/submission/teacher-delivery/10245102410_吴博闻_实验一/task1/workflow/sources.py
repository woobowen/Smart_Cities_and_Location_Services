"""Small task-specific source registry. No model-selected file reads."""
import zipfile
import xml.etree.ElementTree as ET
from .io import ROOT, read_json, bound_path, digest

REGISTRY = ROOT/'task1/config/goal1_sources.json'


def source_context():
    result = {}
    for entry in read_json(REGISTRY):
        path = bound_path(ROOT, entry['path'])
        if not path.is_file() or digest(path) != entry['sha256']:
            raise ValueError('SOURCE_FILE_VERSION_MISMATCH:'+entry['id'])
        if 'member' in entry:
            with zipfile.ZipFile(path) as z:
                tree=ET.fromstring(z.read(entry['member']))
                excerpt='\n'.join(e.text for e in tree.iter() if e.tag.endswith('}t') and e.text)
        else:
            lines=path.read_text().splitlines()
            start,stop=entry['lines']
            if start<1 or stop>len(lines) or start>stop:raise ValueError('INVALID_SOURCE_LOCATOR')
            excerpt='\n'.join(lines[start-1:stop])
        if not excerpt:raise ValueError('EMPTY_SOURCE_EXCERPT')
        result[entry['id']]={**entry,'kind':'source','excerpt':excerpt,
                             'verification_scope':'File and excerpt verified; claim status is separate'}
    return result


def validate_references(request, context, parent_version, run_id, required_feedback=()):
    for ref in request['evidence_refs'] + request['feedback_refs']:
        if ref not in context:raise ValueError('UNKNOWN_EVIDENCE_REFERENCE:'+ref)
        item=context[ref]
        if item['kind']!='source' and (item.get('parent_version')!=parent_version or item.get('run_id')!=run_id):
            raise ValueError('WRONG_REFERENCE_PARENT_OR_RUN:'+ref)
    if required_feedback and not set(required_feedback).issubset(request['feedback_refs']):
        raise ValueError('MISSING_ACTUAL_FEEDBACK_REFERENCE')
    if required_feedback:
        if not any(context[r]['kind']=='review' for r in required_feedback):
            raise ValueError('FEEDBACK_REQUIRES_CURRENT_REVIEW')
        if not any(context[r]['kind']=='tool' and context[r].get('status')=='VERIFIED' for r in required_feedback):
            raise ValueError('FEEDBACK_REQUIRES_VERIFIED_TOOL')
