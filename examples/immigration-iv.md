# Example: Effect of Immigration on Wages (Shift-Share IV)

This example demonstrates the skill guiding a researcher using a Bartik/shift-share instrument.

---

## Conversation

### User
```
/causal-inference I'm studying whether immigration reduces wages for native workers. I have data on local labor markets (commuting zones) over time. I want to use historical settlement patterns as an instrument for current immigration flows.
```

### Phase 1-2: Problem Framing & Data

**Skill identifies:**
> - **Research question**: Does immigration to a local labor market reduce native wages?
> - **Treatment**: Immigration inflow (continuous — share of immigrants in local workforce)
> - **Outcome**: Average native wages (or wage growth)
> - **Unit**: Commuting zone × decade
> - **Data**: Panel (CZ-decade)
> - **Estimand**: This is a continuous treatment. You're estimating the marginal effect of a 1pp increase in immigrant share on native wages.
>
> **Endogeneity concern**: Immigrants choose destinations based on economic conditions — places with higher wages and more jobs attract more immigrants. OLS is biased (likely toward zero or even positive).
>
> **Your proposed instrument**: A **shift-share (Bartik) instrument**:
> - **Shares**: Historical settlement patterns — the fraction of each origin-country's immigrants who settled in each CZ in a base year (e.g., 1980)
> - **Shifts**: National inflows of immigrants from each origin country in the current period
> - **Instrument**: Predicted immigration = sum over origin countries of (local share × national inflow)
>
> This is a classic shift-share IV design, following Card (2001).

---

### Phase 3: Method Selection

**Skill recommends:**

> **Shift-Share Instrumental Variables**
>
> There are two modern frameworks for identifying assumptions — you should be clear about which you invoke:
>
> | Framework | Key Assumption | Reference |
> |-----------|---------------|-----------|
> | **Share-based** (GPSS) | The historical settlement shares are exogenous — uncorrelated with local labor market shocks | Goldsmith-Pinkham, Sorkin & Swift (2020) |
> | **Shock-based** (BHJ) | The national origin-country inflows are exogenous — uncorrelated with local shocks (after controlling for exposure) | Borusyak, Hull & Jaravel (2022) |
>
> **Recommendation**: The **shock-based (BHJ)** approach is typically more credible in immigration settings because:
> - It requires fewer assumptions (just quasi-random national shocks, not exogenous local shares)
> - Historical settlement patterns are likely correlated with persistent local economic conditions
> - The identifying variation comes from the many origin-country shocks, so you can test balance and do leave-one-out exercises
>
> **Diagnostics specific to shift-share:**
> - Rotemberg weights: Identify which origin-country shares/shocks are most influential
> - Leave-one-out: Drop the most influential origin country and re-estimate
> - Pre-trend test: Show the instrument does not predict past wage growth
> - Balance: Show national shocks are uncorrelated with local baseline characteristics (weighted by shares)

---

### Phase 5: Implementation

```python
import pyfixest as pf
import pandas as pd
import numpy as np

# ── Data structure ──
# df: CZ-decade panel
# immig_share: actual immigrant share (endogenous)
# bartik_iv: predicted immigration from shift-share instrument
# wage_growth: change in log native wages

# ── OLS (biased baseline) ──
ols = pf.feols('wage_growth ~ immig_share | cz + decade',
               data=df, vcov={'CRV1': 'state'})
print('OLS:')
print(ols.summary())

# ── First stage ──
first_stage = pf.feols('immig_share ~ bartik_iv | cz + decade',
                        data=df, vcov={'CRV1': 'state'})
print('First Stage:')
print(first_stage.summary())

# ── 2SLS ──
iv_model = pf.feols('wage_growth ~ 1 | cz + decade | immig_share ~ bartik_iv',
                     data=df, vcov={'CRV1': 'state'})
print('IV (2SLS):')
print(iv_model.summary())

# ── Reduced form ──
reduced_form = pf.feols('wage_growth ~ bartik_iv | cz + decade',
                         data=df, vcov={'CRV1': 'state'})
print('Reduced Form:')
print(reduced_form.summary())

# ── Pre-trend test (instrument should not predict past wage growth) ──
pretrend = pf.feols('lag_wage_growth ~ bartik_iv | cz + decade',
                     data=df, vcov={'CRV1': 'state'})
print('Pre-trend test (should be insignificant):')
print(pretrend.summary())

# ── Leave-one-out: drop each top-5 origin country ──
top_origins = ['MEX', 'CHN', 'IND', 'PHL', 'VNM']
for origin in top_origins:
    # Recalculate bartik_iv excluding this origin country
    # df_loo['bartik_iv_loo'] = ... (sum of share * shock excluding this origin)
    df_loo = df.copy()
    df_loo['bartik_iv_loo'] = df[f'bartik_excl_{origin}']  # pre-computed
    iv_loo = pf.feols('wage_growth ~ 1 | cz + decade | immig_share ~ bartik_iv_loo',
                       data=df_loo, vcov={'CRV1': 'state'})
    coef = iv_loo.coef().values[0]
    se = iv_loo.se().values[0]
    print(f'Dropping {origin}: Estimate = {coef:.4f} ({se:.4f})')
```

> **Reporting recommendations:**
> 1. Report OLS and IV side-by-side — discuss direction of bias
> 2. Show first-stage F-statistic (should be well above 10)
> 3. Report reduced form — interpretable even if exclusion fails
> 4. Present Rotemberg weights or BHJ shock-level analysis
> 5. Show leave-one-out sensitivity to dominant origin countries
> 6. Discuss LATE interpretation: the effect is local to variation driven by the instrument
