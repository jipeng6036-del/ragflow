from pathlib import Path
import json,re,collections,hashlib,shutil
p=Path('.')
def diagnostics(name):return collections.Counter(x.strip() for x in (p/name).read_text().splitlines() if re.match(r'^.+\(\d+,\d+\): error TS\d+:',x))
bd=diagnostics('exact-baseline-type-check.log');cd=diagnostics('exact-candidate-type-check.log')
def failures(name):
 j=json.loads((p/name).read_text());suites=[];cases=[];load=[]
 for s in j['testResults']:
  f=s['name'].split('/web/',1)[1]
  if s['status']=='failed':
   suites.append(f)
   if not s['assertionResults']:load.append(f)
  cases.extend((f,a['fullName']) for a in s['assertionResults'] if a['status']=='failed')
 return {'counts':{k:j[k] for k in ['numTotalTests','numPassedTests','numFailedTests','numFailedTestSuites','numPassedTestSuites']},'failed_suites':sorted(suites),'failed_assertions':sorted(cases),'load_failures':sorted(load)}
b=failures('exact-baseline-jest-results.json');c=failures('exact-candidate-jest-results.json');red=json.loads((p/'exact-baseline-new-regression.json').read_text());cg=json.loads((p/'exact-candidate-jest-results.json').read_text());green=next(s for s in cg['testResults'] if s['name'].endswith('/parser-form/pdf-form-fields.test.tsx'))
out={'typescript':{'baseline_count':sum(bd.values()),'candidate_count':sum(cd.values()),'baseline_diagnostics':list(bd.elements()),'candidate_diagnostics':list(cd.elements()),'added':list((cd-bd).elements()),'removed':list((bd-cd).elements())},'jest':{'baseline':b,'candidate':c,'added_assertions':sorted(set(c['failed_assertions'])-set(b['failed_assertions'])),'removed_assertions':sorted(set(b['failed_assertions'])-set(c['failed_assertions'])),'added_suites':sorted(set(c['failed_suites'])-set(b['failed_suites'])),'removed_suites':sorted(set(b['failed_suites'])-set(c['failed_suites'])),'load_failures_identical':b['load_failures']==c['load_failures']},'new_regression':{'baseline_failed':red['numFailedTests'],'baseline_passed':red['numPassedTests'],'candidate_passed':len([a for a in green['assertionResults'] if a['status']=='passed']),'candidate_failed':len([a for a in green['assertionResults'] if a['status']=='failed'])}}
out['parity_pass']=not any([out['typescript']['added'],out['typescript']['removed'],out['jest']['added_assertions'],out['jest']['removed_assertions'],out['jest']['added_suites'],out['jest']['removed_suites'],not out['jest']['load_failures_identical']])
out['affected_paths_clean']=not any('pages/agent/form/parser-form/' in x for x in cd) and not any('pages/agent/form/parser-form/' in f for f in c['failed_suites'])
assert out['parity_pass'] and out['affected_paths_clean']
(p/'exact-lf-paired-results.json').write_text(json.dumps(out,indent=2)+'\n')
gates=json.loads((p/'exact-gates.json').read_text());(p/'exact-lf-gates.json').write_text(json.dumps(gates,indent=2)+'\n')
for f in list(p.glob('exact-baseline-*.log'))+list(p.glob('exact-candidate-*.log')):shutil.copyfile(f,p/f.name.replace('exact-','exact-lf-',1))
hooks=json.loads((p/'exact-lf-real-hooks.json').read_text())
for hook in ['pre-commit','web-checks']:
 r=next(r for r in hooks if hook in r['command']);text='COMMAND: '+' '.join(r['command'])+'\nEXIT: '+str(r['code'])+'\n'+r['stdout']+r['stderr'];(p/('exact-lf-'+hook+'.log')).write_text(re.sub(r'\x1b\[[0-9;]*m','',text))
print(json.dumps({'parity_pass':out['parity_pass'],'affected_paths_clean':out['affected_paths_clean'],'ts':[sum(bd.values()),sum(cd.values())],'baseline':b['counts'],'candidate':c['counts'],'new':out['new_regression'],'gates':[(g['phase'],g['name'],g['code']) for g in gates]}))
