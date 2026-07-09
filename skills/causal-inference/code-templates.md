# Code Templates for Causal Inference Methods

This file provides starter code templates in Python for the most commonly used causal inference methods. These are meant as starting points — adapt to the user's specific data and research design.

---

## 1. Difference-in-Differences

### Classic 2x2 DiD
```python
import statsmodels.formula.api as smf
import pandas as pd
import matplotlib.pyplot as plt

# Classic DiD with TWFE
model = smf.ols('outcome ~ treat * post + C(unit) + C(time)', data=df).fit(
    cov_type='cluster', cov_kwds={'groups': df['unit']}
)
print(model.summary())
```

### Staggered DiD — Callaway & Sant'Anna
```python
# Using the csdid package (Python port)
# pip install csdid
from csdid import att_gt

# Group-time ATTs
result = att_gt(
    data=df,
    yname='outcome',
    tname='year',
    idname='unit_id',
    gname='first_treat_year',  # 0 for never-treated
    control_group='nevertreated',  # or 'notyettreated'
    est_method='dr'  # doubly robust
)
print(result.summary())

# Aggregate: simple average
agg_simple = result.aggregate('simple')
print(agg_simple.summary())

# Aggregate: dynamic effects (event study)
agg_dynamic = result.aggregate('dynamic')
agg_dynamic.plot()
plt.title('Event Study: Callaway & Sant\'Anna')
plt.axhline(y=0, linestyle='--', color='gray')
plt.show()
```

### Alternative: DiD with linearmodels / pyfixest
```python
# pip install pyfixest
import pyfixest as pf

# TWFE
twfe = pf.feols('outcome ~ treat_post | unit + time', data=df,
                vcov={'CRV1': 'unit'})
print(twfe.summary())

# Event study with Sun & Abraham
es = pf.feols('outcome ~ sunab(first_treat_year, year) | unit + year', data=df,
              vcov={'CRV1': 'unit'})
pf.iplot(es)
plt.title('Sun & Abraham Event Study')
plt.show()
```

---

## 2. Regression Discontinuity Design

```python
from rdrobust import rdrobust, rdplot
from rddensity import rddensity
import numpy as np

# ── Main RD estimate (sharp) ──
rd_est = rdrobust(Y=df['outcome'], X=df['running_var'], c=0)
print(rd_est)

# ── Fuzzy RD (with endogenous treatment) ──
frd = rdrobust(Y=df['outcome'], X=df['running_var'], fuzzy=df['treatment'], c=0)
print(frd)

# ── RD plot ──
rdplot(y=df['outcome'], x=df['running_var'], c=0,
       title='RD Plot', x_label='Running Variable', y_label='Outcome')

# ── Manipulation test ──
density = rddensity(X=df['running_var'], c=0)
print(density)

# ── Covariate balance at cutoff ──
for cov in ['covar1', 'covar2', 'covar3']:
    print(f'\n=== {cov} ===')
    print(rdrobust(Y=df[cov], X=df['running_var'], c=0))

# ── Bandwidth sensitivity ──
opt_bw = rd_est.bws.values[0, 0]  # optimal bandwidth
for mult in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
    est = rdrobust(Y=df['outcome'], X=df['running_var'], c=0, h=opt_bw * mult)
    coef = est.coef.values[0]
    se = est.se.values[2]  # robust SE
    pv = est.pv.values[2]
    print(f'BW={opt_bw*mult:.1f} ({mult:.2f}x): Estimate={coef:.3f}, SE={se:.3f}, p={pv:.3f}')
```

---

## 3. Instrumental Variables

```python
from linearmodels.iv import IV2SLS
import statsmodels.api as sm

# ── 2SLS ──
iv = IV2SLS(
    dependent=df['outcome'],
    exog=sm.add_constant(df[['control1', 'control2']]),
    endog=df['treatment'],
    instruments=df[['instrument']]
).fit(cov_type='clustered', clusters=df['unit'])
print(iv.summary)
print(f"First-stage F: {iv.first_stage.diagnostics['f.stat']:.2f}")

# ── First stage ──
first_stage = sm.OLS(
    df['treatment'],
    sm.add_constant(df[['instrument', 'control1', 'control2']])
).fit(cov_type='cluster', cov_kwds={'groups': df['unit']})
print('First Stage:')
print(first_stage.summary())

# ── Reduced form ──
reduced_form = sm.OLS(
    df['outcome'],
    sm.add_constant(df[['instrument', 'control1', 'control2']])
).fit(cov_type='cluster', cov_kwds={'groups': df['unit']})
print('Reduced Form:')
print(reduced_form.summary())

# ── With fixed effects using pyfixest ──
import pyfixest as pf

iv_fe = pf.feols('outcome ~ control1 + control2 | unit + year | treatment ~ instrument',
                 data=df, vcov={'CRV1': 'unit'})
print(iv_fe.summary())
```

---

## 4. Synthetic Control

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Using SparseSC ──
# pip install SparseSC
from SparseSC import fit

# Reshape data to (units x time) matrices
outcome_matrix = df.pivot(index='unit_id', columns='year', values='outcome').values
treated_units = [0]  # index of treated unit(s)
T0 = 18  # number of pre-treatment periods

# Fit sparse synthetic control
sc_model = fit(
    features=outcome_matrix[:, :T0],
    targets=outcome_matrix[:, T0:],
    treated_units=treated_units
)

# ── Manual Synthetic Control via constrained optimization ──
from scipy.optimize import minimize

# Separate treated and donor pre-treatment outcomes
Y_pre_treat = outcome_matrix[0, :T0]  # treated unit pre-treatment
Y_pre_donors = outcome_matrix[1:, :T0]  # donor units pre-treatment
n_donors = Y_pre_donors.shape[0]

# Minimize pre-treatment MSPE subject to weights >= 0, sum to 1
def objective(w):
    synthetic = w @ Y_pre_donors
    return np.sum((Y_pre_treat - synthetic) ** 2)

constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
bounds = [(0, 1)] * n_donors
w0 = np.ones(n_donors) / n_donors

result = minimize(objective, w0, method='SLSQP', bounds=bounds, constraints=constraints)
weights = result.x

# Construct synthetic control for all periods
synthetic_all = weights @ outcome_matrix[1:, :]
actual_all = outcome_matrix[0, :]

# ── Path plot ──
years = sorted(df['year'].unique())
plt.figure(figsize=(10, 6))
plt.plot(years, actual_all, 'b-', label='Treated Unit', linewidth=2)
plt.plot(years, synthetic_all, 'r--', label='Synthetic Control', linewidth=2)
plt.axvline(x=years[T0], color='gray', linestyle=':', label='Treatment')
plt.xlabel('Year')
plt.ylabel('Outcome')
plt.title('Synthetic Control: Treated vs. Synthetic')
plt.legend()
plt.show()

# ── Gap plot (treatment effect) ──
gap = actual_all - synthetic_all
plt.figure(figsize=(10, 6))
plt.plot(years, gap, 'k-', linewidth=2)
plt.axvline(x=years[T0], color='gray', linestyle=':')
plt.axhline(y=0, color='gray', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Gap (Actual - Synthetic)')
plt.title('Estimated Treatment Effect')
plt.show()

# ── Pre-treatment RMSPE ──
rmspe_pre = np.sqrt(np.mean((actual_all[:T0] - synthetic_all[:T0]) ** 2))
print(f'Pre-treatment RMSPE: {rmspe_pre:.3f}')

# ── Donor weights ──
donor_ids = df['unit_id'].unique()[1:]
for uid, w in sorted(zip(donor_ids, weights), key=lambda x: -x[1]):
    if w > 0.01:
        print(f'  Unit {uid}: {w:.3f}')

# ── Placebo tests (permutation inference) ──
placebo_gaps = []
for i in range(1, outcome_matrix.shape[0]):
    Y_pre_t = outcome_matrix[i, :T0]
    Y_pre_d = np.delete(outcome_matrix, i, axis=0)[:, :T0]
    Y_all_d = np.delete(outcome_matrix, i, axis=0)

    def obj_placebo(w):
        return np.sum((Y_pre_t - w @ Y_pre_d) ** 2)

    n_d = Y_pre_d.shape[0]
    cons = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bds = [(0, 1)] * n_d
    res = minimize(obj_placebo, np.ones(n_d)/n_d, method='SLSQP', bounds=bds, constraints=cons)
    synthetic_placebo = res.x @ np.delete(outcome_matrix, i, axis=0)
    placebo_gaps.append(outcome_matrix[i, :] - synthetic_placebo)

# Plot all placebo gaps
plt.figure(figsize=(10, 6))
for g in placebo_gaps:
    plt.plot(years, g, color='lightgray', alpha=0.5)
plt.plot(years, gap, 'b-', linewidth=2, label='Treated Unit')
plt.axvline(x=years[T0], color='gray', linestyle=':')
plt.axhline(y=0, color='gray', linestyle='--')
plt.title('Placebo Tests')
plt.legend()
plt.show()
```

### Synthetic Difference-in-Differences
```python
# pip install synthdid
# Note: synthdid has limited Python support; consider using the R package via rpy2
# Alternative: manual implementation following Arkhangelsky et al. (2021)

# Using CausalImpact as a Bayesian alternative (see Section 10)
```

---

## 5. Propensity Score / Matching Methods

### Propensity Score Matching
```python
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd

covariates = ['x1', 'x2', 'x3']
X = df[covariates].values
treat = df['treat'].values

# ── Estimate propensity score ──
ps_model = LogisticRegression(max_iter=1000, C=1.0)
ps_model.fit(X, treat)
df['pscore'] = ps_model.predict_proba(X)[:, 1]

# ── Check overlap ──
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 1, figsize=(8, 5))
ax.hist(df.loc[df['treat']==1, 'pscore'], bins=30, alpha=0.5, label='Treated', density=True)
ax.hist(df.loc[df['treat']==0, 'pscore'], bins=30, alpha=0.5, label='Control', density=True)
ax.set_xlabel('Propensity Score')
ax.legend()
ax.set_title('Propensity Score Distribution')
plt.show()

# ── Nearest-neighbor matching (with caliper) ──
treated_idx = df[df['treat'] == 1].index
control_idx = df[df['treat'] == 0].index

nn = NearestNeighbors(n_neighbors=1, metric='euclidean')
nn.fit(df.loc[control_idx, ['pscore']].values)
distances, indices = nn.kneighbors(df.loc[treated_idx, ['pscore']].values)

caliper = 0.2 * df['pscore'].std()
matched_mask = distances.flatten() < caliper
matched_treated = treated_idx[matched_mask]
matched_control = control_idx[indices.flatten()[matched_mask]]

# ── ATT estimate ──
att = df.loc[matched_treated, 'outcome'].mean() - df.loc[matched_control, 'outcome'].mean()
print(f'ATT (matched): {att:.3f}')

# ── Balance check (standardized mean differences) ──
for cov in covariates:
    mean_t = df.loc[matched_treated, cov].mean()
    mean_c = df.loc[matched_control, cov].mean()
    pooled_std = np.sqrt((df.loc[matched_treated, cov].var() + df.loc[matched_control, cov].var()) / 2)
    smd = (mean_t - mean_c) / pooled_std
    print(f'{cov}: SMD = {smd:.3f} {"OK" if abs(smd) < 0.1 else "IMBALANCED"}')
```

### Inverse Probability Weighting (IPW)
```python
import numpy as np

# IPW weights
pscore = df['pscore'].values
treat = df['treat'].values

# ATT weights: treated get weight 1, controls get weight pscore/(1-pscore)
weights = np.where(treat == 1, 1.0, pscore / (1 - pscore))

