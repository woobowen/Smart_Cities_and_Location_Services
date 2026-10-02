"""Apply documented native-image reading corrections (no chat text edits)."""
from pathlib import Path
p=Path(__file__).parent/'editorial.py'
s=p.read_text();s+='''
# Native screenshot/arrow review, complete report revision 3.
_uu={u['id']:u for u in UNITS}
_uu['W01']['panels'][1]['ay']=548
_uu['W07']['panels'][0]['ay']=52
_uu['W08']['panels'][0]['ay']=224
_uu['W09']['panels'][-1]['ay']=504
_uu['W09']['notes'][-1]=('可读性优先','图型和复杂度都要服从问题。技术图由真实数据或明确结构生成，不能为了高级感损害阅读。')
_uu['W10']['panels'][0]['ay']=67
_uu['W12']['panels'][0]['ay']=275
_uu['W13']['panels'][1]['ay']=917
_uu['E05']['panels'][0]['ay']=107
_uu['E06']['panels'][0]['box']=[240,364,584,432]
_uu['E06']['panels'][0]['ay']=420
_uu['E06']['notes'][0]=('少量有用，比数量重要','这里回引我在执行前收窄论文使用范围的补充，再回看此前研究。不是一次新的检索决定。')
_uu['E13']['panels'][-1]['box']=[82,0,608,415]
_uu['E13']['panels'][-1]['ay']=391
_uu['E14']['panels'][-1]['box']=[82,376,608,881]
_uu['E14']['panels'][-1]['ay']=704
_uu['E15']['panels'][0]['ay']=285
_uu['E15']['panels'][1]['box']=[82,886,608,1247]
_uu['E15']['panels'][1]['ay']=1214
_uu['E16']['panels'][2]['box']=[82,1270,608,1567]
_uu['E16']['panels'][2]['ay']=1525
_uu['E18']['panels'][0]['ay']=339
_uu['E19']['panels'][0]['ay']=927
_uu['E19']['notes'][0]=('转交仍需核对','我转交的是Codex的交付回执，不是自己完成全部检验。冻结、600条确认与全量生产分别核对，不能混称独立测试。')
_uu['E24']['panels'][0]['ay']=107
'''
p.write_text(s)
