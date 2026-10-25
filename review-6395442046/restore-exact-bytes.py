from pathlib import Path
import subprocess,hashlib,json,stat
out={}
for name in ['baseline','candidate']:
 root=Path('/work')/name
 def git(*args):return subprocess.check_output(['git',*args],cwd=root)
 for key,value in [('core.autocrlf','false'),('core.filemode','true'),('core.symlinks','true')]:git('config','--local',key,value)
 git('read-tree','HEAD');git('checkout-index','--all','--force');git('update-index','--refresh')
 mismatches=[];modes=[];count=0
 for row in git('ls-tree','-r','-z','HEAD').split(b'\0'):
  if not row:continue
  info,rel=row.split(b'\t',1);mode,typ,oid=info.split();p=root/rel.decode();count+=1
  data=str(p.readlink()).encode() if mode==b'120000' else p.read_bytes()
  actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest().encode()
  if actual!=oid:mismatches.append(rel.decode())
  if mode in [b'100644',b'100755'] and bool(p.stat().st_mode&stat.S_IXUSR)!=(mode==b'100755'):modes.append(rel.decode())
 out[name]={'head':git('rev-parse','HEAD').decode().strip(),'tracked':count,'blob_mismatches':mismatches,'mode_mismatches':modes,'status':git('status','--short').decode()}
 print(name,count,'blob_mismatches',len(mismatches),'mode_mismatches',len(modes),'status_lines',len(out[name]['status'].splitlines()));assert count==5452 and not mismatches and not modes and not out[name]['status']
Path('/evidence/exact-byte-initial.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
Path('/evidence/archive-byte-check-rejection.json').write_text(json.dumps({'result':'Early Git status gate rejected Windows git archive CRLF conversions before any regression or quality check ran. No false green claimed.','recovery':'core.autocrlf=false, core.symlinks=true, core.filemode=true; git checkout-index --all --force from actual index; complete HEAD blob+mode verification passed for both5452files.','product_edited_at_detection':False},indent=2)+'\n')
