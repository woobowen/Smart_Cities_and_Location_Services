from pathlib import Path
import sys
import pandas as pd
TASK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TASK/'src'));sys.path.insert(0,str(TASK/'scripts'))
from run_rl import load_model,evaluate,json_dump,sha
from rl_dispatch import region_long_term_value,make_q_km,km_fare
from rl_extensions import cost_aware_repositioner
out=TASK/'results/rl/component_ablation_v1';out.mkdir(parents=True,exist_ok=True)
qt,_=load_model(TASK/'results/rl/development_v1/q_f60_s2024');LT=region_long_term_value(qt.V)
json_dump(out/'contract.json',dict(trigger='Cost-awareλ3 QKM movement passed gross revenue/response validation safeguard; isolate long-term edge weighting vs movement on identicalV/map/day inputs',factorial='KM vsQKM × nomove vsλ3move;λ5 retained as cost tradeoff sensitivity',source_sha256=sha(__file__),parent_model_sha256=sha(TASK/'results/rl/development_v1/q_f60_s2024/model.npz'),split='validation'))
val=pd.read_csv(TASK/'results/data/trips_validation.csv');init=pd.read_csv(TASK/'results/data/checkins_train_inner.csv')
evaluate(out,val,init,60,[('km',km_fare,None),('qkm',make_q_km(LT,.5),None),('km_move3',km_fare,cost_aware_repositioner(qt.V,3)),('qkm_move3',make_q_km(LT,.5),cost_aware_repositioner(qt.V,3)),('qkm_move5',make_q_km(LT,.5),cost_aware_repositioner(qt.V,5))])
