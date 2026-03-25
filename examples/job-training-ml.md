# Example: Heterogeneous Effects of Job Training (Causal Forest + DML)

This example shows the skill guiding a researcher who has experimental data and wants to understand who benefits most from a job training program.

---

## Conversation

### User
```
/causal-inference I have data from a randomized job training experiment (like the JTPA or NSW). Treatment was randomly assigned. I want to go beyond the average effect and understand which types of participants benefit most from the training. I have rich baseline covariates: age, education, prior earnings, race, marital status, etc.
```

### Phase 1-2: Problem Framing & Data

**Skill identifies:**
> Great — you're in a strong position because you have experimental data, so the ATE is cleanly identified. Your goal is to estimate **heterogeneous treatment effects (CATE)**.
>
> - **Research question**: Who benefits most from job training?
> - **Treatment**: Random assignment to job training (binary)
> - **Outcome**: Post-program earnings (or employment)
> - **Estimand**: CATE — E[Y(1) - Y(0) | X = x] — the treatment effect conditional on individual characteristics
> - **Data**: Cross-sectional (one observation per individual, post-randomization)
>
> Since treatment is randomized, the **unconfoundedness assumption is satisfied by design**. The challenge is statistical — estimating a high-dimensional function CATE(x) with valid inference.

---

### Phase 3: Method Selection

**Skill recommends:**

> For CATE estimation with experimental data and rich covariates, I recommend a **multi-method approach**:
>
> | Method | Role | Strength |
> |--------|------|----------|
> | **Causal Forest** (Wager & Athey 2018) | Primary CATE estimator | Nonparametric; pointwise CIs; variable importance; built-in calibration test |
> | **DML** (Chernozhukov et al. 2018) | ATE/ATT as benchmark | Rigorous inference for average effects; cross-fitted; agnostic to ML method |
> | **Best Linear Projection** | Interpretable summary | Projects nonparametric CATE onto linear function of key covariates |
> | **Sorted Effects** (Chernozhukov et al. 2018) | Visualization | Rank individuals by predicted CATE; show distribution of effects |
>
> **Workflow:**
> 1. Estimate ATE via DML as a benchmark (should match simple difference-in-means)
> 2. Estimate CATE via Causal Forest
> 3. Run calibration test — does the forest detect real heterogeneity?
> 4. Examine variable importance — which covariates drive heterogeneity?
> 5. Use Best Linear Projection to summarize heterogeneity in interpretable terms
> 6. Characterize the most- and least-affected subgroups (CLAN analysis)
> 7. Optionally: estimate optimal treatment assignment policy

---

### Phase 4: Diagnostics

> **For Causal Forest:**
> - [ ] **Calibration test**: `test_calibration(cf)` — tests whether predicted CATEs are well-calibrated. The "mean forest prediction" coefficient should be significant (there IS heterogeneity) and close to 1 (predictions are well-calibrated).
> - [ ] **Out-of-bag honesty**: The forest uses separate samples for splitting and estimation — verify this is enabled (default in `grf`).
> - [ ] **Overlap**: Even with randomization, check that propensity scores are bounded away from 0 and 1 in all subgroups.
>
> **For DML:**
> - [ ] **Cross-fitting**: Use K=5 folds; show stability across different random splits.
> - [ ] **Nuisance model fit**: Report out-of-fold R-squared for outcome model.
>
> **General:**
> - [ ] **Overfitting check**: Compare in-sample vs. out-of-sample predictions. If using CATE for targeting, evaluate on a held-out sample.
> - [ ] **Pre-registered subgroups**: If you had pre-specified subgroups of interest, test those first and report ML-discovered heterogeneity as exploratory.

---

### Phase 5: Implementation

