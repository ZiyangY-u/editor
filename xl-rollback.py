import sys
import os
from pathlib import Path
import shutil

if __name__ == '__main__':
    if len(sys.argv) < 2: print('No file given... exit'); exit(0)

    fp = sys.argv[1]
    basename = Path(fp).stem
    print(f'basename: {basename}')

    file_path = os.path.abspath(fp)
    directory = os.path.dirname(file_path)
    print(f'directory: {directory}')

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    back_file = ''
    for f in files:
        _fp = Path(f).name
        if not _fp.startswith(basename + '-'): continue;
        if back_file == '' or _fp > back_file:
            back_file = _fp
    print('rollback from:', back_file)
    shutil.copy(back_file, fp)
