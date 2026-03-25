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