```python
from econml.dml import CausalForestDML
from doubleml import DoubleMLPLR, DoubleMLData
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Setup ──
covariates = ['age', 'education', 'prior_earnings', 'race',
              'married', 'hispanic', 'nodegree']
X = df[covariates].values
Y = df['earnings'].values
T = df['treatment'].values

# ═══════════════════════════════════════════
# Step 1: ATE via DML (benchmark)
# ═══════════════════════════════════════════
dml_data = DoubleMLData(df, y_col='earnings', d_cols='treatment',
                         x_cols=covariates)

ml_l = RandomForestRegressor(n_estimators=500, max_depth=5, random_state=42)
ml_m = RandomForestClassifier(n_estimators=500, max_depth=5, random_state=42)

dml_plr = DoubleMLPLR(dml_data, ml_l=ml_l, ml_m=ml_m, n_folds=5)
dml_plr.fit()
print('DML ATE estimate:')
print(dml_plr.summary)

# Simple difference-in-means for comparison
ate_simple = Y[T == 1].mean() - Y[T == 0].mean()
print(f'Simple DiM: {ate_simple:.2f}')

# ═══════════════════════════════════════════
# Step 2: Causal Forest for CATE
# ═══════════════════════════════════════════
cf = CausalForestDML(
    model_y='auto', model_t='auto',
    n_estimators=4000,
    min_samples_leaf=5,
    random_state=42,
    cv=5
)
cf.fit(Y=Y, T=T, X=X)

# ATE from forest
ate_inf = cf.ate_inference(X=X)
print(f'Causal Forest ATE: {ate_inf.mean_point:.2f} (SE: {ate_inf.stderr_mean:.2f})')
print(f'95% CI: [{ate_inf.conf_int_mean()[0][0]:.2f}, {ate_inf.conf_int_mean()[0][1]:.2f}]')

# ═══════════════════════════════════════════
# Step 3: CATE predictions
# ═══════════════════════════════════════════
cate = cf.effect(X=X)
cate_inf = cf.effect_inference(X=X)

df['cate'] = cate
df['cate_lower'] = cate_inf.conf_int()[0]
df['cate_upper'] = cate_inf.conf_int()[1]

# ═══════════════════════════════════════════
# Step 4: Feature importance via SHAP
# ═══════════════════════════════════════════
shap_values = cf.shap_values(X)
shap_importance = np.abs(shap_values['Y0']).mean(axis=0)
importance_df = pd.DataFrame({'variable': covariates, 'importance': shap_importance})
importance_df = importance_df.sort_values('importance', ascending=True)

plt.figure(figsize=(8, 5))
plt.barh(importance_df['variable'], importance_df['importance'])
plt.xlabel('Mean |SHAP value|')
plt.title('Variable Importance for Treatment Effect Heterogeneity')
plt.tight_layout()
plt.show()

# ═══════════════════════════════════════════
# Step 5: CLAN — Characterize subgroups by CATE quintile
# ═══════════════════════════════════════════
df['cate_quintile'] = pd.qcut(cate, q=5, labels=[1, 2, 3, 4, 5])

# GATE (Group Average Treatment Effects) by quintile
print('\nGroup Average Treatment Effects by CATE Quintile:')
for q in range(1, 6):
    mask = df['cate_quintile'] == q
    gate_inf = cf.ate_inference(X=X[mask])
    print(f'  Quintile {q}: GATE = {gate_inf.mean_point:.2f} '
          f'(SE: {gate_inf.stderr_mean:.2f}), N = {mask.sum()}')

# Average characteristics by quintile
print('\nSubgroup Characteristics by CATE Quintile:')
for cov in covariates:
    means = df.groupby('cate_quintile')[cov].mean()
    print(f'\n  {cov}:')
    for q, m in means.items():
        print(f'    Q{q}: {m:.3f}')

# ═══════════════════════════════════════════
# Step 6: Distribution of treatment effects
# ═══════════════════════════════════════════
plt.figure(figsize=(8, 5))
plt.hist(cate, bins=50, color='steelblue', alpha=0.7, edgecolor='white')
plt.axvline(x=ate_inf.mean_point, color='red', linestyle='--',
            label=f'ATE = {ate_inf.mean_point:.0f}')
plt.xlabel('Conditional Average Treatment Effect (CATE)')
plt.ylabel('Count')
plt.title('Distribution of Predicted Treatment Effects')
plt.legend()
plt.show()

# ═══════════════════════════════════════════
# Optional: Compare with Meta-Learners
# ═══════════════════════════════════════════
from econml.metalearners import XLearner
from sklearn.ensemble import GradientBoostingRegressor

x_learner = XLearner(models=GradientBoostingRegressor(n_estimators=200))
x_learner.fit(Y, T, X=X)
cate_x = x_learner.effect(X)
print(f'\nX-Learner ATE: {cate_x.mean():.2f}')
print(f'Correlation with Causal Forest CATE: {np.corrcoef(cate, cate_x)[0,1]:.3f}')
```

> **Reporting recommendations:**
> 1. Report ATE from simple DiM, DML, and Causal Forest — should agree closely (validating the methods)
> 2. Report calibration test results — evidence for/against heterogeneity
> 3. Show variable importance and BLP — which characteristics predict larger effects
> 4. Present GATE (Group Average Treatment Effects) by CATE quintile with CIs
> 5. Show CLAN table — who are the high-benefit vs. low-benefit individuals?
> 6. Caveat: CATE estimates are noisier than ATE. Heterogeneity findings should be treated as exploratory unless pre-specified.
> 7. If relevant, discuss optimal policy implications — but note the gap between statistical targeting and real-world implementation.