# Trim extreme weights
weights = np.clip(weights, 0, np.percentile(weights[treat == 0], 99))

# Weighted outcome means
att_ipw = (
    np.average(df.loc[treat == 1, 'outcome'], weights=weights[treat == 1]) -
    np.average(df.loc[treat == 0, 'outcome'], weights=weights[treat == 0])
)
print(f'ATT (IPW): {att_ipw:.3f}')
```

### Doubly Robust / AIPW
```python
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import cross_val_predict
import numpy as np

covariates = ['x1', 'x2', 'x3']
X = df[covariates].values
Y = df['outcome'].values
D = df['treat'].values

# Propensity score (cross-fitted)
ps_model = LogisticRegression(max_iter=1000)
e_hat = cross_val_predict(ps_model, X, D, cv=5, method='predict_proba')[:, 1]
e_hat = np.clip(e_hat, 0.01, 0.99)

# Outcome model (cross-fitted, separate for treated and control)
mu1_hat = cross_val_predict(LinearRegression(), X[D == 1], Y[D == 1], cv=5)
mu0_hat = cross_val_predict(LinearRegression(), X[D == 0], Y[D == 0], cv=5)

# Full-sample outcome predictions (for AIPW formula)
from sklearn.base import clone
m1 = LinearRegression().fit(X[D == 1], Y[D == 1])
m0 = LinearRegression().fit(X[D == 0], Y[D == 0])
mu1_full = m1.predict(X)
mu0_full = m0.predict(X)

# AIPW estimator for ATT
n = len(Y)
n1 = D.sum()

aipw_att = (1/n1) * np.sum(
    D * Y - (D - e_hat) / (1 - e_hat) * (1 - D) * (Y - mu0_full)
) - (1/n1) * np.sum(
    D * mu0_full
)

# Simpler: using econml's doubly robust estimator
from econml.dr import DRLearner

dr = DRLearner(model_propensity=LogisticRegression(max_iter=1000),
               model_regression=LinearRegression(),
               model_final=LinearRegression())
dr.fit(Y, D, X=X)
ate = dr.ate(X)
print(f'ATE (DR-Learner): {ate:.3f}')
```

### Using causalinference package
```python
from causalinference import CausalModel

cm = CausalModel(Y=df['outcome'].values, D=df['treat'].values,
                 X=df[['x1', 'x2', 'x3']].values)

# OLS
cm.est_via_ols()
print('OLS:', cm.estimates)

# Propensity score matching
cm.est_propensity_s()
cm.est_via_matching()
print('Matching:', cm.estimates)

# Weighting
cm.est_via_weighting()
print('IPW:', cm.estimates)
```

---

## 6. Double/Debiased Machine Learning

```python
from doubleml import DoubleMLPLR, DoubleMLData
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LassoCV

# ── Setup ──
dml_data = DoubleMLData(df, y_col='outcome', d_cols='treat',
                         x_cols=['x1', 'x2', 'x3'])

# ── With Random Forest ──
ml_l = RandomForestRegressor(n_estimators=500, max_depth=5, random_state=42)
ml_m = RandomForestClassifier(n_estimators=500, max_depth=5, random_state=42)

dml_rf = DoubleMLPLR(dml_data, ml_l=ml_l, ml_m=ml_m, n_folds=5)
dml_rf.fit()
print('DML (Random Forest):')
print(dml_rf.summary)

# ── With Lasso ──
ml_l_lasso = LassoCV(cv=5)
ml_m_lasso = LogisticRegressionCV(cv=5, max_iter=1000)

dml_lasso = DoubleMLPLR(dml_data, ml_l=ml_l_lasso, ml_m=ml_m_lasso, n_folds=5)
dml_lasso.fit()
print('DML (Lasso):')
print(dml_lasso.summary)

# ── Sensitivity to number of folds ──
for k in [2, 3, 5, 10]:
    dml_k = DoubleMLPLR(dml_data, ml_l=ml_l, ml_m=ml_m, n_folds=k)
    dml_k.fit()
    print(f'K={k}: coef={dml_k.coef[0]:.4f}, se={dml_k.se[0]:.4f}')
```

---

## 7. Causal Forest / Heterogeneous Treatment Effects

```python
from econml.dml import CausalForestDML
from econml.dr import DRLearner
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

covariates = ['x1', 'x2', 'x3']
X = df[covariates].values
Y = df['outcome'].values
T = df['treat'].values

# ═══════════════════════════════════════════
# Causal Forest (via EconML)
# ═══════════════════════════════════════════
cf = CausalForestDML(
    model_y='auto', model_t='auto',
    n_estimators=2000,
    min_samples_leaf=5,
    random_state=42,
    cv=5  # cross-fitting folds
)
cf.fit(Y=Y, T=T, X=X)

# ── ATE ──
ate_inf = cf.ate_inference(X=X)
print(f'ATE: {ate_inf.mean_point:.3f} (SE: {ate_inf.stderr_mean:.3f})')
print(f'95% CI: [{ate_inf.conf_int_mean()[0][0]:.3f}, {ate_inf.conf_int_mean()[0][1]:.3f}]')

# ── CATE predictions ──
cate = cf.effect(X=X)
cate_inf = cf.effect_inference(X=X)

df['cate'] = cate
df['cate_lower'] = cate_inf.conf_int()[0]
df['cate_upper'] = cate_inf.conf_int()[1]

# ── Distribution of treatment effects ──
plt.figure(figsize=(8, 5))
plt.hist(cate, bins=50, color='steelblue', alpha=0.7, edgecolor='white')
plt.axvline(x=ate_inf.mean_point, color='red', linestyle='--',
            label=f'ATE = {ate_inf.mean_point:.3f}')
plt.xlabel('Conditional Average Treatment Effect (CATE)')
plt.ylabel('Count')
plt.title('Distribution of Predicted Treatment Effects')
plt.legend()
plt.show()

# ── Feature importance (via summary) ──
shap_values = cf.shap_values(X)
shap_importance = np.abs(shap_values['Y0']).mean(axis=0)
importance_df = pd.DataFrame({'variable': covariates, 'importance': shap_importance})
importance_df = importance_df.sort_values('importance', ascending=True)

plt.figure(figsize=(8, 5))
plt.barh(importance_df['variable'], importance_df['importance'])
plt.xlabel('Mean |SHAP value|')
plt.title('Feature Importance for Treatment Effect Heterogeneity')
plt.show()

# ── Group Average Treatment Effects (GATE) by quintile ──
df['cate_quintile'] = pd.qcut(cate, q=5, labels=[1, 2, 3, 4, 5])

for q in range(1, 6):
    mask = df['cate_quintile'] == q
    gate_inf = cf.ate_inference(X=X[mask])
    print(f'Quintile {q}: GATE = {gate_inf.mean_point:.3f} '
          f'(SE: {gate_inf.stderr_mean:.3f}), '
          f'N = {mask.sum()}')

# ── CLAN: Characterize subgroups ──
print('\nSubgroup Characteristics by CATE Quintile:')
for cov in covariates:
    means = df.groupby('cate_quintile')[cov].mean()
    print(f'\n{cov}:')
    for q, m in means.items():
        print(f'  Q{q}: {m:.3f}')
```

### Meta-Learners
```python
from econml.metalearners import SLearner, TLearner, XLearner
from sklearn.ensemble import GradientBoostingRegressor

# ── S-Learner ──
s_learner = SLearner(overall_model=GradientBoostingRegressor(n_estimators=200))
s_learner.fit(Y, T, X=X)
cate_s = s_learner.effect(X)

# ── T-Learner ──
t_learner = TLearner(models=GradientBoostingRegressor(n_estimators=200))
t_learner.fit(Y, T, X=X)
cate_t = t_learner.effect(X)

# ── X-Learner ──
x_learner = XLearner(models=GradientBoostingRegressor(n_estimators=200))
x_learner.fit(Y, T, X=X)
cate_x = x_learner.effect(X)

# Compare meta-learners
print(f'S-Learner ATE: {cate_s.mean():.3f}')
print(f'T-Learner ATE: {cate_t.mean():.3f}')
print(f'X-Learner ATE: {cate_x.mean():.3f}')
```

---

## 8. Sensitivity Analysis

### Oster's Delta
```python
import statsmodels.formula.api as smf
import numpy as np

# Short regression (no controls)
short = smf.ols('outcome ~ treat', data=df).fit()
beta_short = short.params['treat']
r2_short = short.rsquared

# Long regression (with controls)
long = smf.ols('outcome ~ treat + x1 + x2 + x3', data=df).fit()
beta_long = long.params['treat']
r2_long = long.rsquared

# Oster's delta
r2_max = min(1.0, 1.3 * r2_long)  # Oster's suggestion: R2_max = 1.3 * R2_long
delta = (beta_long * (r2_max - r2_long)) / ((beta_short - beta_long) * (r2_long - r2_short))
print(f"Oster's delta: {delta:.2f}")
print(f"  delta > 1 suggests robustness to unobservables")
print(f"  beta_short = {beta_short:.4f}, beta_long = {beta_long:.4f}")
print(f"  R2_short = {r2_short:.4f}, R2_long = {r2_long:.4f}")

# Bias-adjusted estimate (beta* under proportional selection)
beta_star = beta_long - delta * (beta_short - beta_long) * (r2_max - r2_long) / (r2_long - r2_short)
print(f"  Bias-adjusted beta* (delta=1): {beta_star:.4f}")
```

### Cinelli & Hazlett (Omitted Variable Bias)
```python
# Manual implementation of key sensitivity measures
import statsmodels.formula.api as smf
import numpy as np

model = smf.ols('outcome ~ treat + x1 + x2 + x3', data=df).fit()
beta_treat = model.params['treat']
se_treat = model.bse['treat']
t_stat = model.tvalues['treat']
dof = model.df_resid

# Robustness Value (RV): minimum confounding strength to reduce estimate to 0
# RV_q = sqrt(t^2 / (t^2 + dof))  (for q=1, i.e., reducing to 0)
rv = np.sqrt(t_stat**2 / (t_stat**2 + dof))
print(f'Robustness Value (RV): {rv:.3f}')
print(f'  An unobserved confounder would need to explain at least {rv:.1%} of the')
print(f'  residual variance of both treatment and outcome to reduce the estimate to 0.')

# Benchmark against observed covariates
# Partial R-squared of each covariate with outcome (residualized)
for cov in ['x1', 'x2', 'x3']:
    # Partial R2 of covariate with outcome
    restricted = smf.ols(f'outcome ~ treat + {" + ".join(c for c in ["x1","x2","x3"] if c != cov)}', data=df).fit()
    partial_r2_y = 1 - model.ssr / restricted.ssr

    # Partial R2 of covariate with treatment
    treat_full = smf.ols(f'treat ~ {" + ".join(["x1","x2","x3"])}', data=df).fit()
    treat_restricted = smf.ols(f'treat ~ {" + ".join(c for c in ["x1","x2","x3"] if c != cov)}', data=df).fit()
    partial_r2_d = 1 - treat_full.ssr / treat_restricted.ssr

    print(f'  {cov}: partial R2(Y)={partial_r2_y:.4f}, partial R2(D)={partial_r2_d:.4f}')
```

---

## 9. Mediation Analysis

```python
import statsmodels.formula.api as smf
import numpy as np
from scipy import stats

# ── Baron-Kenny (classic, for reference) ──
# Total effect
total = smf.ols('outcome ~ treat + x1 + x2', data=df).fit()
# Mediator model
med = smf.ols('mediator ~ treat + x1 + x2', data=df).fit()
# Outcome model with mediator
out = smf.ols('outcome ~ treat + mediator + x1 + x2', data=df).fit()

