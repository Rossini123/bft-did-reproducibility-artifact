import argparse,json,csv,statistics,math,collections
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--inputs',required=True);a=p.parse_args();r=Path(a.inputs)
v=json.loads((r/'data/e4/accepted_trial_metrics.json').read_text(encoding='utf-8'));checks=0
def check(x):
 global checks
 if not x:raise ValueError('E4 evidence/display predicate failed')
 checks+=1
def success(x):return x['outcome']=='SUCCESSFUL_RECONCILIATION'
def quantile(xs):
 xs=sorted(xs);return statistics.median(xs),xs[math.ceil(.95*len(xs))-1],max(xs)
def check_group(xs,N,ok,stats):
 check(len(xs)==N and sum(success(x) for x in xs)==ok)
 check(quantile([x['convergenceRound'] for x in xs if success(x)])==stats)
check(len(v)==5152 and len({x['trialId'] for x in v})==5152)
check_group([x for x in v if x['inputCategory']=='WITHIN_MODEL'],2800,2800,(2,7,10))
check_group([x for x in v if x['inputCategory']=='ASSUMPTION_CHALLENGE'],2240,2100,(2,11,32))
controls=[x for x in v if x['kind']=='DETERMINISTIC_CONTROL'];check_group(controls,112,70,(2,8,8))
check_group(v,5152,4970,(2,8,32))
check(all(x['controlVerdict']=='PASS' for x in controls))
stochastic=[x for x in v if x['kind']=='STOCHASTIC'];check(len(stochastic)==5040)
byz=[x for x in stochastic if x['f']>0];check(len(byz)==3780 and all(success(x) for x in byz))
check(sum(x['contacts'] for x in v)==81025225 and sum(x['ledgerQueries'] for x in v)==14740559)
ns=[10,25,50,100,250,500,1000];check(sorted({x['n'] for x in v})==ns)
check({x['fanout'] for x in v}=={5} and {x['horizon'] for x in v}=={200})
matched=[x for x in v if x['initialStateProfile']=='D2' and x['byzantineBehavior']=='B3' and math.isclose(x['actualFraction'],.2)]
benign=[x for x in stochastic if x['initialStateProfile']=='D2' and x['byzantineBehavior']=='B0' and x['f']==0 and x['networkRegime']=='N0']
check(len(matched)==700 and len(benign)==140 and all(success(x) for x in matched+benign))
cells=[];cdf=[]
for n in ns:
 for network in ['N0','N1','N2','N3','N4']:
  g=[x for x in matched if x['n']==n and x['networkRegime']==network];check(len(g)==20)
  med,p95,mx=quantile([x['convergenceRound'] for x in g]);cells.append({'n':n,'network':network,'N':20,'median':med,'p95':p95,'max':mx,'meanContacts':statistics.mean(x['contacts'] for x in g),'meanQueries':statistics.mean(x['ledgerQueries'] for x in g)})
  if n in [100,500,1000] and network in ['N0','N4']:
   for rnd in range(201):cdf.append({'n':n,'network':network,'round':rnd,'reconciled':sum(success(x) and x['convergenceRound']<=rnd for x in g),'denominator':20})
 for_network=[x for x in benign if x['n']==n];check(len(for_network)==20)
# Compare matched-cell display statistics against the selected bound condition CSV, not a newly fitted series.
conditions=list(csv.DictReader((r/'data/e4/results_by_condition.csv').open(encoding='utf-8-sig',newline='')))
for c in cells:
 z=[x for x in conditions if x['stratum_type']=='condition' and x['n']==str(c['n']) and x['networkRegime']==c['network'] and x['initialStateProfile']=='D2' and x['byzantineBehavior']=='B3' and x['actualFraction'] and math.isclose(float(x['actualFraction']),.2)]
 check(len(z)==1);z=z[0]
 for k,col in [('median','successful_round_median'),('p95','successful_round_p95'),('meanContacts','contacts_all_outcomes_mean'),('meanQueries','queries_all_outcomes_mean')]:check(math.isclose(c[k],float(z[col]),rel_tol=1e-12,abs_tol=1e-9))
targets={'B1':(7,9,13,36.607,3.196),'B2':(7,9,11,36.107,3.188),'B4':(7,9,12,34.000,4.407),'B5':(6,7,8,28.393,4.198)}
for behavior,t in targets.items():
 g=[x for x in v if x['panel']=='C' and x['initialStateProfile']=='D1' and x['networkRegime']=='N4' and x['byzantineBehavior']==behavior]
 check_group(g,140,140,t[:3]);check(round(statistics.mean(x['contacts']/x['n'] for x in g),3)==t[3]);check(round(statistics.mean(x['ledgerQueries']/(x['n']-x['f']) for x in g),3)==t[4])
d4=[x for x in stochastic if not success(x)];check(len(d4)==140 and all(x['initialStateProfile']=='D4' and x['f']==0 and x['byzantineBehavior']=='B0' and x['networkRegime']=='N0' for x in d4))
querymeans=[2790.100,6527.000,12775.700,25356.300,62966.800,125627.600,251089.850]
for n,q in zip(ns,querymeans):
 g=[x for x in d4 if x['n']==n];check(len(g)==20 and all(x['endpoint']==200 for x in g));check(statistics.mean(x['contacts'] for x in g)==n*1000);check(round(statistics.mean(x['ledgerQueries'] for x in g),3)==q)
check(sum(x['contacts'] for x in d4)==38700000 and sum(x['ledgerQueries'] for x in d4)==9742667)
print(json.dumps({'PASS':True,'checks':checks,'matched_cells':len(cells),'cdf_points':len(cdf),'scope':'Recorded metrics/category tables/matched figure numeric series; no simulation, probability theorem, regression, or raw trace/control rerun','unresolved_stochastic':140,'unresolved_controls':42}))
