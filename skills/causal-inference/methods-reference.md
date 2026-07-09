# Causal Inference Methods: Detailed Reference

This document provides in-depth reference material for each causal inference method covered by the skill. For each method, it covers: definition, identifying assumptions, estimand, data requirements, strengths, limitations, and key references.

---

## 1. Experimental Methods

### 1.1 Randomized Controlled Trial (RCT)

**Definition**: Units are randomly assigned to treatment and control groups. Randomization ensures that, in expectation, the two groups are identical on all observed and unobserved characteristics.

**Identifying Assumptions**:
- **SUTVA (Stable Unit Treatment Value Assumption)**: Treatment of one unit does not affect outcomes of other units; no hidden variations of treatment
- **Random assignment was properly implemented**: No systematic deviations from the randomization protocol
- **No attrition bias**: Outcome data is observed for all (or a random subset of) randomized units

**Estimand**: ATE (Average Treatment Effect), or ITT (Intent-to-Treat) if there is non-compliance.

**Key Diagnostics**:
- Balance tables: Compare means of baseline covariates across treatment arms
- Attrition analysis: Test whether attrition rates and patterns differ by treatment status
- Compliance analysis: Report take-up rates; estimate LATE via IV if non-compliance

**Implementation Notes**:
- Simple difference in means is unbiased; regression with baseline covariates improves precision (Lin 2013)
- Cluster-robust standard errors if randomization is at cluster level
- Pre-registration and pre-analysis plans are best practice

**Key References**:
- Angrist & Pischke (2009), *Mostly Harmless Econometrics*, Ch. 2
- Athey & Imbens (2017), "The Econometrics of Randomized Experiments"
- Gerber & Green (2012), *Field Experiments*

### 1.2 Cluster Randomized Trial

**Definition**: Randomization occurs at the group (cluster) level — e.g., villages, schools, clinics — but outcomes are measured at the individual level.

**Additional Considerations**:
- Must account for intra-cluster correlation (ICC)
- Effective sample size is closer to the number of clusters, not individuals
- Need cluster-robust standard errors or randomization inference at cluster level
- Power depends heavily on number of clusters (not individuals per cluster)

**Key References**:
- Cameron, Gelbach & Miller (2008), "Bootstrap-Based Improvements for Inference with Clustered Errors"
- Baird, Bohren, McIntosh & Ozler (2018)

### 1.3 Geo Experiments & iROAS (Industry Ad/Measurement Design)

**Definition**: Randomize whole geographic regions rather than users/cookies, then estimate a counterfactual for treated geos from control geos. Standard for ad-effectiveness measurement.

**When to use**: User/cookie randomization fails — multi-device users, cookie churn, offline or lagged conversions. Randomize whole regions instead, ideally **DMAs** (Nielsen Designated Market Areas, ~210 in US, clustered by media market + commuting patterns so they absorb commuter "bleed").

**Design phases**: pretest (4–8 wk) / test (3–5 wk) / cooldown. Estimate the counterfactual for treated geos from the pretest period + control geos.

**Headline metric**: **iROAS = incremental revenue / incremental spend**.

**Key Assumptions & Threats**:
- **SUTVA violation = "bleed"/spillover** across geo borders → attenuation bias. Mitigations: DMAs as sealed units; **buffer "donut" zones** between arms; **graph-partitioned allocation** (assign adjacent geos to the same arm to minimize shared borders).
- **Small-N heterogeneity** (NY DMA ≫ Anchorage): **stratify/block by geo size**, or pull an extreme outlier into an **N=1 synthetic-control** case study.

**Virtual DMAs** (borderless digital/social platforms): partition the *network graph* via **Louvain/Leiden community detection** (signals: social/co-play graph, experience overlap, temporal cohorts) so cross-cluster information flow is minimized. Validate before spending: **modularity / edge-density ratio → SIR "contagion" simulation → geo A/A test** (measured lift must hug 0).

**Packages**: GeoLift (Meta), CausalImpact, geexperiments / Trimmed-Match (Google).

### 1.4 Ramp-Up Time Confounders & Epoch-Conditioning

**Definition**: When an experiment's **treatment:control assignment weight** changes over time AND a **time-based confounder** exists (arrival time correlated with user type and outcome, e.g. frequent users arrive early), the naive global ATE is biased (a Simpson's paradox).

**Key distinction**:
- **Partial-traffic ramp** (enroll 2%→10%, always 50/50 *within* the enrolled slice): **SAFE**.
- **Full-traffic ramp** (100% enrolled, weights 90/10 → 50/50): **BIASED**.
- **Golden rule**: change *total enrolled traffic* freely, never the *T:C weight*.

**Estimator (fix)**: **epoch-conditioning** — within-epoch arm means recombined by total-traffic weights:
```
theta_adj = Sum_j W_j * (ybar_{1,j} - ybar_{0,j}),   W_j = N_j / N_total
```

**MAB / Thompson-Sampling lock-in**: a bandit is a continuous automated ramp; under a time confounder it locks onto the early-arriving segment and can pick the wrong arm (losing to a static 50/50 A/B). Fix inference by integrating over continuous assignment time; fix routing with a **restless/contextual bandit** (encode time-of-day / day-of-week as state).

