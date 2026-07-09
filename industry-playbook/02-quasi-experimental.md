# 02. Quasi-Experimental Designs

When you can't randomize, sometimes the world has — through a policy
rollout that hit some places before others (DiD), an eligibility
threshold (RDD), or an external shifter (IV). Three designs, three
identifying assumptions. Pick the one whose assumption is most
defensible in your setting.

```
DiD   →  Parallel trends:  treated and control would have moved together absent treatment
RDD   →  Continuity at cutoff:  E[Y(0) | X = c] continuous at the eligibility threshold
IV    →  Exclusion + relevance:  instrument shifts T without affecting Y directly
```

---

## §2.1 Difference-in-Differences (DiD)

### Simple case: 2 × 2 DiD

Two periods (pre, post), two groups (treated, control). The OLS
coefficient on the `Treated × Post` interaction:

```
τ̂_DiD  =  ( Ȳ_T,post  −  Ȳ_T,pre )  −  ( Ȳ_C,post  −  Ȳ_C,pre )
```

Equivalently, run:

```
Y_it  =  α_i  +  λ_t  +  τ · (T_i · Post_t)  +  ε_it
```

Cluster SE at the unit level (the level of treatment assignment).

**When to use.** Single policy event, all treated units adopt
simultaneously, clean control group.

**Worked example.** *Effect of a state-level minimum-wage hike on
county-level employment.* A subset of counties raise minimum wage
on 2024-01-01. Use neighboring counties as controls. Verify
employment trends co-moved for 3 years pre-policy.

**Sanity check.**
- **Pre-period event-study.** Coefficients on `T × {−3, −2, −1}`
  should be statistically and economically zero. Visible pre-trend
  invalidates parallel trends.
- **Placebo treatment date.** Shift the treatment date 1–2 years
  earlier on the same units; the effect should be null.
- **Cluster SEs at the unit level.** Wrong clustering can shrink
  SEs by 5–10×.
- **Spillover check.** Could control units be indirectly affected
  (labor mobility, supply-chain links)? If yes, SUTVA is violated.

### Escalate when: staggered adoption

In real industry settings, units adopt at *different* times — states
roll out a feature month-by-month, markets enable a product on
different dates. The naive two-way-fixed-effects (TWFE) coefficient
on `D_it` is **biased** when treatment effects are heterogeneous over
time (Goodman-Bacon 2021): TWFE weights some 2×2 comparisons
negatively, and "forbidden comparisons" of late-treated vs.
already-treated units can flip the sign.

**Use Callaway-Sant'Anna (CS, 2021).** Estimate group-time average
treatment effects `ATT(g, t)` for each cohort × calendar-time cell
using not-yet-treated (or never-treated) units as the comparison
group. Aggregate to event time, calendar time, or overall.

```
ATT(g, t)  =  E[ Y_t(1) − Y_t(0)  |  G = g ]
```

**Sun-Abraham (2021)** is a numerically near-equivalent OLS
formulation; pick CS for the aggregation toolkit, SA for OLS plumbing.

**Worked example.** *Feature ramp by city over 18 months.* Cities 1–5
go live in Q1, cities 6–10 in Q2, etc. CS gives the event-time effect
trajectory uncontaminated by TWFE's forbidden comparisons.

**Sanity check.**
- **Goodman-Bacon decomposition** of any TWFE you're comparing
  against — quantifies how badly TWFE was biased.
- **Pre-treatment placebo** on `ATT(g, t)` for `t < g` cells
  should be ≈ 0.
- **Compare never-treated vs. not-yet-treated comparison choices** —
  large divergence signals anticipation effects.
- **Cluster-bootstrap SEs** at the unit level; default analytic SEs
  are too narrow with few cohorts.

### Escalate further: few treated units, weak parallel trends

When you have **one or a handful of treated units** and the pre-trends
aren't quite parallel, use **Synthetic DiD** (Arkhangelsky-Athey-
Hirshberg-Imbens-Wager 2021). Combines synthetic-control unit weights
(to match pre-treatment levels) with DiD time weights (to emphasize
relevant pre-periods).

```
τ̂_SDiD  =  weighted DiD where weights minimize pre-treatment imbalance
```

