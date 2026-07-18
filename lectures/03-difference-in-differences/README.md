# Lecture 3 — Difference-in-Differences

> **Prerequisites:** [Lecture 1 — Foundations & Estimands](../01-foundations-and-estimands.md) (potential outcomes, ATT, SUTVA). Helpful: [Lecture 2 §2.4 — Geo Experiments](../02-experimentation/2.4-geo-experiments.md), since DiD is what you reach for when you *can't* randomize the geos.
> **Deepens:** [`industry-playbook/02-quasi-experimental.md`](../../industry-playbook/02-quasi-experimental.md).

Lecture 2 was about experiments you run. This one is about the far more
common industry situation: **the feature already launched in one market
and not another, and nobody randomized anything.** DiD is the workhorse
of quasi-experimental causal inference — you launch in New York, hold
back Chicago, and difference your way to an effect. It is also the method
people most often run as a magic wand: fit the regression, read the
interaction coefficient, ship. This lecture is about why that
coefficient is trustworthy exactly when one untestable assumption holds,
and what the modern literature discovered when it stopped holding.

---

## 1. The core idea

You launch a driver-incentive program in Miami and not Orlando. You
cannot compare Miami's rides to Orlando's — Miami is a bigger, different
market. That's the **level** difference, and it's confounded by
everything that makes the two cities different.

DiD's move: compare the **change**. Difference each city against its own
past (killing everything time-invariant about the city — its size, its
baseline demand, its geography), then difference the two changes against
each other (killing anything that moved *both* cities — a national
holiday, a gas-price shock, a summer bump everywhere). What survives both
differences is the treatment effect.

```
                    Pre-period      Post-period      Change (Δ)
  Treatment (Miami)    Y_T0     →      Y_T1          Y_T1 − Y_T0
  Control   (Orlando)  Y_C0     →      Y_C1          Y_C1 − Y_C0
                                                     ─────────────
  DiD = (Y_T1 − Y_T0) − (Y_C1 − Y_C0)    ← difference of the differences
```

- **First difference** (down the columns) removes each unit's fixed,
  time-invariant level. Miami being bigger than Orlando drops out.
- **Second difference** (across the rows) removes the common time trend.
  A summer bump that hits both cities drops out.

What's left is the change in Miami *above and beyond* what Orlando did.
The estimand is the **ATT** (Lecture 1 §4) — the effect on the treated
units, not the whole population, because we only learn what treatment did
*to Miami*.

---

## 2. The one assumption everything rests on

**Parallel trends:** absent the treatment, Miami and Orlando would have
changed *by the same amount*. Not been at the same level — changed by the
same amount.

```math
E[Y_{i,1}(0) - Y_{i,0}(0) \mid \text{Treated}] = E[Y_{i,1}(0) - Y_{i,0}(0) \mid \text{Control}]
```

Read the counterfactual carefully: it's about $Y(0)$ — what Miami *would
have done untreated*. That is never observed. **Parallel trends is a
claim about a world that didn't happen, so it is fundamentally
untestable.** This is the entire drama of DiD, and it's Lecture 1's
"counterfactual is missing by construction" wearing a panel-data suit.

Three things follow, and they organize the whole lecture:

1. **You can't test it, so you triangulate it.** Pre-trends, placebos,
   and event studies each check a *consequence* of parallel trends, never
   the thing itself. Passing them is necessary, not sufficient (§4).
2. **Pre-trends ≠ parallel trends** (Roth 2022). Flat pre-treatment
   coefficients are reassuring, but low-powered pre-trend tests routinely
   fail to detect the very violations that would bias you most. "Pre-trends
   look fine" is the beginning of the defense, not the end.
3. **The assumption is scale-dependent.** Parallel trends in levels is
   *not* parallel trends in logs. If it holds for $Y$ it generally fails
   for $\log Y$, and vice versa. You are choosing a functional form when
   you choose the outcome, and the choice is an identifying assumption,
   not a formatting decision.

The supporting assumptions — **no anticipation** (units don't react
before treatment), **stable composition** (the groups don't change who's
in them differentially), and **SUTVA** (no spillover from treated to
control) — are each a way parallel trends can be quietly false.

---

## 3. The map

DiD has two independent axes of difficulty. Almost every mistake in the
field is misjudging which cell you're in.

