# Lecture 2 — Experimentation

> **Prerequisites:** [Lecture 1 — Foundations & Estimands](../01-foundations-and-estimands.md). This lecture assumes potential outcomes, SUTVA, and the ITT/LATE distinction.
> **Deepens:** [`industry-playbook/01-experiments-first.md`](../../industry-playbook/01-experiments-first.md).

Lecture 1 established that every causal method is a strategy for imputing
a missing counterfactual, and that the credibility of the method is the
credibility of the assumption doing the imputing. Randomization is the
one strategy where that assumption is *manufactured* rather than argued.
This lecture is about what that buys you, what it costs, and — mostly —
what to do when the simple version breaks.

---

## 1. The core philosophy

> **Run the simplest experiment that satisfies SUTVA without destroying
> statistical power.**

That sentence is the whole chapter. Both halves are load-bearing, and
they pull against each other:

- **SUTVA** (no interference between units) is what makes the estimand
  *exist*. Violate it and you are not estimating a noisy version of the
  right thing — you are estimating something that isn't defined. No
  sample size, no robustness check, and no clever estimator recovers
  from it. This is the §2.3 lesson of Lecture 1: SUTVA failure is a
  definition error, not an estimation error.
- **Power** is what makes the estimand *knowable*. An unbiased estimate
  with a confidence interval spanning every decision you might make is
  not an answer. It's an expensive way to say "we don't know."

Every design in this lecture is a trade between the two. Individual
randomization has the most power and the weakest SUTVA claim. Geo
randomization has the strongest SUTVA claim and almost no power. The job
is not to maximize either one. **It is to find the coarsest randomization
unit that seals the interference, and not one grain coarser.**

### The escalation ladder

When SUTVA breaks, you change *what you randomize*, and you always pay
for it in power:

```
  Randomize WHAT?            Seals which interference?        Power cost
  ────────────────────────────────────────────────────────────────────────
  Individual users     ──▶   none                             none      §2.1
        │                    (assumes isolation)
        │ interference via a social/interaction graph
        ▼
  Clusters of users    ──▶   direct network effects           Deff =
        │                    (within-cluster spillover)       1+(m−1)ρ  §2.3
        │ interference via a shared physical/market resource
        ▼
  Geographies          ──▶   marketplace + offline media      N ≈ 200
        │                    (supply, ad exposure)            units     §2.4
        │ can't split the market at all — one supply pool
        ▼
  Time blocks          ──▶   bipartite/shared-resource        N = #blocks,
                             interference within one market   carryover §2.5
```

Read it top-down and stop at the first row that seals your interference.
Most teams stop too late (over-clustering, then wondering why nothing is
ever significant) or too early (shipping a user-level A/B on a
marketplace and believing the number).

### The two interference structures

Knowing *which* kind you have tells you which row to jump to.

| | **Direct network interference** | **Bipartite / shared-resource interference** |
|---|---|---|
| **Mechanism** | Treating A changes A's behavior, which B observes | Treating A consumes a resource B needed |
| **Examples** | Social feed, messaging, multiplayer | Uber drivers, DoorDash couriers, ad budget, inventory |
| **Bias direction** | **Attenuation** — control contaminated toward treatment, effect looks *smaller* | **Exaggeration** — treatment cannibalizes control's supply, effect looks *larger* |
| **Fix** | Cluster on the interference graph (§2.3) | Randomize geos (§2.4) or time (§2.5) |

**The bias directions are opposite, and that is the most practically
useful fact in this lecture.** Network spillover makes you *under*-ship
good features. Marketplace cannibalization makes you *over*-ship bad
ones — the treatment arm's gains are partly stolen from control, so a
zero-sum reshuffle reads as a win. If you only remember one thing:
**a marketplace A/B test with a big positive result is the single most
dangerous artifact in industry experimentation**, because the bias and
the ambition point the same direction.

---

## 2. The chapters

| # | Chapter | Covers | Read when |
|---|---|---|---|
| **2.1** | [RCT & Assumptions](./2.1-rct-and-assumptions.md) | Why randomization works, balance tables, attrition, compliance, Lin (2013), A/A tests | Always — the baseline every other design degrades from |
| **2.2** | [Power & Multi-Arm](./2.2-power-and-multi-arm.md) | Sample size formula, the inverse-square law, MDE, FWER, Bonferroni, the runtime explosion | Before launching anything |
| **2.3** | [Cluster Randomization](./2.3-cluster-randomization.md) | ICC, design effect, natural vs. graph clusters, Louvain, exposure mapping | Direct network effects |
| **2.4** | [Geo Experiments & iROAS](./2.4-geo-experiments.md) | DMAs, bleed, buffer donuts, virtual DMAs, incrementality | Marketing spend, offline media, marketplaces |
| **2.5** | [Switchbacks](./2.5-switchbacks.md) | Time-slicing, carryover, washout math, optimal window derivation | Shared-resource interference in a single market |
| **2.6** | [Ramp-Up, Epoch-Conditioning & Bandits](./2.6-ramp-up-and-bandits.md) | Time-confounded ramps, Simpson's paradox, the golden rule, MAB lock-in | Any experiment whose traffic allocation changed mid-flight |