**Worked example.** *California-style tobacco-tax effect on per-capita
cigarette sales.* California's pre-trend isn't parallel to most other
states; SDiD weights up the few that do co-move.

**Sanity check.**
- **Unit weights `ω` should be diffuse** — if 1–2 controls carry all
  the weight, generalization is fragile.
- **Pre-treatment fit** — weighted control should overlap the treated
  unit's pre-period closely.
- **Permutation placebo** — run SDiD with each control unit playing
  the treated role; the actual treated unit should sit in the tail.

### Escalate to BSTS: single-series reads with honest uncertainty

When you have **one treated unit + many candidate control series** and
need a counterfactual with a credible interval (not just a point),
reach for **CausalImpact** — a Bayesian structural time series (BSTS)
model: local trend + seasonality + **spike-and-slab** priors that do
automatic control-series selection → posterior counterfactual and
credible interval for the cumulative effect.

**Load-bearing assumption: controls are unaffected by the treatment.**
- **Cannibalization** (treatment depresses a control) → effect
  **overestimated**.
- **Halo** (treatment lifts a control) → effect **underestimated**.

**Falsify with an in-time placebo:** set a dummy intervention date
*inside* the pre-period; the estimated effect there must be ≈ 0.

**Choose plain DiD instead** when the pre-period is short (BSTS needs
enough history to learn trend + seasonality), the setting is
regulated / auditable, or you need a SQL-only estimate.

---

## §2.2 Regression Discontinuity Design (RDD)

When treatment is determined (or strongly influenced) by a continuous
running variable crossing a cutoff. Units just above and just below
the cutoff are nearly identical except for treatment status.

### Sharp RDD

Treatment is deterministic at the cutoff: `T_i = 𝟙(X_i ≥ c)`.

```
τ  =  lim_{x ↓ c} E[Y | X = x]  −  lim_{x ↑ c} E[Y | X = x]
```

**Estimator:** local linear regression on each side of `c` within an
MSE-optimal bandwidth (use Calonico-Cattaneo-Titiunik / CCT
implementation). The `rdrobust` package handles this end-to-end.

**Identifying assumption.** Continuity of `E[Y(0) | X]` at `c` —
falsifiable by the **McCrary density test** (running-variable density
should not jump at `c`; a jump signals manipulation).

**Worked example.** *Effect of a small-business loan on firm
survival.* Loans approved at credit-score-based eligibility index
≥ 600. Compare 5-year survival rates of firms scoring 595 vs. 605
using local linear regression with CCT bandwidth.

**Sanity check.**
- **McCrary density test.** No discontinuity in `X` density at `c`.
- **Placebo cutoffs.** Run RDD at non-cutoff values (e.g., `c ± 10`);
  effect should be null.
- **Covariate balance at the cutoff.** Pre-determined covariates
  (age, gender, prior outcomes) shouldn't jump at `c`. Imbalance
  signals manipulation or confounded eligibility.
- **Bandwidth robustness.** Re-estimate at 0.5×, 1×, 1.5×, 2× the
  CCT-optimal bandwidth; the point estimate should be stable.
- **Local linear vs local quadratic.** Both should give similar
  estimates; large divergence means linear is missing curvature.

### Fuzzy RDD

Treatment probability jumps at `c` but not from 0 to 1. Use a Wald
estimator (equivalent to 2SLS with `𝟙(X ≥ c)` as instrument):

```
τ_LATE  =  (jump in E[Y | X])  /  (jump in E[T | X])
```

Estimates **LATE on compliers** — units who take treatment because
they crossed the cutoff but wouldn't otherwise.

**Worked example.** *Effect of a charter-school program on test
scores.* Cutoff is a lottery rank, but some lottery winners don't
enroll. Fuzzy RDD identifies LATE on lottery compliers.

**Sanity check.** All sharp-RDD checks **plus**:
- **First-stage F > 10** (Stock-Yogo) — the cutoff must produce a
  strong jump in `P(T=1)`.
- **Monotonicity** — no "defiers" (units that take treatment if
  ineligible and skip if eligible). Argue from institutional context.
- **Interpret as LATE on compliers, not ATE.**

---