```
                     │  Parallel trends plausible?
                     │
   ──────────────────┼──────────────────────────────────────────────
    One treatment    │  YES → §3.1 Classic 2×2 / Geo-DiD
    time (sharp)     │  NO  → §3.2 Synthetic Control (weight controls
                     │        until pre-trends are forced parallel)
                     │        ...or §3.4 DDD (difference out the shock)
   ──────────────────┼──────────────────────────────────────────────
    Staggered        │  The TWFE regression you'd reflexively run is
    adoption         │  BIASED and can flip signs → §3.3 (the trap AND
    (many times)     │  the modern estimators that fix it)
```

**The horizontal axis is about credibility; the vertical axis is about
timing, and it is the one that surprises people.** A classic 2×2 with a
believable control is one of the safest designs in causal inference.
Adding *variation in treatment timing* — the thing that looks like
"just more data" — silently breaks the standard estimator, because
two-way fixed effects starts using already-treated units as controls.
That discovery (Goodman-Bacon 2021 and the wave after it) is the single
biggest development in applied econometrics of the last decade, and §3.3 is
entirely about it.

---

## 4. Chapters

| # | Chapter | Covers | Read when |
|---|---|---|---|
| **3.1** | [Classic 2×2 & Geo-Controls](./3.1-classic-did-and-geo-controls.md) | The regression, coefficient-by-coefficient; event studies; placebos; the Miami/Orlando trap | Every DiD starts here |
| **3.2** | [Synthetic Control](./3.2-synthetic-control.md) *(bridge)* | The weighted-control idea in one screen; full treatment (ASCM, SDID, matrix completion, inference) in [Lecture 6](../06-synthetic-control/) | Single treated market, skeptical control |
| **3.3** | [Staggered DiD: The TWFE Trap and Its Fixes](./3.3-staggered-did.md) | Goodman-Bacon's four comparisons and the forbidden one; negative weights; the verified sign-flip; then the full estimator zoo (CS, Wooldridge ETWFE, Sun-Abraham, de Chaisemartin-D'Haultfœuille, Borusyak et al., Gardner) with a use-case-first selection guide | Any rollout with variation in timing |
| **3.4** | [Triple Differences](./3.4-triple-differences.md) | DDD: difference out a confounding shock with a second control dimension; the parallel-DiD assumption | Parallel trends implausible, but you have an eligibility split |

---

## 5. Through-lines

**Every diagnostic tests a proxy, never the assumption.** Parallel trends
is about an unobserved counterfactual. Pre-trends, placebos, and event
studies are necessary consequences of it — passing them cannot prove it,
and (Roth 2022) failing to reject them is weak evidence at realistic
power. Report them as a *defense*, never a *proof*.

**The danger is timing variation, not sample size.** A 2×2 is safe.
"We have 300 markets adopting over 3 years" feels like more power and is
actually a minefield, because TWFE turns already-treated units into
controls (§3.3). The instinct that more data is safer is exactly backwards
here.

**Every estimator answers one question: what is a clean control?** Classic
DiD says "the untreated group." Synthetic control says "a weighted blend
that matches pre-trends." Callaway-Sant'Anna says "never-treated or
not-yet-treated, never already-treated." Imputation says "the untreated
cells, extrapolated." Naming that answer *is* choosing the method.

**Each added difference relaxes one assumption and demands a new one.**
Levels-comparable → trends-comparable (DiD) → differential-trends-comparable
(DDD). Every layer buys robustness to one class of confounder and costs
you a data dimension and a subtler assumption to defend.

---

## 6. References

- **Roth, Sant'Anna, Bilinski & Poe (2023).** "What's Trending in Difference-in-Differences? A Synthesis of the Recent Econometrics Literature." *Journal of Econometrics.* — The one survey to read; maps the entire modern landscape §3.3 covers.
- **Roth (2022).** "Pretest with Caution: Event-Study Estimates After Testing for Parallel Trends." *AER: Insights.* — Why pre-trends ≠ parallel trends (§2).
- **Goodman-Bacon (2021).** "Difference-in-Differences with Variation in Treatment Timing." *Journal of Econometrics.* — The decomposition that started §3.3.
- **Callaway & Sant'Anna (2021).** "Difference-in-Differences with Multiple Time Periods." *Journal of Econometrics.*
- **Abadie, Diamond & Hainmueller (2010).** "Synthetic Control Methods for Comparative Case Studies." *JASA.*
- **Cunningham (2021).** *Causal Inference: The Mixtape*, Ch. 9. — The most readable book-length DiD treatment.
- **Angrist & Pischke (2009).** *Mostly Harmless Econometrics*, Ch. 5.