---

## 2. Difference-in-Differences (DiD)

### 2.1 Classic Two-Period, Two-Group DiD

**Definition**: Compare the change in outcomes over time between a treatment group (exposed to intervention) and a control group (not exposed). The "difference in differences" removes time-invariant unobserved confounders and common time trends.

**Identifying Assumptions**:
- **Parallel trends**: In the absence of treatment, the treatment and control groups would have experienced the same change in outcomes over time
- **No anticipation**: Units do not change behavior before treatment in response to anticipated treatment
- **Stable composition**: The composition of treatment and control groups does not change differentially over time (especially for repeated cross-sections)
- **SUTVA**: No spillovers between groups

**Estimand**: ATT (Average Treatment Effect on the Treated)

**Specification (2x2)**:
```
Y_it = alpha + beta * Treat_i + gamma * Post_t + delta * (Treat_i x Post_t) + epsilon_it
```
where delta is the DiD estimate of the ATT.

**Diagnostics**:
- Visual parallel pre-trends: Plot outcome means by group over time
- Event study / leads-and-lags: Include pre-treatment interaction terms; test joint significance of pre-treatment "effects"
- Placebo tests: Apply DiD to pre-treatment periods or to outcomes unaffected by treatment

**Pitfalls**:
- Parallel trends is untestable (pre-trends ≠ parallel trends; Roth 2022)
- With staggered timing, classic TWFE can be severely biased (Goodman-Bacon 2021)

### 2.2 Staggered DiD (Heterogeneous Treatment Effects)

**The Problem**: When different units adopt treatment at different times, the standard TWFE estimator is a weighted average of all possible 2x2 DiD comparisons — some of which use already-treated units as controls. With heterogeneous treatment effects across time or cohort, the weights can be negative, producing a biased and potentially sign-reversed estimate.

**Modern Solutions**:

| Estimator | Approach | Key Feature |
|-----------|----------|-------------|
| **Callaway & Sant'Anna (2021)** | Group-time ATT; aggregate flexibly | Non-parametric; DR option; `did` package |
| **Sun & Abraham (2021)** | Interaction-weighted estimator | Uses "last treated" or "never treated" as clean control; `eventstudyinteract` |
| **de Chaisemartin & D'Haultfoeuille (2020)** | Instantaneous treatment effect using switchers | `did_multiplegt`; handles switching treatments |
| **Borusyak, Jaravel & Spiess (2024)** | Imputation: estimate counterfactual from untreated observations | Efficient; `did_imputation` |
| **Gardner (2022)** | Two-stage: first partial out FE, then estimate | `did2s` package |
| **Wooldridge (2021)** | Extended TWFE with cohort-specific effects | Standard regression framework; intuitive |

**Practical Guidance**:
- Use multiple estimators as robustness checks
- Always present an event study plot with pre-treatment coefficients
- Report results from at least one robust estimator alongside TWFE

**Key References**:
- Goodman-Bacon (2021), "Difference-in-Differences with Variation in Treatment Timing"
- Roth, Sant'Anna, Bilinski & Poe (2023), "What's Trending in Difference-in-Differences?"
- de Chaisemartin & D'Haultfoeuille (2023), "Two-Way Fixed Effects and Differences-in-Differences Estimators with Several Treatments"

### 2.3 Triple Differences (DDD)

**Definition**: Adds a third "difference" dimension — e.g., within-group variation (age/gender) that determines treatment exposure. Relaxes parallel trends by allowing group-specific trends as long as the *differential* trend is parallel.

**When to use**: When parallel trends for simple DiD is implausible, but you have a within-group source of variation.

---

## 3. Regression Discontinuity Design (RDD)

### 3.1 Sharp RDD

**Definition**: Treatment is a deterministic function of a running variable crossing a known cutoff. Units just above and just below the cutoff are compared as if in a local randomized experiment.

**Identifying Assumptions**:
- **Continuity of potential outcomes at the cutoff**: In the absence of treatment, the expected outcome would be a smooth function of the running variable at the cutoff
- **No manipulation / sorting**: Units cannot precisely manipulate their running variable to land on a preferred side of the cutoff
- **Local randomization**: Units near the cutoff are comparable

**Estimand**: LATE at the cutoff (local to units near the threshold)

**Implementation**:
- Local polynomial regression (linear is standard; triangular kernel)
- Bandwidth selection: MSE-optimal (Calonico, Cattaneo & Titiunik 2014)
- Bias-corrected confidence intervals with robust standard errors

**Diagnostics**:
- **McCrary (2008) density test** or **Cattaneo, Jansson & Ma (2020)**: Test for bunching at the cutoff
- **Covariate smoothness**: Test that pre-determined covariates are continuous at the cutoff
- **Sensitivity to bandwidth**: Show estimates across a range of bandwidths
- **Placebo cutoffs**: Test for discontinuities at non-cutoff values

### 3.2 Fuzzy RDD

