"""Read the assignment identity supplied by the user, without inference."""
from datetime import date
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_identity(root=ROOT):
    value = json.loads((Path(root)/'task1/config/assignment.json').read_text(encoding='utf8'))
    if not isinstance(value['student_id'], str) or not value['student_id'].isascii() or not value['student_id'].isdigit():
        raise ValueError('STUDENT_ID_MUST_BE_AN_ASCII_DIGIT_STRING')
    if not isinstance(value['student_name'], str) or not value['student_name'].strip():
        raise ValueError('TRUSTED_STUDENT_NAME_REQUIRED')
    if any(c in value['student_name'] for c in '\\{}%&#_$^~\n\r'):
        raise ValueError('UNSAFE_TEX_IDENTITY')
    date.fromisoformat(value['report_revision_date'])
    return value


def write_report_metadata(root=ROOT):
    value = read_identity(root)
    day = date.fromisoformat(value['report_revision_date'])
    fields = {'StudentName': value['student_name'], 'StudentID': value['student_id'],
              'ReportDate': f'{day.year} 年 {day.month} 月 {day.day} 日',
              'ExperimentStatus': '技术送审稿；待最终审核',
              'ProcessStatus': ('承接全文验收；第76页授权修正；具体 Evidence Lock 按原记录'
                                if value.get('process_report_status') == 'PRIOR_FULL_ACCEPTANCE_P76_AUTHORIZED_REVISION'
                                else '全文已验收；具体 Evidence Lock 按原记录'
                                if value.get('process_report_status') == 'USER_ACCEPTED_FULL_REPORT'
                                else '送审稿；原始互动证据与批准呈现方案待补')}
    text = '% Generated from task1/config/assignment.json; date is the report revision date.\n'
    text += ''.join('\\newcommand{\\'+key+'}{'+content+'}\n' for key, content in fields.items())
    target = Path(root)/'task1/reports/metadata.tex'
    target.write_text(text, encoding='utf8')
    return target
