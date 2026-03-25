# Example: California Tobacco Control Program (Synthetic Control)

This example replicates the classic Abadie, Diamond & Hainmueller (2010) analysis of California's Proposition 99.

---

## Conversation

### User
```
/causal-inference California passed a large tobacco tax and control program (Proposition 99) in 1988. I want to estimate its effect on per-capita cigarette sales. I have state-level annual data for all 50 states from 1970-2000.
```

### Phase 1-2: Problem Framing & Data

**Skill identifies:**
> - **Research question**: Did California's Proposition 99 reduce cigarette consumption?
> - **Treatment**: Proposition 99 (comprehensive tobacco control program)
> - **Treated unit**: California (1 unit)
> - **Outcome**: Per-capita cigarette sales (packs)
> - **Time**: 1970-2000 (18 pre-treatment years, 12 post-treatment years)
> - **Donor pool**: Other US states that did NOT implement similar large programs during this period
>
> **Why DiD won't work well here**: With only 1 treated unit, there's no obvious single comparison state. Any individual state comparison is arbitrary — "Why New York and not Texas?"
>
> **This is a textbook Synthetic Control setting**: single treated unit, many potential donors, long pre-treatment period.

---

### Phase 3: Method Selection

**Skill recommends:**

> **Synthetic Control Method (Abadie, Diamond & Hainmueller 2010)**
>
> The idea: construct a weighted combination of donor states that closely reproduces California's pre-1988 cigarette sales trajectory. This "Synthetic California" serves as the counterfactual. The treatment effect = actual California - synthetic California after 1988.
>
> **Donor pool considerations:**
> - Exclude states that implemented their own large tobacco programs during the study period
> - Exclude states with unusual cigarette tax changes
> - Standard donor pool: ~38 states after exclusions
>
> **Also consider as robustness:**
>
> | Method | Why |
> |--------|-----|
> | **Augmented SCM** | If pre-treatment fit is imperfect, ASCM adds a bias-correction term |
> | **SDID** | Synthetic DiD — reweights both units AND time periods |

---

### Phase 4: Diagnostics

> **Pre-treatment fit**: The synthetic California must closely track actual California before 1988. Report RMSPE. If fit is poor, consider Augmented SCM.
>
> **Inference via placebo tests**:
> 1. Apply SCM to every donor state (pretending each was "treated" in 1988)
> 2. Compute post/pre RMSPE ratio for each
> 3. California's ratio should be an outlier — the p-value is its rank / number of states
>
> **Robustness**:
> - Leave-one-out: drop each major donor state and re-estimate
> - In-time placebo: pretend treatment happened in 1983 — effect should be ~0 before 1988
> - Backdating: shift treatment date and verify effect appears only at actual date

---

### Phase 5: Implementation

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# ── Data: state-year panel ──
# df columns: state_id, year, cigsale, lnincome, beer, age15to24, retprice, treat
# California = state_id 3, treatment year = 1988

treated_id = 3
treat_year = 1988
donor_ids = [s for s in df['state_id'].unique() if s != treated_id]
years = sorted(df['year'].unique())
pre_years = [y for y in years if y < treat_year]
T0 = len(pre_years)

# Reshape to (units x time) matrix
outcome_matrix = df.pivot(index='state_id', columns='year', values='cigsale')
Y_treat = outcome_matrix.loc[treated_id].values
Y_donors = outcome_matrix.loc[donor_ids].values
n_donors = len(donor_ids)

# ── Classic Synthetic Control: minimize pre-treatment MSPE ──
def objective(w):
    synthetic = w @ Y_donors[:, :T0]
    return np.sum((Y_treat[:T0] - synthetic) ** 2)

constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
bounds = [(0, 1)] * n_donors
w0 = np.ones(n_donors) / n_donors

result = minimize(objective, w0, method='SLSQP', bounds=bounds, constraints=constraints)
weights = result.x
synthetic_all = weights @ Y_donors

