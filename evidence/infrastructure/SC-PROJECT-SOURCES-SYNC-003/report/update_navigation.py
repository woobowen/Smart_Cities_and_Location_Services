"""Rebind current reader navigation to the accepted report, not old C checks."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[4]
EV=Path(__file__).resolve().parent
P=ROOT/'task1/evidence/goal3/teacher_delivery_mapping.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads(P.read_text());old_hash=sha(P)
text=(EV/'approved-text.txt').read_text();pages=text.split('\f')[:-1]
norm=lambda s:re.sub(r'\s+','',s)
# Actual approved PDF physical pages and exact textual anchors.
loc={
'TD-01':[(3,'先区分采样现象与位置错误'),(4,'数据文件未注明坐标参考系'),(25,'局部工作坐标的计算')],
'TD-02':[(5,'何时应将相邻观测断开'),(22,'新增 500,312 个覆盖点原来被过滤的原因')],
'TD-03':[(5,'怎样检查方向突变，而不将它直接当作噪声')],
'TD-04':[(6,'怎样减少点数并控制简化偏差'),(7,'P 专项另作判断')],
'TD-05':[(6,'为什么不能只比较删点率或最后一步误差'),(21,'全量处理后，原始点去了哪里'),(22,'覆盖增加与存储量增加为何不同')],
'TD-06':[(8,'时间和距离阈值怎样改变切分'),(9,'哪些短段过滤条件造成信息丢失'),(10,'方向阈值与简化容差的取舍')],
'TD-07':[(11,'三种操作能否交换顺序')],
'TD-08':[(12,'一条建议怎样进入实际计算')],
'TD-09':[(13,'四种运行方式分别能看到什么')],
'TD-10':[(14,'示范记忆是否影响建议与结果')],
'TD-11':[(14,'局部检查合格，为什么仍未采用'),(15,'记录 7764 的建议核验'),(16,'反例揭示了哪些隐含假设')],
'TD-12':[(1,'Experiment Report'),(25,'读数与实验的复算入口')],
'TD-13':[(12,'两类结果分别处理')],
'TD-14':[(17,'分别检查两项过滤调整的作用'),(18,'方向条件规则能否提供额外收益'),(19,'组合在新记录上退化之后，怎样取舍')],
'TD-15':[(7,'参考设置、数据分工与比较条件'),(19,'组合在新记录上退化之后，怎样取舍')],
'TD-16':[(20,'选定方案在预留记录上的表现')],
'TD-17':[(21,'全量处理后，原始点去了哪里'),(22,'较大偏差来自哪一步'),(23,'记录 352 的局部边界案例')],
'TD-18':[(4,'图 1'),(9,'图 2'),(10,'图 3'),(12,'图 5'),(15,'图 6'),(19,'图 7'),(20,'图 8'),(21,'图 9'),(23,'图 10')],
'TD-20':[(1,'吴博闻')],
'TD-22':[(25,'读数与实验的复算入口')]
}
for e in d['entries']:
 original_process=[r for r in e['reports'] if r['report']!='E']
 reports=[]
 for page,anchor in loc.get(e['id'],[]):
  assert norm(anchor) in norm(pages[page-1]),(e['id'],page,anchor)
  reports.append({'report':'E','path':'task1/reports/experiment1/experiment1.pdf','pdf_pages_one_based':[page],
   'printed_page_labels':['' if page==1 else 'i' if page==2 else str(page-2)],'section_or_figure':anchor,'verified_text_anchor':anchor})
 e['reports']=reports+original_process
r=d['reports']['E'];r.update(pages=25,pdf_sha256_at_navigation=sha(ROOT/r['path']),
 text_path=str((EV/'approved-text.txt').relative_to(ROOT)),text_sha256=sha(EV/'approved-text.txt'),
 page_text_sha256={str(i):hashlib.sha256(t.encode()).hexdigest() for i,t in enumerate(pages,1)},
 page_render_sha256={str(i):sha(EV/f'render200/approved/page-{i:02d}.png') for i in range(1,26)},
 binding_boundary='SC-PROJECT-SOURCES-SYNC-003 current accepted-report navigation only. Previous 22-page C receipts remain historical; current source/render review is in the task report evidence.')
d['navigation_revision']={'task_id':'SC-PROJECT-SOURCES-SYNC-003','date':'2026-09-29','previous_22_page_navigation_commit':'4483f520eabb5358d1f35cf5c33a81d3b01e47e0','previous_navigation_sha256':old_hash,'notebook_and_process_bindings_changed':False,'source':'user-accepted 25-page Experiment PDF; exact per-page extracted anchors checked'}
P.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
lines=['# 实验一教师要求与实际作业入口','','这是当前读者导航，不是验收总表。机器定位见 [teacher_delivery_mapping.json](teacher_delivery_mapping.json)。本次仅将 Experiment 入口迁移到用户已验收25页版本；Notebook 与 Process 绑定不变，旧22页审核保留其历史范围。','',
'**B**：[基础 Notebook](../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb)；**L**：[系统 Notebook](../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb)。单元从0开始；JSON保留原stable ID/source hash。','',
'**E**：[Experiment PDF](../../reports/experiment1/experiment1.pdf)，25页；**P**：[Process PDF](../../reports/process1/process1.pdf)，12页送审稿。页码均含封面，是PDF物理页。Experiment正文印刷页1对应物理页3；其封面与目录分别为物理页1、2。','',
'| 导航 | 教师/阶段要求 | Notebook 单元 | PDF 页码与章节 |','|---|---|---|---|']
for e in d['entries']:
 nbs='；'.join(n['notebook']+' '+','.join(str(c['index_zero_based']) for c in n['cells']) for n in e['notebooks'])
 refs='；'.join(r['report']+' '+','.join(map(str,r['pdf_pages_one_based']))+'（'+r['section_or_figure']+'）' for r in e['reports'])
 lines.append(f"| {e['id']} | {e['topic']} | {nbs} | {refs} |")
lines+=['','G1 R01—R16、G2 R01—R10 的原要求映射保留在JSON；G3分区与自动发布规则来自用户授权，不倒写为教师规定。','',
'教师课件第26页规定10月5日前将 `.ipynb` 与报告压缩，以学号_姓名_实验一命名；未给具体截止时刻。本次为REVIEW_ONLY，未发送教师。Process原始互动素材、批准annotation spec、Evidence Lock和网页GPT/用户最终验收仍按独立状态处理。','',
'[当前审阅入口](REVIEW_PACKET.md)区分新报告集成与历史FULL复算。本轮没有重新运行全量数据或实验模型。']
P.with_suffix('.md').write_text('\n'.join(lines)+'\n')
print('Updated 22 navigation entries; all new Experiment anchors found in actual physical pages.')
