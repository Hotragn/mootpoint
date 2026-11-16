"""Build a credential-free local reproduction archive from explicit path/type allowlists."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
SUFFIXES={'.py','.md','.txt','.json','.jsonl','.csv','.tsv','.png','.svg','.drawio','.html'}
DIRECTORIES=['analysis','data','harness','tests','paper','runs/dev','runs/test','runs/test_r1','runs/pilot']

def main():
    files=set()
    for name in DIRECTORIES:
        for path in (ROOT/name).rglob('*'):
            relative=path.relative_to(ROOT)
            if (not path.is_file() or path.is_symlink() or
                any(part.startswith('.') or part in {'build','__pycache__'} for part in relative.parts) or
                path.suffix not in SUFFIXES):continue
            files.add(relative)
    for name in ['README.md','DATA_LICENSES.md','PLAN.md','DECISIONS.md','RUBRIC.md',
                 'requirements.txt','paper/template/apart_template.docx',
                 'submission/FORM-ANSWERS.md','submission/UPGRADE-NOTES.md',
                 'submission/Pettugani_MootPoint_AI-Epistemics-2026.pdf',
                 'submission/Pettugani_MootPoint_AI-Epistemics-2026_slides.pdf']:
        path=ROOT/name
        assert path.exists(),name
        files.add(Path(name))
    manifest={str(p):hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(files)}
    target=ROOT/'submission/MootPoint-reproducibility.zip'
    with ZipFile(target,'w',compression=ZIP_DEFLATED,compresslevel=6) as archive:
        for name in sorted(files):archive.write(ROOT/name,str(Path('MootPoint')/name))
        archive.writestr('MootPoint/MANIFEST.sha256.json',json.dumps(manifest,indent=2)+'\n')
    with ZipFile(target) as archive:
        assert archive.testzip() is None
        for name,sha in manifest.items():
            assert hashlib.sha256(archive.read('MootPoint/'+name)).hexdigest()==sha
        assert all(not any(p in {'.env','.git','.venv','cache.sqlite'} for p in Path(n).parts) for n in archive.namelist())
    print(f'Archive verified: {len(files)} files, {target.stat().st_size/1024/1024:.1f} MiB')

if __name__=='__main__':main()
