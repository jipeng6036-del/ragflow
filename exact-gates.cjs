const fs=require('fs'),cp=require('child_process');const env={...process.env,NODE_OPTIONS:'--max-old-space-size=6144',PYTHONDONTWRITEBYTECODE:'1'};const records=[];const test='src/pages/agent/form/parser-form/pdf-form-fields.test.tsx';
function run(phase,name,args){const logfile='exact-'+phase+'-'+name+'.log',fd=fs.openSync('/evidence/'+logfile,'w');const start=Date.now();const r=cp.spawnSync(args[0],args.slice(1),{cwd:'/work/'+phase+'/web',env,stdio:['ignore',fd,fd]});fs.closeSync(fd);records.push({phase,name,command:args,code:r.status,signal:r.signal,ms:Date.now()-start,log:logfile});fs.writeFileSync('/evidence/exact-gates.json',JSON.stringify(records,null,2));console.log(phase,name,r.status);}
for(const phase of ['baseline','candidate']){
 for(const [name,args] of [['lint',['npm','run','lint']],['type-check',['npm','run','type-check']],['build',['npm','run','build']],['test',['npm','test','--','--runInBand','--json','--outputFile=/evidence/exact-'+phase+'-jest-results.json']]])run(phase,name,args);
 if(phase==='baseline'){fs.copyFileSync('/work/candidate/web/'+test,'/work/baseline/web/'+test);run(phase,'new-regression',['npm','test','--','--runInBand','--runTestsByPath',test,'--coverage=false','--json','--outputFile=/evidence/exact-baseline-new-regression.json']);fs.unlinkSync('/work/baseline/web/'+test);}
 if(phase==='candidate'){
 run(phase,'related',['npm','test','--','--runInBand','src/pages/agent/form/parser-form','--coverage=false']);
 run(phase,'format',['./node_modules/.bin/oxfmt','--check','src/pages/agent/form/parser-form/pdf-form-fields.tsx',test]);
 }
}