**Definition**: The probability of treatment jumps at the cutoff but does not go from 0 to 1. Equivalent to an IV strategy where crossing the cutoff is the instrument for actual treatment take-up.

**Estimand**: LATE for compliers at the cutoff

**Implementation**: IV/2SLS where the first stage is the discontinuity in treatment probability and the reduced form is the discontinuity in the outcome.

### 3.3 Regression Kink Design (RKD)

**Definition**: Instead of a jump (discontinuity) in the level of treatment at the cutoff, there is a kink (change in slope) in the treatment function. Identifies the effect by comparing the change in slope of the outcome at the kink point.

**Key References**:
- Card, Lee, Pei & Weber (2015), "Inference on Causal Effects in a Generalized Regression Kink Design"

### 3.4 Geographic / Spatial RD

**Definition**: The "cutoff" is a geographic boundary (state line, school district boundary, time zone). Units on either side of the boundary are compared.

**Additional concerns**: Need to account for spatial correlation; boundary fixed effects; distance-to-boundary as running variable.

---

## 4. Instrumental Variables (IV)

### 4.1 Standard 2SLS

**Definition**: Use an instrument Z that affects outcome Y only through the endogenous treatment D.

**Identifying Assumptions**:
- **Relevance**: Z is correlated with D (first stage is strong)
- **Exclusion restriction**: Z affects Y only through D (not directly)
- **Independence**: Z is as good as randomly assigned (or conditional on covariates)
- **Monotonicity** (for LATE interpretation): Z affects D in the same direction for all units (no defiers)

**Estimand**: LATE (Local Average Treatment Effect) — the effect for compliers (units whose treatment status is affected by the instrument)

**Diagnostics**:
- **First-stage F-statistic**: Rule of thumb F > 10 (Stock & Yogo); modern: effective F-statistic (Olea & Pflueger 2013)
- **Reduced form**: Show direct effect of Z on Y (should be significant and same sign as structural estimate)
- **Over-identification test** (Hansen J): If multiple instruments, test that all give consistent estimates
- **Exclusion restriction**: Not testable — must argue qualitatively
- **Placebo instruments**: Show instrument does not predict pre-treatment outcomes

### 4.2 Shift-Share / Bartik Instruments

**Definition**: Instrument = sum of (local shares) x (national growth rates). Common in labor/trade economics.

**Two identification strategies**:
- **Share-based** (Goldsmith-Pinkham, Sorkin & Swift 2020): Exogeneity comes from the shares being as good as randomly assigned
- **Shock-based** (Borusyak, Hull & Jaravel 2022): Exogeneity comes from the shocks being as good as randomly assigned; shares just determine exposure

**Diagnostics**: Rotemberg weights to identify influential shares/shocks; pre-trend tests.

### 4.3 Judge / Examiner IV

**Definition**: Exploit quasi-random assignment of cases to judges (or examiners, case workers) who vary in leniency. Judge leniency (leave-one-out mean) serves as instrument for treatment (e.g., incarceration, disability benefits).

**Key Assumptions**: Random assignment of cases to judges; exclusion restriction (judge affects outcome only through the treatment); monotonicity (more lenient judges weakly increase treatment for all case types).

**Key References**:
- Kling (2006), Maestas, Mullen & Stainbaugh (2013)
- Frandsen, Lefgren & Leslie (2023) — tests for monotonicity

---

## 5. Synthetic Control Method (SCM)

### 5.1 Classic SCM

**Definition**: For a single treated unit, construct a weighted combination of untreated "donor" units that best reproduces the treated unit's pre-treatment outcomes. The post-treatment gap between the treated unit and its synthetic control estimates the treatment effect.

**Identifying Assumptions**:
- The outcome can be well-approximated by a factor model
- Good pre-treatment fit between treated unit and synthetic control
- No interference between treated and donor units
- Donor pool does not include units affected by the treatment (spillovers)

**Inference**: Permutation / placebo tests — apply the method to each donor unit and compare the treated unit's effect to the distribution of placebo effects. Compute p-values from the rank of the treated unit's effect size.

**Diagnostics**:
- Pre-treatment fit (RMSPE or visual)
- Ratio of post/pre RMSPE for inference
- Sparsity of weights (interpretability)
- Leave-one-out donor robustness

### 5.2 Augmented SCM (ASCM)

**Definition**: Adds a bias-correction term using ridge regression to correct for imperfect pre-treatment fit in standard SCM.

**Advantage**: Reduces bias when pre-treatment fit is imperfect; always at least as good as SCM.

**Key Reference**: Ben-Michael, Feller & Rothstein (2021)

### 5.3 Synthetic Difference-in-Differences (SDID)

**Definition**: Combines elements of DiD and SCM. Reweights units (like SCM) AND time periods to create a doubly-robust estimator.

**Advantage**: Valid under weaker conditions than either DiD or SCM alone.

**Key Reference**: Arkhangelsky, Athey, Hirshberg, Imbens & Wager (2021)

---

## 6. Selection-on-Observables Methods

### 6.1 Propensity Score Methods

**Propensity Score**: e(X) = P(D=1 | X). The probability of receiving treatment given observed covariates.

