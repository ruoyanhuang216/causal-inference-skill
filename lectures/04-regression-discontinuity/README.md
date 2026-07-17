# Lecture 4 — Regression Discontinuity Design

> **Prerequisites:** [Lecture 1 — Foundations & Estimands](../01-foundations-and-estimands.md) (potential outcomes, LATE, the complier typology). RDD's estimand *is* a LATE, and Fuzzy RDD *is* an IV, so Lecture 1 §4–6 is load-bearing here.
> **Deepens:** [`industry-playbook/02-quasi-experimental.md`](../../industry-playbook/02-quasi-experimental.md).

Every product has arbitrary thresholds. Credit approved at a score of 650.
A bonus at 50 rides. A shadowban at spam-score 80. Free shipping over \$35.
Each of these is a **natural experiment hiding in a business rule** — and
regression discontinuity is how you extract it. RDD is the closest thing
observational data offers to a randomized experiment, and it comes with the
narrowest estimand in the book. This lecture is about that trade.

---

## 1. The core idea

A user who scores **649** on a credit check is, for all practical purposes,
identical to one who scores **650**. Nobody is meaningfully more
creditworthy for a single point. Yet if the approval rule is "approve at
650," the 650 gets a loan and the 649 doesn't. The cutoff is *arbitrary*, so
**right at the threshold, treatment is as good as randomly assigned.**

That is the entire idea. Compare units just above the cutoff to units just
below it, and you have something that behaves like a local randomized
experiment — one the business ran for you, for free, by writing a rule.

```
   Outcome Y
      │                                          ●  ← treated side
      │                                    ● ●
      │                              ● ●          }  τ = the jump at the cutoff
      │                        ● ●   ─────────────    (the causal effect)
      │                  ● ●  ↑
      │            ● ●        the discontinuity
      │      ● ●
      │  ● ●   ← control side
      └──────────────────────┼───────────────────────  running variable X
                          cutoff c
```

The causal effect is the **vertical jump** in the outcome exactly at the
cutoff. Everything smooth is confounding to be differenced away; the only
thing allowed to jump is the treatment.

---

## 2. The one assumption, and the one thing that breaks it

**Continuity of potential outcomes at the cutoff.** Absent treatment, the
expected outcome $E[Y(0) \mid X]$ would be a *smooth, continuous* function
through the cutoff. The only thing permitted to jump at $c$ is the treatment
itself.

```math
\lim_{x \uparrow c} E[Y(0) \mid X = x] = \lim_{x \downarrow c} E[Y(0) \mid X = x]
```

Continuity itself is untestable — it's a claim about the unobserved $Y(0)$
on the treated side. But it has one concrete enemy you *can* detect:

**No manipulation (no sorting).** If units can *precisely control* which side
of the cutoff they land on, the people just above and just below are no
longer comparable — they differ in whatever trait drove them to sort. A
driver who forces two extra rides to hit a 50-ride bonus is not the same as
one who happened to stop at 49; the first is a "hustler" and the second a
"casual," and **an unobserved confounder (motivation) has jumped at the
cutoff.** Continuity is dead.

This is the pivot of the whole lecture: **the assumption is continuity, the
failure mode is sorting, and the test is a density check** (McCrary). When
you can detect a pile-up of units on the favorable side, you've caught the
one violation RDD can't survive.

---

## 3. The estimand: a LATE, and a narrow one

**RDD does not estimate the ATE.** It estimates a **LATE at the cutoff** —
the effect for units *right at the threshold*, and nobody else:

```math
\tau_{\text{RDD}} = \lim_{x \downarrow c} E[Y \mid X = x] - \lim_{x \uparrow c} E[Y \mid X = x]
```

You learn the effect of the loan for people at a 650 credit score. You learn
**nothing** about it for someone at 750 or 550. This is the same
external-validity limit as Lecture 1's LATE, and it's the standard interview
trap: *"who is this effect for?"* The answer is always "the marginal unit at
the threshold," never "everyone."

This narrowness is the price of RDD's credibility. It buys the cleanest
identification in observational work — local randomization — by restricting
the claim to an infinitesimally thin slice of the population. Internal
validity, purchased with external validity.

---

## 4. The family: one comparison, four disguises

Every RDD variant is the *same* difference-of-limits at a threshold. They
differ only in what jumps and what you divide by:

