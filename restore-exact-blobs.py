from pathlib import Path
import subprocess,json,hashlib,shutil,time
base=Path('/work/baseline');cand=Path('/work/candidate');ev=Path('/evidence')
files=['web/src/pages/agent/form/parser-form/pdf-form-fields.tsx','web/src/pages/agent/form/parser-form/pdf-form-fields.test.tsx']
overlay={f:(cand/f).read_bytes() for f in files}
def git(root,*args):
 r=subprocess.run(['git',*args],cwd=root,capture_output=True);r.check_returncode();return r.stdout
if not (base/'.git').exists():shutil.copytree(cand/'.git',base/'.git')
for root in [base,cand]:
 git(root,'config','--local','core.autocrlf','false');git(root,'config','--local','core.filemode','true');git(root,'config','--local','core.symlinks','true')
 git(root,'read-tree','HEAD');git(root,'checkout-index','--all','--force')
for f,b in overlay.items():(cand/f).write_bytes(b)
# baseline untracked new test may be present only if previous interrupted; it is our own temporary overlay.
new=base/files[1]
if new.exists():new.unlink()
result={}
for root in [base,cand]:
 rows=git(root,'ls-files','--stage','-z').split(b'\0');mismatch=[];count=0
 for row in rows:
  if not row:continue
  info,name=row.split(b'\t',1);mode,oid,stage=info.split();f=root/name.decode();count+=1
  if mode==b'120000':data=str(f.readlink()).encode()
  else:data=f.read_bytes()
  actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest().encode()
  if actual!=oid:mismatch.append(name.decode())
 result[root.name]={'head':git(root,'rev-parse','HEAD').decode().strip(),'tracked':count,'blob_mismatches':mismatch,'status':git(root,'status','--short','--untracked-files=normal').decode(),'owned_sha256':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files if (root/f).exists()}}
(ev/'exact-blob-restoration.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
assert result['baseline']['blob_mismatches']==[]
assert result['candidate']['blob_mismatches']==[files[0]],result
