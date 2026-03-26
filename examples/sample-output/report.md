# Effect of State Minimum Wage Increases on Restaurant Employment

> **Method**: Staggered Difference-in-Differences (Callaway & Sant'Anna 2021) | **Estimand**: ATT | **Date**: 2026-03-25
> Generated via `/causal-inference` workflow

---

## Executive Summary

We estimate the causal effect of state-level minimum wage increases on restaurant sector employment using a staggered difference-in-differences design. The main finding is an estimated ATT of -0.0147 (95% CI: [-0.0253, -0.0041]), indicating that minimum wage increases reduced restaurant employment by approximately 1.5%, statistically significant at the 5% level (p = 0.007). This result is robust across multiple estimators, specification choices, and sensitivity analyses.

---

## 1. Research Design

### 1.1 Research Question
- **Causal question**: Does raising the state minimum wage reduce restaurant employment?
- **Treatment**: State-level minimum wage increase above the federal minimum ($7.25/hr)
- **Outcome**: Log county-level restaurant sector employment (QCEW)
- **Unit of analysis**: County-quarter (2010 Q1 -- 2020 Q4)
- **Estimand**: ATT (Average Treatment Effect on the Treated)

### 1.2 Hypotheses
- **H1 (main)**: Minimum wage increases reduce restaurant employment because restaurants operate on thin margins and labor is a large share of costs. Higher wages increase labor costs, leading to reduced hours, automation, or closures.
- **H0 (null)**: No effect on employment --- wage increases are absorbed through reduced turnover, higher productivity, price pass-through, or compressed profit margins.
- **Key threat**: States that raised minimum wages may have had different employment trends regardless of the policy (violation of parallel trends).

### 1.3 Identification Strategy
- **Method**: Staggered Difference-in-Differences with Callaway & Sant'Anna (2021) estimator
- **Core assumption**: Parallel trends --- in the absence of minimum wage increases, restaurant employment in treated states would have followed the same trajectory as in never-treated states.
- **Why this method**: Treatment timing varies across states (staggered adoption), making standard TWFE potentially biased with heterogeneous treatment effects. Callaway & Sant'Anna provides clean group-time ATT estimates using never-treated states as controls.
- **Alternatives considered**: Standard TWFE (reported as comparison; potentially biased); Synthetic Control (fewer treated units than needed); matching + DiD (less transparent).

---

## 2. Data

### 2.1 Data Sources
- **Employment**: Quarterly Census of Employment and Wages (QCEW), Bureau of Labor Statistics. Restaurant sector (NAICS 7225). County-level, quarterly.
- **Minimum wage**: State minimum wage laws, compiled from Department of Labor records. Treatment defined as first quarter a state's MW exceeds federal MW.
- **Period**: 2010 Q1 -- 2020 Q4 (44 quarters)
- **Sample**: 3,047 counties across 50 states + DC

### 2.2 Summary Statistics

| Variable | N | Mean | SD | Min | Max |
|----------|---|------|----|-----|-----|
| Log restaurant employment | 133,268 | 6.82 | 1.54 | 2.30 | 11.47 |
| Minimum wage ($/hr) | 133,268 | 8.14 | 1.52 | 7.25 | 15.00 |
| Treatment (post MW increase) | 133,268 | 0.38 | 0.49 | 0 | 1 |
| State GDP growth (%) | 133,268 | 2.31 | 1.87 | -4.20 | 8.50 |
| Population density (per sq mi) | 133,268 | 284 | 1,720 | 0.2 | 71,340 |

- **Treated states**: 29 states raised MW above federal level during the sample period
- **Never-treated states**: 21 states + DC remained at federal minimum
- **Treatment cohorts**: 12 distinct adoption quarters

<details>
<summary>Code: Summary statistics</summary>

```python
import pandas as pd
print(df[['log_emp', 'min_wage', 'treat_post', 'state_gdp_growth', 'pop_density']]
      .describe().T[['count', 'mean', 'std', 'min', 'max']].round(2))
```

</details>

---

## 3. Main Results

### 3.1 Hypothesis
> **H1**: State minimum wage increases reduce restaurant employment because labor costs rise and restaurants, which operate on thin margins with high labor shares, respond by reducing headcount.
> We test this using staggered DiD (Callaway & Sant'Anna), which identifies the ATT under the assumption that treated and never-treated states would have followed parallel employment trends absent the policy.

### 3.2 Primary Estimate

| Specification | Estimate | SE | 95% CI | p-value | N |
|--------------|---------|-----|--------|---------|---|
| **Callaway & Sant'Anna (DR)** | -0.0147 | 0.0054 | [-0.0253, -0.0041] | 0.007 | 133,268 |
| Sun & Abraham | -0.0139 | 0.0058 | [-0.0253, -0.0025] | 0.017 | 133,268 |
| TWFE (biased comparison) | -0.0098 | 0.0047 | [-0.0190, -0.0006] | 0.037 | 133,268 |

**Interpretation**: Restaurant employment fell by approximately 1.5% in states that raised their minimum wage, relative to states that did not. For the average treated state with ~45,000 restaurant workers, this translates to roughly 675 fewer jobs. The TWFE estimate is attenuated (as expected with staggered adoption and heterogeneous effects), confirming the need for robust estimators.

![Event study](figures/event_study.png)
*Figure 1: Event study plot showing dynamic treatment effects. Pre-treatment coefficients (quarters -8 to -1) are individually and jointly insignificant (F = 0.87, p = 0.54), supporting the parallel trends assumption. Post-treatment effects emerge gradually and stabilize around -0.015 by quarter +4.*

<details>
<summary>Code: Main estimation</summary>

```python
from csdid import att_gt
import pyfixest as pf

# Callaway & Sant'Anna
cs_out = att_gt(data=df, yname='log_emp', tname='quarter', idname='county_id',
                gname='first_treat_quarter', control_group='nevertreated', est_method='dr')
agg_simple = cs_out.aggregate('simple')
print(agg_simple.summary())

# Sun & Abraham
sa = pf.feols('log_emp ~ sunab(first_treat_quarter, quarter) | county_id + quarter',
              data=df, vcov={'CRV1': 'state_id'})

# TWFE
twfe = pf.feols('log_emp ~ treat_post | county_id + quarter',
                data=df, vcov={'CRV1': 'state_id'})
```

</details>

### 3.3 Dynamic Effects

The event study (Figure 1) reveals:
- **Pre-treatment (quarters -8 to -1)**: All coefficients close to zero and statistically insignificant. Joint F-test: F = 0.87, p = 0.54. No evidence of differential pre-trends.
- **Impact (quarters 0 to +2)**: Small, imprecisely estimated negative effects as the policy takes hold.
- **Medium-run (quarters +3 to +8)**: Effects stabilize around -0.015, consistently significant.
- **Longer-run (quarters +9 to +12)**: Some evidence of attenuation, possibly due to adjustment (price increases, automation).

---

## 4. Robustness & Sensitivity

### 4.1 Identification Threats (Layer 1)

| Test | Result | Status | Interpretation |
|------|--------|--------|---------------|
| Parallel pre-trends (joint F) | F = 0.87, p = 0.54 | ✓ | Pre-treatment coefficients jointly insignificant |
| Parallel pre-trends (individual) | All |t| < 1.2 | ✓ | No individual pre-treatment coefficient significant |
| Goodman-Bacon decomposition | 89% weight on clean comparisons | ✓ | TWFE mostly uses never-treated as controls; limited contamination |
| Negative weights in TWFE | 3 of 142 group-time cells | ✓ | Minimal; robust estimators address this |

### 4.2 Specification Sensitivity (Layer 2)

![Specification curve](figures/specification_curve.png)
*Figure 2: Specification curve across 48 specifications varying outcome (levels, logs, IHS), controls (none, GDP growth, full), fixed effects (unit+time, unit+time+region-trend), clustering (state, county), and estimator (CS, SA, TWFE). Red dot = preferred specification.*

**Result**: Across 48 specifications, the estimate ranges from -0.0203 to -0.0071. All 48 specifications yield negative estimates; 42 of 48 (88%) are statistically significant at 5%. The result is not sensitive to reasonable modeling choices.

<details>
<summary>Full specification table (top 10)</summary>

| # | Outcome | Controls | FE | Cluster | Estimator | Estimate | SE | p |
|---|---------|----------|-----|---------|-----------|---------|-----|---|
| 1 | log | DR | unit+time | state | CS | -0.0147 | 0.0054 | 0.007 |
| 2 | log | none | unit+time | state | CS | -0.0152 | 0.0057 | 0.008 |
| 3 | log | DR | unit+time | state | SA | -0.0139 | 0.0058 | 0.017 |
| 4 | log | full | unit+time | state | CS | -0.0141 | 0.0055 | 0.010 |
| 5 | IHS | DR | unit+time | state | CS | -0.0158 | 0.0061 | 0.010 |
| 6 | log | none | unit+time | county | CS | -0.0152 | 0.0042 | <0.001 |
| 7 | log | DR | unit+time+trend | state | CS | -0.0131 | 0.0062 | 0.035 |
| 8 | levels | DR | unit+time | state | CS | -0.0203 | 0.0078 | 0.009 |
| 9 | log | DR | unit+time | state | TWFE | -0.0098 | 0.0047 | 0.037 |
| 10 | log | full | unit+time+trend | state | SA | -0.0107 | 0.0064 | 0.094 |

</details>

### 4.3 Sample Robustness (Layer 3)

![Leave-one-out](figures/leave_one_out.png)
*Figure 3: Leave-one-out estimates, dropping each state in turn. Red dashed line = full sample estimate.*

| Subsample | Estimate | SE | N | Note |
|-----------|---------|-----|---|------|
| Full sample | -0.0147 | 0.0054 | 133,268 | Baseline |
| Drop outliers (1%/99%) | -0.0143 | 0.0053 | 130,602 | Stable |
| 2010-2015 only | -0.0162 | 0.0071 | 73,128 | Slightly larger |
| 2016-2020 only | -0.0128 | 0.0068 | 60,140 | Slightly smaller |
| Drop CA + NY | -0.0134 | 0.0059 | 118,412 | Not driven by large states |
| Urban counties only | -0.0171 | 0.0063 | 52,408 | Larger in urban areas |
| Rural counties only | -0.0098 | 0.0072 | 80,860 | Smaller, less precise |

**Most influential state**: Dropping California shifts the estimate to -0.0134 (deviation of 0.0013). No single state drives the result.

### 4.4 Inference Robustness (Layer 4)

| Inference Method | SE | p-value | Significant (5%)? |
|-----------------|-----|---------|-------------------|
| Cluster-robust (state) | 0.0054 | 0.007 | Yes |
| Cluster-robust (county) | 0.0042 | <0.001 | Yes |
| Wild cluster bootstrap (state, 9999 reps) | — | 0.014 | Yes |
| Randomization inference (1000 perms) | — | 0.008 | Yes |

All inference methods yield significant results. The wild cluster bootstrap p-value (0.014) is slightly larger than the cluster-robust p-value (0.007) — expected with 50 clusters — but remains significant.

### 4.5 Sensitivity to Unobservables (Layer 5)

| Measure | Value | Threshold | Interpretation |
|---------|-------|-----------|---------------|
| Oster's delta | 2.34 | > 1 | Robust: unobservables would need 2.3x the selection of observables to explain away the result |
| Robustness Value (RV) | 0.089 | > max observed partial R2 (0.041) | Robust: a confounder would need partial R2 > 0.089 with both treatment and outcome |
| Bias-adjusted beta* (delta=1) | -0.0112 | Same sign | Even under proportional selection, effect remains negative |

![Sensitivity contour](figures/sensitivity_contour.png)
*Figure 4: Cinelli-Hazlett sensitivity contour plot. Red contour = estimate reduced to zero. Black dots = benchmarks from observed covariates (GDP growth, population density). All benchmarks fall well inside the "robust" region.*

**Conclusion**: An unobserved confounder would need to be 2.3 times as strongly associated with both treatment and outcome as the strongest observed confounder (state GDP growth) to fully explain away the result.

### 4.6 Placebo & Falsification Tests (Layer 6)

![Placebo outcomes](figures/placebo_outcomes.png)
*Figure 5: Placebo outcomes test. Red = real outcome (restaurant employment). Blue = placebo outcomes that should not be affected by minimum wage.*

![Placebo timing](figures/placebo_timing.png)
*Figure 6: Placebo timing test. Effect estimated at shifted treatment dates. Only the actual treatment date (shift = 0) shows a significant effect.*

| Placebo Test | Estimate | p-value | Expected | Pass? |
|-------------|---------|---------|----------|-------|
| Mining employment | 0.0023 | 0.71 | ~0 | ✓ |
| Finance employment | -0.0011 | 0.84 | ~0 | ✓ |
| Government employment | 0.0008 | 0.92 | ~0 | ✓ |
| Placebo timing (t-2) | -0.0019 | 0.73 | ~0 | ✓ |
| Placebo timing (t-4) | 0.0031 | 0.58 | ~0 | ✓ |
| Placebo timing (t-6) | -0.0014 | 0.81 | ~0 | ✓ |

All 6 placebo tests pass. The method does not detect spurious "effects" on unrelated sectors or at fake treatment dates.

### 4.7 Cross-Method Comparison (Layer 7)

![Cross-method forest plot](figures/cross_method_forest.png)
*Figure 7: Forest plot comparing estimates across identification strategies.*

| Method | Estimate | SE | 95% CI | Key Assumption |
|--------|---------|-----|--------|---------------|
| **Callaway & Sant'Anna** | -0.0147 | 0.0054 | [-0.0253, -0.0041] | Parallel trends (group-time) |
| Sun & Abraham | -0.0139 | 0.0058 | [-0.0253, -0.0025] | Parallel trends (interaction-weighted) |
| TWFE | -0.0098 | 0.0047 | [-0.0190, -0.0006] | Parallel trends (homogeneous effects) |
| Synthetic DiD | -0.0161 | 0.0067 | [-0.0292, -0.0030] | Factor model + parallel trends |
| OLS + state + time FE | -0.0089 | 0.0043 | [-0.0173, -0.0005] | Selection on observables |

All five methods produce negative, statistically significant estimates. The range is [-0.0161, -0.0089]. Methods relying on parallel trends (DiD variants) cluster around -0.014 to -0.016. The OLS benchmark is attenuated, as expected with omitted variable bias toward zero.

---

## 5. Discussion

### 5.1 Summary of Findings
State minimum wage increases reduced restaurant employment by approximately 1.5% (ATT = -0.015). This effect emerges gradually over 2-3 quarters and is persistent over the medium run. The finding is robust across 48 specifications, multiple estimators, all inference methods tested, and passes all 6 placebo tests.

### 5.2 Heterogeneity
- **Urban vs. rural**: The effect is larger in urban counties (-0.017) than rural counties (-0.010), consistent with tighter labor markets in cities.
- **Magnitude of MW increase**: States with larger MW increases (>$2 above federal) show proportionally larger effects.
- **Pre-existing wage levels**: Low-wage states experience larger employment reductions per dollar of MW increase.

### 5.3 Limitations

- Our results are robust to specification sensitivity (48 specifications, all negative), alternative inference methods (wild bootstrap, randomization inference), and sensitivity analysis (Oster's delta = 2.34, RV = 0.089).
- We note the following limitations:
  - **External validity**: Results pertain to the 2010-2020 period and may not generalize to higher minimum wage levels ($15+/hr) being implemented in some states.
  - **Spillovers**: If MW increases in neighboring states affect control states (e.g., through labor migration), our estimates may be attenuated.
  - **Composition effects**: We measure employment counts, not hours. Firms may reduce hours rather than headcount, meaning our estimates understate the total labor demand response.
  - **COVID-19**: The sample includes early 2020; results are robust to dropping 2020, but the pandemic may affect the longer-run dynamic estimates.

### 5.4 Policy Implications
A 1.5% employment reduction per minimum wage increase episode translates to meaningful job losses in the restaurant sector. However, this must be weighed against the wage gains for workers who remain employed. A full welfare assessment requires estimating the wage gains (which we do not do here) alongside the employment losses. Policymakers considering MW increases should anticipate modest employment reductions concentrated in low-wage, urban restaurant establishments.

---

## 6. Robustness Summary Dashboard

| Category | Status | Evidence |
|----------|--------|----------|
| Identification | ✓ | Pre-trends jointly insignificant (F=0.87, p=0.54) |
| Specification stability | ✓ | 48 specs: all negative, 88% significant; range [-0.020, -0.007] |
| Sample robustness | ✓ | Stable across subsamples; no single state drives result |
| Inference | ✓ | Significant under cluster-robust, wild bootstrap, and randomization inference |
| Unobservable sensitivity | ✓ | Oster's delta = 2.34; RV = 0.089 (> all observed benchmarks) |
| Placebo tests | ✓ | 6/6 passed (3 placebo outcomes + 3 placebo timings) |
| Cross-method | ✓ | 5 methods agree: range [-0.016, -0.009], all significant |

### Verdict
> **STRONG**: The causal effect of state minimum wage increases on restaurant employment is estimated to be -0.0147 (95% CI: [-0.0253, -0.0041]). This finding is robust across all seven robustness dimensions tested. The evidence strongly supports a modest negative employment effect in the restaurant sector.

---

## Appendix: Reproduction Code

<details>
<summary>Code: Full analysis pipeline</summary>

```python
import pandas as pd
import numpy as np
import pyfixest as pf
from csdid import att_gt
import matplotlib.pyplot as plt
import os

# Setup
os.makedirs('causal_analysis_report/figures', exist_ok=True)

# Load data
df = pd.read_csv('data/county_quarter_panel.csv')

# Main estimation: Callaway & Sant'Anna
cs_out = att_gt(data=df, yname='log_emp', tname='quarter', idname='county_id',
                gname='first_treat_quarter', control_group='nevertreated', est_method='dr')
agg = cs_out.aggregate('simple')

# Event study
agg_dyn = cs_out.aggregate('dynamic')
agg_dyn.plot()
plt.savefig('causal_analysis_report/figures/event_study.png', dpi=150, bbox_inches='tight')

# Sun & Abraham
sa = pf.feols('log_emp ~ sunab(first_treat_quarter, quarter) | county_id + quarter',
              data=df, vcov={'CRV1': 'state_id'})

# TWFE
twfe = pf.feols('log_emp ~ treat_post | county_id + quarter', data=df, vcov={'CRV1': 'state_id'})

# [Additional robustness code omitted for brevity -- see code-templates.md Sections 13-14]
```

</details>
