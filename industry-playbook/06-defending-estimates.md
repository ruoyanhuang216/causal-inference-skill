# 06. Defending Estimates

The methodology section isn't done when you have a point estimate.
It's done when you can answer "what if your identifying assumption
is wrong?" with a number, not a hand-wave.

This chapter is the **last gate before any stakeholder review**.

---

## The four-question framework (from §0, applied)

Before reporting any causal estimate:

1. **Identifying assumption named?** Parallel trends / unconfoundedness
   / continuity / exclusion / sequential ignorability.
2. **Falsification test run?** Pre-trends / McCrary / placebo
   treatments / negative-control outcomes.
3. **Sensitivity bound reported?** See §6.1 below.
4. **Estimand matches the decision?** ATE vs. CATE vs. LATE — and is
   it the right one for what the stakeholder is choosing?

If you can't answer all four, the analysis isn't ready to present.

---

## §6.1 Sensitivity analysis — quantifying assumption fragility

Pick the framework that matches the estimator. **Always report at
least one.**

### Cinelli-Hazlett Robustness Value (RV) — the industry default

Use for: regression-based estimates, DML, hedonic pricing, anywhere
OLS-style controls handle confounding.

Parameterize the unobserved confounder by two partial `R²`s:

- `R²_{Y∼U | X, T}` — how much residual `Y` variation `U` explains.
- `R²_{T∼U | X}` — how much residual `T` variation `U` explains.

The **Robustness Value (RV)** is the threshold partial `R²`
(assumed equal for both) at which the effect crosses zero. Larger RV
= more robust.

**Benchmarking rule:** always compare RV against the strongest
observed covariate's partial `R²`. "RV = 0.4" is meaningless without
"the strongest observed covariate has R² = 0.05" as context. If RV
> strongest-observed, an unobserved confounder would have to
dominate every observed control to overturn the conclusion.

**Software.** `sensemakr` in R and Python; integrated with `econml`.

### Rosenbaum bounds — for matched designs

Use for: propensity-score matching, CEM, any matched-pair design.

Measures sensitivity via `Γ`, the odds ratio of treatment-assignment
differential between matched pairs due to an unobserved confounder.
`Γ = 1` = no unobserved confounding; `Γ = 2` = a confounder doubles
treatment odds in one member of a matched pair.

Report the maximum `Γ` at which significance survives. Compare to
the strongest *observed* confounder's odds ratio for benchmarking.

### VanderWeele E-value — for risk-ratio framings

Use for: epidemiology, public-health framings where the estimand is
a risk ratio.

```
E-value  =  RR  +  √( RR · (RR − 1) )       for RR > 1
```

Larger E-value = more robust. Direct interpretation: the minimum
risk-ratio strength an unobserved confounder needs with both `T`
and `Y` to fully explain away the effect.

### Manski bounds — worst-case partial identification

Use for: settings where you want to drop the identifying assumption
entirely and bound the effect under monotonicity-style restrictions
only.

Usually produces wide bounds; useful as a "sanity check on the
sanity check" — your favored method's point estimate should lie
inside the Manski bound. Outside it = your assumptions are doing
more work than you realized.

### Negative-control outcomes — falsification check

Use for: any observational design.

Identify an outcome `Y_NC` that should be unaffected by `T` under
correct identification (a pre-treatment outcome, or one
mechanistically independent of the treatment channel). Run the
same estimator on `Y_NC`:

- Null effect on `Y_NC` → identification consistent with the data.
- Non-null effect → residual confounding; estimate is biased.

---

## §6.2 Design-specific falsification tests

Before sensitivity, run the *design-specific* falsification tests:

| Design | Falsification test |
| --- | --- |
| DiD | Pre-period event-study (coefficients on `T × {−3, −2, −1}` ≈ 0); placebo treatment date (1–2 years earlier); leave-one-out (drop each treated unit; estimate shouldn't depend on a single unit) |
| RDD | McCrary density test (no jump in `X` density at `c`); placebo cutoffs; covariate balance at cutoff; bandwidth robustness |
| IV | First-stage F > 10; reduced-form check (`Y` on `Z` directly); Sargan/Hansen over-identification; Anderson-Rubin under weak instruments |
| DML / matching | Balance diagnostics (SMD < 0.1); overlap histogram; specification curve (varying nuisance models / control sets) |

A failure on these tests is more damaging than a failed sensitivity
bound — it says the design itself is broken.

---

## §6.3 Specification curves and robustness checks

When stakeholders ask "is this number robust?", show the
**specification curve**: a plot of the point estimate across many
reasonable analytic choices.

Plot 30–100 specifications varying:
- Control sets (different subsets of features)
- Functional form (log vs. level, with / without interactions)
- Sample inclusion criteria (with / without outliers, subsets by
  segment)
- Nuisance model choice (LightGBM vs. lasso vs. linear)
- Time windows (varying pre- and post-periods for DiD)

Report:
- **Median estimate** and 25th / 75th percentile range
- **Pre-registered "preferred" specification** highlighted on the
  curve
- **% of specifications with point estimate significantly different
  from zero** in the same direction

A specification curve that's tightly clustered around a single sign
is robust. One that flips sign across reasonable specifications is
not, and the methodology section should say so.

---

## §6.4 Cross-method comparison

When the stakes warrant, run **multiple methods on the same data**
and report the spread:

- DML
- DR-learner / AIPW (classical baseline)
- Propensity-score matching (if `n` is small enough)
- Synthetic control / SDiD (if you have a panel)

Plot the point estimates + CIs as a forest plot. **Agreement across
methods = robust.** Wide disagreement = the right answer depends on
which assumptions you trust.

---

## §6.5 Reporting templates

### What to put in the PR doc / lab report

1. **Headline number** (1 sentence): "Treatment X increased
   outcome Y by Z, p < 0.01, 95% CI [a, b]."
2. **Identification one-liner**: "Identified via [design + estimator
   + critical assumption]."
