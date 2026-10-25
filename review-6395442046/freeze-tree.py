from pathlib import Path
import subprocess,hashlib,json,stat
files=['web/src/pages/agent/form/parser-form/pdf-form-fields.tsx','web/src/pages/agent/form/parser-form/pdf-form-fields.test.tsx'];out={}
for name in ['baseline','candidate']:
 root=Path('/work')/name
 def git(*args):return subprocess.check_output(['git',*args],cwd=root)
 mismatches=[];badmodes=[];count=0
 for row in git('ls-tree','-r','-z','HEAD').split(b'\0'):
  if not row:continue
  info,rel=row.split(b'\t',1);mode,typ,oid=info.split();p=root/rel.decode();count+=1
  data=str(p.readlink()).encode() if mode==b'120000' else p.read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest().encode()
  if actual!=oid:mismatches.append(rel.decode())
  if mode in [b'100644',b'100755'] and bool(p.stat().st_mode&stat.S_IXUSR)!=(mode==b'100755'):badmodes.append(rel.decode())
 config=['web/package.json','web/package-lock.json','web/tsconfig.json','web/jest.config.ts','lefthook.yml','AGENTS.md','web/AGENTS.md']
 out[name]={'head':git('rev-parse','HEAD').decode().strip(),'branch':git('branch','--show-current').decode().strip(),'tracked_count':count,'head_blob_mismatches':mismatches,'head_mode_mismatches':badmodes,'status':git('status','--short').decode(),'owned':{f:{'sha256':hashlib.sha256((root/f).read_bytes()).hexdigest(),'raw_blob_sha1':hashlib.sha1(b'blob '+str((root/f).stat().st_size).encode()+b'\0'+(root/f).read_bytes()).hexdigest(),'mode':oct((root/f).stat().st_mode&0o777)} for f in files},'config_sha256':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in config if(root/f).exists()}}
 if name=='candidate':
  out[name]['staged_files']=git('ls-files','--stage','--',*files).decode();out[name]['staged_numstat']=git('diff','--cached','--numstat').decode();out[name]['unstaged_diff']=git('diff','--name-only').decode();git('diff','--cached','--check');Path('/evidence/candidate.patch').write_bytes(git('diff','--cached','--binary'))
 assert count==5452 and not badmodes
 assert set(mismatches)==(set() if name=='baseline' else set(files))
Path('/evidence/tree-manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:{key:v for key,v in x.items() if key in ['head','tracked_count','head_blob_mismatches','head_mode_mismatches','status','owned','staged_numstat','unstaged_diff']}for k,x in out.items()}))
