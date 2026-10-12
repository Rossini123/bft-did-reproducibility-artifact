import argparse,json,csv,statistics,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--inputs',required=True);a=p.parse_args();r=Path(a.inputs)
def load(n):return json.loads((r/n).read_text(encoding='utf-8'))
checks=0
def check(v):
 global checks
 if not v:raise ValueError('Recorded evidence predicate failed')
 checks+=1
e1=load('data/e1/recorded_summary.json');pairs=load('data/e1/recorded_conflict_pair_witnesses.json')
check(e1['rawFiles']==48 and e1['conflictPairs']==12 and e1['dualValidCertificatePairs']==0 and len(pairs)==12)
for v in pairs:
 f,n,q=(v['configuration'][k] for k in ('f','n','q'));check(n==3*f+1 and q==2*f+1)
 val=[]
 for name,proposal in v['proposalCounts'].items():
  s=proposal['signerIndices'];check(proposal['signatureCount']==len(s))
  valid=len(set(i for i in s if 0<=i<n))
  check(valid==proposal['distinctValidSignerCount'])
  eligible=(len(s)==len(set(s)) and all(0<=i<n for i in s) and valid>=q)
  obs=next(o for o in v['observations'] if o['proposal']==name)
  check(eligible==obs['certificateValid']);val.append(eligible)
 check(sum(val)<=1 and sum(bool(o['accepted']) for o in v['observations'])<=1)
e2=list(csv.DictReader((r/'data/e2/e2_cases.csv').open(encoding='utf-8-sig',newline='')))
check(len(e2)==27)
for v in e2:
 q=int(v['q']);check(int(v['n'])==3*int(v['f'])+1 and q==2*int(v['f'])+1)
 check((int(v['r'])>=q)==(v['classification']=='QUORUM_AVAILABLE_AND_COMMITTABLE'))
check(sum(v['classification']=='QUORUM_AVAILABLE_AND_COMMITTABLE' for v in e2)==15)
cases=load('data/e3/boundary_and_control_recorded_witnesses.json');check(len(cases)==60)
for v in cases:
 f,n,q=(v['configuration'][k] for k in ('f','n','q'));check(n==3*f+1 and q==2*f+1)
 tx={x['label']:x for x in v['transactions']};s=v['scenario']
 if s in ['S0','S1','S2','S4','S5']:
  enough=v['responsiveCount']>=q;check(enough==(v['classification']=='QUORUM_AVAILABLE_AND_COMMITTABLE'))
  if enough:
   check(tx['commitRecovery']['status']==1 and v['certificateSubmitted']['distinctValidSignerCount']>=q)
  else:check('commitRecovery' not in tx and v['certificateSubmitted'] is None)
 elif s=='S7':
  flags=[]
  for z in v['proposalCounts'].values():
   ii=z['signerIndices'];check(z['distinctValidSignerCount']==len(set(i for i in ii if 0<=i<n)))
   flags.append(len(ii)==len(set(ii)) and all(0<=i<n for i in ii) and len(ii)>=q)
  check(sum(flags)<=1);check(sum(tx[k]['status']==1 for k in ['conflict_A','conflict_B'])<=1)
 elif s=='S8':
  check(v['churn']['epochAfter']>v['churn']['epochBefore'])
  for k in ['epoch1Commit','rotateWatchers','epoch2Commit']:check(tx[k]['status']==1)
  for k in ['staleEpochCertificate','oldSignatureBytes','oldMembershipCertificate']:check(tx[k]['status']==0)
  check(v['finalState']['epoch1Completed'] and v['finalState']['epoch2Completed'])
 elif s=='S9':
  regression=[x for x in v['transactions'] if x['label'].startswith('regression_')]
  check(bool(regression))
  check(all(x['status']==0 and x['revertName']==v['expectedRevert'] for x in regression))
 else:raise ValueError('Unexpected scenario')
summary=list(csv.DictReader((r/'data/e3/availability_summary.csv').open(encoding='utf-8-sig',newline='')))
# Exact summary-column names are supplied by its executed schema; a missing column fails, not guessed.
def field(row,names):
 return next(row[k] for k in names if k in row)
total=sum(int(x['total']) for x in summary)
committed=sum(int(x['committed']) for x in summary)
unavailable=sum(int(x['quorumUnavailable']) for x in summary)
check((total,committed,unavailable)==(2200,1998,202))
ordinary=[x for x in cases if x['scenario'] in ['S0','S1','S2','S4','S5']]
check(len(ordinary)==20 and sum(x['classification']=='QUORUM_AVAILABLE_AND_COMMITTABLE' for x in ordinary)==12)
trials=[load(p.relative_to(r)) for p in sorted((r/'sepolia/historical').glob('trial_*.json'))];check(len(trials)==40)
transactions=[x for v in trials for x in v['transactions']];check(len(transactions)==160 and len({x['txHash'] for x in transactions})==160)
for x in transactions:check(int(x['gasUsed'])*int(x['effectiveGasPrice'])==int(x['actualFeeWei']) and x['receiptStatus']==1)
check(sum(int(x['actualFeeWei']) for x in transactions)==36032243477586029)
check(sum(int(x['gasUsed']) for x in transactions)==33813868)
commit=[x for x in transactions if x['label']=='commitRecovery'];check(len(commit)==40)
lat=[x['inclusionLatencyMs']/1000 for x in commit]
check(round(statistics.mean(lat),3)==14.147 and round(statistics.median(lat),3)==11.314 and round(statistics.stdev(lat),3)==5.308)
print(json.dumps({'PASS':True,'checks':checks,'scope':'Independent quorum/membership/count and recorded receipt/state predicates; not ECDSA signature recovery or experiment rerun','E1_pairs':12,'E2_cases':27,'E3_boundary':20,'E3_controls':40,'Sepolia_lifecycles':40,'Sepolia_transactions':160,'actualFeeWei':36032243477586029}))
