"""Refresh the existing TD index against current cells and actual PDF pages.

Old page text is used only to relocate already-approved content. Current anchors
are checked from the actual PDF, and C still reviews the resulting navigation.
"""
from datetime import datetime, timezone
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[5]
EV = ROOT/'task1/evidence/goal3'
ANCHOR = '1a5e26b43189aef64a46f8986b3cc442fa50d2c5'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(text):
    return re.sub(r'\s+', '', text)


def main():
    original = subprocess.check_output(['git','show',ANCHOR+':task1/evidence/goal3/teacher_delivery_mapping.json'],cwd=ROOT)
    nav = json.loads(original)
    nav['updated_at_utc'] = datetime.now(timezone.utc).isoformat()
    nav['closeout_task'] = 'SC-LAB1-G3-CLOSEOUT-001'
    nav['prior_navigation_git_anchor'] = ANCHOR
    nav['status'] = 'CURRENT_CONTENT_LOCATED_NOT_ACCEPTANCE'
    auth = 'task1/evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/AUTHORIZATION.md'
    nav['sources']['closeout_authorization_excerpt'] = {'path':auth,'sha256':sha(ROOT/auth)}
    notebooks = {}
    for key,item in nav['notebooks'].items():
        nb = json.loads((ROOT/item['path']).read_text())
        normalized = [{'index_zero_based':i,'id':c['id'],'cell_type':c['cell_type'],'source':''.join(c['source'])} for i,c in enumerate(nb['cells'])]
        item['source_cells_sha256'] = hashlib.sha256(json.dumps(normalized,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        item['cell_count'] = len(nb['cells'])
        item['file_sha256'] = sha(ROOT/item['path'])
        notebooks[key] = normalized
    pages, relocated = {}, {}
    build = json.loads((EV/'report_build/build_receipt.json').read_text())
    for key,item in nav['reports'].items():
        stem = 'experiment1' if key=='E' else 'process1'
        textfile = EV/'report_build'/f'{stem}_text.txt'
        text = subprocess.check_output(['pdftotext','-layout',str(ROOT/item['path']),'-']).decode('utf8')
        assert textfile.read_text() == text
        current = text.split('\f')
        if not current[-1].strip(): current.pop()
        pages[key] = current
        oldtext = subprocess.check_output(['git','show',ANCHOR+':'+str(textfile.relative_to(ROOT))],cwd=ROOT).decode('utf8').split('\f')
        if not oldtext[-1].strip(): oldtext.pop()
        relocated[key] = {1:1,2:2}
        for n,old in enumerate(oldtext[2:],3):
            ranked = sorted(((SequenceMatcher(None,compact(old),compact(new),autojunk=False).ratio(),j) for j,new in enumerate(current[2:],3)),reverse=True)
            relocated[key][n] = ranked[0][1]
        record = next(r for r in build['reports'] if r['report']==stem)
        assert record['sha256'] == sha(ROOT/item['path'])
        item.update(pages=len(current),pdf_sha256_at_navigation=record['sha256'],text_sha256=sha(textfile),
                    page_text_sha256=record['text']['page_text_sha256'],
                    page_render_sha256={str(int(Path(p).stem.split('-')[-1])):h for p,h in record['render']['page_sha256'].items()},
                    binding_boundary='Navigation only. Current full visual/content review is separately bound in closeout C receipt.')
        item.pop('page_render_sha256_at_B_visual_review',None)
    for entry in nav['entries']:
        for nb in entry['notebooks']:
            for loc in nb['cells']:
                cell = notebooks[nb['notebook']][loc['index_zero_based']]
                loc.update(cell_id=cell['id'],cell_type=cell['cell_type'],source_sha256=hashlib.sha256(cell['source'].encode()).hexdigest(),source_first_line=cell['source'].splitlines()[0])
        if entry['id']=='TD-20':
            entry['reports'][0]['verified_text_anchor']='吴博闻'
            entry['reports'][0]['section_or_figure']='封面正式身份已同步'
            entry['what_to_read']='身份已由本轮用户直接提供并同步；真实互动原图、完整消息范围、批准spec与Lock仍待外部输入。身份闭合不代表Process或最终提交闭合。'
        if entry['id']=='TD-22':
            entry['what_to_read']=entry['what_to_read'].replace('正式身份/互动证据缺项时REVIEW_ONLY','身份已同步；互动证据与最终审核缺项时REVIEW_ONLY')
            entry['reports'][-1]['verified_text_anchor']='NOT_READY'
        for loc in entry['reports']:
            key=loc['report']; anchor=compact(loc['verified_text_anchor'])
            positions={relocated[key][n] for n in loc['pdf_pages_one_based']}
            hits=[i for i,text in enumerate(pages[key],1) if anchor in compact(text) and (i!=2)]
            if not hits: raise ValueError('CURRENT_PDF_ANCHOR_MISSING:'+entry['id']+':'+anchor)
            if not any(n in positions for n in hits): positions.add(hits[-1])
            loc['pdf_pages_one_based']=sorted(positions)
            loc['printed_page_labels']=['' if n==1 else pages[key][n-1].strip().splitlines()[-1].strip() for n in sorted(positions)]
    (EV/'teacher_delivery_mapping.json').write_text(json.dumps(nav,ensure_ascii=False,indent=2)+'\n')
    lines=['# 实验一教师要求与实际作业入口','',
           '这是原 TD 导航的当前修订，不是另一套已通过总表。机器定位见 [teacher_delivery_mapping.json](teacher_delivery_mapping.json)；完整要求与质量证据见 [MASTER_REQUIREMENTS_REVIEW](closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/MASTER_REQUIREMENTS_REVIEW.md)。',
           '', '**B**：[基础 Notebook](../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb)；**L**：[系统 Notebook](../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb)。单元从0开始；JSON保存stable ID/source hash。',
           '',f'**E**：[Experiment PDF](../../reports/experiment1/experiment1.pdf)，{len(pages["E"])}页；**P**：[Process PDF](../../reports/process1/process1.pdf)，{len(pages["P"])}页。页码均含封面，是当前PDF物理页。正文定位与实际执行、目视、外部验收分别登记。','',
           '| 导航 | 教师/阶段要求 | Notebook 单元 | PDF 页码与章节 |','|---|---|---|---|']
    for e in nav['entries']:
        nb='；'.join(n['notebook']+' '+','.join(str(c['index_zero_based']) for c in n['cells']) for n in e['notebooks'])
        pdf='；'.join(r['report']+' '+','.join(map(str,r['pdf_pages_one_based']))+'（'+r['section_or_figure']+'）' for r in e['reports'])
        refs=' / '.join(x+' '+','.join(e[y]) for x,y in [('G1','g1_requirement_ids'),('G2','g2_requirement_ids')] if e[y]) or '批准的G3要求'
        lines.append(f'| {e["id"]} | {e["topic"]}<br>{refs} | {nb} | {pdf} |')
    lines += ['', 'G1 R01—R16、G2 R01—R10 的原要求映射保留；G3分区与自动发布规则来自用户授权，不倒写为教师规定。', '',
              '教师课件第26页：10月5日前将 `.ipynb` 与实验报告压缩ZIP，以“学号_姓名_实验一”命名，发至 `52285903012@stu.ecnu.edu.cn`；未规定具体截止时刻。本轮未发送。身份现为吴博闻 / 10245102410；互动原图/完整消息范围、批准annotation spec与Evidence Lock仍缺，最终网页GPT与用户审核尚未完成。', '',
              '当前运行回执、PDF逐页文本/200dpi页图、包与发布版本见 [REVIEW_PACKET](REVIEW_PACKET.md)。本导航不把文件存在等同于执行或验收通过。','']
    (EV/'teacher_delivery_mapping.md').write_text('\n'.join(lines))
    print(json.dumps({'entries':len(nav['entries']),'current_pages':{k:len(v) for k,v in pages.items()},'status':nav['status']}))


if __name__=='__main__': main()