total_effect = total.params['treat']
direct_effect = out.params['treat']
indirect_effect = med.params['treat'] * out.params['mediator']

print(f'Total effect: {total_effect:.4f}')
print(f'Direct effect: {direct_effect:.4f}')
print(f'Indirect effect (via mediator): {indirect_effect:.4f}')
print(f'Proportion mediated: {indirect_effect / total_effect:.1%}')

# ── Bootstrap inference for indirect effect ──
n_boot = 1000
indirect_boot = np.zeros(n_boot)
for b in range(n_boot):
    boot_idx = np.random.choice(len(df), size=len(df), replace=True)
    boot_df = df.iloc[boot_idx]
    med_b = smf.ols('mediator ~ treat + x1 + x2', data=boot_df).fit()
    out_b = smf.ols('outcome ~ treat + mediator + x1 + x2', data=boot_df).fit()
    indirect_boot[b] = med_b.params['treat'] * out_b.params['mediator']

ci_lower = np.percentile(indirect_boot, 2.5)
ci_upper = np.percentile(indirect_boot, 97.5)
print(f'Indirect effect 95% CI (bootstrap): [{ci_lower:.4f}, {ci_upper:.4f}]')

# ── Sensitivity analysis: what if sequential ignorability is violated? ──
# Vary rho (correlation of mediator and outcome residuals)
print('\nSensitivity to violation of sequential ignorability:')
for rho in [0, 0.1, 0.2, 0.3, 0.5]:
    # Simplified: indirect effect attenuated by factor (1 - rho^2)
    adjusted = indirect_effect * (1 - rho**2)
    print(f'  rho={rho:.1f}: adjusted indirect effect = {adjusted:.4f}')
```

---

## 10. CausalImpact (Bayesian Structural Time Series)

```python
from causalimpact import CausalImpact
import pandas as pd

# Data: DataFrame with DatetimeIndex
# First column = outcome series, remaining columns = control series
data = pd.DataFrame({
    'y': outcome_series,
    'x1': control_series_1,
    'x2': control_series_2
}, index=dates)

pre_period = ['2020-01-01', '2020-06-30']
post_period = ['2020-07-01', '2020-12-31']

ci = CausalImpact(data, pre_period, post_period)

# Summary statistics
print(ci.summary())

# Narrative report
print(ci.summary(output='report'))

# Plot: original, pointwise effects, cumulative effects
ci.plot()
```

---

## 11. Interrupted Time Series

```python
import statsmodels.formula.api as smf
import statsmodels.api as sm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ── Create time variables ──
df['time'] = range(1, len(df) + 1)
df['intervention'] = (df['time'] >= intervention_point).astype(int)
df['time_after'] = np.where(df['intervention'] == 1, df['time'] - intervention_point, 0)

# ── Segmented regression ──
model = smf.ols('outcome ~ time + intervention + time_after', data=df).fit(
    cov_type='HAC', cov_kwds={'maxlags': 4}  # Newey-West SEs for autocorrelation
)
print(model.summary())
print(f'\nLevel change at intervention: {model.params["intervention"]:.3f} (p={model.pvalues["intervention"]:.4f})')
print(f'Slope change after intervention: {model.params["time_after"]:.3f} (p={model.pvalues["time_after"]:.4f})')

# ── Plot ──
plt.figure(figsize=(10, 6))
plt.scatter(df['time'], df['outcome'], color='gray', alpha=0.5, s=20)

# Pre-intervention fit
pre = df[df['intervention'] == 0]
plt.plot(pre['time'], model.predict(pre), 'b-', linewidth=2, label='Pre-intervention trend')

# Post-intervention fit
post = df[df['intervention'] == 1]
plt.plot(post['time'], model.predict(post), 'r-', linewidth=2, label='Post-intervention trend')

# Counterfactual (extend pre-trend)
cf_params = model.params.copy()
cf_params['intervention'] = 0
cf_params['time_after'] = 0
counterfactual = cf_params['Intercept'] + cf_params['time'] * post['time']
plt.plot(post['time'], counterfactual, 'b--', alpha=0.5, label='Counterfactual')

plt.axvline(x=intervention_point, color='gray', linestyle=':', label='Intervention')
plt.xlabel('Time')
plt.ylabel('Outcome')
plt.title('Interrupted Time Series Analysis')
plt.legend()
plt.show()

# ── Test for autocorrelation ──
from statsmodels.stats.diagnostic import acorr_ljungbox
lb_test = acorr_ljungbox(model.resid, lags=[4, 8, 12], return_df=True)
print('\nLjung-Box test for autocorrelation:')
print(lb_test)
```

---

## 12. Structural Estimation: BLP Demand

### BLP with PyBLP
```python
import pyblp
import numpy as np
import pandas as pd

# ── Data preparation ──
# product_data: DataFrame with columns:
#   market_ids, product_ids, shares, prices, x1, x2, ..., demand_instruments0, ...
# Must include: market shares, product characteristics, prices, instruments

# ── Define the problem ──
# Formulation: (X1 for linear params, X2 for random coefficients, X3 for supply)
product_formulations = (
    pyblp.Formulation('1 + x1 + x2', absorb='C(brand_id)'),  # X1: linear in beta (+ brand FE)
    pyblp.Formulation('1 + x1 + prices'),                      # X2: random coefficients on these
)

# Integration: Monte Carlo or product rule for simulating heterogeneity
mc_integration = pyblp.Integration('halton', size=200, specification_options={'seed': 0})

# Build the problem
problem = pyblp.Problem(
    product_formulations,
    product_data,
    integration=mc_integration
)
print(problem)

# ── Solve (estimate) ──
# Initial guess for sigma (random coefficient SDs) and pi (demographic interactions)
initial_sigma = np.diag([0.5, 0.5, 0.5])  # diagonal = independent random coefficients

results = problem.solve(
    sigma=initial_sigma,
    optimization=pyblp.Optimization('bfgs', {'gtol': 1e-8}),
    iteration=pyblp.Iteration('squarem', {'atol': 1e-14}),  # contraction mapping for delta
    method='1s'  # '1s' for one-step GMM, '2s' for efficient two-step
)
print(results)

# ── Key outputs ──
# Price coefficient and random coefficient SDs
print('\nParameter estimates:')
print(results.beta)     # linear parameters
print(results.sigma)    # random coefficient standard deviations

# ── Elasticities ──
elasticities = results.compute_elasticities()
# Own-price elasticities (diagonal of each market's elasticity matrix)
own_elasticities = results.extract_diagonal_means(elasticities)
print(f'\nMean own-price elasticity: {own_elasticities.mean():.3f}')

# Aggregate elasticity matrix for a specific market
market_id = product_data['market_ids'].unique()[0]
market_mask = product_data['market_ids'] == market_id
market_elasticities = elasticities[market_mask][:, market_mask]
print(f'\nElasticity matrix for market {market_id}:')
print(pd.DataFrame(market_elasticities,
                    index=product_data.loc[market_mask, 'product_ids'],
                    columns=product_data.loc[market_mask, 'product_ids']).round(3))

# ── Consumer surplus ──
cs = results.compute_consumer_surpluses()
print(f'\nMean consumer surplus: {cs.mean():.2f}')

# ── Markup and marginal cost recovery (supply side) ──
# Assuming Nash-Bertrand pricing
costs = results.compute_costs()  # implied marginal costs
markups = results.compute_markups()
print(f'Mean markup: {markups.mean():.3f}')
print(f'Mean marginal cost: {costs.mean():.2f}')

# Check: any negative marginal costs? (red flag)
print(f'Negative marginal costs: {(costs < 0).sum()} / {len(costs)}')
```

### BLP Counterfactuals: Merger Simulation
```python
# ── Merger simulation ──
# Suppose firms 1 and 2 merge. Update ownership matrix.

# Current ownership: product_data['firm_ids']
# New ownership: change firm 2's products to firm 1
product_data_merger = product_data.copy()
product_data_merger.loc[product_data_merger['firm_ids'] == 2, 'firm_ids'] = 1

# Solve for new equilibrium prices
merger_results = results.solve_approximate_merger(
    product_data_merger[['firm_ids']],
    iteration=pyblp.Iteration('simple', {'atol': 1e-12})
)

# Price changes
delta_prices = merger_results.product_data['prices'] - product_data['prices']
print('Price changes from merger:')
print(delta_prices.describe())

# Consumer surplus change
cs_post = results.compute_consumer_surpluses(prices=merger_results.product_data['prices'])
cs_change = (cs_post - cs).mean()
print(f'Change in mean consumer surplus: {cs_change:.2f}')
```

### Multinomial Logit (Individual-Level)
```python
import statsmodels.api as sm
from scipy.optimize import minimize
from scipy.special import logsumexp
import numpy as np

# ── Data: long format ──
# Each row = (individual i, alternative j)
# Columns: choice (0/1), price, x1, x2, ...

def log_likelihood_logit(params, X, choice, n_individuals, n_alternatives):
    """Conditional logit log-likelihood."""
    V = X @ params  # utilities
    V = V.reshape(n_individuals, n_alternatives)
    choice_mat = choice.reshape(n_individuals, n_alternatives)

    # Log-sum-exp for numerical stability
    log_denom = logsumexp(V, axis=1, keepdims=True)
    log_probs = V - log_denom

    # Log-likelihood
    ll = np.sum(choice_mat * log_probs)
    return -ll  # minimize negative LL

# Estimate
X = df[['price', 'x1', 'x2']].values
choice = df['choice'].values
n_ind = df['individual_id'].nunique()
n_alt = df['alternative_id'].nunique()

result = minimize(log_likelihood_logit, x0=np.zeros(X.shape[1]),
                  args=(X, choice, n_ind, n_alt), method='BFGS')
print('Parameters:', result.x)
print('Price coefficient:', result.x[0])

# Alternatively, use a package
# pip install xlogit
from xlogit import MultinomialLogit

model = MultinomialLogit()
model.fit(X=df[['x1', 'x2']], y=df['choice'], varnames=['x1', 'x2'],
          ids=df['individual_id'], alts=df['alternative_id'],
          price=df['price'])
model.summary()
```

### Dynamic Discrete Choice (Rust-Style)
```python
import numpy as np
from scipy.special import logsumexp
from scipy.optimize import minimize

# ── Simplified bus engine replacement example ──
# State: mileage (discretized into bins)
# Actions: {0: keep, 1: replace}
# Utility: u(keep, s) = -theta_1 * s (maintenance cost increases with mileage)
#          u(replace, s) = -RC (replacement cost, independent of state)

n_states = 50  # mileage bins
beta = 0.99    # discount factor

def solve_value_function(theta_1, RC, trans_probs, beta=0.99, tol=1e-10):
    """Solve for EV (expected value) via value function iteration."""
    EV = np.zeros(n_states)
    for _ in range(10000):
        # Flow utility for each action in each state
        u_keep = -theta_1 * np.arange(n_states)
        u_replace = -RC * np.ones(n_states)

        # Choice-specific value functions
        v_keep = u_keep + beta * trans_probs @ EV
        v_replace = u_replace + beta * trans_probs[0] @ EV  # reset to state 0 after replacement

        # Update EV (using logsum formula for Type-I EV errors)
        V = np.column_stack([v_keep, v_replace])
        EV_new = logsumexp(V, axis=1)

        if np.max(np.abs(EV_new - EV)) < tol:
            break
        EV = EV_new
    return EV

def ccp_from_EV(theta_1, RC, trans_probs, EV):
    """Compute conditional choice probabilities from EV."""
    u_keep = -theta_1 * np.arange(n_states)
    u_replace = -RC * np.ones(n_states)

    v_keep = u_keep + beta * trans_probs @ EV
    v_replace = u_replace + beta * trans_probs[0] @ EV

    # Probability of replacement
    p_replace = 1 / (1 + np.exp(v_keep - v_replace))
    return p_replace

