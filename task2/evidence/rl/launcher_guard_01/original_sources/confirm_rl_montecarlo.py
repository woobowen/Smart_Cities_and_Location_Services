"""One bounded fresh-resampling confirmation of frozen models, no parameter choice."""
from pathlib import Path
import sys,json
import pandas as pd
TASK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TASK/'src'));sys.path.insert(0,str(TASK/'scripts'))
from run_rl import load_model,evaluate,sha,json_dump
from rl_dispatch import region_long_term_value,make_q_km,km_fare
from rl_extensions import cost_aware_repositioner
out=TASK/'results/rl/final_montecarlo_v1';out.mkdir(parents=True,exist_ok=True)
qt,_=load_model(TASK/'results/rl/final_v1/q_f60');LT=region_long_term_value(qt.V)
json_dump(out/'contract.json',dict(trigger='Original frozen5day confirmation gives selectedKMmove3 gross difference640.81 with descriptive pairedt95[-64.07,1345.68]; clarify simulation MonteCarlo variability without altering that experiment or method',
     fixed_seeds=list(range(60000,60020)),models='same frozen full70 q_f60, no retraining or checkpoint choice',model_sha256=sha(TASK/'results/rl/final_v1/q_f60/model.npz'),
     policies=['km','qkm','km_move3','qkm_move5'],scope='20new independently seeded proxy simulation resamplings of same heldout datepool, not20new real dates or population evidence',
     stop='one20simulation batch only; report every seed; no post-test tuning or winner switch',source_sha256=sha(__file__),selection_contract_sha256=sha(TASK/'evidence/rl/FINAL_SELECTION.json')))
data=TASK/'results/data';test=pd.read_csv(data/'trips_test.csv');init=pd.read_csv(data/'checkins_train.csv')
evaluate(out,test,init,60,[('km',km_fare,None),('qkm',make_q_km(LT,.5),None),('km_move3',km_fare,cost_aware_repositioner(qt.V,3)),('qkm_move5',make_q_km(LT,.5),cost_aware_repositioner(qt.V,5))],seeds=range(60000,60020),split='heldout_secondary_montecarlo_confirmation')
