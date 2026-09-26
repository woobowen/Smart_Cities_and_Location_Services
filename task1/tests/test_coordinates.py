import math
import pytest
from task1.workflow.coordinates import working_xy, conditional_contract, conditional_adapter
from task1.workflow.coordinate_review import validate_coordinates


def test_origin_and_known_direction_independent_proj():
    m=conditional_contract()['analysis_model'];lon=m['origin_lon_degrees'];lat=m['origin_lat_degrees']
    points=[[lon,lat],[lon+.001,lat],[lon,lat+.001],[lon,lat]]
    xy=working_xy(points)
    assert xy[0]==[0.,0.] and xy[-1]==[0.,0.]
    assert 90<xy[1][0]<100 and 110<xy[2][1]<112
    r=validate_coordinates({'fixture:x':[[0,1,2,3],points]})
    assert r['status']=='VERIFIED' and r['max_coordinate_crosscheck_error_m']<1e-6
    assert r['source_crs']=='UNVERIFIED' and r['source_datum_proven'] is False


@pytest.mark.parametrize('points',[[[0,0]],[[181,31]],[[121,91]],[[True,31]],[[121,float('nan')]],[[121]]])
def test_invalid_or_outside_domain_rejected(points):
    with pytest.raises(ValueError):working_xy(points)


def test_adapter_preserves_raw_and_indices():
    m=conditional_contract()['analysis_model'];p=[m['origin_lon_degrees'],m['origin_lat_degrees']]
    raw=[[1,1,4],[p,p,p]]
    r=conditional_adapter('x',raw)
    assert r['indices']==[0,1,2] and r['timestamps']==[1,1,4]
    r['timestamps'][0]=999
    assert raw[0]==[1,1,4]
