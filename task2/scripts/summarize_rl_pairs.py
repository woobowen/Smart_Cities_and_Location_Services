"""Traceable descriptive paired simulation-day differences, primary/secondary separate."""
from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
from scipy.stats import t
TASK=Path(__file__).resolve().parents[1]
for folder,subdir,pairs in [('final_v1','enhancements',[('km_move3','qkm'),('km_move3','km'),('qkm_move5','qkm'),('double_beta1','q_beta1'),('qnsga_constraint','qkm')]),
                           ('final_montecarlo_v1','',[('km_move3','qkm'),('km_move3','km'),('qkm_move5','qkm')])]:
 root=TASK/'results/rl'/folder;p=root/subdir/'day_metrics.json'
 if not p.exists():continue
 d=pd.DataFrame(json.loads(p.read_text()));rows=[]
 for candidate,reference in pairs:
  a=d[d.policy==candidate].set_index('day_seed');b=d[d.policy==reference].set_index('day_seed');keys=sorted(set(a.index)&set(b.index))
  for col in ['revenue','answer_rate','avg_pickup','completed_revenue','empty_km']:
   diff=(a.loc[keys,col]-b.loc[keys,col]).to_numpy();mean=float(diff.mean());sd=float(diff.std(ddof=1));half=float(t.ppf(.975,len(diff)-1)*sd/np.sqrt(len(diff)))
   rows.append(dict(candidate=candidate,reference=reference,metric=col,n_paired_simulated_days=len(diff),seeds=keys,mean_difference=mean,sample_sd=sd,descriptive_t95_low=mean-half,descriptive_t95_high=mean+half,differences=diff.tolist()))
 (root/'paired_differences.json').write_text(json.dumps(dict(scope='Descriptive paired-day t interval over independently seeded resamplings of same heldout proxy-date pool, one trained model; not populationconfidence or new real operating dates. Primary5 and secondary20 never silently pooled.',source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows),indent=2))
 print(folder,[(r['candidate'],r['reference'],round(r['mean_difference'],2),round(r['descriptive_t95_low'],2),round(r['descriptive_t95_high'],2)) for r in rows if r['metric']=='revenue'])
