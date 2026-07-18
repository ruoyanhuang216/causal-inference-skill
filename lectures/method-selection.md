# Method Selection — Which Causal Method, When?

> The navigator for the whole series. Start with the question you're facing;
> follow the branch to the lecture. The organizing axis is **how much the world
> does the identification for you** — the more designed the variation, the more
> credible (and the higher up this tree) the method.

The single most important question comes first, because a "yes" outranks
everything below it:

```
                        ┌─────────────────────────────────────┐
                        │  Can you RANDOMIZE the treatment?    │
                        └─────────────────────────────────────┘
                              │ YES                    │ NO
                              ▼                         ▼
                    ┌──────────────────┐    ┌──────────────────────────────┐
                    │ Lecture 2         │    │ Did the WORLD hand you        │
                    │ EXPERIMENTATION   │    │ exogenous variation?          │
                    └──────────────────┘    └──────────────────────────────┘
                              │                         │ YES            │ NO
                              ▼                         ▼                ▼
                    (interference? →           (design-based ID)   (no design →
                     cluster/geo/switchback)    L3 / L4 / L5        assume it away)
```

---

## The master decision tree

```
CAN YOU RANDOMIZE?
│
├─ YES ──────────────────────────────────────────► Lecture 2  EXPERIMENTATION
│     ├─ users independent ...................... 2.1 RCT
│     ├─ need sample size / many arms ........... 2.2 Power & Multi-Arm
│     ├─ network spillovers (social feed) ....... 2.3 Cluster Randomization
│     ├─ marketing / offline / marketplace ...... 2.4 Geo Experiments (iROAS)
│     ├─ shared-supply marketplace (Uber) ....... 2.5 Switchbacks
│     ├─ traffic ramp / bandit .................. 2.6 Ramp-Up & Bandits
│     └─ confounded ranker logs ................. 2.7 Feedback Loops (1% holdback)
│
└─ NO. What did the world give you instead?
   │
   ├─ A ROLLOUT over time (treated vs. control groups, before/after)
   │     ├─ parallel pre-trends plausible ....... Lecture 3  DiD (3.1)
   │     ├─ staggered adoption timing ........... 3.3 Staggered DiD (never TWFE!)
   │     └─ a concurrent shock hit one group .... 3.4 Triple Differences
   │
   ├─ A CUTOFF / threshold rule (score ≥ c → treated)
   │     ├─ treatment flips deterministically ... Lecture 4  Sharp RDD (4.1)
   │     ├─ take-up only jumps (not 0→1) ........ 4.2 Fuzzy RDD
   │     ├─ the SLOPE changes, not the level .... 4.3 Regression Kink
   │     └─ the cutoff is a map BORDER .......... 4.4 Geographic RD
   │
   ├─ An INSTRUMENT (moves treatment, no other path to outcome)
   │     ├─ a plausible lever ................... Lecture 5  2SLS (5.1)
   │     ├─ shares × global shocks .............. 5.2 Shift-Share / Bartik
   │     └─ randomly-assigned humans decide ..... 5.3 Judge / Examiner IV
   │
   ├─ ONE or a FEW treated units + a donor pool / panel
   │     ├─ one treated unit, clean pre-trend ... Lecture 6  Synthetic Control (6.1)
   │     ├─ treated unit is a level outlier ..... 6.2 ASCM / SDID
   │     ├─ messy: staggered + toggling ......... 6.3 Matrix Completion
   │     ├─ one treated TIME SERIES, no control . 6.4 Interrupted Time Series
   │     └─ one series + controls + seasonality . 6.5 CausalImpact (BSTS)
   │
   ├─ The SAME UNITS over TIME (panel), treatment toggles
   │     ├─ time-invariant confounders .......... Lecture 7  Fixed Effects (7.1)
   │     ├─ need static-var coefficients too .... 7.2 Mundlak (CRE)
   │     ├─ outcome depends on its own lag ...... 7.3 Arellano-Bond GMM
   │     └─ millions of sparse groups (CTR) ..... 7.4 Empirical Bayes
   │
   └─ NO design at all — but RICH COVARIATES (assume unconfoundedness)
        ├─ few covariates, want matched pairs ... Lecture 8  PSM (8.2)
        ├─ use all data, reweight ............... 8.3 IPW / overlap weights (ATO)
        ├─ want the safety net (default) ........ 8.4 AIPW (doubly robust)
        ├─ automated pipeline / exact balance ... 8.5 Entropy Balancing / CEM
        ├─ 500 nonlinear confounders ............ Lecture 9  DML (9.1)
        │     ├─ bounded outcome, extreme e(X) .. 9.4 TMLE
        │     └─ endogenous + high-dim .......... 9.3 DML-IV
        └─ you want to know WHOM to treat ....... Lecture 10  Heterogeneity & Uplift
              ├─ per-user CATE + valid CIs ...... 10.1 Causal Forests
              ├─ target the persuadables ........ 10.2 Uplift & Qini
              ├─ turn scores into IF/ELSE rules . 10.3 Policy Learning
              ├─ any ML → CATE (imbalanced?) .... 10.4 Meta-Learners (X-learner)
              └─ need uncertainty / small sample  10.5 BART / BCF

WANT TO SIMULATE A POLICY NEVER OBSERVED (a merger, a new product)?
   └─ ................................................ Lecture 14  Structural (BLP)
```

