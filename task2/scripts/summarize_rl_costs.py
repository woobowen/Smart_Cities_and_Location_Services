"""Derived cost diagnostics from raw metrics, with explicit scope and assumptions."""
from pathlib import Path
import hashlib,json
import pandas as pd
TASK=Path(__file__).resolve().parents[1];ROOT=TASK/'results/rl'
index=json.loads((ROOT/'ACTIVE_RUNS.json').read_text());rows=[];inputs={}
for run in index['runs']:
 if not run['active']:continue
 p=TASK/run['metrics_path'];inputs[str(p.relative_to(TASK))]=hashlib.sha256(p.read_bytes()).hexdigest()
 for r in json.loads(p.read_text()):
  for cost in [0,1,3,5]:
   rows.append(dict(run_id=run['run_id'],identity=run['identity'],policy=r['policy'],day_seed=r['day_seed'],
               hypothetical_cost_per_empty_km=cost,accepted_fare=r['revenue'],pickup_km=r['pickup_km'],reposition_km=r['empty_km'],
               total_empty_km=r['pickup_km']+r['empty_km'],fare_minus_reposition_cost=r['revenue']-cost*r['empty_km'],
               fare_minus_all_empty_cost=r['revenue']-cost*(r['pickup_km']+r['empty_km'])))
p=ROOT/'COST_SCENARIOS.csv';pd.DataFrame(rows).to_csv(p,index=False)
(ROOT/'COST_SCENARIOS.json').write_text(json.dumps(dict(source_sha256=inputs,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 scope='Derived illustrative fare minus explicit empty-distance costs, not measured profitability. Pickup plus reposition are empty; excludes loaded travel/fixed/operatingcosts. Toy proxy currency, cost rates0/1/3/5 predeclared diagnostics, no retuning or realprice claim.'),indent=2))
print('derived rows',len(rows))
