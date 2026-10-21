"""Back up repository history and public build only; no databases or secrets."""
from pathlib import Path
import hashlib,json,subprocess,tarfile
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'.cache/public-backup'

def main():
 DEST.mkdir(parents=True,exist_ok=True)
 bundle=DEST/'repository.bundle'
 subprocess.run(['git','bundle','create',str(bundle),'--all'],cwd=ROOT,check=True)
 subprocess.run(['git','bundle','verify',str(bundle)],cwd=ROOT,check=True)
 source=ROOT/'dist'
 if not (source/'index.html').is_file():raise ValueError('Verified public build required')
 files=[p for p in source.rglob('*') if p.is_file()]
 if any(p.is_symlink() or p.name.startswith('.env') or p.suffix in ('.sqlite','.db','.bundle') for p in files):raise ValueError('Unexpected private or non-public build material')
 archive=DEST/'public-site.tar.gz'
 with tarfile.open(archive,'w:gz') as tar:
  for file in files:tar.add(file,arcname=file.relative_to(source).as_posix(),recursive=False)
 with tarfile.open(archive) as tar:
  if len(tar.getmembers())!=len(files):raise ValueError('Backup file count differs')
 checks={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (bundle,archive)}
 (DEST/'checksums.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'publicFiles':len(files),'databaseDataIncluded':False,'backups':checks}))
if __name__=='__main__':main()
