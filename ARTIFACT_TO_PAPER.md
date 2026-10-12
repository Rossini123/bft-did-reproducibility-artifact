# Artifact-to-paper mapping

- Measured Sepolia gas table: sepolia/historical/trial_f*.json receipt gas fields; 40 records and160 transactions.
- Measured Sepolia latency table/figure: same records, commitRecovery inclusionLatencyMs; client-observed submission-call-to-receipt, not finality.
- Observed fees: gasUsed x effectiveGasPrice in integer wei; decimal ETH derived, never the authority.
- Hypothetical analytical example: mean f=2 commit gas164,278.8 x10gwei x3,000USD/ETH gives4.928364USD, approximately4.93; not a measurement.
- E1: data/e1/e1_cases.csv, recorded_summary.json, recorded_conflict_pair_witnesses.json.
- E2: data/e2/e2_cases.csv.
- E3: data/e3/availability_summary.csv plus20 boundary and40 control witnesses; recorded_scenario_totals.json.
- E4 outcome table, adversarial/D4 table and both E4 figures: data/e4/accepted_trial_metrics.json, results_by_condition.csv, results_by_byzantine_condition.csv and d4_query_witnesses.json; verify_e4_displays.py checks matched35 cells,700 trials, benign140,120 overlapping CDF cases, category quantiles, PanelC normalization and D4 totals.

Protocol proofs are formal manuscript arguments, not empirical artifact claims. No confidence/significance claim or fitted regression is generated.
