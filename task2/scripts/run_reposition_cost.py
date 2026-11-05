"""Cost-aware reposition validation using a frozen parent model."""
from pathlib import Path
try:
    from .experiment_cli import fixed_output_args
except ImportError:  # Direct-file invocation has no package context.
    from experiment_cli import fixed_output_args
TASK=Path(__file__).resolve().parents[1]


def parse_args(argv=None):
    return fixed_output_args(TASK/"results/rl/reposition_cost_validation_v1",__doc__,argv)


def main(argv=None):
    args=parse_args(argv)
    out=args.output
    out.mkdir(parents=True,exist_ok=False)
    import sys,json
    import pandas as pd
    sys.path.insert(0,str(TASK/'src'));sys.path.insert(0,str(TASK/'scripts'))
    from rl_dispatch import DEFAULT,region_long_term_value,make_q_km,km_fare
    from rl_extensions import cost_aware_repositioner
    from run_rl import load_model,evaluate,json_dump,sha
    parent=TASK/'results/rl/development_v1/q_f60_s2024'
    qt,meta=load_model(parent);LT=region_long_term_value(qt.V)
    json_dump(out/'followup_manifest.json',dict(trigger='V-only reposition adds ~5000km/day for gross revenue gain ~415 (QKM), so movement-value threshold must account for cost',
              conditions=[0,1,3,5],cost_status='hypothetical teaching currency/km, not observed vehicle expense',
              source_sha256={str(p.relative_to(TASK)):sha(p) for p in [Path(__file__),TASK/'src/rl_extensions.py']},
              parent_model_sha256=sha(parent/'model.npz'),split='validation',selection='compare separate gross revenue, response and empty km; no arbitrary combined quality score'))
    val=pd.read_csv(TASK/'results/data/trips_validation.csv');init=pd.read_csv(TASK/'results/data/checkins_train_inner.csv')
    policies=[('qkm',make_q_km(LT,.5),None)]
    for c in [0,1,3,5]:
        policies.append((f'qkm_move_cost{c}',make_q_km(LT,.5),cost_aware_repositioner(qt.V,c)))
    evaluate(out,val,init,60,policies)


if __name__=="__main__":
    main()
