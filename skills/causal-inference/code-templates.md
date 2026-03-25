# Code Templates for Causal Inference Methods

This file provides starter code templates in R, Python, and Stata for the most commonly used causal inference methods. These are meant as starting points — adapt to the user's specific data and research design.

---

## 1. Difference-in-Differences

### R (Classic 2x2 DiD)
```r
library(fixest)

# Classic 2x2 DiD
did_model <- feols(outcome ~ treat * post | unit + time, data = df,
                   cluster = ~unit)
summary(did_model)

# Event study (dynamic effects)
event_model <- feols(outcome ~ i(rel_time, treat, ref = -1) | unit + time,
                     data = df, cluster = ~unit)
iplot(event_model, main = "Event Study")
```

### R (Staggered DiD — Callaway & Sant'Anna)
```r
library(did)

# Group-time ATTs
cs_att <- att_gt(
  yname = "outcome",
  tname = "year",
  idname = "unit_id",
  gname = "first_treat_year",  # 0 for never-treated
  data = df,
  control_group = "nevertreated",  # or "notyettreated"
  est_method = "dr"  # doubly robust
)
summary(cs_att)

# Aggregate: simple average
agg_simple <- aggte(cs_att, type = "simple")
summary(agg_simple)

# Aggregate: dynamic effects (event study)
agg_dynamic <- aggte(cs_att, type = "dynamic")
ggdid(agg_dynamic)
```

### R (Staggered DiD — Sun & Abraham)
```r
library(fixest)

# Interaction-weighted estimator
sa_model <- feols(outcome ~ sunab(first_treat_year, year) | unit + year,
                  data = df, cluster = ~unit)
summary(sa_model)
iplot(sa_model)
```

### Python (Classic DiD)
```python
import statsmodels.formula.api as smf

model = smf.ols('outcome ~ treat * post + C(unit) + C(time)', data=df).fit(
    cov_type='cluster', cov_kwds={'groups': df['unit']}
)
print(model.summary())
```

### Stata (Classic DiD)
```stata
* Classic DiD with TWFE
reghdfe outcome treat##post, absorb(unit time) cluster(unit)

* Event study
reghdfe outcome ib(-1).rel_time##treat, absorb(unit time) cluster(unit)
event_plot, default_look
```

### Stata (Staggered DiD)
```stata
* Callaway & Sant'Anna
csdid outcome, ivar(unit_id) time(year) gvar(first_treat_year) method(dripw)
csdid_plot

* de Chaisemartin & D'Haultfoeuille
did_multiplegt outcome unit time treat, robust_dynamic dynamic(5) placebo(5)
```

---

## 2. Regression Discontinuity Design

### R
```r
library(rdrobust)
library(rddensity)

# Main RD estimate (sharp)
rd_est <- rdrobust(y = df$outcome, x = df$running_var, c = 0)
summary(rd_est)

# RD plot
rdplot(y = df$outcome, x = df$running_var, c = 0,
       title = "RD Plot", x.label = "Running Variable", y.label = "Outcome")

# Manipulation test
density_test <- rddensity(X = df$running_var, c = 0)
summary(density_test)
rdplotdensity(density_test, df$running_var)

# Covariate balance at cutoff
for (var in c("covar1", "covar2", "covar3")) {
  cat("\n---", var, "---\n")
  print(summary(rdrobust(y = df[[var]], x = df$running_var, c = 0)))
}

# Bandwidth sensitivity
for (bw_mult in c(0.5, 0.75, 1, 1.25, 1.5, 2)) {
  est <- rdrobust(y = df$outcome, x = df$running_var, c = 0,
                  h = rd_est$bws[1, 1] * bw_mult)
  cat(sprintf("BW multiplier: %.2f, Estimate: %.3f (%.3f)\n",
              bw_mult, est$coef[1], est$se[3]))
}
```

### Python
```python
from rdrobust import rdrobust, rdplot
from rddensity import rddensity

# Main estimate
rd = rdrobust(Y=df['outcome'], X=df['running_var'], c=0)
print(rd)

# Plot
rdplot(y=df['outcome'], x=df['running_var'], c=0)

# Manipulation test
density = rddensity(X=df['running_var'], c=0)
print(density)
```

### Stata
```stata
* Main estimate
rdrobust outcome running_var, c(0)

* Plot
rdplot outcome running_var, c(0)

* Manipulation test
rddensity running_var, c(0)

* Bandwidth sensitivity
rdrobust outcome running_var, c(0) h(5)
rdrobust outcome running_var, c(0) h(10)
rdrobust outcome running_var, c(0) h(15)
```