def nfxp_likelihood(params, data_states, data_actions, trans_probs):
    """NFXP: nested fixed point log-likelihood."""
    theta_1, RC = params
    if theta_1 < 0 or RC < 0:
        return 1e10

    EV = solve_value_function(theta_1, RC, trans_probs)
    p_replace = ccp_from_EV(theta_1, RC, trans_probs, EV)

    # Likelihood
    p_action = np.where(data_actions == 1, p_replace[data_states], 1 - p_replace[data_states])
    ll = np.sum(np.log(np.clip(p_action, 1e-15, 1)))
    return -ll

# Estimate
result = minimize(nfxp_likelihood, x0=[0.01, 5.0],
                  args=(data_states, data_actions, trans_probs),
                  method='Nelder-Mead')
print(f'theta_1 (maintenance cost): {result.x[0]:.4f}')
print(f'RC (replacement cost): {result.x[1]:.2f}')
```

---

## 13. Robustness Check Templates (Phase 6)

### Specification Curve / Robustness Table
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyfixest as pf

# ── Define specifications to loop over ──
specs = []

# Vary outcome transformation
for outcome in ['outcome', 'log_outcome', 'rank_outcome']:
    # Vary controls
    for controls in ['', ' + x1', ' + x1 + x2 + x3']:
        # Vary fixed effects
        for fe in ['unit', 'unit + time', 'unit + time']:
            # Vary clustering
            for cluster_var in ['unit', 'state']:
                formula = f'{outcome} ~ treat_post{controls} | {fe}'
                try:
                    model = pf.feols(formula, data=df, vcov={'CRV1': cluster_var})
                    specs.append({
                        'outcome': outcome,
                        'controls': controls.strip(' +') or 'none',
                        'fe': fe,
                        'cluster': cluster_var,
                        'estimate': model.coef().values[0],
                        'se': model.se().values[0],
                        'pvalue': model.pvalue().values[0],
                        'n_obs': model.nobs,
                    })
                except Exception as e:
                    pass

spec_df = pd.DataFrame(specs)
spec_df['ci_lower'] = spec_df['estimate'] - 1.96 * spec_df['se']
spec_df['ci_upper'] = spec_df['estimate'] + 1.96 * spec_df['se']
spec_df = spec_df.sort_values('estimate').reset_index(drop=True)

# ── Specification curve plot ──
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1],
                                sharex=True, gridspec_kw={'hspace': 0.05})

# Top panel: coefficient estimates with CIs
ax1.scatter(range(len(spec_df)), spec_df['estimate'], s=15, color='steelblue', zorder=3)
ax1.vlines(range(len(spec_df)), spec_df['ci_lower'], spec_df['ci_upper'],
           color='steelblue', alpha=0.3, linewidth=1)
ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

# Highlight preferred specification
preferred_idx = spec_df.index[len(spec_df) // 2]  # or whichever is preferred
ax1.scatter([preferred_idx], [spec_df.loc[preferred_idx, 'estimate']],
            s=50, color='red', zorder=4, label='Preferred')
ax1.set_ylabel('Treatment Effect Estimate')
ax1.set_title('Specification Curve')
ax1.legend()

# Bottom panel: specification indicators
# (simplified — mark which specs are significant)
colors = ['green' if p < 0.05 else 'lightgray' for p in spec_df['pvalue']]
ax2.bar(range(len(spec_df)), [1]*len(spec_df), color=colors, width=1.0)
ax2.set_ylabel('p < 0.05')
ax2.set_xlabel('Specification (sorted by estimate)')
ax2.set_yticks([])

plt.tight_layout()
plt.show()

# ── Print robustness table ──
print(spec_df[['outcome', 'controls', 'fe', 'cluster', 'estimate', 'se', 'pvalue', 'n_obs']].to_string(index=False))
```

### Placebo Tests (Outcomes and Timing)
```python
import pyfixest as pf
import matplotlib.pyplot as plt
import numpy as np

# ── Placebo outcomes ──
# Test the treatment effect on outcomes that SHOULD NOT be affected
placebo_outcomes = ['placebo_outcome1', 'placebo_outcome2', 'placebo_outcome3']
real_outcome = 'outcome'
all_outcomes = [real_outcome] + placebo_outcomes

placebo_results = []
for y in all_outcomes:
    model = pf.feols(f'{y} ~ treat_post | unit + time', data=df, vcov={'CRV1': 'unit'})
    placebo_results.append({
        'outcome': y,
        'estimate': model.coef().values[0],
        'se': model.se().values[0],
        'pvalue': model.pvalue().values[0],
        'is_real': y == real_outcome
    })

placebo_df = pd.DataFrame(placebo_results)

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
colors = ['red' if r else 'steelblue' for r in placebo_df['is_real']]
ax.barh(placebo_df['outcome'], placebo_df['estimate'], color=colors, alpha=0.7)
ax.errorbar(placebo_df['estimate'], placebo_df['outcome'],
            xerr=1.96 * placebo_df['se'], fmt='none', color='black', capsize=3)
ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('Estimate')
ax.set_title('Placebo Outcomes Test (red = real outcome)')
plt.tight_layout()
plt.show()

# ── Placebo timing ──
# Shift treatment date backward and re-estimate
placebo_timing_results = []
for shift in [-8, -6, -4, -2, 0]:  # 0 = actual treatment date
    # Create shifted treatment indicator
    df[f'treat_post_shift{shift}'] = (
        (df['time'] >= df['first_treat'] + shift) & (df['first_treat'] > 0)
    ).astype(int)
    model = pf.feols(f'outcome ~ treat_post_shift{shift} | unit + time',
                     data=df, vcov={'CRV1': 'unit'})
    placebo_timing_results.append({
        'shift': shift,
        'estimate': model.coef().values[0],
        'se': model.se().values[0],
        'is_real': shift == 0
    })

timing_df = pd.DataFrame(placebo_timing_results)
fig, ax = plt.subplots(figsize=(8, 5))
colors = ['red' if r else 'gray' for r in timing_df['is_real']]
ax.bar(timing_df['shift'], timing_df['estimate'], color=colors, alpha=0.7)
ax.errorbar(timing_df['shift'], timing_df['estimate'],
            yerr=1.96 * timing_df['se'], fmt='none', color='black', capsize=5)
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('Treatment Timing Shift (periods)')
ax.set_ylabel('Estimate')
ax.set_title('Placebo Timing Test (red = actual treatment)')
plt.tight_layout()
plt.show()
```

### Sensitivity Analysis: Oster + Cinelli-Hazlett Combined
```python
import statsmodels.formula.api as smf
import numpy as np
import matplotlib.pyplot as plt

# ═══════════════════════════════════════════
# Oster's Delta
# ═══════════════════════════════════════════
short = smf.ols('outcome ~ treat', data=df).fit()
long = smf.ols('outcome ~ treat + x1 + x2 + x3', data=df).fit()

beta_s, beta_l = short.params['treat'], long.params['treat']
r2_s, r2_l = short.rsquared, long.rsquared
r2_max = min(1.0, 1.3 * r2_l)

delta = (beta_l * (r2_max - r2_l)) / ((beta_s - beta_l) * (r2_l - r2_s))
beta_star = beta_l - (beta_s - beta_l) * (r2_max - r2_l) / (r2_l - r2_s)

print('=== Oster (2019) Sensitivity ===')
print(f'  Short regression beta: {beta_s:.4f} (R2 = {r2_s:.4f})')
print(f'  Long regression beta:  {beta_l:.4f} (R2 = {r2_l:.4f})')
print(f'  R2_max (1.3 * R2_long): {r2_max:.4f}')
print(f'  Delta: {delta:.2f}')
print(f'  Interpretation: {"ROBUST (delta > 1)" if abs(delta) > 1 else "SENSITIVE (delta < 1)"}')
print(f'  Bias-adjusted beta* (delta=1): {beta_star:.4f}')

# ═══════════════════════════════════════════
# Cinelli & Hazlett (2020) — Robustness Value
# ═══════════════════════════════════════════
model = smf.ols('outcome ~ treat + x1 + x2 + x3', data=df).fit()
t_stat = model.tvalues['treat']
dof = model.df_resid

rv = np.sqrt(t_stat**2 / (t_stat**2 + dof))

print(f'\n=== Cinelli & Hazlett (2020) Sensitivity ===')
print(f'  t-statistic: {t_stat:.3f}')
print(f'  Robustness Value (RV): {rv:.3f}')
print(f'  Interpretation: A confounder would need partial R2 > {rv:.3f}')
print(f'  with BOTH treatment and outcome to nullify the result.')

# Benchmark against observed covariates
print(f'\n  Benchmarks (partial R2 of observed covariates):')
covariates = ['x1', 'x2', 'x3']
for cov in covariates:
    others = [c for c in covariates if c != cov]
    restricted = smf.ols(f'outcome ~ treat + {" + ".join(others)}', data=df).fit()
    partial_r2_y = 1 - model.ssr / restricted.ssr

    treat_full = smf.ols(f'treat ~ {" + ".join(covariates)}', data=df).fit()
    treat_rest = smf.ols(f'treat ~ {" + ".join(others)}', data=df).fit()
    partial_r2_d = 1 - treat_full.ssr / treat_rest.ssr

    stronger = 'STRONGER than RV' if min(partial_r2_y, partial_r2_d) > rv else 'weaker than RV'
    print(f'    {cov}: R2(Y)={partial_r2_y:.4f}, R2(D)={partial_r2_d:.4f} ({stronger})')

# ═══════════════════════════════════════════
# Sensitivity contour plot (simplified)
# ═══════════════════════════════════════════
r2d_grid = np.linspace(0, 0.3, 100)
r2y_grid = np.linspace(0, 0.3, 100)
R2D, R2Y = np.meshgrid(r2d_grid, r2y_grid)

# Adjusted estimate as function of confounder strength
# Simplified bias formula: bias ≈ sqrt(R2D * R2Y) * se * sqrt(dof) / (1 - R2D)
bias = np.sqrt(R2D * R2Y) * np.sqrt(model.ssr / dof) / np.sqrt(
    model.ssr / dof * (1 - R2D)) * np.abs(t_stat) / t_stat
adjusted = beta_l - np.sign(beta_l) * np.abs(bias) * model.bse['treat'] * t_stat

fig, ax = plt.subplots(figsize=(8, 6))
contours = ax.contour(R2D, R2Y, adjusted, levels=[0], colors='red', linewidths=2)
ax.contourf(R2D, R2Y, adjusted, levels=np.linspace(adjusted.min(), adjusted.max(), 20),
            cmap='RdYlGn', alpha=0.5)
ax.set_xlabel('Partial R² with Treatment')
ax.set_ylabel('Partial R² with Outcome')
ax.set_title(f'Sensitivity Contour (red line: estimate = 0)')

# Plot benchmarks
for cov in covariates:
    others = [c for c in covariates if c != cov]
    restricted = smf.ols(f'outcome ~ treat + {" + ".join(others)}', data=df).fit()
    pr2_y = 1 - model.ssr / restricted.ssr
    treat_full = smf.ols(f'treat ~ {" + ".join(covariates)}', data=df).fit()
    treat_rest = smf.ols(f'treat ~ {" + ".join(others)}', data=df).fit()
    pr2_d = 1 - treat_full.ssr / treat_rest.ssr
    ax.plot(pr2_d, pr2_y, 'ko', markersize=8)
    ax.annotate(cov, (pr2_d, pr2_y), textcoords='offset points', xytext=(5, 5))

plt.colorbar(ax.contourf(R2D, R2Y, adjusted, levels=20, cmap='RdYlGn', alpha=0.5),
             label='Adjusted Estimate')
plt.tight_layout()
plt.show()
```

