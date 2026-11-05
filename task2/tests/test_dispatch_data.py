"""Known-answer time/space fixtures for the teacher proxy data contract."""
from datetime import date,timedelta
from pathlib import Path
import sys
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from dispatch_data import load_checkins,build_trips,temporal_split,KM_PER_LAT,KM_PER_LON


def test_utc_offset_is_minutes_and_coordinate_order_is_lon_lat(tmp_path):
    p=tmp_path/'checkins.csv'
    pd.DataFrame([dict(userId=1,venueId='v',venueCategoryId='c',venueCategory='fixture',
        latitude=40.61,longitude=-74.04,timezoneOffset=-240,
        utcTimestamp='Tue Apr 03 18:00:09 +0000 2012')]).to_csv(p,index=False)
    c=load_checkins(p)
    assert c.iloc[0].local==pd.Timestamp('2012-04-03 14:00:09')
    assert c.iloc[0].minute==840
    assert np.isclose(c.iloc[0].x,KM_PER_LON*.01)
    assert np.isclose(c.iloc[0].y,KM_PER_LAT*.01)


def test_gap_endpoints_and_same_day_are_inclusive_but_cross_day_rejected():
    # Two separate users exercise 10/180 minute endpoint inclusion and midnight.
    c=pd.DataFrame([
        [1,0.,0.,'2012-04-03 08:00',480,2],
        [1,1.,0.,'2012-04-03 08:10',490,3],
        [1,2.,0.,'2012-04-03 11:10',670,4],
        [2,0.,0.,'2012-04-03 23:55',1435,5],
        [2,2.,0.,'2012-04-04 00:05',5,6],
    ],columns=['userId','x','y','local','minute','source_row'])
    c['local']=pd.to_datetime(c['local'])
    t=build_trips(c)
    assert t[['origin_source_row','destination_source_row']].values.tolist()==[[2,3],[3,4]]
    assert t.gap_min.tolist()==[10.,180.]
    assert t.trip_km.tolist()==[1.,1.]
    assert t.fare.tolist()==[7.,7.]


def test_chronological_70_percent_and_training_inner_validation():
    dates=[date(2020,1,1)+timedelta(days=i) for i in range(20)]
    t=pd.DataFrame({'date':dates,'minute':[480]*20})
    s=temporal_split(t,validation_fraction=.2)
    assert len(s['trips_train'])==14
    assert len(s['trips_train_inner'])==11
    assert len(s['trips_validation'])==3
    assert len(s['trips_test'])==6
    assert s['trips_train_inner'].date.max()<s['trips_validation'].date.min()
    assert s['trips_validation'].date.max()<s['trips_test'].date.min()
