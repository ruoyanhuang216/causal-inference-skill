# Changelog

## 2026-07-09 — Experimentation-at-Scale / industry (product-DS) enrichment

Added an **industry / "causal inference at product scale"** layer distilled from the
[Unofficial Google Data Science blog](https://www.unofficialgoogledatascience.com/).
The skill's academic/econometric coverage was already comprehensive, so this fills the
*industry blind spots* only — **non-duplicative**: existing DML, meta-learners (S/T/X/R/DR),
CausalImpact, placebo tests, and the uplift four-quadrants/Qini in the playbook were left
untouched. All changes are additive (+~740 lines across 9 files; no existing content removed).

### New methods — `skills/causal-inference/methods-reference.md`
- **Geo experiments & iROAS** (§1.3): geo/DMA randomization when cookie randomization fails
  (multi-device, offline/lagged conversions); pretest/test/cooldown; `iROAS = Δrevenue/Δspend`;
  SUTVA "bleed" mitigations (DMA units, buffer donuts, graph-partitioned allocation);
  **virtual DMAs** via Louvain/Leiden community detection for borderless digital platforms,
  validated by modularity → SIR contagion sim → geo-A/A test.
- **Ramp-up time confounders & epoch-conditioning** (§1.4): changing T:C assignment weights over
  time + a time-based confounder ⇒ biased ATE; partial- vs full-traffic ramp distinction;
  epoch-conditioning estimator; MAB/Thompson-Sampling lock-in failure.
- **Confounded feedback loops & alternating optimization** (§7.6): ranker/recommender
  quality↔placement confounding; observational quality-score stream + small randomized holdback,
  fit by alternating optimization (each the other's fixed offset); PSI/KL + "causal canary" drift monitoring.
- **Empirical Bayes / random-effects partial pooling** (§10.4): adaptive per-group shrinkage
  `W_j = n_j/(n_j + σ²_data/σ²_prior)` vs Ridge's single global λ; Gamma–Poisson closed form;
  cold start (n=0 → prior); Thompson-Sampling bandit bridge.
- **Enriched CausalImpact/BSTS** (§11.2): spike-and-slab control selection; in-time placebo /
  false-positive-rate falsification; contaminated-control endogeneity (cannibalization → overestimate,
  halo → underestimate); DiD-vs-BSTS decision.

### Workflow — `skills/causal-inference/SKILL.md`
- New **"Experimentation at Scale"** method-selection track (geo/virtual-DMAs, ramp time-confounding,
  alternating optimization).
- **Uplift targeting layer** on the ML/CATE track: four quadrants (incl. sleeping-dogs),
  Qini/AUUC/decile offline evaluation (randomized data), breakeven rule `treat iff τ̂(X) > c/V`.
- **DML traps**: nested cross-fitting (hyperparameter-tuning leakage), the √N guarantee, and the
  DAG feature-selection rule (drop mediators = over-controlling, drop colliders = Berkson's paradox).
- **Empirical Bayes partial pooling** for high-cardinality categoricals.

### Diagnostics — `skills/causal-inference/diagnostics.md`
Six new checks: contaminated-control test, in-time placebo/FPR, ramp-up weight-change,
DAG mediator/collider exclusion, nested cross-fitting, and uplift-eval-requires-randomized-data.

### Code templates — `skills/causal-inference/code-templates.md`
Six new runnable snippets (§15–20): **E-value** sensitivity; **nested cross-fitting** for DML;
**Empirical-Bayes shrinkage** (Gamma–Poisson + Normal `W_j` + Thompson-Sampling stub);
**geo experiment** (TBR/iROAS + virtual-DMA construction via `networkx` + geo-A/A check);
**uplift evaluation** (Qini/AUUC + decile-uplift); **BSTS contaminated-control diagnostic**.

### Industry playbook — `industry-playbook/`
- `01-experiments-first.md`: geo experiments & iROAS; ramp-up time-confounding + MAB lock-in.
- `02-quasi-experimental.md`: BSTS/CausalImpact single-series reads + contaminated controls + in-time placebo.
- `03-observational.md`: alternating optimization for feedback loops; nested cross-fitting note.
- `04-heterogeneity-and-targeting.md`: breakeven `τ>c/V` rule; Empirical Bayes pooling + Thompson bridge.

### Docs — `README.md`
Added an "Experimentation at Scale (industry)" row to *Methods Covered*.

### Verification
New Python templates syntax-compile clean; the example figure pipeline re-runs successfully
(`examples/sample-output/generate_figures.py` → 5 figures, exit 0); installed skill copy re-synced.