### Wild Cluster Bootstrap
```python
# pip install wildboottest
from wildboottest.wildboottest import wildboottest
import pyfixest as pf

# Main estimate
model = pf.feols('outcome ~ treat_post | unit + time', data=df, vcov={'CRV1': 'state'})
print('Cluster-robust estimate:')
print(model.summary())

# Wild cluster bootstrap (for few clusters)
boot_result = wildboottest(
    model=model,
    param='treat_post',
    cluster=df['state'],
    B=9999,
    seed=42
)
print(f'\nWild Cluster Bootstrap:')
print(f'  t-stat: {boot_result["t_stat"]:.3f}')
print(f'  Bootstrap p-value: {boot_result["pvalue"]:.4f}')
print(f'  CI: [{boot_result["ci"][0]:.4f}, {boot_result["ci"][1]:.4f}]')

# Compare inference methods
print(f'\nComparison:')
print(f'  Cluster-robust p-value: {model.pvalue().values[0]:.4f}')
print(f'  Wild bootstrap p-value: {boot_result["pvalue"]:.4f}')
if boot_result['pvalue'] < 0.05 and model.pvalue().values[0] < 0.05:
    print('  Both significant at 5% — inference is robust.')
elif boot_result['pvalue'] >= 0.05 and model.pvalue().values[0] < 0.05:
    print('  WARNING: Significant under cluster-robust but NOT under wild bootstrap.')
    print('  Significance may be an artifact of few clusters.')
```

### Randomization Inference
```python
import numpy as np
import matplotlib.pyplot as plt

def compute_test_stat(outcome, treatment):
    """Simple difference in means as test statistic."""
    return outcome[treatment == 1].mean() - outcome[treatment == 0].mean()

# Observed test statistic
observed_stat = compute_test_stat(df['outcome'].values, df['treat'].values)

# Permutation distribution
n_perms = 10000
perm_stats = np.zeros(n_perms)
treatment = df['treat'].values.copy()
outcome = df['outcome'].values

for i in range(n_perms):
    np.random.shuffle(treatment)
    perm_stats[i] = compute_test_stat(outcome, treatment)

# Two-sided p-value
p_value = np.mean(np.abs(perm_stats) >= np.abs(observed_stat))

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(perm_stats, bins=100, density=True, alpha=0.7, color='steelblue',
        label='Permutation distribution')
ax.axvline(x=observed_stat, color='red', linewidth=2, linestyle='--',
           label=f'Observed = {observed_stat:.3f}')
ax.axvline(x=-observed_stat, color='red', linewidth=2, linestyle='--', alpha=0.5)
ax.set_xlabel('Test Statistic')
ax.set_ylabel('Density')
ax.set_title(f'Randomization Inference (p = {p_value:.4f})')
ax.legend()
plt.tight_layout()
plt.show()

print(f'Observed statistic: {observed_stat:.4f}')
print(f'Randomization inference p-value (two-sided): {p_value:.4f}')
```

### Subsample Robustness
```python
import pyfixest as pf
import pandas as pd
import matplotlib.pyplot as plt

# ── Leave-one-out by group ──
groups = df['state'].unique()
loo_results = []

for g in groups:
    df_loo = df[df['state'] != g]
    model = pf.feols('outcome ~ treat_post | unit + time',
                     data=df_loo, vcov={'CRV1': 'state'})
    loo_results.append({
        'dropped': g,
        'estimate': model.coef().values[0],
        'se': model.se().values[0],
        'n_obs': model.nobs
    })

loo_df = pd.DataFrame(loo_results).sort_values('estimate')

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(range(len(loo_df)), loo_df['estimate'], s=20, color='steelblue')
ax.fill_between(range(len(loo_df)),
                loo_df['estimate'] - 1.96 * loo_df['se'],
                loo_df['estimate'] + 1.96 * loo_df['se'],
                alpha=0.2, color='steelblue')
ax.axhline(y=0, color='black', linewidth=0.5)

# Full sample estimate for reference
full_model = pf.feols('outcome ~ treat_post | unit + time', data=df, vcov={'CRV1': 'state'})
ax.axhline(y=full_model.coef().values[0], color='red', linestyle='--',
           label=f'Full sample: {full_model.coef().values[0]:.4f}')

ax.set_xlabel('Specification (one state dropped)')
ax.set_ylabel('Estimate')
ax.set_title('Leave-One-Out Robustness')
ax.legend()
plt.tight_layout()
plt.show()

# Flag influential states
full_est = full_model.coef().values[0]
loo_df['deviation'] = abs(loo_df['estimate'] - full_est)
influential = loo_df.nlargest(3, 'deviation')
print('Most influential states (largest change when dropped):')
for _, row in influential.iterrows():
    print(f"  Drop {row['dropped']}: estimate = {row['estimate']:.4f} "
          f"(deviation = {row['deviation']:.4f})")
```

### Multiple Testing Correction
```python
import numpy as np
from statsmodels.stats.multitest import multipletests

# Suppose you have p-values from testing multiple outcomes
outcomes = ['outcome1', 'outcome2', 'outcome3', 'outcome4', 'outcome5']
p_values = np.array([0.003, 0.021, 0.048, 0.087, 0.230])

# Bonferroni correction
bonf_reject, bonf_pvals, _, _ = multipletests(p_values, method='bonferroni')

# Benjamini-Hochberg (FDR control)
bh_reject, bh_pvals, _, _ = multipletests(p_values, method='fdr_bh')

# Holm (step-down Bonferroni — less conservative)
holm_reject, holm_pvals, _, _ = multipletests(p_values, method='holm')

# Summary table
import pandas as pd
correction_df = pd.DataFrame({
    'outcome': outcomes,
    'raw_p': p_values,
    'bonferroni_p': bonf_pvals,
    'bonferroni_sig': bonf_reject,
    'holm_p': holm_pvals,
    'holm_sig': holm_reject,
    'bh_p': bh_pvals,
    'bh_sig': bh_reject,
})
print('Multiple Testing Corrections:')
print(correction_df.to_string(index=False))
print(f'\nRaw significant (p < 0.05): {sum(p_values < 0.05)} / {len(p_values)}')
print(f'Bonferroni significant: {sum(bonf_reject)} / {len(p_values)}')
print(f'Holm significant: {sum(holm_reject)} / {len(p_values)}')
print(f'Benjamini-Hochberg significant: {sum(bh_reject)} / {len(p_values)}')
```

### Cross-Method Comparison Table
```python
import pandas as pd

# After running multiple methods, compile results
comparison = pd.DataFrame([
    {'method': 'DiD (TWFE)', 'estimate': 0.045, 'se': 0.012,
     'assumption': 'Parallel trends', 'note': 'May be biased with heterogeneous effects'},
    {'method': 'DiD (Callaway-Sant\'Anna)', 'estimate': 0.052, 'se': 0.015,
     'assumption': 'Parallel trends (group-time)', 'note': 'Robust to heterogeneous effects'},
    {'method': 'Synthetic Control', 'estimate': 0.048, 'se': 0.018,
     'assumption': 'Factor model', 'note': 'Permutation p-value'},
    {'method': 'OLS + controls', 'estimate': 0.038, 'se': 0.010,
     'assumption': 'Selection on observables', 'note': 'Biased benchmark'},
    {'method': 'Matching (PSM)', 'estimate': 0.041, 'se': 0.014,
     'assumption': 'Conditional independence', 'note': 'ATT'},
])

comparison['ci_lower'] = comparison['estimate'] - 1.96 * comparison['se']
comparison['ci_upper'] = comparison['estimate'] + 1.96 * comparison['se']
comparison['significant'] = comparison['ci_lower'] > 0

print('Cross-Method Comparison:')
print(comparison[['method', 'estimate', 'se', 'ci_lower', 'ci_upper', 'assumption']].to_string(index=False))

# Forest plot
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 5))
y_pos = range(len(comparison))
ax.errorbar(comparison['estimate'], y_pos, xerr=1.96 * comparison['se'],
            fmt='o', color='steelblue', capsize=5, markersize=8)
ax.axvline(x=0, color='black', linewidth=0.5)
ax.set_yticks(y_pos)
ax.set_yticklabels(comparison['method'])
ax.set_xlabel('Treatment Effect Estimate')
ax.set_title('Cross-Method Comparison (Forest Plot)')
plt.tight_layout()
plt.show()
```

---

## 14. Report Generation (Phase 7)

### Report Scaffolding & Figure Management
```python
import os
from datetime import date

# ── Create report directory structure ──
report_dir = 'causal_analysis_report'
figures_dir = os.path.join(report_dir, 'figures')
os.makedirs(figures_dir, exist_ok=True)

def save_figure(fig, name, caption=''):
    """Save a matplotlib figure to the report figures directory."""
    path = os.path.join(figures_dir, f'{name}.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f'Saved: {path}')
    return f'![{caption}](figures/{name}.png)'

# ── Report accumulator ──
# Build this throughout the analysis; used to compile the final report
report_data = {
    'title': 'Effect of [Treatment] on [Outcome]',
    'date': date.today().isoformat(),
    'research_question': '',
    'treatment': '',
    'outcome': '',
    'unit': '',
    'estimand': '',  # ATE, ATT, LATE, CATE
    'method': '',
    'core_assumption': '',
    'why_method': '',
    'alternatives_considered': '',
    'main_estimate': {
        'estimate': None,
        'se': None,
        'ci_lower': None,
        'ci_upper': None,
        'pvalue': None,
        'n': None,
    },
    'robustness': {
        'identification': [],  # [{'test': str, 'result': str, 'pass': bool, 'note': str}]
        'specifications': [],  # [{'name': str, 'estimate': float, 'se': float, 'pvalue': float, 'n': int}]
        'subsamples': [],
        'inference': [],       # [{'method': str, 'se': float, 'pvalue': float, 'significant': bool}]
        'sensitivity': {},     # {'oster_delta': float, 'rv': float, ...}
        'placebos': [],        # [{'test': str, 'estimate': float, 'pvalue': float, 'pass': bool}]
        'cross_method': [],    # [{'method': str, 'estimate': float, 'se': float, 'assumption': str}]
    },
    'figures': [],            # [{'ref': str (markdown ref), 'section': str}]
    'limitations': [],
    'code_blocks': [],        # [{'section': str, 'label': str, 'code': str}]
}
```

