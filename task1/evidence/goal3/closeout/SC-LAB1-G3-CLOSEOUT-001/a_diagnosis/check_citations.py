"""Capture byte identities for already-read primary sources; do not redistribute them."""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

OUT = Path(__file__).resolve().parent
URLS = [
    ('S10', 'https://www.jmlr.org/papers/volume11/cawley10a/cawley10a.pdf'),
    ('REF-PROJ-CART', 'https://proj.org/en/stable/operations/conversions/cart.html'),
    ('REF-PROJ-TOPO', 'https://proj.org/en/stable/operations/conversions/topocentric.html'),
]
rows=[]
for sid,url in URLS:
    item={'source_id':sid,'url':url,'attempted_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'body_saved':False}
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            b=r.read()
            item.update(status=r.status,content_type=r.headers.get('Content-Type'),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    except Exception as exc:
        item.update(status='BYTE_FETCH_FAILED',error=str(exc),sha256=None)
    rows.append(item)
rows[0].update({
    'title':'On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation',
    'authors':['Gavin C. Cawley','Nicola L. C. Talbot'],
    'publication':'Journal of Machine Learning Research 11 (2010), 2079–2107',
    'web_primary_source_read_status':'SUCCESS',
    'document_pages':29,
    'actually_read':[
        {'section':'§1 introduction','physical_pages_one_based':[1,2],'printed_pages':[2079,2080],'paragraph':'selection-criterion variance and optimistic evaluation bias'},
        {'section':'§4.4 and §5–5.1','physical_pages_one_based':[16,17],'printed_pages':[2094,2095],'paragraph':'finite-sample optimization risk; treating selection as part of fitting; internal evaluation protocol'},
        {'section':'§5.3','physical_pages_one_based':[24],'printed_pages':[2102],'paragraph':'selection on all data followed by repartitioning contaminates held-out evaluation'},
        {'section':'§6 conclusions','physical_pages_one_based':[25],'printed_pages':[2103],'paragraph':'selection and fitting should be jointly included in evaluation'},
    ],
    'reading_level':'FULL_TEXT_SPECIFIED_SECTIONS_ONLY',
    'not_read_or_reproduced':'No full-paper line-by-line audit, independent derivation, figure/table value verification or author experiment reproduction.',
    'supported_claim':'有限样本上的反复方法选择可能利用该样本的偶然特征；已参与选择的数据随后改称测试集会产生选择偏差风险。',
    'task_inference':'本项目把开发、候选选择和冻结后最终确认分开，是对一般风险的边界性借鉴；论文不规定600条样本、S0参数或提供本项目统计无偏保证。',
    'history_boundary':'本轮定点全文核查仅修补当前引用证据，不追溯升级历史阅读层级，不证明过去设计由这次阅读引发。',
})
rows[1].update({'web_primary_source_read_status':'SUCCESS','actually_read':'Operation definition, axis semantics, +ellps parameter. Page currently labeled PROJ 9.9.0; not a statement about installed software.','supported_claim':'经纬度与椭球高转换为地心直角坐标；具体椭球需显式给定。'})
rows[2].update({'web_primary_source_read_status':'SUCCESS','actually_read':'Definition, fixed topocentric origin, cart-to-topocentric pipeline requirement and units. Page currently labeled PROJ 9.9.0.','supported_claim':'ECEF至固定原点ENU变换；地理坐标先经cart转换，East/North为指定原点的切平面方向。'})
result={'role':'A_SOURCE_DIAGNOSIS','task_id':'SC-LAB1-G3-CLOSEOUT-001','primary_read_tool':'web.run open/find; exact URLs and scope above','byte_capture_command':'python check_citations.py','accesses':rows,'new_research_experiments':0,'new_record_model_calls':0,'source_crs_effect':'none; formulas do not certify input datum','copyright_scope':'No full paper is stored in this evidence directory or supplied to the teacher ZIP.'}
(OUT/'citation_access_receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print([(r['source_id'],r['status']) for r in rows])
