# Lecture 8 — Selection on Observables

> **Prerequisites:** [Lecture 1 — Foundations & Estimands](../01-foundations-and-estimands.md) (potential outcomes, the assumption stack, overlap). This lecture finally makes you *pay* for the overlap assumption the design-based lectures could ignore.
> **Deepens:** [`industry-playbook/03-observational.md`](../../industry-playbook/03-observational.md).

This is the pivot of the series. Lectures 2–6 all lived on one side of a
line: **the world handed you exogenous variation** — you randomized, or found
a rollout, a cutoff, an instrument, a clean donor pool. This lecture crosses
to the other side, the one industry lands on constantly:

> *"We launched the feature six months ago, users opted in whenever they
> wanted, and now I need the causal impact."*

No parallel trends. No cutoff. No instrument. No design at all. You are forced
onto **selection on observables** — the most-used and most-misused family in
data science. You assume you measured every confounder, and you match or
weight your way to a comparison. It is powerful, it is the daily bread of
applied DS, and its central assumption is **untestable and usually false**.
This lecture is about doing it as well as it can honestly be done — and
knowing exactly where it fails.

---

## 1. The core idea and the theorem that makes it tractable

You want to compare a treated user to a control user who is *identical* across
50 covariates — age, tenure, spend, geo, device. In high dimensions, **exact
matching is impossible** (the curse of dimensionality): no two users match on
all 50.

**Rosenbaum & Rubin (1983)** rescue it. You don't need to match on all 50
covariates $X$ — only on a single scalar, the **propensity score**:

```math
e(X) = P(D = 1 \mid X)
```

the probability of treatment given covariates. Their theorem: **if
unconfoundedness holds given $X$, it also holds given $e(X)$.** Two users with
the same propensity — both had a 75% chance of treatment — but one got it and
one didn't, can be compared as a localized coin flip. A 50-dimensional
matching problem collapses to one dimension.

---

## 2. The two assumptions

Everything rests on these, and the first is the Achilles heel.

### Unconfoundedness (conditional independence)

```math
\{Y(1), Y(0)\} \perp\!\!\!\perp D \mid X
```

**"Selection on observables."** You must have measured *every* variable that
influences both treatment *and* outcome — **zero unobserved confounders.** It
is impossible to prove, untestable in principle, and the thing every peer
reviewer attacks. §8.1 is largely about why no amount of modeling fixes a
violation of it.

### Overlap (common support)

```math
0 < P(D = 1 \mid X) < 1 \quad \text{for all } X
```

Every user must have a nonzero chance of *either* arm. A user with a 100%
propensity has **no counterfactual clone** and must be dropped. This is the
assumption the design-based lectures got to ignore — and it's where selection
on observables quietly dies, at propensity scores near 0 and 1 (§8.3, §8.4).

---

## 3. The map

Four chapters, one workflow: estimate the propensity, then either **match** or
**weight**, then **defend**.

| # | Chapter | Covers | Estimand |
|---|---|---|---|
| **8.1** | [The Propensity Score & Unconfoundedness](./8.1-propensity-and-unconfoundedness.md) | Rosenbaum-Rubin, the two assumptions, the R² illusion, the Spotify opt-in trap, the "get closer to identical twins" playbook | — |
| **8.2** | [Propensity Score Matching](./8.2-propensity-score-matching.md) | End-to-end (the DoorDash promo): estimation → overlap → caliper matching → Love plot → ATT → Rosenbaum bounds | ATT |
| **8.3** | [Inverse Probability Weighting](./8.3-inverse-probability-weighting.md) | The pseudo-population; ATE vs. ATT weights; unit-level math; the variance danger; stabilized weights | ATE / ATT |
| **8.4** | [Doubly Robust / AIPW](./8.4-doubly-robust-aipw.md) | Two chances to be right (verified); semiparametric efficiency; T-learner vs. S-learner | ATE (default) |
| **8.5** | [Advanced Matching & Weighting](./8.5-advanced-matching-and-weighting.md) | Beyond PSM (King-Nielsen critique): CEM, Mahalanobis distance, entropy balancing; which constraint picks which method | ATT / ATE |

---

## 4. Through-lines

**The golden rule — say it in interviews:** *"Propensity score matching does
not solve selection bias; it only solves the curse of dimensionality for the
variables we happen to have measured."* Unconfoundedness is an assumption about
the world, not a property you can earn with a better model. §8.1.

**Balance diagnostics prove programming, not identification.** A flawless Love
plot (every covariate balanced) proves only that you balanced the columns *in
your table*. It is completely silent about the unobserved confounder in the
next column you didn't collect. The better your balance looks, the more
seductive the trap. §8.1 §5.

**Overlap is where it dies, and "too good" is a symptom.** Extreme propensity
scores have no twins. And a propensity model with near-perfect AUC has
*perfectly separated* the groups — which means no control looks like a treated
unit and overlap is destroyed. A great predictive model can be a terrible
causal one. §8.1 §4, §8.3.

**Doubly robust is the modern default.** AIPW gives you two chances to be right
(unbiased if *either* the outcome model or the propensity model is correct —
verified) and tames IPW's variance explosion by weighting *residuals*, not raw
outcomes. If you're doing selection on observables and not using a doubly-
robust estimator, you're leaving efficiency on the table. §8.4.

---

## 5. References

- **Rosenbaum & Rubin (1983).** "The Central Role of the Propensity Score in Observational Studies for Causal Effects." *Biometrika.* — The founding theorem (§1).
- **Imbens & Rubin (2015).** *Causal Inference for Statistics, Social, and Biomedical Sciences.* Ch. 12–21 — the definitive book-length treatment.
- **Stuart (2010).** "Matching Methods for Causal Inference: A Review and a Look Forward." *Statistical Science.* — The practical matching survey.
- **Chernozhukov et al. (2018).** "Double/Debiased Machine Learning." *Econometrics Journal.* — The ML-nuisance extension of AIPW (Lecture 9).
- **Hernán & Robins (2020).** *Causal Inference: What If.* Ch. 12–15 — IPW and doubly-robust estimation, freely available.
