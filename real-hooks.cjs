const fs=require('fs'),cp=require('child_process'); const cwd='/work/candidate';const records=[];
function run(args,env={}){const r=cp.spawnSync(args[0],args.slice(1),{cwd,env:{...process.env,...env},input:args.includes('--files-from-stdin')?'web/src/pages/agent/form/parser-form/pdf-form-fields.tsx\0web/src/pages/agent/form/parser-form/pdf-form-fields.test.tsx\0':undefined,encoding:'utf8'});records.push({command:args,code:r.status,stdout:r.stdout,stderr:r.stderr});fs.writeFileSync('/evidence/exact-lf-real-hooks.json',JSON.stringify(records,null,2));console.log(args.join(' '),r.status);if(r.status)throw Error(r.stderr||r.stdout);return r.stdout;}
run(['git','config','--local','core.autocrlf','false']);
run(['git','config','--local','core.filemode','true']);
run(['git','rev-parse','HEAD']);run(['git','status','--short','--untracked-files=normal']);
const files=['web/src/pages/agent/form/parser-form/pdf-form-fields.tsx','web/src/pages/agent/form/parser-form/pdf-form-fields.test.tsx'];
run(['git','add','--',...files]);run(['git','diff','--cached','--name-status']);run(['git','diff','--cached','--check']);
run(['/work/hook-tools/node_modules/.bin/lefthook','version']);
run(['/work/hook-tools/node_modules/.bin/lefthook','run','pre-commit','--files-from-stdin','--no-auto-install'],{LEFTHOOK_CHECK_ONLY:'1'});
run(['/work/hook-tools/node_modules/.bin/lefthook','run','web-checks','--files-from-stdin','--no-auto-install'],{LEFTHOOK_CHECK_ONLY:'1'});
run(['git','status','--short','--untracked-files=normal']);