```
                    │ What jumps at the cutoff?         │ Estimand
  ──────────────────┼───────────────────────────────────┼─────────────────────
   Sharp   (§4.1)   │ treatment goes 0 → 1 (a level)    │ jump in Y
   Fuzzy   (§4.2)   │ treatment PROBABILITY jumps        │ jump in Y ÷ jump in P(D)
                    │   (e.g. 0.2 → 0.8)                 │   = a local Wald / LATE
   Kink    (§4.3)   │ the SLOPE of treatment changes     │ jump in slope(Y)
                    │   (a kink, not a jump)             │   ÷ jump in slope(policy)
   Geographic(§4.4) │ treatment changes across a 2D      │ jump in Y across the
                    │   spatial BORDER                   │   boundary
```

- **Sharp** — the cutoff deterministically flips treatment. Jump in the
  outcome *is* the effect.
- **Fuzzy** — the cutoff only *shifts the probability* of treatment.
  Crossing the cutoff becomes an **instrument** for treatment, and the
  estimand is a Wald ratio — Lecture 1's LATE, localized to the cutoff.
- **Kink** — treatment *intensity* changes slope at the cutoff (a benefit
  formula that caps out). You compare the change in the outcome's slope to
  the change in the policy's slope.
- **Geographic** — the cutoff is a border on a map; the running variable is
  distance to it, and the geometry is 2D.

---

## 5. Chapters

| # | Chapter | Covers | Read when |
|---|---|---|---|
| **4.1** | [Sharp RDD](./4.1-sharp-rdd.md) | Local randomization, the `X−c` centering, local linear regression, bandwidth & kernel, the four diagnostics, the driver-bonus manipulation probe | Every RDD starts here |
| **4.2** | [Fuzzy RDD](./4.2-fuzzy-rdd.md) | The cutoff as an instrument; local Wald / 2SLS; weak-instrument F; the compliance types *at the cutoff*; the shadowban probe | Treatment take-up is imperfect at the cutoff |
| **4.3** | [Regression Kink Design](./4.3-regression-kink.md) | Level vs. slope; ratio of slope-changes; local quadratic; the FinTech credit-cap probe | The policy changes *slope*, not level |
| **4.4** | [Geographic RD](./4.4-geographic-rd.md) | Borders as cutoffs; distance-to-boundary; 2D estimation; spatial placebo borders; the Roblox probe | The cutoff is a line on a map |

---

## 6. Through-lines

**Cleanest identification, narrowest estimand.** RDD gives you a
quasi-experiment from a business rule — but only for the marginal unit at
the threshold. Never report it as the ATE. §3.

**One assumption (continuity), one detectable enemy (sorting).** Continuity
is untestable, but manipulation of the running variable is not — the density
test catches it. When units sort, an unobserved confounder jumps at the
cutoff, and no amount of local-linear machinery repairs it. §2.

**Every variant is a difference of limits at a threshold.** Sharp, fuzzy,
kink, geographic — same skeleton, different numerator and denominator. Learn
the sharp case cold and the rest are specializations. §4.

**Bandwidth is the bias-variance tradeoff made visible.** Wide windows pull
in far-away, differently-shaped units (bias); narrow windows starve you of
data (variance). Don't guess it — use an MSE-optimal rule (CCT) and *show
the sensitivity curve*. §4.1.

---

## 7. References

- **Cattaneo, Idrobo & Titiunik (2020).** *A Practical Introduction to Regression Discontinuity Designs* (2 vols., Cambridge Elements). — The definitive modern practitioner guide; everything in this lecture, done rigorously.
- **Imbens & Lemieux (2008).** "Regression Discontinuity Designs: A Guide to Practice." *Journal of Econometrics.* — The classic how-to.
- **Lee & Lemieux (2010).** "Regression Discontinuity Designs in Economics." *Journal of Economic Literature.* — The other classic; strong on the local-randomization interpretation.
- **Calonico, Cattaneo & Titiunik (2014).** "Robust Nonparametric Confidence Intervals for Regression-Discontinuity Designs." *Econometrica.* — MSE-optimal bandwidth and bias-corrected inference (the `rdrobust` package).
- **Cunningham (2021).** *Causal Inference: The Mixtape*, Ch. 6. — The most readable book-length RDD intro.
