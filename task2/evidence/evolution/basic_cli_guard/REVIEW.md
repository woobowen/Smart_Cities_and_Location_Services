# Basic NSGA runner: CLI-only repair

The original five basic runs and all other checked EA artifacts remain byte
identical. Their executed runner SHA is still
`76a143f0a03a06b23f4f162fd332a42befeffa9219175e9aae7ded56017fb5fc`;
`source_before.py` preserves those bytes. The current CLI revision is
`48e654a605dc9e1ceeff1dd253f97b05231c540e62f84e123e802faad23e7dc2`.

`--help` now exits before scientific imports. Existing directories, files and
symlinks are rejected; fresh experiments must use a new `--output` directory.
The default path is unchanged and refuses the existing reviewed run. The
scientific main body and conversion function are AST-identical after excluding
only output-path selection and directory creation.

The author executed12 direct/module CLI cases with `-S -B` (no site-packages or
bytecode writes), plus isolated fresh-path parsing. The306 protected result,
aggregate and figure hashes did not change. See `verify_guard.py`, `before.json`
and `result.json`. No EA generation, model training, figure build or statistical
replicate was executed. R's independent follow-up is recorded separately.
