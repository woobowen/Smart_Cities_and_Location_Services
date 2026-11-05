"""Generate from public teacher-starter code in an isolatedroot, without dataZIPs."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[3];TASK=ROOT/'task2';OUT=Path(__file__).resolve().parent
script=TASK/'scripts/build_notebooks.py';starter=TASK/'teacher_materials/advanced/实验3 多目标与强化学习派单（学生版）.ipynb'
rows=[]
with tempfile.TemporaryDirectory(prefix='dispatch_public_nbgen_') as directory:
 d=Path(directory);sp=d/'task2/scripts/build_notebooks.py';sp.parent.mkdir(parents=True);shutil.copyfile(script,sp)
 st=d/'task2/teacher_materials/advanced'/starter.name;st.parent.mkdir(parents=True);shutil.copyfile(starter,st)
 p=subprocess.run([str(ROOT/'.venv/bin/python'),str(sp)],capture_output=True,text=True,check=True)
 assert not (d/'归档.zip').exists() and not (d/'实验2(1).zip').exists()
 for name in ['作业2_运力调度_完成版.ipynb','实验3_多目标与强化学习派单_完成版.ipynb']:
  gen=json.loads((d/'task2/notebooks'/name).read_text());cur=json.loads((TASK/'notebooks'/name).read_text())
  def payload(nb):return [(c['cell_type'],''.join(c['source'])) for c in nb['cells']]
  assert payload(gen)==payload(cur),name
  rows.append(dict(notebook=name,generated_source_identical_to_executed_current=True,cells=len(gen['cells']),executed_current_sha256=hashlib.sha256((TASK/'notebooks'/name).read_bytes()).hexdigest()))
report=dict(reviewer='/root/reinforcement',scope='Independent regeneration-source integration, notanother fullNotebook execution',generator_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),starter_sha256=hashlib.sha256(starter.read_bytes()).hexdigest(),source_zip_absent=True,original_executed_notebooks_untouched=True,checks=rows,status='PASS_IN_STATED_SCOPE')
(OUT/'public_notebook_generator_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
