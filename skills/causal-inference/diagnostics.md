# Diagnostics and Assumption Testing Checklists

This document provides method-specific diagnostic checklists. For each method, it lists the assumptions, how to test them, and what to do if they fail.

---

## 1. Randomized Controlled Trial (RCT)

### Pre-Analysis
- [ ] **Balance test**: Compare covariate means across treatment arms. Use F-test for joint significance. Small imbalances are expected — focus on economically meaningful differences.
- [ ] **Compliance rates**: Report treatment take-up rates by arm.
- [ ] **Pre-registration**: Was a pre-analysis plan filed? Follow it.

### Post-Analysis
- [ ] **Ramp-up assignment-weight check** (online experiments): Did the treatment:control ratio change over the run (e.g., 90/10 → 50/50 full-traffic ramp)? If yes AND a time-based confounder is plausible (arrival-time ↔ user type), the pooled ATE is biased — epoch-condition (reweight within constant-weight epochs by total traffic). Changing only the total enrolled fraction at a constant 50/50 split is fine.
- [ ] **Attrition check**: Test whether attrition rates differ by treatment. Test whether attrition is predicted by treatment x baseline covariates interaction.
- [ ] **ITT vs. LATE**: If non-compliance, report ITT (reduced form) as primary and LATE (IV) as secondary.
- [ ] **Lee bounds**: If differential attrition, compute bounds on the treatment effect.
- [ ] **Spillover check**: If possible, test whether control outcomes are affected by proximity to treated units.
- [ ] **Multiple testing correction**: If testing multiple outcomes, apply Bonferroni, BH, or Romano-Wolf correction.

---

## 2. Difference-in-Differences (DiD)

### Pre-Treatment Diagnostics
- [ ] **Visual parallel trends**: Plot raw outcome means by group over time. Do they track together pre-treatment?
- [ ] **Event study / leads-and-lags**: Estimate dynamic effects. Are pre-treatment coefficients jointly and individually insignificant?
- [ ] **Roth (2022) pre-test power**: Even if pre-treatment coefficients are insignificant, is the test powered to detect meaningful violations?
- [ ] **Honest confidence intervals**: Roth & Sant'Anna — construct CIs robust to pre-trend violations.

### Specification Diagnostics
- [ ] **Parallel trends in levels vs. logs**: Test both; consider which is more appropriate.
- [ ] **Placebo outcomes**: Apply DiD to outcomes that should NOT be affected by treatment. A significant "effect" suggests confounding.
- [ ] **Placebo treatment timing**: Pretend treatment happened earlier. A significant "effect" suggests pre-existing trends.
- [ ] **Varying control groups**: Show robustness to different comparison groups.
- [ ] **Goodman-Bacon decomposition**: (For staggered DiD) Decompose TWFE estimate into 2x2 components. Check for problematic comparisons.

### Staggered DiD Specific
- [ ] **Negative weights**: Check whether TWFE assigns negative weights to any group-time treatment effects.
- [ ] **Multiple robust estimators**: Report at least two of: Callaway-Sant'Anna, Sun-Abraham, Borusyak-Jaravel-Spiess, Gardner, de Chaisemartin-D'Haultfoeuille.
- [ ] **Heterogeneity by cohort**: Test whether treatment effects differ across adoption cohorts.

---

## 3. Regression Discontinuity Design (RDD)

### Validity Tests
- [ ] **Manipulation test**: McCrary (2008) density test or Cattaneo, Jansson & Ma (2020) `rddensity`. Test for bunching at cutoff.
- [ ] **Covariate smoothness**: Test that pre-determined covariates (age, gender, pre-treatment outcomes) are continuous at the cutoff. Run RD with each covariate as the outcome.
- [ ] **Donut hole**: Exclude observations very close to the cutoff and re-estimate. If results change dramatically, manipulation may be an issue.

### Robustness
- [ ] **Bandwidth sensitivity**: Show estimates across a range of bandwidths (0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x the optimal).
- [ ] **Polynomial order**: Show local linear (preferred) vs. local quadratic.
- [ ] **Kernel choice**: Triangular (default) vs. uniform vs. Epanechnikov. Results should be similar.
- [ ] **Placebo cutoffs**: Test for discontinuities at values away from the true cutoff. Should find nothing.
- [ ] **Bias-corrected CIs**: Use Calonico, Cattaneo & Titiunik (2014) `rdrobust` for proper inference.

