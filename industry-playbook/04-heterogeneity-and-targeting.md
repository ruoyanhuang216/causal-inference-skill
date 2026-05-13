# 04. Heterogeneity and Targeting

The industry question this chapter answers: **whom should I treat**
when treatment has a cost (budget, friction, possible harm)? The ATE
tells you whether the policy works on average; CATE tells you *who*
responds.

This is the most operationally valuable part of causal inference for
most product / marketing / pricing teams.

---

## The 4-segment taxonomy (mandatory framing)

Every targeting problem maps onto these four segments:

| Segment | `Y(0)` | `Y(1)` | Effect `τ_i` | Targeting action |
| --- | --- | --- | --- | --- |
| **Persuadable** | 0 | 1 | +1 | **Target** |
| **Sure thing** | 1 | 1 | 0 | Skip (wasted budget) |
| **Lost cause** | 0 | 0 | 0 | Skip (wasted budget) |
| **Do-not-disturb** (sleeping dog) | 1 | 0 | −1 | **Avoid** (active harm) |

Estimating per-user `τ(x) = E[Y(1) − Y(0) | X = x]` lets you target
persuadables and avoid sleeping dogs. **Uplift modeling = CATE
estimation with marketing vocabulary.**

The trap: most candidates know the persuadable / sure-thing / lost-
cause segments. The "do-not-disturb" segment is the staff-level
signal. Always mention it.

---

## The industry default: Causal forest

Most general-purpose CATE method. Gives pointwise `τ̂(x)` with valid
confidence intervals. Use it first; escalate to meta-learners if
needed.

### How it works

A **generalized random forest** (Athey-Tibshirani-Wager 2019) with
two key properties:

1. **Honest splitting** — for each tree, split the training sample
   into (a) a *splitting* subsample used to choose splits and (b)
   an *estimation* subsample used to compute leaf treatment effects.
   Required for valid CIs.
2. **Local-moment estimator at a query point `x`** — weight all
   training observations by the forest's similarity kernel `α_i(x)`
   (fraction of trees in which `x_i` is a co-leaf with `x`), then
   solve the DML moment locally:

```
τ̂(x)  =  ( Σ α_i(x) · (T_i − m̂(X_i)) · (Y_i − ĝ(X_i)) )
           /
         ( Σ α_i(x) · (T_i − m̂(X_i))² )
```

### Worked example

*Heterogeneous price-elasticity for a discount campaign.* For each
user `x`, estimate `τ̂(x)` = effect of a 10% discount on purchase
probability. Use `τ̂(x)` directly for targeting: discount users with
estimated `τ̂(x)` above a threshold; hold out a 5% randomized control
for ongoing calibration.

```python
from econml.grf import CausalForest

cf = CausalForest(n_estimators=2000, criterion='het', honest=True)
cf.fit(X=X_features, T=T, y=Y)
tau_hat = cf.predict(X_eligible_users)
```

### Sanity check

- **Calibration test** (Chernozhukov-Demirer-Duflo-Fernández-Val 2018
  "best linear projection"). Regress the test-set outcome residual
  on `τ̂(x)`. Slope ≈ 1 means CATE is well-calibrated; slope ≈ 0
  means the forest is noise — just report the ATE.
- **OOB CATE distribution.** Histogram `τ̂(x)` on out-of-bag samples.
  Spike at the mean = no heterogeneity found.
- **Overlap.** Histogram `m̂(X)` — same diagnostic as DML.
- **Random-seed stability.** Individual `τ̂(x)` shouldn't change
  wildly across seeds.
- **Honest-split assertion.** Confirm the implementation actually
  uses honest splitting; non-honest forests overstate CATE
  significance.

---

## Escalate to meta-learners when

The causal forest commits you to the forest function class for the
CATE. If you have a domain reason to use a different model (deep
networks for high-dim text / image features, linear models for
interpretability), use the **meta-learner stack** instead.

### R-learner — Neyman-orthogonal CATE

Same Neyman-orthogonal recipe as DML, but estimating `τ(x)` instead
of a scalar `τ`:

1. Cross-fit nuisance models `m̂(X)`, `ĝ(X)`.
2. Compute residuals `Ỹ`, `T̃`.
3. Fit a *flexible* final-stage model `τ̂(x)` minimizing
   `Σ T̃_i² · (Ỹ_i − τ(X_i) · T̃_i)²` on residuals.

The final stage can be anything: LightGBM, neural net, linear.

**Use R-learner when.** Want flexible CATE function class and
balanced treated / control samples. Default choice if you're not
using causal forest.

### X-learner — for unbalanced treatment groups

When one arm is much smaller than the other (e.g., 5% treated),
X-learner imputes counterfactuals separately by arm using opposite-
arm models, then propensity-weight-averages the two CATE estimates.

**Use X-learner when.** Treated / control sample sizes are very
unbalanced.

### DR-learner — the doubly-robust default

Same residualization as R, but uses the doubly-robust AIPW score
(§3) as the regression target. Robust to misspecification in either
nuisance model.

**Use DR-learner when.** You're unsure about nuisance specification
and want the most robust meta-learner.

### What about S-learner and T-learner?

- **T-learner** (two-model): train one outcome model on treated,
  one on control, take the difference. **Errors don't cancel** —
  noise in independent fits dominates the treatment signal when
  `τ` is small.
