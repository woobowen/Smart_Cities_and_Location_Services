"""Frozen final confirmation in a fresh output directory; existing runs are preserved."""
from pathlib import Path
import argparse
import sys,json
TASK=Path(__file__).resolve().parents[1]


def parse_args(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=TASK/'results/rl/final_v1',
                        help='Fresh output directory; any existing target is refused before loading data or models')
    args=parser.parse_args(argv)
    candidate=args.output.expanduser()
    if candidate.is_symlink() or candidate.resolve().exists():
        parser.error('Output already exists; preserve it and choose a fresh --output directory.')
    args.output=candidate.resolve()
    return args


def main(argv=None):
    # Parse help and reject existing outputs before importing the experiment stack.
    args=parse_args(argv)
    import pandas as pd
    sys.path.insert(0,str(TASK/'src'));sys.path.insert(0,str(TASK/'scripts'))
    from run_rl import fit,evaluate,json_dump,sha
    from rl_dispatch import region_long_term_value,make_q_km,km_fare,greedy_nearest
    from rl_extensions import cost_aware_repositioner
    from rl_fusion import NSGADispatch
    contract_path=TASK/'evidence/rl/FINAL_SELECTION.json'
    contract=json.loads(contract_path.read_text())
    assert contract['state']=='FROZEN_BEFORE_HELDOUT_TEST'
    out=args.output
    out.mkdir(parents=True,exist_ok=False)
    freeze=out/'selection_contract.json'
    freeze.write_bytes(contract_path.read_bytes())
    data=TASK/'results/data'
    train=pd.read_csv(data/'trips_train.csv');init=pd.read_csv(data/'checkins_train.csv')
    val=pd.read_csv(data/'trips_validation.csv')
    # Validation monitoring now overlaps refit data: no checkpoint selection.
    dataid={f.name:sha(f) for f in [data/'trips_train.csv',data/'checkins_train.csv']}
    models={}
    for fleet in [40,60,100]:
        models[fleet]=fit(out/f'q_f{fleet}',train,init,val,fleet=fleet,n=300,data_identity=dataid)
    single_b1=fit(out/'q_beta1',train,init,val,n=300,beta=1,data_identity=dataid)
    double_b1=fit(out/'double_beta1',train,init,val,n=300,beta=1,double=True,data_identity=dataid)
    json_dump(out/'before_test_manifest.json',dict(frozen_contract_sha256=sha(freeze),runner_sha256=sha(__file__),data_identity=dataid,
               model_paths=[str(p.relative_to(out)) for p in out.glob('*/model.npz')],model_paths_base='output_directory',final_training='all first70percent dates,300actual simulations each; val monitoring in-training after refit, no epoch selection',
               fixed_test_seeds=list(range(50000,50005)),evaluation_identity='heldout proxy-date simulation; not real operational days'))
    test=pd.read_csv(data/'trips_test.csv')
    for fleet,qt in models.items():
        LT=region_long_term_value(qt.V)
        evaluate(out/f'fleet{fleet}',test,init,fleet,[('greedy',greedy_nearest,None),('km',km_fare,None),('qkm',make_q_km(LT,.5),None)],split='heldout_test')
    V=models[60].V;LT=region_long_term_value(V)
    knee=NSGADispatch(LT,seed=2024,choice='knee');constraint=NSGADispatch(LT,seed=2024,choice='constraint')
    evaluate(out/'enhancements',test,init,60,[('greedy',greedy_nearest,None),('km',km_fare,None),('qkm',make_q_km(LT,.5),None),
        ('km_move3',km_fare,cost_aware_repositioner(V,3)),('qkm_move3',make_q_km(LT,.5),cost_aware_repositioner(V,3)),
        ('qkm_move5',make_q_km(LT,.5),cost_aware_repositioner(V,5)),
        ('q_beta1',make_q_km(region_long_term_value(single_b1.V),1),None),
        ('double_beta1',make_q_km(region_long_term_value(double_b1.V),1),None),
        ('qnsga_knee',knee,None),('qnsga_constraint',constraint,None)],split='heldout_test')
    json_dump(out/'fusion_fronts.json',dict(knee=knee.fronts,constraint=constraint.fronts))
    json_dump(out/'completion_manifest.json',dict(contract_sha256=sha(freeze),test_data_sha256=sha(data/'trips_test.csv'),runner_sha256=sha(__file__),
               metric_paths=[str(p.relative_to(out)) for p in out.glob('*/day_metrics.json')],metric_paths_base='output_directory',state='COMPLETED_HELDOUT_EVALUATION_NO_RETUNING'))


if __name__=='__main__':
    main()