### Fuzzy RD Specific
- [ ] **First stage**: Show discontinuity in treatment probability at cutoff. Must be meaningful.
- [ ] **Visual**: Plot treatment probability by running variable with the discontinuity.

---

## 4. Instrumental Variables (IV)

### First Stage
- [ ] **F-statistic**: Report effective F-statistic. Rule of thumb: F > 10 (Stock & Yogo); better: use Olea & Pflueger (2013) critical values.
- [ ] **Visual first stage**: Plot treatment against instrument (residualized if needed).

### Exclusion Restriction (Not Directly Testable)
- [ ] **Narrative argument**: Write out why the instrument affects the outcome only through treatment. Consider all possible channels.
- [ ] **Placebo outcomes**: Show instrument does not predict outcomes that should not be affected by treatment.
- [ ] **Pre-treatment outcomes**: Show instrument does not predict outcomes measured before treatment could have had an effect.
- [ ] **Reduced form**: Always report the reduced form (instrument → outcome). This is interpretable even if exclusion fails.

### Over-Identification (Multiple Instruments)
- [ ] **Hansen J test**: Test whether all instruments give consistent estimates. Rejection suggests at least one instrument is invalid. (But J-test has low power.)
- [ ] **Report each instrument separately**: Show first stage and IV estimate for each instrument individually.

### Weak Instruments
- [ ] If F < 10 or effective F is low, use: LIML estimator, Anderson-Rubin confidence set (robust to weak instruments), or tF procedure (Lee, McCrary, Moreira & Porter).
- [ ] **Sensitivity to instrument strength**: Report how estimates change if instrument is assumed to be weaker.

### Monotonicity (for LATE)
- [ ] **Test where possible**: In examiner/judge designs, Frandsen, Lefgren & Leslie (2023) provide a direct test.
- [ ] **Discuss**: What population does LATE apply to? Are compliers relevant for the policy question?

---

## 5. Synthetic Control Method (SCM)

### Pre-Treatment Fit
- [ ] **Visual comparison**: Plot treated unit vs. synthetic control over the full pre-treatment period.
- [ ] **RMSPE**: Report pre-treatment root mean squared prediction error. Should be small relative to the outcome's scale.
- [ ] **Weights**: Report donor weights. Very sparse weights (one or two donors dominating) may be fragile.
- [ ] **Contaminated-control / endogeneity check** (also DiD, CausalImpact/BSTS): Donor/control series must be unaffected by the treatment. Test: a valid control shows no discontinuity at the intervention date (regress each control on a treatment-period dummy; flag significant breaks). Bias if violated: control depressed (cannibalization) → overestimate the effect; control lifted (halo/spillover) → underestimate. For digital ecosystems prefer structurally isolated controls (other-platform, economically orthogonal categories, upstream pre-treatment metrics).

### Inference
- [ ] **Placebo / permutation test**: Run SCM for every donor unit. Plot the distribution of placebo effects. Where does the treated unit rank?
- [ ] **Post/pre RMSPE ratio**: The treated unit's ratio should be an outlier.
- [ ] **P-value**: Fraction of placebos with effects as large as the treated unit.

### Robustness
- [ ] **Leave-one-out donor**: Re-estimate dropping each major donor. Results should be stable.
- [ ] **Alternate predictor sets**: Show results with different sets of matching variables.
- [ ] **In-time placebo**: Apply SCM using a pre-treatment period as the "intervention time." Effect should be near zero.
- [ ] **In-time placebo / false-positive-rate check** (BSTS/CausalImpact & SCM): Slide a dummy intervention date across the pre-treatment period and re-estimate; a sound model returns effect ≈0 with credible/confidence intervals covering zero. Persistent nonzero "effects" on null dates ⇒ overfitting/misspecification — don't trust the real estimate.
- [ ] **Backdating**: Shift treatment date earlier. Effect should appear only at actual treatment time.

---

## 6. Selection-on-Observables / Matching