3. **Pre-registered metric and MDE** (if experimental).
4. **One falsification test result** (most credibility-relevant for
   the design).
5. **One sensitivity bound** (RV, Γ, or E-value, with benchmark).
6. **One slice of heterogeneity** (segment that matters most for
   the decision).
7. **One thing that didn't work** (alternative method or
   specification that failed; demonstrates honest exploration).
8. **What you'd do differently** if redoing the analysis from
   scratch (the senior-IC retrospective signal).

If your PR doc has these eight, you've earned the right to recommend
shipping. If it doesn't, write them in.

### What to put in the GM slide

1. The headline number + CI + sign of business impact.
2. One robustness diagnostic — typically the specification curve or
   cross-method forest plot.
3. The decision the number supports.

GMs don't read methodology; they read whether the methodology was
serious. Show the diagnostic; don't explain DML.

---

## §6.6 Common pitfalls (avoid these in any write-up)

- **Simpson's paradox.** Aggregate trend reverses when stratified.
  Always show per-segment readouts alongside the aggregate.
- **Post-treatment controls.** Conditioning on a variable affected
  by `T` blocks the causal pathway. Drop all post-treatment features.
- **Selection into the sample.** If outcomes are only observed for a
  selected subset (clicks among ad-shown users, conversions among
  visitors), you have a selection problem, not a clean ATE.
- **Peeking.** Looking at p-values mid-experiment inflates Type I
  error. Pre-register; if you must peek, use sequential testing.
- **Ratio metrics with user-level randomization.** If the
  randomization unit is the user but the metric is a ratio of
  session-level quantities, the variance formula is wrong.
- **Survivorship.** Right-censored outcomes (churn, default,
  failure) need survival-aware estimators, not naive linear
  regression.
- **Reporting only one specification.** Pre-registering the
  preferred spec and showing the spec curve is honest. Picking the
  spec that gives the result you wanted is p-hacking.
- **Mistaking ITT for CACE.** Report both when there's non-
  compliance; they answer different questions.
- **Confusing AUC with Qini for uplift models.** AUC measures
  classification; Qini measures uplift ranking.

---

## §6.7 What good defense looks like in practice

A staff-level analyst defending a $10M-decision causal estimate
should be able to fluently answer all of:

1. "What's the design?"
2. "What assumption are you making?"
3. "What would have to be true for the estimate to be wrong by a
   factor of 2?"
4. "Did you check pre-trends / covariate balance / overlap?" (The
   design-specific test.)
5. "What does your spec curve look like? How many specs flip sign?"
6. "What does a different estimator give on the same data?"
7. "If you had to redo this, what would you do differently?"

The first three are non-negotiable. The remaining four are what
makes the difference between a defended estimate and a shipped
estimate.

---

## Decision matrix — which defense for which estimate?

| Estimate type | Falsification test | Sensitivity bound | Robustness check |
| --- | --- | --- | --- |
| DML / hedonic / regression-based | Negative-control outcome | Cinelli-Hazlett RV | Spec curve + nuisance-model variation |
| Propensity matching | Balance (SMD < 0.1); placebo treatment | Rosenbaum Γ | Caliper sensitivity |
| DiD | Pre-trend event study; placebo date | RV on the parallel-trends assumption (Rambachan-Roth 2023) | Leave-one-out per treated unit |
| RDD | McCrary density; placebo cutoffs; covariate balance | Bandwidth robustness | Donut RDD (drop observations near `c`) |
| IV | First-stage F; reduced-form check; Sargan J | Conley near-exogeneity / Plausibly exogenous | Anderson-Rubin CI |
| Causal forest / CATE | Honest-split assertion; calibration test | Forest-based prediction intervals | Random-seed stability |
| Uplift model | Decile chart monotonicity | Qini on randomized holdout | Re-fit with alternative meta-learner |
| Structural (BLP / Merton) | Counterfactual sanity | Out-of-sample fit | Parameter stability across periods |

---

## The bottom line

Defending an estimate is about **quantifying how much you could be
wrong**, not proving you're right. In industry, you'll rarely be 100%
confident in any identifying assumption — what stakeholders need is
a defensible bound on the estimate's fragility.

If you remember one thing from this chapter: **always run a sensitivity
analysis and benchmark it against the strongest observed
confounder**. Doing this consistently is what separates a senior
causal-inference practitioner from a junior one.