# ── Path plot (actual vs synthetic) ──
plt.figure(figsize=(10, 6))
plt.plot(years, Y_treat, 'b-', linewidth=2, label='California')
plt.plot(years, synthetic_all, 'r--', linewidth=2, label='Synthetic California')
plt.axvline(x=treat_year, color='gray', linestyle=':', label='Proposition 99')
plt.xlabel('Year')
plt.ylabel('Per-Capita Cigarette Sales (packs)')
plt.title('California vs. Synthetic California')
plt.legend()
plt.show()

# ── Gap plot (treatment effect over time) ──
gap = Y_treat - synthetic_all
plt.figure(figsize=(10, 6))
plt.plot(years, gap, 'k-', linewidth=2)
plt.axvline(x=treat_year, color='gray', linestyle=':')
plt.axhline(y=0, color='gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Gap in Cigarette Sales')
plt.title('Effect of Proposition 99')
plt.show()

# ── Donor weights ──
print('Donor weights (non-zero):')
for sid, w in sorted(zip(donor_ids, weights), key=lambda x: -x[1]):
    if w > 0.01:
        print(f'  State {sid}: {w:.3f}')

# ── Pre-treatment RMSPE ──
rmspe_pre = np.sqrt(np.mean((Y_treat[:T0] - synthetic_all[:T0]) ** 2))
print(f'Pre-treatment RMSPE: {rmspe_pre:.2f}')

# ── Placebo tests (permutation inference) ──
placebo_gaps = {}
for i, donor in enumerate(donor_ids):
    Y_placebo = Y_donors[i]
    Y_placebo_donors = np.vstack([Y_treat.reshape(1, -1),
                                   np.delete(Y_donors, i, axis=0)])

    def obj_placebo(w):
        return np.sum((Y_placebo[:T0] - w @ Y_placebo_donors[:, :T0]) ** 2)

    n_d = Y_placebo_donors.shape[0]
    cons = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bds = [(0, 1)] * n_d
    res = minimize(obj_placebo, np.ones(n_d)/n_d, method='SLSQP', bounds=bds, constraints=cons)
    if res.success:
        placebo_gaps[donor] = Y_placebo - res.x @ Y_placebo_donors

# Plot all placebo gaps
plt.figure(figsize=(10, 6))
for donor, pg in placebo_gaps.items():
    plt.plot(years, pg, color='lightgray', alpha=0.5)
plt.plot(years, gap, 'b-', linewidth=2, label='California')
plt.axvline(x=treat_year, color='gray', linestyle=':')
plt.axhline(y=0, color='gray', linestyle='--')
plt.title('Placebo Tests: California vs. All Donors')
plt.legend()
plt.show()

# ── Post/pre RMSPE ratio for inference ──
rmspe_post_treat = np.sqrt(np.mean(gap[T0:] ** 2))
ratio_treat = rmspe_post_treat / rmspe_pre

ratios = []
for donor, pg in placebo_gaps.items():
    rmspe_pre_d = np.sqrt(np.mean(pg[:T0] ** 2))
    rmspe_post_d = np.sqrt(np.mean(pg[T0:] ** 2))
    if rmspe_pre_d > 0:
        ratios.append(rmspe_post_d / rmspe_pre_d)

p_value = np.mean([r >= ratio_treat for r in ratios])
print(f'Post/pre RMSPE ratio (California): {ratio_treat:.2f}')
print(f'Permutation p-value: {p_value:.3f}')
```

> **Key results to report:**
> 1. Path plot: actual CA vs. synthetic CA — clear divergence after 1988
> 2. Gap plot: treatment effect grows over time (cumulative effect of sustained program)
> 3. Donor weights: which states form synthetic CA (typically CO, CT, MT, NV, UT)
> 4. Placebo test: CA has the largest post/pre RMSPE ratio → p-value ~ 0.03
> 5. Robustness: leave-one-out donors, ASCM, SDID estimates