### Overlap and Balance
- [ ] **Common support**: Plot propensity score distributions for treated and control. Sufficient overlap?
- [ ] **Trim extreme propensity scores**: Drop observations with e(X) < 0.05 or > 0.95.
- [ ] **Balance tables**: Compare covariate means before and after matching/weighting. Report standardized mean differences (should be < 0.1).
- [ ] **Variance ratios**: After matching, variance ratios of covariates should be close to 1.

### Propensity Score Model
- [ ] **Specification**: Try logit/probit; consider including interactions and polynomials.
- [ ] **Overfitting**: If ML is used for propensity scores, use cross-validation.
- [ ] **Prognostic score**: Consider also matching on predicted outcomes (Hansen 2008).

### Sensitivity Analysis (CRITICAL for this method class)
- [ ] **Oster's delta**: How much selection on unobservables would explain away the result? Delta > 1 is reassuring.
- [ ] **Rosenbaum bounds**: For matched samples — how much hidden bias before significance is lost?
- [ ] **Cinelli & Hazlett (2020)**: Sensitivity contour plots; robustness values.
- [ ] **E-value**: Minimum confounding strength to reduce effect to null.
- [ ] **Compare methods**: If OLS, matching, IPW, AIPW, entropy balancing all give similar results, this is reassuring.

---

## 7. Machine Learning Causal Methods