### Compile Report from Accumulated Data
```python
def generate_report(rd):
    """Generate the full markdown report from the report_data dictionary."""

    # Helper: format code block in <details>
    def code_block(label, code):
        return f'''<details>
<summary>Code: {label}</summary>

```python
{code}
```

</details>'''

    # Helper: robustness status
    def status(passed):
        return '✓' if passed else '⚠'

    # ── Build main estimate table ──
    me = rd['main_estimate']
    main_table = f'''| Specification | Estimate | SE | 95% CI | p-value | N |
|--------------|---------|-----|--------|---------|---|
| **Preferred** | {me["estimate"]:.4f} | {me["se"]:.4f} | [{me["ci_lower"]:.4f}, {me["ci_upper"]:.4f}] | {me["pvalue"]:.4f} | {me["n"]:,} |'''

    # ── Build identification threats table ──
    id_rows = '\n'.join([
        f'| {t["test"]} | {t["result"]} | {status(t["pass"])} | {t["note"]} |'
        for t in rd['robustness']['identification']
    ])
    id_table = f'''| Test | Result | Status | Interpretation |
|------|--------|--------|---------------|
{id_rows}''' if id_rows else '*No identification tests recorded yet.*'

    # ── Build inference table ──
    inf_rows = '\n'.join([
        f'| {t["method"]} | {t["se"]:.4f} | {t["pvalue"]:.4f} | {"Yes" if t["significant"] else "No"} |'
        for t in rd['robustness']['inference']
    ])
    inf_table = f'''| Inference Method | SE | p-value | Significant (5%)? |
|-----------------|-----|---------|-------------------|
{inf_rows}''' if inf_rows else '*No inference robustness tests recorded yet.*'

    # ── Build sensitivity summary ──
    sens = rd['robustness']['sensitivity']
    sens_rows = []
    if 'oster_delta' in sens:
        sens_rows.append(f'| Oster\'s δ | {sens["oster_delta"]:.2f} | > 1 | {"Robust" if abs(sens["oster_delta"]) > 1 else "Sensitive"} |')
    if 'rv' in sens:
        sens_rows.append(f'| Robustness Value (RV) | {sens["rv"]:.3f} | > max observed partial R² | — |')
    sens_table = f'''| Measure | Value | Threshold | Interpretation |
|---------|-------|-----------|---------------|
{chr(10).join(sens_rows)}''' if sens_rows else '*No sensitivity analysis recorded yet.*'

    # ── Build placebo table ──
    placebo_rows = '\n'.join([
        f'| {t["test"]} | {t["estimate"]:.4f} | {t["pvalue"]:.4f} | ≈ 0 | {status(t["pass"])} |'
        for t in rd['robustness']['placebos']
    ])
    placebo_table = f'''| Placebo Test | Estimate | p-value | Expected | Pass? |
|-------------|---------|---------|----------|-------|
{placebo_rows}''' if placebo_rows else '*No placebo tests recorded yet.*'

    # ── Build cross-method table ──
    cm_rows = '\n'.join([
        f'| {t["method"]} | {t["estimate"]:.4f} | {t["se"]:.4f} | [{t["estimate"]-1.96*t["se"]:.4f}, {t["estimate"]+1.96*t["se"]:.4f}] | {t["assumption"]} |'
        for t in rd['robustness']['cross_method']
    ])
    cm_table = f'''| Method | Estimate | SE | 95% CI | Key Assumption |
|--------|---------|-----|--------|---------------|
{cm_rows}''' if cm_rows else '*No cross-method comparison recorded yet.*'

    # ── Build robustness dashboard ──
    def layer_status(items, key='pass'):
        if not items:
            return '—', 'Not tested'
        passed = sum(1 for i in items if i.get(key, True))
        total = len(items)
        return (status(passed == total), f'{passed}/{total} passed')

    id_s, id_e = layer_status(rd['robustness']['identification'])
    spec_s = ('✓', f'{len(rd["robustness"]["specifications"])} specs tested') if rd['robustness']['specifications'] else ('—', 'Not tested')
    sample_s = ('✓', f'{len(rd["robustness"]["subsamples"])} subsamples') if rd['robustness']['subsamples'] else ('—', 'Not tested')
    inf_s, inf_e = layer_status(rd['robustness']['inference'], key='significant')
    placebo_s, placebo_e = layer_status(rd['robustness']['placebos'])

    # ── Build limitations ──
    limitations_text = '\n'.join([f'- {l}' for l in rd['limitations']]) if rd['limitations'] else '- No specific limitations identified from robustness checks.'

    # ── Assemble report ──
    report = f'''# {rd["title"]}

> **Method**: {rd["method"]} | **Estimand**: {rd["estimand"]} | **Date**: {rd["date"]}
> Generated via `/causal-inference` workflow

---

## Executive Summary

We estimate the causal effect of {rd["treatment"]} on {rd["outcome"]} using {rd["method"]}.
The main finding is an estimated effect of {me["estimate"]:.4f} (95% CI: [{me["ci_lower"]:.4f}, {me["ci_upper"]:.4f}]),
which is {"statistically significant" if me["pvalue"] < 0.05 else "not statistically significant"} at the 5% level (p = {me["pvalue"]:.4f}).

---

## 1. Research Design

### 1.1 Research Question
- **Causal question**: {rd["research_question"]}
- **Treatment**: {rd["treatment"]}
- **Outcome**: {rd["outcome"]}
- **Unit of analysis**: {rd["unit"]}
- **Estimand**: {rd["estimand"]}

### 1.2 Identification Strategy
- **Method**: {rd["method"]}
- **Core assumption**: {rd["core_assumption"]}
- **Why this method**: {rd["why_method"]}
- **Alternatives considered**: {rd["alternatives_considered"]}

---

## 2. Main Results

### 2.1 Primary Estimate

{main_table}

---

## 3. Robustness & Sensitivity

### 3.1 Identification Threats

{id_table}

### 3.2 Specification Sensitivity

{"![Specification curve](figures/specification_curve.png)" if any(f["section"] == "specification" for f in rd["figures"]) else "*Specification curve not generated.*"}

### 3.3 Inference Robustness

{inf_table}

### 3.4 Sensitivity to Unobservables

{sens_table}

{"![Sensitivity contour](figures/sensitivity_contour.png)" if any(f["section"] == "sensitivity" for f in rd["figures"]) else ""}

### 3.5 Placebo & Falsification Tests

{placebo_table}

{"![Placebo outcomes](figures/placebo_outcomes.png)" if any(f["section"] == "placebo" for f in rd["figures"]) else ""}

### 3.6 Cross-Method Comparison

{cm_table}

{"![Cross-method forest plot](figures/cross_method_forest.png)" if any(f["section"] == "cross_method" for f in rd["figures"]) else ""}

---

## 4. Robustness Dashboard

| Category | Status | Evidence |
|----------|--------|----------|
| Identification | {id_s} | {id_e} |
| Specification stability | {spec_s[0]} | {spec_s[1]} |
| Sample robustness | {sample_s[0]} | {sample_s[1]} |
| Inference | {inf_s} | {inf_e} |
| Unobservable sensitivity | {"✓" if sens.get("oster_delta", 0) and abs(sens["oster_delta"]) > 1 else "⚠" if sens else "—"} | {"δ = " + f'{sens["oster_delta"]:.2f}' if "oster_delta" in sens else "Not tested"} |
| Placebo tests | {placebo_s} | {placebo_e} |
| Cross-method | {"✓" if rd["robustness"]["cross_method"] else "—"} | {f'{len(rd["robustness"]["cross_method"])} methods compared' if rd["robustness"]["cross_method"] else "Not tested"} |

---

## 5. Limitations

{limitations_text}

---

## Appendix: Reproduction Code

'''

    # Add all code blocks
    for cb in rd['code_blocks']:
        report += f'''
{code_block(cb["label"], cb["code"])}
'''

    return report

# ── Write report to file ──
report_text = generate_report(report_data)
with open(os.path.join(report_dir, 'report.md'), 'w') as f:
    f.write(report_text)
print(f'Report written to {report_dir}/report.md')
```

### Helper: Add Results to Report Throughout the Workflow
```python
# ── Use these helpers during Phases 1-6 to accumulate data ──

def add_main_estimate(rd, estimate, se, pvalue, n):
    """Record the main result from Phase 5."""
    rd['main_estimate'] = {
        'estimate': estimate,
        'se': se,
        'ci_lower': estimate - 1.96 * se,
        'ci_upper': estimate + 1.96 * se,
        'pvalue': pvalue,
        'n': n,
    }

def add_identification_test(rd, test_name, result_str, passed, note):
    """Record an identification test from Phase 6 Layer 1."""
    rd['robustness']['identification'].append({
        'test': test_name, 'result': result_str, 'pass': passed, 'note': note
    })

def add_specification(rd, name, estimate, se, pvalue, n):
    """Record a specification from Phase 6 Layer 2."""
    rd['robustness']['specifications'].append({
        'name': name, 'estimate': estimate, 'se': se, 'pvalue': pvalue, 'n': n
    })

def add_inference_test(rd, method, se, pvalue):
    """Record an inference robustness test from Phase 6 Layer 4."""
    rd['robustness']['inference'].append({
        'method': method, 'se': se, 'pvalue': pvalue, 'significant': pvalue < 0.05
    })

def add_sensitivity(rd, **kwargs):
    """Record sensitivity measures from Phase 6 Layer 5."""
    rd['robustness']['sensitivity'].update(kwargs)

def add_placebo(rd, test_name, estimate, pvalue, threshold=0.05):
    """Record a placebo test from Phase 6 Layer 6."""
    rd['robustness']['placebos'].append({
        'test': test_name, 'estimate': estimate, 'pvalue': pvalue, 'pass': pvalue > threshold
    })

def add_cross_method(rd, method, estimate, se, assumption):
    """Record a cross-method comparison from Phase 6 Layer 7."""
    rd['robustness']['cross_method'].append({
        'method': method, 'estimate': estimate, 'se': se, 'assumption': assumption
    })

def add_figure(rd, fig, name, caption, section):
    """Save figure and record it in report data."""
    ref = save_figure(fig, name, caption)
    rd['figures'].append({'ref': ref, 'section': section})
    return ref

def add_code(rd, section, label, code):
    """Record a code block for the appendix."""
    rd['code_blocks'].append({'section': section, 'label': label, 'code': code})

def add_limitation(rd, text):
    """Record a limitation discovered during robustness checks."""
    rd['limitations'].append(text)

# ── Example usage throughout the workflow ──
# Phase 1:
# report_data['research_question'] = 'Does minimum wage increase reduce employment?'
# report_data['treatment'] = 'State-level minimum wage increase'
# ...
#
# Phase 5:
# add_main_estimate(report_data, estimate=model.coef()[0], se=model.se()[0],
#                   pvalue=model.pvalue()[0], n=model.nobs)
#
# Phase 6:
# add_identification_test(report_data, 'Parallel pre-trends (joint F)',
#                         'F=1.23, p=0.31', True, 'Pre-treatment coefficients jointly insignificant')
# add_sensitivity(report_data, oster_delta=2.34, rv=0.12)
# add_placebo(report_data, 'Placebo outcome: weather', 0.002, 0.89)
#
# Phase 7:
# report_text = generate_report(report_data)
```

---

## 15. E-value (Sensitivity to Unobserved Confounding)