---

## 3. Instrumental Variables

### R
```r
library(fixest)
library(ivreg)

# 2SLS with fixest
iv_model <- feols(outcome ~ controls | unit + year | treatment ~ instrument,
                  data = df, cluster = ~unit)
summary(iv_model)

# Check first-stage F
fitstat(iv_model, type = "ivf")

# Reduced form
rf_model <- feols(outcome ~ instrument + controls | unit + year,
                  data = df, cluster = ~unit)
summary(rf_model)

# First stage
fs_model <- feols(treatment ~ instrument + controls | unit + year,
                  data = df, cluster = ~unit)
summary(fs_model)
```

### Python
```python
from linearmodels.iv import IV2SLS

# 2SLS
iv = IV2SLS(
    dependent=df['outcome'],
    exog=df[['const', 'controls']],
    endog=df['treatment'],
    instruments=df['instrument']
).fit(cov_type='clustered', clusters=df['unit'])
print(iv.summary)
print(f"First-stage F: {iv.first_stage.diagnostics['f.stat']:.2f}")
```

### Stata
```stata
* 2SLS
ivregress 2sls outcome controls (treatment = instrument), first robust
estat firststage
estat endogenous

* With fixed effects
ivreghdfe outcome controls (treatment = instrument), absorb(unit year) cluster(unit)

* Weak instrument robust
rivtest  /* Anderson-Rubin test */
```

---

## 4. Synthetic Control

### R
```r
library(Synth)
library(augsynth)

# Classic Synthetic Control
synth_data <- dataprep(
  foo = df,
  predictors = c("predictor1", "predictor2"),
  predictors.op = "mean",
  dependent = "outcome",
  unit.variable = "unit_id",
  time.variable = "year",
  treatment.identifier = treated_unit,
  controls.identifier = donor_units,
  time.predictors.prior = pre_years,
  time.optimize.ssr = pre_years,
  time.plot = all_years
)
synth_out <- synth(synth_data)
path.plot(synth_out, synth_data)
gaps.plot(synth_out, synth_data)

# Augmented SCM (easier interface)
ascm <- augsynth(outcome ~ treat, unit = unit_id, time = year, data = df,
                 progfunc = "ridge", scm = TRUE)
summary(ascm)
plot(ascm)
```

### R (Synthetic DiD)
```r
library(synthdid)

# Prepare data as matrix
setup <- panel.matrices(df, unit = "unit_id", time = "year",
                        outcome = "outcome", treatment = "treat")

# SDID estimate
sdid <- synthdid_estimate(setup$Y, setup$N0, setup$T0)
print(sdid)
plot(sdid)

# Comparison: SC and DiD
sc <- sc_estimate(setup$Y, setup$N0, setup$T0)
did <- did_estimate(setup$Y, setup$N0, setup$T0)
```

### Stata
```stata
* Synthetic Control
synth outcome predictor1 predictor2 outcome(pre_years), ///
  trunit(treated_id) trperiod(treat_year) figure
```

---

## 5. Propensity Score / Matching Methods

### R (Matching)
```r
library(MatchIt)
library(cobalt)

# Propensity score matching (nearest neighbor)
m_out <- matchit(treat ~ x1 + x2 + x3, data = df,
                 method = "nearest", distance = "logit", caliper = 0.2)

# Check balance
summary(m_out)
love.plot(m_out, thresholds = 0.1)
bal.plot(m_out, var.name = "x1")

# Estimate treatment effect on matched data
m_data <- match.data(m_out)
model <- lm(outcome ~ treat, data = m_data, weights = weights)
# Use cluster-robust SEs by subclass
library(lmtest)
library(sandwich)
coeftest(model, vcov = vcovCL(model, cluster = m_data$subclass))
```

### R (IPW / AIPW)
```r
library(WeightIt)
library(cobalt)

# Inverse probability weights
w_out <- weightit(treat ~ x1 + x2 + x3, data = df,
                  method = "ps", estimand = "ATT")
summary(w_out)
bal.tab(w_out, thresholds = 0.1)

# Entropy balancing
w_ebal <- weightit(treat ~ x1 + x2 + x3, data = df,
                   method = "ebal", estimand = "ATT")
bal.tab(w_ebal)

# AIPW using the weights
library(lmtest)
library(sandwich)
model <- lm(outcome ~ treat, data = df, weights = w_out$weights)
coeftest(model, vcov = vcovHC(model, type = "HC2"))
```