### Double/Debiased ML (DML)
- [ ] **DAG feature-selection check**: Confirm the adjustment set contains confounders only. Exclude mediators (variables on the T→M→Y path — controlling them blocks the effect → biased toward zero) and exclude colliders (caused by both T and Y — conditioning induces Berkson's-paradox spurious correlation). Draw the DAG before choosing features.
- [ ] **Cross-fitting**: Use K >= 2 folds (5 is common). Report sensitivity to K.
- [ ] **Nested cross-fitting check**: Hyperparameter tuning of ML nuisances must occur in an inner CV loop within each training fold, never on the fold used to compute the causal residuals — otherwise tuning leakage violates orthogonality and invalidates the CIs.
- [ ] **ML model performance**: Report out-of-sample R-squared for nuisance models.
- [ ] **Sensitivity to ML method**: Try different ML algorithms (lasso, random forest, boosting). Results should be stable.
- [ ] **Compare to parametric**: Report OLS/logit alongside DML. Large differences suggest nonlinearity matters.

### Causal Forest
- [ ] **Calibration test**: `test_calibration()` in `grf`. Tests whether treatment effects are well-calibrated.
- [ ] **Variable importance**: Report which covariates drive heterogeneity.
- [ ] **CLAN analysis**: Characterize the most- and least-affected groups.
- [ ] **Best linear projection**: Summarize heterogeneity via linear model of CATE on key covariates.
- [ ] **Overlap assumption**: Like all observational methods, requires overlap.
- [ ] **Uplift-model validation check**: Uplift/CATE targeting models can only be validated offline on randomized data (decile-uplift monotonicity, Qini/AUUC above the random baseline). Confounded/observational test data makes these diagnostics meaningless.

---

## 8. Panel Data / Fixed Effects

### Strict Exogeneity
- [ ] **Lead test**: Include future treatment in the model. Significant coefficient suggests feedback effects (violation of strict exogeneity).
- [ ] **Granger causality test**: Test whether past outcomes predict current treatment.

### Specification
- [ ] **Hausman test**: Compare FE and RE. If they differ significantly, RE is inconsistent — use FE.
- [ ] **Unit root / stationarity**: For long panels, test for unit roots. Non-stationary data requires differencing or cointegration.
- [ ] **Cluster standard errors**: Cluster at the unit level (or higher) to account for serial correlation (Bertrand, Duflo & Mullainathan 2004).

---

## 9. Event Study

### Pre-Treatment Coefficients
- [ ] **Joint F-test**: Test that all pre-treatment coefficients are jointly zero.
- [ ] **Individual significance**: Are any individual pre-treatment coefficients significant?
- [ ] **Pre-trend pattern**: Is there a discernible trend in pre-treatment coefficients? (Even if individually insignificant, a trending pattern is concerning.)

### Interpretation Pitfalls
- [ ] **Reference period**: Which period is normalized to zero? Choice matters.
- [ ] **Endpoint effects**: Long-run effects may reflect compositional changes or mean reversion.
- [ ] **Staggered bias**: If using TWFE with staggered treatment, pre-treatment coefficients can be biased too. Use robust estimators.

---

## 10. Structural Estimation

### Model Specification
- [ ] **Economic motivation**: Is the model grounded in economic theory? Can you write down the agent's optimization problem?
- [ ] **Functional form sensitivity**: Try alternative utility specifications (linear, log, CES). Do key results (elasticities, counterfactuals) change?
- [ ] **Distributional assumptions**: For random coefficients, try Normal, Log-Normal, triangular. Test sensitivity.
- [ ] **Nesting structure**: For nested logit, try alternative nesting structures. Results should be robust.
- [ ] **IIA test**: For logit models, test IIA via Hausman-McFadden test or compare with more flexible models.

### Identification & Instruments (Demand Estimation)
- [ ] **First-stage relevance**: Instruments must predict prices. Report first-stage F-statistic.
- [ ] **Instrument validity**: Argue why instruments satisfy exclusion (e.g., cost shifters don't directly affect utility). Do BLP instruments, Hausman instruments, or differentiation IVs give similar results?
- [ ] **Overidentification test**: If using GMM with more instruments than endogenous variables, report Hansen J.
- [ ] **Weak instruments**: If first stage is weak, estimates (especially random coefficients) may be unreliable.

### Model Fit
- [ ] **In-sample fit**: Compare predicted market shares to observed. Report RMSE or correlation. Plot predicted vs. actual.
- [ ] **Substitution patterns**: Do estimated own-price elasticities have correct sign and reasonable magnitude? Are cross-price elasticities sensible? (Close substitutes should have higher cross-elasticity.)
- [ ] **Demand curves**: Plot estimated demand curves. Do they look reasonable?
- [ ] **Hit rate**: For individual-level choice models, what fraction of choices does the model predict correctly?

### Out-of-Sample Validation
- [ ] **Holdout sample**: Estimate on subset of data, predict on holdout. Compare fit.
- [ ] **Temporal validation**: Estimate on early periods, predict later periods.
- [ ] **Cross-market validation**: Estimate on some markets, predict others.
- [ ] **Known policy changes**: If a price change or product entry occurred, does the model predict the observed response?

### Counterfactual Robustness
- [ ] **Multiple specifications**: Run counterfactuals under alternative model specifications. Are qualitative conclusions robust?
- [ ] **Supply-side assumptions**: Try Bertrand, Cournot, collusion. How much do counterfactuals depend on the assumed conduct?
- [ ] **Cost recovery**: Are implied marginal costs reasonable? Negative marginal costs indicate model misspecification.
- [ ] **Equilibrium existence and uniqueness**: For supply-side counterfactuals, verify that the computed equilibrium exists and is unique (or discuss multiplicity).
- [ ] **Confidence intervals on counterfactuals**: Propagate parameter uncertainty through the counterfactual simulation (delta method, bootstrap, or Bayesian posterior).

### Dynamic Model Specific
- [ ] **State space coverage**: Are there enough observations in each state to identify the model? Sparse states lead to noisy CCP estimates.
- [ ] **Discount factor sensitivity**: Vary beta (e.g., 0.90, 0.95, 0.99). How sensitive are results?
- [ ] **Forward-looking vs. myopic**: Compare dynamic model to static model. Is the dynamic component empirically important?
- [ ] **Policy function check**: Do estimated policy functions match observed choice patterns in the data?
- [ ] **Simulation test**: Simulate data from estimated model. Re-estimate on simulated data. Do you recover parameters? (Monte Carlo validation.)

---

## 11. General Robustness Checks (Apply to All Methods)

- [ ] **Placebo tests**: Apply method to outcomes, periods, or populations where no effect is expected.
- [ ] **Subsample stability**: Re-estimate on subsamples (e.g., by region, time period, demographic group).
- [ ] **Functional form**: Try levels, logs, ranks, percentiles for the outcome.
- [ ] **Outlier sensitivity**: Winsorize extreme outcome values and re-estimate.
- [ ] **Alternative standard errors**: Compare heteroskedasticity-robust, cluster-robust, wild bootstrap, randomization inference.
- [ ] **Multiple testing**: If testing multiple outcomes, report adjusted p-values.
- [ ] **Bounding exercise**: Report at least one sensitivity/bounding analysis appropriate for the method.
