"""Publication-boundary tests: retain objectives, reject membership/context."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from project_public_results import project_run,project_km,project_fusion_collection


def all_keys(value):
    if isinstance(value,dict):
        return set(value).union(*(all_keys(v) for v in value.values()))
    if isinstance(value,list):
        return set().union(*(all_keys(v) for v in value))
    return set()


def test_real_run_projection_keeps_numeric_objectives_without_membership():
    source=dict(F=[[-10.1234567890123,2.5],[0.,0.]],n_obj=2,n_eval=30100,algorithm='nsga2',
        genes=[[1,0],[0,0]],pairs=[[[9,2]],[]],initial_genes=[[1,0]],
        cand=[[1,2]],n_cand=[2],trip_indices=[98],source_row=[7],fare=[10.1234567890123],
        history=[dict(generation=0,HV=.5,F=[[-10.1234567890123,2.5]],pairs=[[[9,2]]])],
        provenance=dict(evolution_sha256='a'*64,source_data_sha256='b'*64,
                        nested_private=dict(pickup=[[2.5]],driver_zone=[2]),pairs=[[[9,2]]]))
    public=project_run(source)
    assert public['F']==source['F'] and public['history'][0]['F']==source['history'][0]['F']
    assert public['provenance']==dict(evolution_sha256='a'*64,source_data_sha256='b'*64)
    assert not all_keys(public)&{'genes','pairs','initial_genes','cand','n_cand','trip_indices','source_row','fare','pickup','driver_zone','nested_private'}


def test_scalar_km_projection_removes_binding_but_retains_scalar_front():
    source=dict(n_obj=2,runs=[dict(lam=.5,F=[-10.,2.],pairs=[(3,8)],gene=[1,2],fare=[10.])],
                ideal=[-100.,0.],nadir=[0.,30.],provenance={})
    public=project_km(source)
    assert public['runs']==[dict(lam=.5,F=[-10.,2.])]
    assert not all_keys(public)&{'pairs','gene','fare'}


def test_fusion_retains_only_objective_point_selection():
    source={'knee':[dict(t=5,F=[[-10.,2.],[0.,0.]],selected=0,n_eval=1240,runtime=.01,
                        pairs=[(3,8)],genes=[[1,2]],weights=[[10.]],drv_zone=[2])],
            'constraint':[]}
    public=project_fusion_collection(source)
    assert public['knee'][0]['F']==source['knee'][0]['F']
    assert public['knee'][0]['selected']==0
    assert set(public['knee'][0])=={'t','F','selected','n_eval','runtime'}
    assert not all_keys(public)&{'pairs','genes','weights','drv_zone'}