### R (Doubly Robust with AIPW package)
```r
library(AIPW)

aipw_est <- AIPW$new(
  Y = df$outcome,
  A = df$treat,
  W = df[, c("x1", "x2", "x3")],
  Q.SL.library = c("SL.glm", "SL.ranger"),
  g.SL.library = c("SL.glm", "SL.ranger"),
  k_split = 5,
  verbose = FALSE
)
aipw_est$stratified_fit()$summary()
```

### Python
```python
from sklearn.linear_model import LogisticRegression
from causalinference import CausalModel

# Using causalinference package
cm = CausalModel(Y=df['outcome'].values, D=df['treat'].values,
                 X=df[['x1', 'x2', 'x3']].values)
cm.est_via_matching()
print(cm.estimates)

cm.est_via_ols()
print(cm.estimates)

cm.est_propensity_s()
cm.est_via_weighting()
print(cm.estimates)
```

### Stata
```stata
* Propensity score matching
teffects psmatch (outcome) (treat x1 x2 x3), atet nn(1)
tebalance summarize

* IPW
teffects ipw (outcome) (treat x1 x2 x3), atet
tebalance summarize

* AIPW (doubly robust)
teffects aipw (outcome x1 x2 x3) (treat x1 x2 x3), atet

* Entropy balancing
ebalance treat x1 x2 x3
```

---

## 6. Double/Debiased Machine Learning

### R
```r
library(DoubleML)
library(mlr3)
library(mlr3learners)

# Setup
dml_data <- DoubleMLData$new(df, y_col = "outcome", d_cols = "treat",
                              x_cols = c("x1", "x2", "x3"))

# Choose ML methods
ml_l <- lrn("regr.ranger", num.trees = 500)  # outcome model
ml_m <- lrn("classif.ranger", num.trees = 500)  # treatment model

# Partially Linear Model
dml_plr <- DoubleMLPLR$new(dml_data, ml_l = ml_l, ml_m = ml_m, n_folds = 5)
dml_plr$fit()
print(dml_plr)
dml_plr$summary()
```

### Python
```python
from doubleml import DoubleMLPLR, DoubleMLData
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

# Setup
dml_data = DoubleMLData(df, y_col='outcome', d_cols='treat',
                         x_cols=['x1', 'x2', 'x3'])

# ML methods
ml_l = RandomForestRegressor(n_estimators=500)
ml_m = RandomForestClassifier(n_estimators=500)

# Fit
dml = DoubleMLPLR(dml_data, ml_l=ml_l, ml_m=ml_m, n_folds=5)
dml.fit()
print(dml.summary)
```

---

## 7. Causal Forest / Heterogeneous Treatment Effects

### R
```r
library(grf)

# Prepare data
X <- as.matrix(df[, c("x1", "x2", "x3")])
Y <- df$outcome
W <- df$treat

# Estimate causal forest
cf <- causal_forest(X, Y, W, num.trees = 2000)

# Average treatment effect
ate <- average_treatment_effect(cf, target.sample = "all")
cat(sprintf("ATE: %.3f (%.3f)\n", ate[1], ate[2]))

# ATT
att <- average_treatment_effect(cf, target.sample = "treated")
cat(sprintf("ATT: %.3f (%.3f)\n", att[1], att[2]))

# Heterogeneous effects
cate <- predict(cf, estimate.variance = TRUE)
df$cate <- cate$predictions
df$cate_se <- sqrt(cate$variance.estimates)

# Calibration test
test_calibration(cf)

# Variable importance
varimp <- variable_importance(cf)
names(varimp) <- c("x1", "x2", "x3")
sort(varimp, decreasing = TRUE)

# Best linear projection
blp <- best_linear_projection(cf, X)
print(blp)
```

### Python
```python
from econml.dml import CausalForestDML
import numpy as np

# Fit
cf = CausalForestDML(
    model_y='auto', model_t='auto',
    n_estimators=2000, random_state=42
)
cf.fit(Y=df['outcome'], T=df['treat'], X=df[['x1', 'x2', 'x3']])

# ATE
ate = cf.ate(X=df[['x1', 'x2', 'x3']])
ate_inf = cf.ate_inference(X=df[['x1', 'x2', 'x3']])
print(f"ATE: {ate_inf.mean_point:.3f} ({ate_inf.stderr_mean:.3f})")

# CATE
cate = cf.effect(X=df[['x1', 'x2', 'x3']])
```

---

## 8. Sensitivity Analysis

