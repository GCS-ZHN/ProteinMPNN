#!/usr/bin/env python3
from pathlib import Path
import sys


def create(path: Path, interpreter: str = sys.executable):
    """Create an executable file for the given python script."""
    path = path.absolute().resolve()
    if str(path) == __file__:
        return

    executable_path = Path('bin') / path.stem
    executable_path.parent.mkdir(exist_ok=True)
    with open(executable_path, 'w') as executable_file:
        print('#!/usr/bin/env bash', file=executable_file)
        print(f'{interpreter} {path} $@', file=executable_file)
    executable_path.chmod(0o755)

if __name__ == '__main__':
    for path in Path('helper_scripts').glob('*.py'):
        create(path)
    
    for path in Path.cwd().glob('*.py'):
        create(path)