**Key Result (Rosenbaum & Rubin 1983)**: If CIA holds conditional on X, it also holds conditional on e(X). This reduces a high-dimensional matching problem to one dimension.

#### Propensity Score Matching (PSM)
- Match treated units to control units with similar propensity scores
- Variants: nearest-neighbor (with/without replacement), caliper matching, kernel matching
- Check: common support / overlap; balance of covariates after matching

#### Inverse Probability Weighting (IPW)
- Weight each observation by inverse of propensity score: treated by 1/e(X), controls by 1/(1-e(X))
- Caution: extreme weights when propensity scores near 0 or 1 → trim or use stabilized weights
- Estimate: Horvitz-Thompson estimator or Hajek (normalized) estimator

#### Doubly Robust / AIPW
- Combines outcome regression and propensity score weighting
- Consistent if EITHER the outcome model OR the propensity score model is correctly specified
- Semiparametrically efficient (achieves the efficiency bound)
- Recommended as default for selection-on-observables designs

### 6.2 Matching Methods (Non-Propensity-Score)

#### Coarsened Exact Matching (CEM)
- Coarsen covariates into bins; exact match within bins; prune unmatched
- Advantage: Bounds maximum imbalance by design (Iacus, King & Porro 2012)

#### Mahalanobis Distance Matching
- Match on multivariate Mahalanobis distance
- Better than PSM when number of covariates is small and continuous

#### Entropy Balancing
- Find weights for control group that exactly match specified moments (mean, variance, skewness) of treated group covariates
- Advantage: Achieves exact balance by construction; no iterative checking
- Key Reference: Hainmueller (2012)

### 6.3 Overlap / Trimming Weighting

- **Overlap weights** (Li, Morgan & Zaslavsky 2018): Weight = e(X)(1-e(X)); emphasizes units in the region of equipoise
- **Trimming**: Drop observations with extreme propensity scores (e.g., < 0.1 or > 0.9)
- These improve precision and reduce sensitivity to model misspecification

---

## 7. Machine Learning for Causal Inference

### 7.1 Double/Debiased Machine Learning (DML)

**Definition**: Use ML to estimate nuisance parameters (propensity score, outcome model) while preserving valid statistical inference for the causal parameter.

**Key Innovation**: Cross-fitting (sample splitting) to avoid overfitting bias + Neyman orthogonality to reduce sensitivity to ML estimation error.

**Steps**:
1. Split data into K folds
2. For each fold, estimate nuisance functions (E[Y|X], E[D|X]) using other folds
3. Compute the "orthogonalized" causal parameter using residuals
4. Average across folds

**Packages**: `doubleml` (Python/R), `hdm` (R)

**Key Reference**: Chernozhukov, Chetverikov, Demirer, Duflo, Hansen, Newey & Robins (2018)

### 7.2 Causal Forest

**Definition**: Extension of random forests to estimate heterogeneous treatment effects (CATE = E[Y(1)-Y(0)|X=x]).

**How it works**:
- Builds an ensemble of "causal trees" that partition the covariate space
- Each leaf estimates a local treatment effect
- Uses honesty (separate samples for splitting and estimation) for valid inference
- Provides pointwise confidence intervals for CATE

**Use cases**: Discovering treatment effect heterogeneity; optimal policy learning; targeting

**Packages**: `grf` (R), `econml` (Python)

**Key Reference**: Wager & Athey (2018); Athey, Tibshirani & Wager (2019)

### 7.3 Meta-Learners for CATE Estimation

| Learner | Approach | Pros | Cons |
|---------|----------|------|------|
| **S-learner** | Single model: Y ~ X, D; CATE = mu(X,1) - mu(X,0) | Simple | Regularization can shrink treatment effect to 0 |
| **T-learner** | Separate models for treated and control | Captures heterogeneity | Doesn't share information across groups |
| **X-learner** (Kunzel et al. 2019) | Two-stage: impute individual effects, then model them | Good with unbalanced groups | More complex |
| **R-learner** (Nie & Wager 2021) | Minimize residual-on-residual loss | Directly targets CATE | Requires careful tuning |
| **DR-learner** | Doubly-robust pseudo-outcomes, then regression | Efficient; robust | Requires propensity score |

### 7.4 BART for Causal Inference

**Definition**: Bayesian Additive Regression Trees — flexible nonparametric model that naturally provides posterior uncertainty.

**Causal use**: Estimate E[Y|X,D] flexibly; compute CATE as difference in predictions under D=1 vs D=0.

**Advantage**: Handles nonlinearity, interactions, and provides uncertainty quantification without bootstrap.

**Key Reference**: Hill (2011); Hahn, Murray & Carvalho (2020) — Bayesian Causal Forest (BCF)

### 7.5 Targeted Learning / TMLE

**Definition**: Targeted Minimum Loss-based Estimation. A semiparametric framework that combines ML for nuisance estimation with a targeting step to ensure the estimator is efficient and well-calibrated.

**Steps**:
1. Initial estimate of outcome model using Super Learner (ensemble ML)
2. "Targeting" step: update the initial estimate to optimize bias-variance for the specific causal parameter
3. Inference via influence function

