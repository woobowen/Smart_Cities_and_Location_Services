"""Small, standard-library-only guards for immutable experiment launchers."""
import argparse
from pathlib import Path


def require_fresh_output(parser, output):
    """Validate without reading inputs, importing experiments, or creating files."""
    target = Path(output).expanduser()
    if target.is_symlink() or target.exists():
        parser.error('Output already exists; preserve it and choose a fresh --output directory.')
    return target.resolve()


def fixed_output_args(default, description, argv=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--output', type=Path, default=default,
                        help='Fresh output directory; existing targets are refused before loading inputs')
    args = parser.parse_args(argv)
    args.output = require_fresh_output(parser, args.output)
    return args
