#!/usr/bin/env python3
"""Build the MOO figure set in a temporary tree with no real-data raw inputs."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    originals=sorted(list((ROOT/'task2/figures/formal').glob('evolution_*.png'))+
                     list((ROOT/'task2/figures/candidates').glob('evolution_*.png')))
    files=[ROOT/'templates/latex/common/p2_cloud_sorbet_colors.tex',
           ROOT/'task2/scripts/build_figures.py',ROOT/'task2/scripts/build_evolution_figures.py',
           ROOT/'task2/src/evolution.py',ROOT/'task2/src/front_metrics.py',
           ROOT/'task2/evidence/evolution/FINAL_CONFIRMATION_CONTRACT.json']
    files += list((ROOT/'task2/results/evolution/basic').glob('basic_nsga2_seed*.json'))
    files += list((ROOT/'task2/public_results/evolution').rglob('*.json'))
    result=dict(scope='Fresh temporary tree containing only public aggregate projections, public code/palette/frozen contract and five separately synthetic basic-task JSONs.',
                verifier_sha256=sha(__file__),copied_input_sha256={str(p.relative_to(ROOT)):sha(p) for p in files},
                private_real_raw_inputs_copied=False)
    with tempfile.TemporaryDirectory(prefix='smartcities-public-figures-') as directory:
        target=Path(directory)
        for source in files:
            copied=target/source.relative_to(ROOT)
            copied.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,copied)
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        run=subprocess.run([sys.executable,str(target/'task2/scripts/build_evolution_figures.py')],
                           cwd=target,env=env,text=True,capture_output=True)
        result.update(exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr)
        if run.returncode:
            raise RuntimeError(f'Public-only figure build failed: {run.stderr}')
        comparisons=[]
        for original in originals:
            copied=target/original.relative_to(ROOT)
            if not copied.is_file():
                raise AssertionError(f'Missing fresh aggregate figure {original.name}')
            comparisons.append(dict(path=str(original.relative_to(ROOT)),original_png_sha256=sha(original),
                                    public_only_png_sha256=sha(copied),byte_identical=sha(original)==sha(copied)))
        result.update(comparisons=comparisons,all_png_byte_identical=all(v['byte_identical'] for v in comparisons))
        if not result['all_png_byte_identical']:
            raise AssertionError('Public-only figure output changed numerical/visual rendering')
    output=ROOT/'task2/evidence/evolution/public_only_figure_build.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print('Public-only build successful; byte-identical PNGs',len(originals))


if __name__=='__main__':
    main()