**Advantage**: Semiparametrically efficient; doubly robust; confidence intervals have correct coverage even with ML nuisance estimation.

**Packages**: `tmle` / `tmle3` (R), `zepid` (Python)

**Key Reference**: van der Laan & Rose (2011), *Targeted Learning*

### 7.6 Confounded Feedback Loops & Alternating Optimization

**Definition**: Rankers/recommenders create a feedback loop — the system only shows high-quality items prominently, so item **quality** and **prominence/placement** are confounded in the logs. A naive model's estimate of the placement effect is therefore biased.

**When to use**: Estimating the causal effect of placement/ranking in a logged recommender or search system where the logging policy itself depends on predicted quality.

**Estimator (fix)**: combine a **massive observational stream** (learn a high-dimensional quality score, beta_1 * X_1) with a **small randomized holdback** (~1%, where placement is randomized → learn the unbiased causal effect beta_pi). Fit by **alternating optimization**: each block is the other's fixed **offset**, and the causal parameter beta_pi is updated ONLY on randomized data, quarantining the observational confounding.

**Monitoring**: drift via **PSI/KL** on the quality score, plus a rolling holdback ATE as a "causal canary."

**Extension**: generalizes to HTE by replacing the scalar beta_pi with tau(X_user).

---

## 8. Causal Mediation Analysis

### 8.1 Modern Causal Mediation Framework

**Goal**: Decompose the total effect of treatment D on outcome Y into:
- **Natural Direct Effect (NDE)**: Effect of D on Y not through mediator M
- **Natural Indirect Effect (NIE)**: Effect of D on Y through mediator M
- Total Effect = NDE + NIE (under certain conditions)

**Identifying Assumptions** (strong!):
1. No unmeasured treatment-outcome confounding
2. No unmeasured mediator-outcome confounding
3. No unmeasured treatment-mediator confounding
4. No treatment-induced mediator-outcome confounding (the "cross-world" assumption)

**Methods**:
- **Baron-Kenny (1986)**: Classic regression-based approach. Known issues: requires linearity, no interaction, can mislead with binary outcomes
- **Imai, Keele & Tingley (2010)**: Nonparametric identification and sensitivity analysis. `mediation` package (R)
- **VanderWeele (2015)**: Comprehensive framework; allows treatment-mediator interaction

### 8.2 Sensitivity Analysis for Mediation

- Sequential ignorability is untestable — always do sensitivity analysis
- Imai et al. (2010): Sensitivity parameter rho (correlation of residuals)
- E-value approach for mediation

---

## 9. Bounds and Partial Identification

### 9.1 Manski Bounds

**Definition**: Under minimal assumptions (no functional form, no distributional assumptions), derive worst-case bounds on treatment effects. Typically very wide.

**Use case**: When you want to know what can be learned without strong assumptions.

### 9.2 Lee Bounds (2009)

**Definition**: Bounds on treatment effects in the presence of sample selection (attrition, non-response) where treatment affects whether the outcome is observed.

**Approach**: Trim the "excess" observations from the group with higher response rates to restore balance.

### 9.3 Oster's Delta (2019)

**Definition**: Coefficient stability approach. Asks: how much selection on unobservables (relative to selection on observables) would be needed to explain away the estimated treatment effect?

**Output**: delta — if delta > 1, the result is robust to substantial unobserved confounding.

**Implementation**: `psacalc` (Stata), manual computation in R/Python.

### 9.4 Cinelli & Hazlett (2020)

**Definition**: Omitted variable bias framework based on partial R-squared. Reports:
- **Robustness value (RV)**: The minimum strength of confounding (in partial R-squared terms) needed to reduce the estimate to zero
- **Sensitivity contour plots**: Visual display of how the estimate changes with varying confounder strength

**Package**: `sensemakr` (R)

---

## 10. Panel Data Methods

### 10.1 Fixed Effects (FE)

**Definition**: Include unit and/or time fixed effects to absorb time-invariant unobserved heterogeneity.

**Assumption**: After removing unit-specific means, remaining variation in treatment is uncorrelated with remaining variation in unobservables (strict exogeneity).

**Pitfalls**:
- Cannot identify effects of time-invariant treatments
- Strict exogeneity rules out feedback from past outcomes to current treatment
- TWFE with staggered treatment and heterogeneous effects is biased (see DiD section)

### 10.2 Correlated Random Effects (CRE) / Mundlak

**Definition**: Include group means of time-varying covariates as additional regressors in a random effects model. Under Mundlak's (1978) specification, this is numerically equivalent to FE for time-varying regressors but also allows estimation of time-invariant effects.

### 10.3 Dynamic Panel GMM

**Definition**: For models with lagged dependent variables (Y_it depends on Y_{i,t-1}), standard FE is biased (Nickell bias). GMM estimators use lagged levels/differences as instruments.

- **Arellano-Bond (1991)**: Difference GMM; instruments differences with lagged levels
- **Blundell-Bond (1998)**: System GMM; adds level equation with lagged differences as instruments. Better with persistent series.

