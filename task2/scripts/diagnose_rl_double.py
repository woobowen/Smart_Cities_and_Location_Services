"""Descriptive Double-Q policy-value diagnostics; no training."""
from pathlib import Path
try:
    from .experiment_cli import fixed_output_args
except ImportError:  # Direct-file invocation has no package context.
    from experiment_cli import fixed_output_args
TASK=Path(__file__).resolve().parents[1]


def parse_args(argv=None):
    return fixed_output_args(TASK/"results/rl/double_v2_rngfix",__doc__,argv)


def main(argv=None):
    args=parse_args(argv)
    out=args.output
    out.mkdir(parents=True,exist_ok=False)
    import sys,json
    import numpy as np
    sys.path.insert(0,str(TASK/'src'));sys.path.insert(0,str(TASK/'scripts'))
    from run_rl import load_model,sha,json_dump
    from run_rl_followup import value_diagnostics
    root=TASK/'results/rl/double_v2_rngfix'
    rows=[]
    for name in ['q','double']:
     for seed in range(2024,2029):
      p=root/f'{name}_b1_s{seed}'
      if not p.exists():p=TASK/'results/rl/double_validation_v1'/f'{name}_b1_s{seed}'
      qt,meta=load_model(p)
      for day in range(50000,50005):
       tr=root/f'{name}_b1_s{seed}_validation'/f'trace_beta1_{day}.json'
       metrics,points=value_diagnostics(json.loads(tr.read_text()),qt.V)
       rows.append(dict(learner=name,train_seed=seed,day_seed=day,model_sha256=sha(p/'model.npz'),trace_sha256=sha(tr),**metrics))
    json_dump(out/'value_bias_diagnostics.json',dict(scope='V minus realized discounted return under each actual policy, conditional on idle states; not a direct estimate of optimal-value bias because policies/state visitation differ',rows=rows))
    for name in ['q','double']:
     a=[r for r in rows if r['learner']==name]
     print(name,{k:float(np.mean([r[k] for r in a])) for k in ['mean_estimate','mean_policy_return','optimism_gap','mae_to_policy_return']})


if __name__=="__main__":
    main()