## §2.3 Instrumental Variables (IV) and 2SLS

When you can't condition your way out of confounding, you find a
**third variable** `Z` that randomly shifts the treatment but doesn't
affect the outcome through any other channel.

### Setup

```
Y_i  =  α  +  β · T_i  +  ε_i        (outcome equation)
T_i  =  π_0  +  π_1 · Z_i  +  ν_i    (first stage)
```

**Four identifying assumptions:**
1. **Relevance** — `Cov(Z, T) ≠ 0`.
2. **Exclusion** — `Z` affects `Y` *only* through `T`.
3. **Monotonicity** — no defiers.
4. **Independence** — `Z` is as-good-as-randomly-assigned given the
   conditioning set.

### 2SLS estimator

Stage 1: regress `T` on `Z` (and controls) → `T̂`.
Stage 2: regress `Y` on `T̂` (and controls). Coefficient on `T̂` is
the IV estimate.

For just-identified IV (one `Z`, no controls), this is the **Wald
form**:

```
β̂_2SLS  =  Cov(Y, Z)  /  Cov(T, Z)
```

### Three high-leverage industry instruments

- **Hausman / shift-share IV.** Use prices / shocks in *other*
  geographies as instruments for local prices / quantities. Argument:
  common upstream costs drive cross-geo correlation; idiosyncratic
  demand is local. Workhorse in retail / pricing.
- **Lottery / quota assignment.** When eligibility is rationed by
  lottery, the lottery outcome is a clean instrument. Used in
  charter schools, housing programs, mobile-data carrier slots.
- **Random-judge / random-assigner designs.** When the
  decision-maker is randomly assigned and varies in stringency,
  their leniency rate is an instrument for the decision. Used in
  credit decisions, content moderation, loan officers.

**Worked example.** *Effect of a marketing-channel exposure on user
LTV.* Direct attribution is biased (selection — people who *click*
are different from those who don't). Use the **assigned bid floor**
as an instrument: bid-floor changes randomly shift who sees the ad,
without directly affecting LTV.

### Modern ML-augmented IV

When you have many controls and want flexible nuisance estimation:

- **DML-IV** (Chernozhukov et al. 2018). Same Neyman-orthogonal
  recipe as DML (§3), with an IV-moment-condition score. ML for the
  nuisance components, cross-fitting for valid inference.
- **IV forests** (Athey-Tibshirani-Wager 2019). Generalized random
  forests with IV-moment splits; produces heterogeneous LATE `τ(x)`
  with pointwise CIs.

### Sanity check

- **First-stage F > 10** (Stock-Yogo). Weak instruments bias 2SLS
  toward OLS — exactly the bias you're trying to escape.
- **Anderson-Rubin test** for confidence intervals robust to weak
  instruments.
- **Exclusion-restriction defense.** Argue from institutional
  context why `Z` enters the outcome only through `T`. Reviewers
  press here harder than anywhere else.
- **Sargan / Hansen J test** with multiple instruments.
- **Reduced-form check.** Regress `Y` directly on `Z`. If the
  reduced form is null, the IV estimate is noise even with strong
  first stage.
- **LATE vs. ATE clarification.** What you estimate is the effect
  on *compliers*, not the population ATE.

---

## Decision matrix

| Situation | Method |
| --- | --- |
| Single treatment date, parallel pre-trends, clean control | Classic 2×2 DiD |
| Staggered adoption across units | Callaway-Sant'Anna (default); Sun-Abraham if you prefer OLS plumbing |
| 1 treated unit + weak parallel trends | Synthetic DiD |
| Deterministic eligibility threshold | Sharp RDD with CCT bandwidth |
| Eligibility threshold with imperfect take-up | Fuzzy RDD = 2SLS at cutoff |
| External shifter of treatment (Hausman / lottery / random assigner) | 2SLS (and DML-IV if many controls) |
| Heterogeneous LATE wanted | IV forests / generalized random forests |

---

## When to escalate to observational methods (§3)

If you can't defend any of: parallel trends, continuity at a cutoff,
or a valid instrument — you're in observational territory.
Identification then leans on unconfoundedness given observable `X`,
which is weaker than design-based identification but more general.
See §3 for the modern industry default (DML).