**Diagnostics**: AR(1) and AR(2) tests; Hansen J test for over-identifying restrictions; number of instruments should be << number of groups.

### 10.4 Empirical Bayes / Random-Effects Partial Pooling

**Definition**: For sparse **high-cardinality categoricals** (advertiser / city / campaign IDs; some groups with 10M rows, some with 3), model group effects as random effects alpha_j ~ N(mu, sigma^2_prior) and shrink each group's estimate toward the global mean.

**When to use**: Fixed effects overfit the rare tail; complete pooling underfits. Random effects give adaptive shrinkage between the two.

**Estimator**: the Bayes estimate is adaptive shrinkage:
```
alphahat_j = W_j * ybar_j + (1 - W_j) * mu,   W_j = n_j / (n_j + sigma^2_data / sigma^2_prior)
```
Shrinks *per group* by its own sample size (vs Ridge's single global lambda = **homogeneous** shrinkage). Conjugate **Gamma–Poisson** for counts gives a closed form: lambdahat_j = (a + c_j) / (b + n_j).

**Cold start** (n=0 → estimate = prior mu) falls out for free.

**Bridge to bandits**: the posterior mean AND variance feed **Thompson Sampling** → automatic explore/exploit (a new arm's wide posterior gets sampled from its tail; variance shrinks → exploration fades).

**Fitting**: **EM** (Empirical-Bayes point estimates; scales), **Gibbs/MCMC** (full posterior).

**Packages**: `statsmodels` MixedLM, `PyMC`, `lme4` / `brms` (R).

---

## 11. Time Series Causal Methods

### 11.1 Interrupted Time Series (ITS)

**Definition**: Segmented regression on a single time series with a known intervention point. Estimates change in level and/or slope after intervention.

**Model**:
```
Y_t = beta_0 + beta_1*t + beta_2*D_t + beta_3*(t - T0)*D_t + epsilon_t
```
where D_t = 1 after intervention, T0 is intervention time.

**Concerns**: Autocorrelation; seasonal effects; concurrent events; Newey-West SEs.

### 11.2 CausalImpact (Bayesian Structural Time Series)

**Definition**: Bayesian approach that constructs a synthetic counterfactual using control time series and a structural time series model. Posterior inference on the causal effect.

**Advantages**: Automatically handles seasonality, trends, and regression on covariates; provides posterior intervals.

**Control selection**: a **spike-and-slab** prior auto-selects the few predictive control series from many candidates.

**Falsification — in-time placebo / false-positive-rate check**: slide a dummy intervention date across the pre-period; a sound model returns effect ≈ 0 with a CI covering zero.

**Contaminated-control endogeneity**: controls must be *unaffected by the treatment*. Cannibalization (control depressed by the treatment) → **overestimate**; halo (control lifted) → **underestimate**.

**DiD-vs-BSTS decision**: use **DiD** when the pre-period is short/sparse, the analysis is regulated/auditable, or it must be SQL-only; use **BSTS** when you have rich, autocorrelated series with many candidate controls and need honest uncertainty.

**Package**: `CausalImpact` (R), `causalimpact` (Python)

**Key Reference**: Brodersen, Gallusser, Koehler, Remy & Scott (2015)

---

## 12. Causal Discovery

### 12.1 Constraint-Based Methods
- **PC Algorithm**: Tests conditional independence to orient edges in the DAG
- **FCI (Fast Causal Inference)**: Handles latent confounders

### 12.2 Score-Based Methods
- **GES (Greedy Equivalence Search)**: Searches over DAG space to maximize BIC score

### 12.3 Continuous Optimization
- **NOTEARS** (Zheng et al. 2018): Formulates DAG learning as continuous optimization with acyclicity constraint

### 12.4 Important Caveats
- Causal discovery from observational data alone has fundamental limitations
- Results are typically up to Markov equivalence class (can't distinguish all edge orientations)
- Requires strong assumptions (faithfulness, causal sufficiency)
- Best used for hypothesis generation, not confirmation

---

## 13. Structural Estimation

Structural estimation uses economic theory to specify agents' optimization problems and equilibrium interactions. The model is estimated by matching model-implied moments (market shares, choice probabilities, prices) to data. Estimated parameters enable counterfactual simulations that go beyond observed variation.

### 13.1 Discrete Choice Demand Models

#### Multinomial / Conditional Logit (McFadden 1974)

**Definition**: Consumer i chooses product j that maximizes utility:
```
U_ij = X_j * beta + alpha * p_j + xi_j + epsilon_ij
```
where epsilon_ij is i.i.d. Type-I Extreme Value. Closed-form choice probabilities via logit formula.

**Limitations**:
- **IIA (Independence of Irrelevant Alternatives)**: Proportional substitution — removing a product redistributes its share proportionally. Unrealistic for differentiated products.
- No unobserved consumer heterogeneity

**Use case**: Simple baseline; individual-level data with few alternatives; good for conjoint analysis.

#### Mixed Logit / Random Coefficients Logit

**Definition**: Allow preference parameters to vary across consumers:
```
U_ij = X_j * beta_i + alpha_i * p_j + xi_j + epsilon_ij
beta_i ~ F(theta)  (e.g., Normal, Log-Normal)
```
Choice probabilities require simulation (no closed form).

**Advantages**: Flexible substitution patterns; captures preference heterogeneity; nests logit and probit as special cases.

**Estimation**: Maximum Simulated Likelihood (MSL) or Method of Simulated Moments.

**Key Reference**: Train (2009), *Discrete Choice Methods with Simulation*

#### BLP — Berry, Levinsohn & Pakes (1995)

**Definition**: Aggregate-level demand estimation for differentiated products. The key innovation: use market share data (not individual choices) and handle price endogeneity.

**Model**:
```
U_ij = delta_j + mu_ij + epsilon_ij
delta_j = X_j * beta - alpha * p_j + xi_j    (mean utility)
mu_ij = X_j * Sigma * v_i                      (individual deviation)
```

**Estimation algorithm**:
1. Guess nonlinear parameters (Sigma)
2. For each guess, invert market shares to recover delta_j (BLP contraction mapping)
3. Use IV regression of delta_j on (X_j, p_j) to recover (beta, alpha) and residual xi_j
4. Form GMM objective: E[Z' * xi] = 0
5. Optimize over Sigma to minimize GMM objective

**Instruments for price**:
- **BLP instruments**: Characteristics of competing products in the same market (sums, counts)
- **Hausman instruments**: Prices of the same product in other markets (common cost shocks)
- **Cost shifters**: Input costs, tariffs, exchange rates
- **Gandhi-Houde (2020) differentiation IVs**: Functions of product distances in characteristic space — better captures local competition
- **Optimal instruments**: Chamberlain (1987) / Reynaert & Verboven (2014)

**Key outputs**:
- Own-price elasticities
- Cross-price elasticities (flexible substitution, not IIA)
- Consumer surplus
- Inputs for merger simulation, optimal pricing, product design

**Key References**:
- Berry (1994), "Estimating Discrete-Choice Models of Product Differentiation"
- Berry, Levinsohn & Pakes (1995), "Automobile Prices in Market Equilibrium"
- Nevo (2000), "A Practitioner's Guide to Estimation of Random-Coefficients Logit Models of Demand"
- Conlon & Gortmaker (2020), "Best Practices for Differentiated Products Demand Estimation with PyBLP"

#### Nested Logit

**Definition**: Products are grouped into nests (categories). Within-nest substitution is higher than across-nest substitution. The nesting parameter sigma in [0,1] governs substitution — sigma=0 is logit, sigma→1 means all substitution is within-nest.

**Advantage over logit**: Breaks IIA across nests while maintaining tractability.

**Use case**: Clear hierarchical choice structure (e.g., inside vs. outside good; car type → brand).

#### Latent Class Models

**Definition**: Assume K discrete consumer types (segments), each with distinct preference parameters. Segment membership is probabilistic.

**Estimation**: EM algorithm or direct MLE. Choose K via BIC/AIC or cross-validation.

**Use case**: Marketing segmentation; targeting; when continuous heterogeneity distributions are hard to justify.

### 13.2 Supply-Side Models

#### Nash-Bertrand Pricing

**Definition**: Firms simultaneously set prices to maximize profits. For multi-product firms, FOCs account for cannibalization across own products.

**First-order conditions**:
```
p - mc = -[Ownership * dS/dp]^{-1} * S
```
where Ownership is a matrix indicating which firm owns which product, dS/dp is the matrix of share derivatives (from demand), and S is the vector of market shares.

**Key use**: Back out marginal costs from observed prices + estimated demand. Then simulate counterfactuals.

#### Merger Simulation

**Steps**:
1. Estimate demand (e.g., BLP)
2. Recover marginal costs from supply-side FOCs under pre-merger ownership
3. Change ownership matrix to reflect merger
4. Solve for new equilibrium prices (and quantities)
5. Compute changes in prices, consumer surplus, profits

**Key Reference**: Nevo (2000); Werden & Froeb (1994)

#### Entry / Exit Models

**Definition**: Firms enter a market if expected profits exceed a fixed cost. Observed entry patterns identify profit function parameters and fixed costs.

- **Bresnahan & Reiss (1991)**: How many firms can a market support?
- **Berry (1992)**: Entry with heterogeneous firms
- **Seim (2006)**: Entry with spatial differentiation

### 13.3 Dynamic Structural Models

#### Single-Agent Dynamic Discrete Choice

**Framework**: Agent chooses action a_t in each period to maximize:
```
max E[ sum_{t=0}^{inf} beta^t * u(a_t, s_t, epsilon_t; theta) ]
```
subject to state transitions s_{t+1} = f(s_t, a_t).

**Key challenge**: Solving the dynamic programming (DP) problem — computing the value function.

#### Nested Fixed Point (NFXP) — Rust (1987)

**Approach**: For each candidate parameter theta:
1. Solve the full DP problem (value function iteration)
2. Compute choice probabilities
3. Evaluate likelihood
4. Iterate on theta

**Pros**: Consistent, asymptotically efficient.
**Cons**: Computationally expensive — must solve DP at every parameter guess.

**Classic application**: Rust (1987) — bus engine replacement decisions.

#### CCP Estimation — Hotz & Miller (1993)

**Key insight**: The value function can be expressed in terms of observable **conditional choice probabilities** (CCPs). No need to solve the DP directly.

**Steps**:
1. **First stage**: Estimate CCPs nonparametrically from data (e.g., frequency of each choice in each state)
2. **Second stage**: Use the CCP-to-value-function mapping to form moment conditions; estimate structural parameters

**Pros**: Much faster — avoids repeated DP solution. Flexible.
**Cons**: First-stage CCP estimates can be noisy in sparse states; finite-dependence property needed for some formulations.

**Extensions**:
- Arcidiacono & Miller (2011): EM algorithm for unobserved types
- Arcidiacono & Ellickson (2011): Practical guide

#### MPEC — Mathematical Programming with Equilibrium Constraints (Su & Judd 2012)

**Approach**: Formulate estimation as a constrained optimization problem:
- Objective: Minimize distance between model and data moments
- Constraints: Bellman equation must hold (value function is consistent with policy)

**Advantage**: Often faster and more robust than NFXP; can use off-the-shelf optimizers (KNITRO, IPOPT).

#### Dynamic Games

When multiple strategic agents interact over time:
- **Bajari, Benkard & Levin (2007)**: Two-step estimator. First estimate policy functions, then recover payoff parameters.
- **Aguirregabiria & Mira (2007)**: Sequential estimation with CCP updates.
- **Pakes, Ostrovsky & Berry (2007)**: Simple estimators for dynamic games.

**Applications**: Store entry/exit, dynamic pricing, advertising dynamics, R&D competition.

### 13.4 Consumer Search Models

#### Sequential Search — Weitzman (1979)

**Framework**: Consumer draws utility from each option sequentially, paying a search cost c per draw. Optimal rule: search in order of reservation values; stop when best found utility exceeds next reservation value.

**Identification**: Search costs identified from: how many options consumers examine, the order of search, and the relationship between chosen option and set size.

**Key References**:
- Hortacsu & Syverson (2004): Search in financial markets
- Honka (2014): Consumer search for insurance
- Kim, Albuquerque & Bronnenberg (2010): Online search with learning
- De los Santos, Hortacsu & Wildenbeest (2012): Testing search models

#### Consideration Set Models

**Definition**: Consumers first form a consideration set (limited attention), then choose from it. Separates awareness/attention from preference.

**Identification**: Requires data on both what was considered and what was chosen (click data, eye tracking), or can be partially identified from choice data alone under restrictions.

### 13.5 Learning Models

#### Bayesian Learning — Erdem & Keane (1996)

**Framework**: Consumers have prior beliefs about product quality. Each purchase/signal updates beliefs via Bayes' rule. Consumers optimally trade off exploration (learning about uncertain products) vs. exploitation (choosing the known-best product).

**Identification**: Over time, consumers who are learning show:
- Decreasing probability of switching
- Increasing purchase frequency of preferred brands
- Responsiveness to signals (advertising, WOM) decreasing over time

**Applications**: New product adoption, advertising effectiveness, experience goods, physician prescribing.

### 13.6 Structural Estimation: Identification

**Critical principle**: Structural estimation does NOT bypass the need for identification. Every parameter must be identified from variation in the data.

**Common identification sources**:
| Parameter | Identified from |
|-----------|----------------|
| Price coefficient (alpha) | Price variation + instruments (cost shifters, BLP IVs) |
| Preference heterogeneity (Sigma) | Variation in substitution patterns across markets |
| Search costs | Number of alternatives examined; order of search |
| Switching costs | Excess persistence in choices beyond preference heterogeneity |
| Discount factor (beta) | Typically calibrated (e.g., beta=0.99); hard to identify separately from other parameters |
| Fixed costs (entry) | Observed entry/exit decisions across markets of varying profitability |
| Learning speed | Rate at which choice behavior stabilizes over time |

### 13.7 Structural Estimation: Practical Considerations

**Common estimation methods**:
| Method | When to use |
|--------|-------------|
| **MLE / Simulated MLE** | Likelihood is tractable (possibly via simulation); most efficient |
| **GMM / Simulated GMM** | Moment conditions available; BLP uses GMM |
| **Method of Simulated Moments (MSM)** | Match model-simulated moments to data moments |
| **Indirect Inference** | Estimate auxiliary model on real and simulated data; match auxiliary parameters |
| **Bayesian (MCMC)** | Want full posterior; complex models; hierarchical structures |
| **MPEC** | Dynamic models; formulate as constrained optimization |

**Computational tools** (Python):
- `PyBLP` — BLP demand estimation (Conlon & Gortmaker)
- `scipy.optimize` — general purpose optimization
- `JAX` / `autograd` — automatic differentiation for GMM/MLE
- `Pyomo` / `casadi` — MPEC formulation
- `numba` — JIT compilation for value function iteration
- `emcee` / `PyMC` — Bayesian MCMC estimation