```python
import numpy as np
from scipy.stats import norm

# ── E-value: how strong an unmeasured confounder would need to be ──
# VanderWeele & Ding (2017). Works on the RISK RATIO scale. The E-value is
# the minimum strength of association (on the RR scale) that an unobserved
# confounder U would need to have with BOTH the treatment and the outcome —
# above and beyond the measured covariates — to fully explain away the effect.

def evalue_rr(rr, lo=None, hi=None):
    """E-value for a risk ratio and (optionally) its confidence interval.

    Parameters
    ----------
    rr : float   point-estimate risk ratio (>0)
    lo, hi : float   lower/upper CI limits on the RR scale (optional)

    Returns
    -------
    dict with the point E-value and the E-value for the CI limit closest to 1.
    """
    def _e(x):
        # invert protective effects so we always work with RR >= 1
        x = 1.0 / x if x < 1 else x
        return x + np.sqrt(x * (x - 1.0))

    out = {'evalue_point': _e(rr)}

    # E-value for the CI: use the limit CLOSEST to the null (RR = 1).
    if lo is not None and hi is not None:
        if lo <= 1 <= hi:
            # CI crosses the null -> nothing to explain away
            out['evalue_ci'] = 1.0
        elif hi < 1:                      # protective effect, CI below 1
            out['evalue_ci'] = _e(hi)     # limit closest to 1 is the upper
        else:                             # harmful effect, CI above 1
            out['evalue_ci'] = _e(lo)     # limit closest to 1 is the lower
    return out


# ── Approximate conversions to the RR scale (VanderWeele & Ding) ──
def or_to_rr(or_ratio):
    """Approximate rare-outcome OR -> RR via the sqrt rule (RR ~ sqrt(OR))."""
    return np.sqrt(or_ratio)

def smd_to_rr(d):
    """Standardized mean difference (Cohen's d) -> approximate RR.

    VanderWeele (2017): RR ~ exp(0.91 * d). Use when the outcome is continuous
    and the effect is reported as a standardized mean difference.
    """
    return np.exp(0.91 * d)


# ── Example ──
rr, ci_lo, ci_hi = 1.65, 1.20, 2.27          # e.g. from a Cox / log-binomial model
res = evalue_rr(rr, ci_lo, ci_hi)
print(f'Risk ratio: {rr:.2f}  (95% CI {ci_lo:.2f}-{ci_hi:.2f})')
print(f'E-value (point estimate): {res["evalue_point"]:.2f}')
print(f'E-value (CI limit closest to null): {res["evalue_ci"]:.2f}')
print(f'Interpretation: an unobserved confounder would need to be associated with '
      f'both treatment and outcome by a risk ratio of RR_UD >= {res["evalue_point"]:.2f} '
      f'each (above measured covariates) to fully explain away the observed effect. '
      f'To move the CI to include the null, RR_UD >= {res["evalue_ci"]:.2f} suffices.')

# From an odds ratio or a standardized mean difference instead:
print(f'E-value from OR=1.8:  {evalue_rr(or_to_rr(1.8))["evalue_point"]:.2f}')
print(f'E-value from d=0.30:  {evalue_rr(smd_to_rr(0.30))["evalue_point"]:.2f}')
```

---

## 16. Nested Cross-Fitting for DML (Leak-Free Hyperparameter Tuning)

```python
import numpy as np
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.base import clone

# ── Nested cross-fitting for the partially-linear DML model ──
# Y = theta * T + g(X) + e ,   T = m(X) + v
#
# Orthogonality (Neyman) of the DML score requires that the nuisance
# predictions ĝ(X), m̂(X) for a given observation are made by a model that
# NEVER saw that observation. If we tune hyperparameters on the SAME data we
# then predict, the winning params are chosen partly by fitting noise in the
# hold-out fold -> tuning leakage -> the orthogonality that debiases theta
# breaks. The fix: tune in an INNER CV loop that lives entirely inside each
# OUTER training fold, refit on the full outer-train fold with the chosen
# params, and only THEN predict the held-out outer fold.

def dml_plr_nested(X, T, Y, base_learner, param_grid,
                   n_outer=5, n_inner=3, random_state=0):
    """Nested cross-fit DML for the partially-linear regression coefficient theta."""
    X, T, Y = np.asarray(X), np.asarray(T, float), np.asarray(Y, float)
    n = len(Y)
    Y_res = np.empty(n)   # Ỹ = Y - ĝ(X)   (out-of-fold residuals)
    T_res = np.empty(n)   # T̃ = T - m̂(X)

    outer = KFold(n_splits=n_outer, shuffle=True, random_state=random_state)
    for tr, te in outer.split(X):
        inner = KFold(n_splits=n_inner, shuffle=True, random_state=random_state)

        # --- tune g(X) = E[Y|X] on the OUTER-TRAIN fold only ---
        gs_y = GridSearchCV(clone(base_learner), param_grid,
                            cv=inner, scoring='neg_mean_squared_error')
        gs_y.fit(X[tr], Y[tr])
        g_model = clone(base_learner).set_params(**gs_y.best_params_)
        g_model.fit(X[tr], Y[tr])                 # refit on FULL outer-train fold

        # --- tune m(X) = E[T|X] on the OUTER-TRAIN fold only ---
        gs_t = GridSearchCV(clone(base_learner), param_grid,
                            cv=inner, scoring='neg_mean_squared_error')
        gs_t.fit(X[tr], T[tr])
        m_model = clone(base_learner).set_params(**gs_t.best_params_)
        m_model.fit(X[tr], T[tr])

        # --- predict the held-out OUTER fold (never seen in tuning or fitting) ---
        Y_res[te] = Y[te] - g_model.predict(X[te])
        T_res[te] = T[te] - m_model.predict(X[te])

    # ── Final stage: regress Ỹ on T̃ (no intercept) -> theta ──
    theta = float(T_res @ Y_res / (T_res @ T_res))

    # Heteroskedasticity-robust SE from the orthogonal score psi = T̃(Ỹ - theta T̃)
    psi = T_res * (Y_res - theta * T_res)
    jac = -(T_res @ T_res) / n
    se = float(np.sqrt(np.mean(psi ** 2) / jac ** 2 / n))
    return theta, se


# ── Example ──
rng = np.random.default_rng(0)
n, p = 2000, 10
X = rng.normal(size=(n, p))
T = X[:, 0] + 0.5 * X[:, 1] + rng.normal(size=n)
Y = 1.3 * T + X[:, 0] ** 2 + rng.normal(size=n)   # true theta = 1.3

param_grid = {'max_depth': [3, 5, None], 'min_samples_leaf': [1, 5, 20]}
theta, se = dml_plr_nested(
    X, T, Y,
    base_learner=RandomForestRegressor(n_estimators=300, random_state=0),
    param_grid=param_grid, n_outer=5, n_inner=3,
)
print(f'Nested cross-fit DML theta: {theta:.4f} (SE {se:.4f})')
print(f'95% CI: [{theta - 1.96*se:.4f}, {theta + 1.96*se:.4f}]  (true = 1.30)')
```

---

## 17. Empirical-Bayes Partial-Pooling Shrinkage (High-Cardinality Groups)

```python
import numpy as np
import pandas as pd

# ── Why: with thousands of sparse groups (users, zip codes, SKUs, ad
# creatives), a raw per-group mean is noisy and n_j = 0 groups have no
# estimate at all. Empirical Bayes shrinks each group toward the global
# prior by an amount that depends on how much data that group has: lots of
# data -> trust the group; little/none -> fall back to the prior (cold start).

# ═══════════════════════════════════════════
# (a) Gamma–Poisson closed form  (count / rate data)
# ═══════════════════════════════════════════
# c_j events over n_j exposure in group j. Rate lambda_j ~ Gamma(a, b) prior.
# Posterior is conjugate:  lambda_j | data ~ Gamma(a + c_j, b + n_j)
#   -> posterior mean  lambda_hat_j = (a + c_j) / (b + n_j)
# Estimate the prior (a, b) by method-of-moments on the observed group rates.

def gamma_poisson_eb(counts, exposure):
    counts, exposure = np.asarray(counts, float), np.asarray(exposure, float)
    rates = counts / np.where(exposure > 0, exposure, np.nan)
    m = np.nanmean(rates)                      # prior mean  = a / b
    v = np.nanvar(rates)                       # prior var   = a / b^2
    # Method of moments:  a/b = m,  a/b^2 = v  ->  b = m/v,  a = m^2/v
    b = m / v if v > 0 else 1.0
    a = m * b
    lam_hat = (a + counts) / (b + exposure)    # n_j = 0 -> a/b = prior mean
    return lam_hat, a, b

# ═══════════════════════════════════════════
# (b) Normal shrinkage weight  (continuous group means)
# ═══════════════════════════════════════════
# Group mean ybar_j with within-group noise var sigma2_data/n_j, group-level
# signal var sigma2_prior around global mu. Shrinkage weight:
#   W_j = n_j / (n_j + sigma2_data / sigma2_prior)
#   alpha_hat_j = W_j * ybar_j + (1 - W_j) * mu
# n_j = 0 -> W_j = 0 -> alpha_hat_j = mu  (pure prior; cold start).

def normal_eb(group_means, group_ns, sigma2_data, sigma2_prior, mu):
    ybar = np.asarray(group_means, float)
    n = np.asarray(group_ns, float)
    W = n / (n + sigma2_data / sigma2_prior)
    return W * ybar + (1 - W) * mu, W


# ── Example ──
rng = np.random.default_rng(1)
groups = np.arange(6)
counts = np.array([0, 2, 5, 40, 120, 0])
exposure = np.array([0, 10, 30, 100, 500, 25])
lam, a, b = gamma_poisson_eb(counts, exposure)
print('Gamma-Poisson EB rates (prior mean = a/b = {:.4f}):'.format(a / b))
for g, c, e, l in zip(groups, counts, exposure, lam):
    tag = '  <- cold start (n=0 -> prior)' if e == 0 else ''
    print(f'  group {g}: c={c:>3} n={e:>4}  lambda_hat={l:.4f}{tag}')

means = np.array([3.1, 5.0, 4.2, 4.6, 4.55, 0.0])
ns    = np.array([2,   3,   30,  200, 900,  0])
mu = 4.5
alpha, W = normal_eb(means, ns, sigma2_data=4.0, sigma2_prior=0.25, mu=mu)
print('\nNormal shrinkage (global mu = {:.2f}):'.format(mu))
for g, yb, n_, w, al in zip(groups, means, ns, W, alpha):
    print(f'  group {g}: ybar={yb:.2f} n={n_:>3}  W={w:.3f}  alpha_hat={al:.3f}')

# ═══════════════════════════════════════════
# Optional: Thompson Sampling loop (Beta–Bernoulli bandit)
# ═══════════════════════════════════════════
# Each arm has a Beta(alpha, beta) posterior over its success rate. On each
# round we SAMPLE one draw from every arm's posterior, pull the arm with the
# max draw, observe a reward, and update that arm — automatically balancing
# exploration (wide posteriors) against exploitation (high means).
def thompson_sampling(true_rates, n_rounds=5000, seed=0):
    rng = np.random.default_rng(seed)
    k = len(true_rates)
    alpha = np.ones(k); beta = np.ones(k)      # uniform priors
    pulls = np.zeros(k, int)
    for _ in range(n_rounds):
        draws = rng.beta(alpha, beta)          # one posterior sample per arm
        arm = int(np.argmax(draws))            # pick the max draw
        reward = rng.random() < true_rates[arm]
        alpha[arm] += reward; beta[arm] += 1 - reward
        pulls[arm] += 1
    return pulls, alpha / (alpha + beta)

pulls, post_means = thompson_sampling([0.03, 0.05, 0.08, 0.055])
print('\nThompson sampling pulls per arm:', pulls.tolist(),
      '| best arm =', int(np.argmax(post_means)))
```

---

## 18. Geo Experiment: iROAS (TBR/GeoLift) + Virtual DMAs

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm

# ═══════════════════════════════════════════
# (a) TBR / GeoLift-style iROAS
# ═══════════════════════════════════════════
# Fit a control -> treated relationship on the PRE-test period, project the
# treated counterfactual through the test window, and read off the incremental
# response. iROAS = incremental response / incremental spend.

def tbr_iroas(treated_pre, control_pre, treated_test, control_test,
              spend_delta_test):
    """Time-Based Regression incremental ROAS.

    treated_pre/control_pre : pretest series (aligned by period)
    treated_test/control_test : test-window series
    spend_delta_test : incremental media spend in the treated geo during test
    """
    # Pretest fit: treated ~ a + b * control  (control captures common shocks)
    Xpre = sm.add_constant(np.asarray(control_pre, float))
    fit = sm.OLS(np.asarray(treated_pre, float), Xpre).fit()

    # Counterfactual treated response in the test window (had there been no ad)
    Xtest = sm.add_constant(np.asarray(control_test, float), has_constant='add')
    counterfactual = fit.predict(Xtest)

    incremental = np.asarray(treated_test, float) - counterfactual
    iroas = incremental.sum() / np.asarray(spend_delta_test, float).sum()
    return iroas, incremental, counterfactual