- **S-learner** (single-model with `T` as a feature): tree splits
  prioritize the main effect over the treatment interaction, so the
  model **underfits the treatment effect**.

Both are pedagogical baselines. Don't ship with them.

---

## Evaluation — the Qini curve and decile chart

ROC / AUC don't apply to uplift (you don't observe `τ_i` directly).
Standard metrics:

### Qini curve

Sort the population by predicted uplift `τ̂(x)` descending. For
each top-`k%` slice, compute

```
(# treated responders in top-k%)
   − (# control responders in top-k%) · (n_T / n_C)
```

Plot against `k`. **Qini coefficient** = area above the random-
targeting diagonal — uplift's analog of AUC.

### Decile chart

Bucket by predicted-uplift decile; plot *actual* uplift in each
decile. **Monotonic decline** = model is ranking correctly.
**Non-monotone or flat** = model is mostly noise.

### Uplift @ K%

Average actual uplift among top-`K%` users by `τ̂(x)`. The
operating-point metric at a fixed budget.

### AUUC

Area under the uplift curve; similar to Qini with different
normalization. Some packages report AUUC instead.

### Sanity check before deploying

- **Randomized historical training data.** Observational uplift
  inherits all the DML / confounder issues from §3. If past data
  isn't randomized, treat the model as suggestive and validate via
  an A/B before scaling.
- **Qini monotonicity** across deciles.
- **Holdout A/B in production.** Leave 5% as randomized control;
  recalibrate quarterly. Catches drift before it costs revenue.
- **Counterfactual feasibility.** Can you legally / operationally
  withhold treatment from low-uplift users? In credit / healthcare
  / regulated contexts, sometimes you can't.

---

## End-to-end industry pattern: email-campaign targeting under a budget

*Setup.* Marketing wants to send a discount email to 30% of the user
base; budget fixed. Past randomized email tests provide
training data `(X, T, Y)` for several million users.

*Pipeline.*

1. Fit a causal forest (or DR-learner with LightGBM final stage) on
   randomized historical data → `τ̂(x)`.
2. Rank current eligible users by `τ̂(x)`; send email to top 30%.
3. Hold out 5% of the eligible population as randomized control.
4. **Weekly recalibration:** compare actual uplift per decile to
   predicted; retune the targeting threshold if calibration drifts.

*Report to the GM.* Qini curve + per-decile actual-vs-predicted +
incremental revenue vs. random targeting at the same budget.

---

## Mediation — when the *mechanism* matters

Sometimes the business question is not "does the campaign work?"
but "*how* does it work?" An email might drive purchases directly
(brand reminder) or indirectly (click → landing page → purchase).
Decomposing total effect into direct + indirect informs *which
lever to optimize*.

### Decomposition

Total effect = direct effect + indirect effect (through mediator
`M`).

For binary `T` and continuous `M`, `Y`:

- **NDE** (natural direct effect): `E[Y(1, M(0)) − Y(0, M(0))]`
- **NIE** (natural indirect effect): `E[Y(1, M(1)) − Y(1, M(0))]`
- Total = NDE + NIE.

### Identification — sequential ignorability

Treatment must be unconfounded given `X`, *and* the mediator must be
unconfounded given `X` and `T`. Strong assumption — typically
untestable. Sensitivity analysis is mandatory.

### Worked example

*Email campaign → click → purchase.* Direct effect: how much does
the email itself boost purchases (brand awareness, reminder)?
Indirect effect: how much of the boost comes via the click-through
path? Answer determines whether to optimize the email subject line
(direct) or the landing-page conversion funnel (indirect).

### Sanity check

- **Sequential ignorability sensitivity** (Imai-Keele-Yamamoto 2010).
  Report the magnitude of mediator-outcome confounding that would
  zero out the indirect effect. If small confounders flip the
  conclusion, the result is fragile.
- **`NDE + NIE ≈ ATE`** within MC error — large gap signals
  specification error.
- **Reverse causality check.** Does `M` plausibly cause `T`? If
  yes, the DAG fails and mediation isn't identified.
- **Multiple-mediator robustness.** If a second plausible mediator
  exists, NIE misattributes the path. Include candidates jointly.

### Modern: DML-augmented mediation

Farbmacher-Huber-Lafférs-Langen-Spindler (2022) extends the
Neyman-orthogonality trick to mediation, using ML for the four
nuisance functions (treatment-given-X, mediator-given-T-and-X,
outcome-given-M-T-X, etc.). Same software ecosystem as DML.

---

## Decision matrix

| Situation | Method |
| --- | --- |
| Heterogeneous targeting under budget; flexible features | Causal forest (default) |
| Want a specific CATE function class (linear, deep, sparse) | R-learner |
| Treated and control samples very unbalanced | X-learner |
| Robust to nuisance misspecification | DR-learner |
| Decompose mechanism into direct + indirect | Causal mediation (DML-augmented) |
| Targeting + reporting headline metric | Qini curve + decile chart + uplift @ K% |

---

## When CATE methods *don't* help

- **ATE is the decision.** "Treat everyone or no one" → just estimate
  the ATE.
- **Treatment is free and non-disruptive.** Target everyone, skip
  the modeling.
- **No randomized historical data.** Observational CATE inherits
  every confounder problem from §3 — validate via A/B before
  scaling.

The most common staff-level interview mistake here: forgetting that
the "do-not-disturb" segment exists and reporting AUC instead of
Qini.
