"""Independent exact comparison of hash-recovered old fusion bytes with replay."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import hashlib
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',type=Path,required=True)
    args=parser.parse_args()
    capture=args.snapshot.resolve()
    previous=capture/'surviving_prior_receipts'
    old_receipt=previous/'task2/evidence/independent_ea_on_rl/policy_result.json'
    expected=next(row['source_front_sha256'] for row in json.loads(old_receipt.read_text())['fusion'] if row['phase']=='final_v1')
    recovered=capture/'hash_verified_original_recovery/fusion_fronts.json'
    current=ROOT/'task2/results/rl/final_v1/fusion_fronts.json'
    assert sha(recovered)==expected,'Recovered bytes do not match the original independently recorded SHA'
    before,after=json.loads(recovered.read_text()),json.loads(current.read_text())
    assert set(before)==set(after)
    equal_fields=changed_runtime=frames=0
    for name in before:
        assert len(before[name])==len(after[name])
        for old,new in zip(before[name],after[name]):
            assert set(old)==set(new)
            for key in old:
                if key=='runtime':
                    assert isinstance(old[key],(int,float)) and isinstance(new[key],(int,float))
                    changed_runtime+=int(old[key]!=new[key])
                else:
                    assert old[key]==new[key],f'Unexpected changed field: {name}/{frames}/{key}'
                    equal_fields+=1
            frames+=1
    result=dict(reviewer='/root/evolution',identity='APPENDED_RECOVERED_OLD_FRONT_VS_FIXED_MODEL_REPLAY',
        completed_utc=datetime.now(timezone.utc).isoformat(),verifier_sha256=sha(__file__),
        prior_independent_receipt_sha256=sha(old_receipt),
        prior_full_front_sha256=expected,recovered_old_full_front_sha256=sha(recovered),
        replayed_full_front_sha256=sha(current),recovered_bytes_cryptographically_match_prior_receipt=True,
        frame_count=frames,non_runtime_fields_exactly_equal=equal_fields,changed_runtime_fields=changed_runtime,
        exact_equal_scope='Full objective F, t, selected point, NFE and selected local matching pairs, including all list order and numeric values.',
        limits='This verifies actual recovery of only the original fusion_fronts.json bytes. The four original full day_metrics.json files and their per-day runtime bytes remain unavailable; no recovery is claimed for them.',
        status='PASS_ONLY_RUNTIME_FIELDS_CHANGED')
    (OUT/'recovered_front_result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Recovered old raw SHA verified; frames',frames,'exact non-runtime fields',equal_fields,'changed runtime fields',changed_runtime)


if __name__=='__main__':main()