# ── Example ──
rng = np.random.default_rng(2)
ctrl_pre = rng.normal(100, 10, 40)
trt_pre = 1.2 * ctrl_pre + rng.normal(0, 3, 40)          # treated tracks control
ctrl_test = rng.normal(100, 10, 14)
trt_test = 1.2 * ctrl_test + rng.normal(0, 3, 14) + 8.0  # +8/day true lift
spend = np.full(14, 5.0)
iroas, incr, cf = tbr_iroas(trt_pre, ctrl_pre, trt_test, ctrl_test, spend)
print(f'Total incremental response: {incr.sum():.1f}')
print(f'Total incremental spend:    {spend.sum():.1f}')
print(f'iROAS: {iroas:.3f}  (incremental response per $ of incremental spend)')

# ═══════════════════════════════════════════
# (b) Virtual DMAs via community detection + geo-A/A check
# ═══════════════════════════════════════════
# Real DMAs can be too small / correlated for clean geo tests. Build "virtual
# DMAs" by clustering geos that co-interact (spillover, shared media), then
# validate the design with a geo-A/A test: randomly split the clusters into
# sham arms and confirm the measured lift is ~0 (a nonzero A/A lift means the
# clustering leaked structure that will bias real experiments).
import networkx as nx

def build_virtual_dmas(edges):
    """edges: list of (geo_i, geo_j, weight) co-interaction tuples."""
    G = nx.Graph()
    for i, j, w in edges:
        G.add_edge(i, j, weight=w)
    try:                                                   # networkx >= 3.0
        comms = nx.community.louvain_communities(G, weight='weight', seed=0)
    except AttributeError:
        comms = nx.community.greedy_modularity_communities(G, weight='weight')
    modularity = nx.community.modularity(G, comms, weight='weight')
    geo2cluster = {g: c for c, comm in enumerate(comms) for g in comm}
    return comms, geo2cluster, modularity, G

def geo_aa_check(cluster_outcomes, geo2cluster, seed=0):
    """Assign clusters to two sham arms; measured A/A lift should be ~0."""
    rng = np.random.default_rng(seed)
    clusters = sorted(set(geo2cluster.values()))
    arm = {c: rng.integers(0, 2) for c in clusters}
    a = [v for g, v in cluster_outcomes.items() if arm[geo2cluster[g]] == 0]
    b = [v for g, v in cluster_outcomes.items() if arm[geo2cluster[g]] == 1]
    return np.mean(a) - np.mean(b)          # sham "lift"

# ── Example ──
edges = [('NYC', 'Newark', 5), ('NYC', 'Boston', 1), ('LA', 'SD', 4),
         ('LA', 'SF', 2), ('SF', 'SD', 1), ('Newark', 'Boston', 3)]
comms, geo2cluster, modularity, G = build_virtual_dmas(edges)
print(f'\nVirtual DMAs (n={len(comms)}): {[sorted(c) for c in comms]}')
print(f'Modularity: {modularity:.3f}  (higher = cleaner cluster separation)')

outcomes = {'NYC': 102, 'Newark': 99, 'Boston': 101, 'LA': 98, 'SD': 100, 'SF': 97}
aa_lift = geo_aa_check(outcomes, geo2cluster)
print(f'Geo-A/A sham lift: {aa_lift:.3f}  (should be ~0; large => design leaks)')
```

---

## 19. Uplift Evaluation (Qini / AUUC / Decile-Uplift)

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Requires RANDOMIZED data. The Qini/AUUC curves compare the outcomes of
# treated vs control units among those the MODEL ranks as most persuadable.
# Because targeting is by PREDICTED uplift but treatment was assigned at
# random, the treated/control contrast within any top-k slice is unbiased.
# On observational data these curves are confounded and meaningless.

def qini_curve(uplift_pred, treatment, outcome):
    """Cumulative Qini curve: incremental gains vs random targeting.

    Returns fraction-targeted grid and cumulative Qini values.
    """
    order = np.argsort(-np.asarray(uplift_pred))     # best-scored first
    t = np.asarray(treatment)[order]
    y = np.asarray(outcome, float)[order]

    n_t = np.cumsum(t)                               # treated seen so far
    n_c = np.cumsum(1 - t)                           # control seen so far
    y_t = np.cumsum(y * t)                           # treated responses
    y_c = np.cumsum(y * (1 - t))                     # control responses

    # Qini: treated responses minus control responses rescaled to treated count
    with np.errstate(divide='ignore', invalid='ignore'):
        qini = y_t - y_c * np.where(n_c > 0, n_t / n_c, 0.0)
    frac = np.arange(1, len(t) + 1) / len(t)
    return frac, qini

def qini_coefficient(frac, qini):
    """AUUC / Qini coefficient = area between the model curve and the random
    (straight-line) baseline, normalized to [-1, 1]-ish (higher is better)."""
    baseline = qini[-1] * frac                       # random targeting = diagonal
    area_model = np.trapz(qini, frac)
    area_base = np.trapz(baseline, frac)
    return area_model - area_base

def decile_uplift_table(uplift_pred, treatment, outcome, q=10):
    """Empirical ATE within each predicted-uplift decile.

    A well-calibrated model shows MONOTONICALLY DECLINING empirical uplift
    from the top decile (most persuadable) to the bottom.
    """
    df = pd.DataFrame({'pred': uplift_pred, 't': treatment, 'y': outcome})
    df['decile'] = pd.qcut(df['pred'].rank(method='first'), q,
                           labels=range(q, 0, -1))     # 10 = highest predicted
    rows = []
    for d, g in df.groupby('decile', observed=True):
        ate = g.loc[g.t == 1, 'y'].mean() - g.loc[g.t == 0, 'y'].mean()
        rows.append({'decile': int(d), 'n': len(g),
                     'pred_uplift': g['pred'].mean(), 'empirical_ate': ate})
    return pd.DataFrame(rows).sort_values('decile', ascending=False)


# ── Example ──
rng = np.random.default_rng(3)
n = 5000
X = rng.normal(size=n)
T = rng.integers(0, 2, n)                              # randomized assignment
true_uplift = 0.3 * (X > 0)                            # only X>0 units respond
Y = (rng.random(n) < 0.2 + true_uplift * T).astype(int)
pred = 0.3 * (X > 0) + rng.normal(0, 0.05, n)          # model's predicted uplift

frac, qini = qini_curve(pred, T, Y)
q_coef = qini_coefficient(frac, qini)
print(f'Qini coefficient (AUUC vs random): {q_coef:.2f}  (>0 = model beats random)')
print('\nDecile-uplift table (top decile should have the largest empirical ATE):')
print(decile_uplift_table(pred, T, Y).to_string(index=False))

plt.figure(figsize=(7, 5))
plt.plot(frac, qini, 'b-', label='Model (Qini)')
plt.plot(frac, qini[-1] * frac, 'k--', label='Random targeting')
plt.xlabel('Fraction of population targeted')
plt.ylabel('Cumulative incremental outcomes')
plt.title('Qini Curve')
plt.legend()
plt.show()
```

---

## 20. BSTS Contaminated-Control Diagnostic

```python
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# ── For CausalImpact / BSTS / synthetic-control style designs, every control
# series must be UNAFFECTED by the intervention — otherwise the counterfactual
# absorbs part of the treatment effect and the estimated impact is biased
# toward zero (a "contaminated" or "spillover" control). Screen each candidate
# control by regressing it on a post-intervention dummy (plus trend/season
# controls). A significant post coefficient flags a control that itself
# responds to the treatment -> drop it before fitting the model.

def screen_controls(data, control_cols, post_col='post',
                    trend_col='t', season_col=None, alpha=0.05):
    """Flag control series that respond to the intervention.

    data : DataFrame with a post-period dummy, a trend, optional season, and
           one column per candidate control series.
    Returns a table of coefficients / p-values and the list of flagged controls.
    """
    rows, flagged = [], []
    for c in control_cols:
        rhs = f'{post_col} + {trend_col}'
        if season_col is not None:
            rhs += f' + C({season_col})'
        m = smf.ols(f'Q("{c}") ~ {rhs}', data=data).fit(
            cov_type='HAC', cov_kwds={'maxlags': 4})     # autocorrelation-robust
        coef = m.params[post_col]
        pval = m.pvalues[post_col]
        is_flag = pval < alpha
        rows.append({'control': c, 'post_coef': coef, 'p_value': pval,
                     'contaminated': is_flag})
        if is_flag:
            flagged.append(c)
    return pd.DataFrame(rows), flagged


# ── Example ──
rng = np.random.default_rng(4)
T = 120
t = np.arange(T)
post = (t >= 80).astype(int)
season = t % 12
base = 50 + 0.1 * t + 3 * np.sin(2 * np.pi * season / 12)
data = pd.DataFrame({
    't': t, 'post': post, 'season': season,
    'clean_ctrl_1': base + rng.normal(0, 2, T),
    'clean_ctrl_2': base * 1.1 + rng.normal(0, 2, T),
    'dirty_ctrl':   base + 6.0 * post + rng.normal(0, 2, T),  # jumps post-intervention
})

table, flagged = screen_controls(
    data, ['clean_ctrl_1', 'clean_ctrl_2', 'dirty_ctrl'],
    post_col='post', trend_col='t', season_col='season')
print(table.to_string(index=False))
print(f'\nFlagged (contaminated) controls to DROP: {flagged}')
print('Keep only the un-flagged controls when fitting CausalImpact/BSTS.')
```

---

## Key Python Packages Summary

| Method | Primary Package | Alternative |
|--------|----------------|-------------|
| DiD (classic) | `statsmodels`, `pyfixest` | `linearmodels` |
| DiD (staggered) | `csdid`, `pyfixest` (sunab) | — |
| RDD | `rdrobust` | — |
| IV | `linearmodels`, `pyfixest` | `statsmodels` (manual 2SLS) |
| Synthetic Control | `SparseSC`, scipy (manual) | — |
| Matching | `causalinference`, sklearn | `pymatch` |
| IPW/AIPW | `econml`, sklearn | `zepid`, `causalml` |
| DML | `doubleml` | `econml` |
| Causal Forest | `econml` | `causalml` |
| Meta-Learners | `econml` | `causalml` |
| Sensitivity | `statsmodels` (manual) | — |
| Mediation | `statsmodels` (manual) | `pingouin` |
| CausalImpact | `causalimpact` | `tfcausalimpact` |
| ITS | `statsmodels` | — |
| BLP Demand | `pyblp` | manual GMM via scipy |
| Discrete Choice | `xlogit`, `biogeme` | scipy (manual MLE) |
| Dynamic Structural | scipy, `numba` | `JAX` |
| Structural (general) | `scipy.optimize`, `JAX` | `Pyomo`, `casadi` (MPEC) |
| Specification Curve | `pyfixest`, `matplotlib` | — |
| Wild Bootstrap | `wildboottest` | — |
| Multiple Testing | `statsmodels.stats.multitest` | — |
| Randomization Inference | `numpy` (manual) | `randomizr` |
| E-value sensitivity | `numpy`, `scipy` (manual) | `EValue` (R) |
| Nested cross-fit DML | `sklearn`, `numpy` (manual) | `doubleml`, `econml` |
| Empirical-Bayes shrinkage | `numpy`, `pandas` (manual) | `PyMC`, `NumPyro` |
| Geo experiment / iROAS | `statsmodels`, `networkx` | `GeoLift` (R), `tbrsim` |
| Uplift (Qini / AUUC) | `numpy`, `pandas` (manual) | `scikit-uplift`, `causalml` |
| Contaminated-control screen | `statsmodels` (manual) | — |