---

## 3. The checks that apply to every design

Four failure modes are design-independent. They belong here rather than
in any one chapter, because they will bite you in all of them.

### 3.1 Pre-experiment A/A tests

Run the analysis pipeline on two arms that receive *identical*
treatment. The estimated effect must be indistinguishable from zero, and
— more importantly — the **p-value distribution across many A/A tests
must be uniform on [0,1]**.

This is not a formality. An A/A test is the only end-to-end check of the
thing you cannot otherwise verify: that your randomization, logging,
assignment, and variance estimator are jointly correct. It catches
bucketing bugs (hash collisions, sticky assignment), logging skew
(treatment fires an extra event), and — most commonly —
**under-estimated variance**, where your SEs are too small because the
data are clustered and your estimator assumed independence.

A single A/A test that "passes" proves little; one test has a 5% chance
of a false positive by construction. **The uniformity of the p-value
distribution over many A/A splits is the real check**, and it is the
diagnostic that most directly answers "are my confidence intervals
honest?" See §2.3 for why clustered data breaks this in a way that looks
like everything is fine.

### 3.2 Sample Ratio Mismatch (SRM)

If you designed a 50/50 split and observe 50.4/49.6 on 1M users, the
experiment is **broken** — not "slightly off." At that sample size the
deviation is wildly beyond chance, and it means users were assigned
non-randomly. Chi-square test on observed vs. expected counts; if
p < 0.001, stop and debug rather than analyze.

SRM is the highest-value automated alert in an experimentation platform
because it is cheap, unambiguous, and catches the failure that destroys
everything downstream: **if assignment isn't random, no analysis on top
of it means anything.** The usual causes are redirect-based
implementations (the treatment redirect drops slow clients), bot
filtering that correlates with the treatment, or a broken hash.

### 3.3 Novelty and primacy effects

- **Novelty:** users engage with a change because it is *new*, not
  because it is *better*. Effect decays toward zero.
- **Primacy:** users are disrupted by a change and underperform until
  they relearn. Effect grows from negative.

Both mean **the day-1 read is not the steady-state effect**, and they
point in opposite directions, so you cannot correct with a rule of
thumb. The diagnostic: plot the effect by *days-since-first-exposure*
(not calendar date, which confounds with the ramp — see §2.6). A flat
line is a real effect. A decaying line is novelty. Segment by new vs.
existing users: novelty should be absent among users who never saw the
old version.

### 3.4 Post-treatment conditioning (the collider trap)

**Never segment experiment results by a variable measured after
treatment began.** Not by engagement, not by "users who saw the
feature," not by session count.

Conditioning on a post-treatment variable opens a collider path and
breaks randomization *inside the segments* — the treated and control
users within a segment are no longer comparable, even though the overall
experiment was perfectly randomized. This is the same error as Lecture
1's "just filter to compliers and compare them to control," and it is
the most common way a clean experiment produces a confidently wrong
subgroup finding.

Slice only on **pre-experiment covariates**: tenure, device, platform,
historical activity, acquisition channel. If you want the effect among
"engaged users," define engagement from the pre-period, freeze it before
launch, and put it in the analysis plan.

The one legitimate exception is **trigger analysis** — restricting to
users who *could have* been affected, based on a condition evaluable
identically in both arms (e.g. "users who reached the checkout page,"
where reaching checkout is upstream of the change). The test: could you
have computed this flag for a control user without knowing their
assignment? If no, it's post-treatment.

---

## 4. What this lecture is opinionated about

- **The randomization unit is a design decision, not an implementation
  detail.** It is chosen before the metric, before the power analysis,
  and it is the only decision that can make the estimand undefined.
- **Interference direction determines your prior.** Attenuation
  (networks) → your null result may be a real effect. Exaggeration
  (marketplaces) → your positive result may be zero-sum.
- **Prefer many small clusters to few large ones** — but only after
  confirming the small clusters actually seal the interference (§2.3).
- **A/A before A/B.** Always.
- **Never change the treatment:control ratio mid-experiment** (§2.6).
  Change total enrolled traffic freely; the ratio, never.

---

## 5. References

- **Gerber & Green (2012).** *Field Experiments: Design, Analysis, and Interpretation.* — The canonical text. Ch. 8 on interference.
- **Athey & Imbens (2017).** "The Econometrics of Randomized Experiments." *Handbook of Economic Field Experiments.*
- **Kohavi, Tang & Xu (2020).** *Trustworthy Online Controlled Experiments.* — The industry bible; SRM, A/A, novelty, and the practical failure modes of §3.
- **Aronow & Samii (2017).** "Estimating Average Causal Effects Under General Interference." *Annals of Applied Statistics* 11(4). — The exposure-mapping framework underlying §2.3.
- **Imbens & Rubin (2015).** Ch. 4–5 — randomization inference.