---

## Fast lookup — by the phrase the stakeholder uses

| They say… | You reach for | Lecture |
|---|---|---|
| "We A/B tested it" | RCT, but check SUTVA & attrition | [2.1](./02-experimentation/2.1-rct-and-assumptions.md) |
| "It's a social feature" | cluster on the interference graph | [2.3](./02-experimentation/2.3-cluster-randomization.md) |
| "Measure the TV/ad campaign" | geo experiment / iROAS (or CausalImpact) | [2.4](./02-experimentation/2.4-geo-experiments.md), [6.5](./06-synthetic-control/6.5-causalimpact-bsts.md) |
| "We rolled it out to some markets first" | DiD (staggered → not TWFE) | [3.1](./03-difference-in-differences/3.1-classic-did-and-geo-controls.md), [3.3](./03-difference-in-differences/3.3-staggered-did.md) |
| "Users qualify at a score threshold" | RDD (sharp/fuzzy) | [4.1](./04-regression-discontinuity/4.1-sharp-rdd.md), [4.2](./04-regression-discontinuity/4.2-fuzzy-rdd.md) |
| "It's opt-in / self-selected" | IV (encouragement), or selection-on-observables + sensitivity | [5.1](./05-instrumental-variables/5.1-standard-2sls.md), [8.1](./08-selection-on-observables/8.1-propensity-and-unconfoundedness.md) |
| "We launched in one big market (California)" | Synthetic Control / SDID | [6.1](./06-synthetic-control/6.1-classic-scm.md), [6.2](./06-synthetic-control/6.2-ascm-and-sdid.md) |
| "One national change, no control" | ITS (weak) → CausalImpact (with controls) | [6.4](./06-synthetic-control/6.4-interrupted-time-series.md), [6.5](./06-synthetic-control/6.5-causalimpact-bsts.md) |
| "We track users daily, feature toggles" | Fixed Effects (cluster the SEs!) | [7.1](./07-panel-data/7.1-fixed-effects.md) |
| "Habit-forming, short panel" | Arellano-Bond GMM (Nickell bias) | [7.3](./07-panel-data/7.3-dynamic-panel-gmm.md) |
| "CTR for a million sparse advertisers" | Empirical Bayes shrinkage | [7.4](./07-panel-data/7.4-empirical-bayes.md) |
| "We just have logs + lots of features" | AIPW / DML (doubly robust) | [8.4](./08-selection-on-observables/8.4-doubly-robust-aipw.md), [9.1](./09-double-machine-learning/9.1-dml-core.md) |
| "Whom should we target?" | causal forest / uplift / policy tree | [10.1](./10-heterogeneity-and-uplift/10.1-causal-forests.md)–[10.3](./10-heterogeneity-and-uplift/10.3-policy-learning.md) |
| "Prove it's robust to a hidden confounder" | Oster's δ / Cinelli-Hazlett / E-value | [11](./11-sensitivity-and-partial-id/) |
| "Why did it work — through what channel?" | causal mediation (with caution) | [12](./12-causal-mediation/) |
| "What would a MERGER do to prices?" | BLP + merger simulation | [14.2](./14-structural-estimation/14.2-supply-and-mergers.md) |

---

## The four questions to ask of *any* estimate (regardless of method)

From [Lecture 1](./01-foundations-and-estimands.md) and the through-lines of the
whole series — memorize these; they separate a junior write-up from a staff one:

1. **What is the estimand?** ATE / ATT / LATE / CATE / ACR / ATO — and is it the
   one the decision needs? (An estimate for the wrong population can flip a
   decision: [8.3](./08-selection-on-observables/8.3-inverse-probability-weighting.md)'s
   ATO, [1](./01-foundations-and-estimands.md)'s LATE-vs-ITT.)
2. **What is the identifying assumption, and what breaks it?** Parallel trends?
   Exclusion? Unconfoundedness? Overlap? Name it, and name the real-world thing
   that violates it.
3. **What's the falsification test, and does it pass?** Pre-trends, McCrary
   density, first-stage F, in-time placebo, covariate balance.
4. **How fragile is it?** Cluster the SEs at the right level; run a sensitivity
   analysis ([Lecture 11](./11-sensitivity-and-partial-id/)); report a bound if the
   assumptions are shaky.

---

## The one distinction that organizes everything

**Reduced-form vs. structural.** Lectures 1–13 estimate **the effect of something
that happened** — credible, but local to the observed variation. Lecture 14
estimates **the parameters of a model** so you can simulate something that
*hasn't* happened — powerful, but assumption-heavy.

If the policy you care about *occurred*, use the reduced-form tools (the top of
this tree) — they're more credible. Reach for structural only when you must
extrapolate to the unobserved: a merger, a new product, a price outside history.
Everything in this series is a different answer to the same question — **where
does the identifying variation come from?** — and the whole art is knowing which
source you actually have.

---

*(Planned: Lecture 13 — DAGs & Causal Discovery, for when you don't even know the
causal graph and must learn its structure from data.)*
