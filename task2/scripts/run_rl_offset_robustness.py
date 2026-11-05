"""Validation robustness to offset-inconsistent proxy pairs."""
from pathlib import Path
try:
    from .experiment_cli import fixed_output_args
except ImportError:  # Direct-file invocation has no package context.
    from experiment_cli import fixed_output_args
TASK=Path(__file__).resolve().parents[1]


def parse_args(argv=None):
    return fixed_output_args(TASK/"results/rl/offset_robustness_v1",__doc__,argv)


def main(argv=None):
    args=parse_args(argv)
    out=args.output
    out.mkdir(parents=True,exist_ok=False)
    import sys
    import numpy as np,pandas as pd
    sys.path.insert(0,str(TASK/'src'));sys.path.insert(0,str(TASK/'scripts'))
    from run_rl import fit,evaluate,json_dump,sha
    from rl_dispatch import region_long_term_value,make_q_km,km_fare,greedy_nearest
    data=TASK/'results/data';train=pd.read_csv(data/'trips_train_inner.csv');val=pd.read_csv(data/'trips_validation.csv');init=pd.read_csv(data/'checkins_train_inner.csv')
    anomaly=pd.read_csv(TASK/'evidence/research_data/time_offset_anomalies.csv')
    keys=set(zip(anomaly.origin_source_row,anomaly.destination_source_row))
    keep=lambda d:np.array([(o,e) not in keys for o,e in zip(d.origin_source_row,d.destination_source_row)])
    filtered_train=train.loc[keep(train)].copy();filtered_val=val.loc[keep(val)].copy()
    filtered_train.to_csv(out/'filtered_inner.csv',index=False);filtered_val.to_csv(out/'filtered_validation.csv',index=False)
    json_dump(out/'robustness_contract.json',dict(trigger='Independent raw timestamp audit found12 local-clock proxy pairs violating10–180min UTC window; inspect sensitivity without overwriting teacher-local-clock primary model',train_removed=len(train)-len(filtered_train),validation_removed=len(val)-len(filtered_val),train_removed_during_operating_hours=int(((~keep(train)) & train.minute.between(360,1439)).sum()),test='not used; no anomalies exist in held-out partition per separate audit',source_sha256=sha(__file__),data_sha256={f.name:sha(f) for f in [data/'trips_train_inner.csv',data/'trips_validation.csv',TASK/'evidence/research_data/time_offset_anomalies.csv']}))
    qt=fit(out/'q_filtered',filtered_train,init,filtered_val,n=300,data_identity={f.name:sha(f) for f in [out/'filtered_inner.csv',out/'filtered_validation.csv']})
    evaluate(out/'validation',filtered_val,init,60,[('greedy',greedy_nearest,None),('km',km_fare,None),('qkm',make_q_km(region_long_term_value(qt.V)),None)])


if __name__=="__main__":
    main()
