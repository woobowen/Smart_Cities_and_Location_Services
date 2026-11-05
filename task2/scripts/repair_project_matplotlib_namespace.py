"""Repair legacy system-site mpl_toolkits shadowing inside the existing project venv only."""
import sys
import sysconfig
from pathlib import Path


def main():
    if sys.prefix==sys.base_prefix:
        raise RuntimeError('This repair may only write inside an active virtual environment')
    site=Path(sysconfig.get_path('purelib'))
    toolkit=site/'mpl_toolkits/mplot3d/axes3d.py'
    if not toolkit.is_file():raise FileNotFoundError(toolkit)
    # Ubuntu matplotlib3.6's .pth otherwise fixes the namespace to its old system toolkit,
    # even when matplotlib itself resolves to the project's newer compatible installation.
    line='import mpl_toolkits, sysconfig; mpl_toolkits.__path__ = [sysconfig.get_path("purelib") + "/mpl_toolkits"] + list(mpl_toolkits.__path__)\n'
    target=site/'smartcities_matplotlib_namespace.pth'
    if target.exists() and target.read_text()!=line:
        raise RuntimeError('Existing namespace configuration differs; preserve it for review')
    target.write_text(line)
    print(target)


if __name__=='__main__':main()
