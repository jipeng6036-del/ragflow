from pathlib import Path
import subprocess,json,hashlib,stat
files=['web/src/pages/agent/form/parser-form/pdf-form-fields.tsx','web/src/pages/agent/form/parser-form/pdf-form-fields.test.tsx'];out={}
def git(root,*args):return subprocess.check_output(['git',*args],cwd=root)
for name in ['baseline','candidate']:
 root=Path('/work')/name;wrong=[];badmode=[];rows=git(root,'ls-tree','-r','-z','HEAD').split(b'\0');count=0
 for row in rows:
  if not row:continue
  info,namebytes=row.split(b'\t',1);mode,typ,oid=info.split();namepath=namebytes.decode();p=root/namepath;count+=1
  data=str(p.readlink()).encode() if mode==b'120000' else p.read_bytes()
  actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest().encode()
  if actual!=oid:wrong.append(namepath)
  if mode in [b'100644',b'100755'] and bool(p.stat().st_mode&stat.S_IXUSR)!=(mode==b'100755'):badmode.append(namepath)
 configs=['web/package.json','web/package-lock.json','web/tsconfig.json','web/jest.config.ts','lefthook.yml','AGENTS.md','web/AGENTS.md']
 out[root.name]={'head':git(root,'rev-parse','HEAD').decode().strip(),'branch':git(root,'branch','--show-current').decode().strip(),'tracked_head_files':count,'head_blob_mismatches':wrong,'head_mode_mismatches':badmode,'status':git(root,'status','--short','--untracked-files=normal').decode(),'config_hashes':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in configs if (root/f).exists()},'owned':{f:{'sha256':hashlib.sha256((root/f).read_bytes()).hexdigest(),'mode':oct((root/f).stat().st_mode&0o777)} for f in files if (root/f).exists()},'git_config':{key:git(root,'config','--local',key).decode().strip() for key in ['core.autocrlf','core.symlinks','core.filemode']}}
 if root.name=='candidate':
  out[root.name]['staged_numstat']=git(root,'diff','--cached','--numstat').decode();out[root.name]['staged_summary']=git(root,'diff','--cached','--summary').decode();git(root,'diff','--cached','--check');Path('/evidence/exact-lf-candidate.patch').write_bytes(git(root,'diff','--cached','--binary'))
Path('/evidence/exact-lf-tree-manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({n:{k:v for k,v in r.items() if k in ['head','tracked_head_files','head_blob_mismatches','head_mode_mismatches','status']} for n,r in out.items()}))
assert out['baseline']['head_blob_mismatches']==[] and out['baseline']['head_mode_mismatches']==[] and out['baseline']['status']==''
assert out['candidate']['head_blob_mismatches']==[files[0]] and out['candidate']['head_mode_mismatches']==[]
