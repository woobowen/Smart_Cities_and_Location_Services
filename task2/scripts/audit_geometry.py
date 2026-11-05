"""Conditional local-plane audit; an ellipsoid assumption is not a source-datum claim."""
from pathlib import Path
import json
import numpy as np
from pyproj import Geod
from task2.src.dispatch_data import load_data,ROOT


def main():
    b=load_data();c=b.checkins.set_index('source_row');t=b.trips
    a,z=c.loc[t.origin_source_row],c.loc[t.destination_source_row]
    _,_,d=Geod(ellps='WGS84').inv(a.longitude.to_numpy(),a.latitude.to_numpy(),z.longitude.to_numpy(),z.latitude.to_numpy())
    plane=np.hypot(t.dx-t.ox,t.dy-t.oy)*1000;relative=(plane-d)/d
    result={'identity':'conditional mathematical geometry audit; not a datum proof',
      'ellipsoid_assumption':'WGS84 for reference computation only; source_crs remains UNVERIFIED',
      'n_proxy_pairs':len(t),'euclidean_planar_vs_ellipsoid_relative_error_min':float(relative.min()),
      'max':float(relative.max()),'median':float(np.median(relative)),
      'max_abs_distance_difference_m':float(np.abs(plane-d).max()),
      'manhattan_vs_euclidean_ratio_range':[float((t.trip_km.to_numpy()*1000/plane).min()),float((t.trip_km.to_numpy()*1000/plane).max())],
      'source_csv_sha256':b.audit['sha256']}
    p=ROOT/'task2/evidence/conditional_geometry_check.json';p.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
