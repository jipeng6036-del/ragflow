from pathlib import Path
import json,re,collections
p=Path('.')
def diag(n):return collections.Counter(l.strip() for l in (p/n).read_text().splitlines() if re.match(r'^.+\(\d+,\d+\): error TS\d+:',l))
def tests(n):
 j=json.loads((p/n).read_text());suites=[];cases=[];load=[]
 for s in j['testResults']:
  f=s['name'].split('/web/',1)[1]
  if s['status']=='failed':
   suites.append(f)
   if not s['assertionResults']:load.append(f)
  cases.extend((f,a['fullName']) for a in s['assertionResults'] if a['status']=='failed')
 return {'counts':{k:j[k] for k in ['numTotalTests','numPassedTests','numFailedTests','numFailedTestSuites','numPassedTestSuites']},'failed_suites':sorted(suites),'failed_assertions':sorted(cases),'load_failures':sorted(load)}
bd=diag('baseline-final-type-check.log');cd=diag('candidate-type-check.log');b=tests('baseline-final-jest-results.json');c=tests('candidate-jest-results.json');red=json.loads((p/'new-regression-baseline-final.json').read_text());green=json.loads((p/'new-regression-candidate.json').read_text())
out={'baseline_revision':'84ae4246afadcf18bb02d8521dee1bbe0c4ffa1e','baseline_full_test_source':'Pristine84ae test file with24cases; the new38case red overlay was removed/restored before this full baseline run.','candidate_test_source':'Frozen38case file, same file path/suite count.','typescript':{'baseline_count':sum(bd.values()),'candidate_count':sum(cd.values()),'baseline_diagnostics':list(bd.elements()),'candidate_diagnostics':list(cd.elements()),'added':list((cd-bd).elements()),'removed':list((bd-cd).elements())},'jest':{'baseline':b,'candidate':c,'added_assertions':sorted(set(c['failed_assertions'])-set(b['failed_assertions'])),'removed_assertions':sorted(set(b['failed_assertions'])-set(c['failed_assertions'])),'added_suites':sorted(set(c['failed_suites'])-set(b['failed_suites'])),'removed_suites':sorted(set(b['failed_suites'])-set(c['failed_suites'])),'load_failures_identical':b['load_failures']==c['load_failures']},'new_regression':{'baseline_failed':red['numFailedTests'],'baseline_passed':red['numPassedTests'],'candidate_failed':green['numFailedTests'],'candidate_passed':green['numPassedTests']}}
out['parity_pass']=not any([out['typescript']['added'],out['typescript']['removed'],out['jest']['added_assertions'],out['jest']['removed_assertions'],out['jest']['added_suites'],out['jest']['removed_suites'],not out['jest']['load_failures_identical']]);out['affected_paths_clean']=not any('pages/agent/form/parser-form/'in d for d in cd)and not any('pages/agent/form/parser-form/'in f for f in c['failed_suites']);assert out['parity_pass']and out['affected_paths_clean']
(p/'paired-results.json').write_text(json.dumps(out,indent=2)+'\n');g=json.loads((p/'baseline-final-gates.json').read_text())+[r for r in json.loads((p/'quality-gates.json').read_text())if r['phase']=='candidate'];(p/'final-quality-gates.json').write_text(json.dumps(g,indent=2)+'\n');print(json.dumps({'parity':out['parity_pass'],'affected_clean':out['affected_paths_clean'],'ts':[sum(bd.values()),sum(cd.values())],'base':b['counts'],'candidate':c['counts'],'redgreen':out['new_regression']}))