### R (Oster's Delta)
```r
# Manual computation
# Short regression (no controls)
short <- lm(outcome ~ treat, data = df)
# Long regression (with controls)
long <- lm(outcome ~ treat + x1 + x2 + x3, data = df)

# Oster's delta (simplified)
beta_short <- coef(short)["treat"]
beta_long <- coef(long)["treat"]
r2_short <- summary(short)$r.squared
r2_long <- summary(long)$r.squared
r2_max <- min(1, 1.3 * r2_long)  # Oster's suggestion

delta <- (beta_long * (r2_max - r2_long)) / ((beta_short - beta_long) * (r2_long - r2_short))
cat(sprintf("Oster's delta: %.2f\n", delta))
# delta > 1 suggests robustness to unobservables
```

### R (Cinelli & Hazlett Sensitivity)
```r
library(sensemakr)

model <- lm(outcome ~ treat + x1 + x2 + x3, data = df)

# Sensitivity analysis
sens <- sensemakr(model, treatment = "treat",
                  benchmark_covariates = c("x1", "x2"),
                  kd = 1:3)
summary(sens)
plot(sens)
ovb_contour_plot(sens)
```

### Stata (Oster)
```stata
* Using psacalc
psacalc delta treat, rmax(1.3) mcontrol(x1 x2 x3)
```

---

## 9. Mediation Analysis

### R
```r
library(mediation)

# Mediator model
med_model <- lm(mediator ~ treat + x1 + x2, data = df)

# Outcome model
out_model <- lm(outcome ~ treat + mediator + x1 + x2, data = df)

# Causal mediation
med_out <- mediate(med_model, out_model, treat = "treat",
                   mediator = "mediator", boot = TRUE, sims = 1000)
summary(med_out)
plot(med_out)

# Sensitivity analysis
sens <- medsens(med_out)
summary(sens)
plot(sens)
```

---

## 10. CausalImpact (Bayesian Structural Time Series)

### R
```r
library(CausalImpact)

# Data: time series matrix (columns: outcome, control_series_1, control_series_2, ...)
data <- zoo(cbind(y, x1, x2), dates)

pre_period <- c(start_date, intervention_date - 1)
post_period <- c(intervention_date, end_date)

impact <- CausalImpact(data, pre.period = pre_period, post.period = post_period)
summary(impact)
summary(impact, "report")  # narrative summary
plot(impact)
```

### Python
```python
from causalimpact import CausalImpact

pre_period = ['2020-01-01', '2020-06-30']
post_period = ['2020-07-01', '2020-12-31']

ci = CausalImpact(data, pre_period, post_period)
print(ci.summary())
print(ci.summary(output='report'))
ci.plot()
```

---

## 11. Interrupted Time Series

### R
```r
library(nlme)

# Create time variables
df$time <- 1:nrow(df)
df$intervention <- as.numeric(df$time >= intervention_point)
df$time_after <- ifelse(df$intervention == 1, df$time - intervention_point, 0)

# Segmented regression with autocorrelation
its_model <- gls(outcome ~ time + intervention + time_after,
                 data = df,
                 correlation = corARMA(p = 1, form = ~time),
                 method = "ML")
summary(its_model)
# intervention coefficient = level change
# time_after coefficient = slope change
```

### Stata
```stata
itsa outcome, single trperiod(intervention_time) lag(1)
actest, lags(12)  /* test for autocorrelation */
```

---

## Key Packages Summary

| Method | R | Python | Stata |
|--------|---|--------|-------|
| DiD (classic) | `fixest` | `statsmodels`, `linearmodels` | `reghdfe` |
| DiD (staggered) | `did`, `fixest` (sunab) | `csdid` | `csdid`, `did_multiplegt` |
| RDD | `rdrobust`, `rddensity` | `rdrobust` | `rdrobust` |
| IV | `fixest`, `ivreg` | `linearmodels` | `ivregress`, `ivreghdfe` |
| Synthetic Control | `Synth`, `augsynth`, `synthdid` | `SparseSC` | `synth` |
| Matching | `MatchIt`, `cobalt` | `causalinference` | `teffects` |
| IPW/AIPW | `WeightIt`, `AIPW` | `zepid`, `causalml` | `teffects` |
| DML | `DoubleML` | `doubleml`, `econml` | `ddml` |
| Causal Forest | `grf` | `econml` | — |
| Sensitivity | `sensemakr` | — | `psacalc` |
| Mediation | `mediation` | — | `medeff` |
| CausalImpact | `CausalImpact` | `causalimpact` | — |
| ITS | `nlme`, `its.analysis` | `statsmodels` | `itsa` |
