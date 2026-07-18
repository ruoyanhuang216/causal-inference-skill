# Lecture 6 — Synthetic Control & Counterfactual Estimators

> **Prerequisites:** [Lecture 3 — Difference-in-Differences](../03-difference-in-differences/) (parallel trends, geo-DiD, the DiD standard-error discussion). SCM is where geo-DiD goes when equal weighting isn't good enough.
> **Deepens:** [`industry-playbook/02-quasi-experimental.md`](../../industry-playbook/02-quasi-experimental.md).

DiD (Lecture 3) needs *many* treated units and *parallel* control trends. This
lecture is for the situation industry hits constantly instead: **one or a few
treated units — one launch market, one policy change — and controls that don't
move in parallel.** The answer is to *build* the counterfactual: find a
weighted combination of untreated units that reproduces the treated unit's
pre-treatment path, then measure the post-treatment gap. This lecture is that
idea and its three modern escalations.

---

## 1. The core idea

You launch in New York and hold back 40 other states. You can't compare New
York to the raw average of the 40 — New York has its own trajectory. So
**learn weights** on the donor states such that the weighted blend tracks New
York's pre-treatment path as closely as possible, freeze those weights, project
forward, and read the post-launch gap as the effect.

Everything in this lecture is a variation on that one move, differing in *how
they build the counterfactual when the simple version isn't enough*:

```
   Can a weighted average of donors reproduce the treated unit's pre-period?

   ┌─ YES, cleanly, one treated unit ──────────────► §6.1 Classic SCM
   │
   ├─ NO — treated unit is a LEVEL OUTLIER  ────────► §6.2 SDID (fixed effect
   │      (above every donor)                          absorbs the gap) or
   │                                                    ASCM (ridge extrapolates)
   │
   └─ NO — the rollout is CHAOTIC ─────────────────► §6.3 Matrix Completion
          (staggered, toggling, many treated)          (treat any treated cell
                                                        as missing, impute it)
```

The estimand throughout is the **ATT** — the effect on the treated unit(s) —
and, as always in this series, you must defend the counterfactual, because
it's the half of the comparison you never observe (Lecture 1 §2).

---

## 2. Chapters

| # | Chapter | Covers | Read when |
|---|---|---|---|
| **6.1** | [Classic Synthetic Control](./6.1-classic-scm.md) | The convex-hull optimization, the five steps, permutation inference, the RMSPE-ratio and leave-one-out diagnostics | Any single-treated-unit comparative case |
| **6.2** | [Augmented SCM & Synthetic DiD](./6.2-ascm-and-sdid.md) | When the treated unit is an outlier: ASCM (ridge extrapolation) vs. SDID (fixed-effect intercept shift + time weights) | Classic SCM's pre-fit is poor |
| **6.3** | [Matrix Completion](./6.3-matrix-completion.md) | Panel causal inference as a missing-data problem; handles staggered + toggling + many treated units | The rollout is too messy for SCM or DiD |

---

## 3. Through-lines

**You're always building the missing half of the comparison.** SCM, SDID, and
matrix completion are three ways to construct $Y(0)$ for treated units. The
whole game is a credible counterfactual, and every diagnostic (pre-fit, LOO,
placebo) interrogates *that*. §6.1 §3.

**The convex hull is a feature until it's a wall.** Non-negativity and
sum-to-one keep classic SCM interpretable and honest — it *can't* silently
extrapolate. But when the treated unit sits above every donor, that same
honesty becomes a flatline, and you escalate to SDID (subtract the gap) or ASCM
(extrapolate it). §6.2.

**Inference is by permutation, not standard errors.** One treated unit is one
cluster — cluster-robust SEs are undefined. You rank the treated unit's
post/pre RMSPE ratio against placebo units. This is the [Lecture 3 §3.4
few-clusters problem](../03-difference-in-differences/3.1-classic-did-and-geo-controls.md#34-the-catch-that-ties-the-lecture-together-few-clusters)
taken to its limit. §6.1 §4.

**Extrapolation vs. intercept shift is the key architectural choice.** A
baseline level gap should be *subtracted* (SDID's fixed effect), not
*extrapolated* (ASCM's ridge). Knowing which is which is the staff-level
distinction. §6.2 §4.

---

## 4. Relationship to the rest of the series

- **SDID is the bridge to [Lecture 3 (DiD)](../03-difference-in-differences/).**
  It literally runs SCM-weighted data through a two-way fixed-effects
  regression — the DiD engine — so it inherits DiD's tolerance for level
  differences.
- **Matrix Completion is the SCM-family cousin of [de Chaisemartin-
  D'Haultfœuille](../03-difference-in-differences/3.3-staggered-did.md)** —
  both handle *non-absorbing* (toggling) treatment that Callaway-Sant'Anna and
  classic SCM cannot.
- **CausalImpact** (the Bayesian structural time-series counterfactual) is the
  same "build a synthetic counterfactual" idea for a single treated *time
  series* with many candidate controls; it's introduced in [Lecture 2 §2.4
  (geo experiments)](../02-experimentation/2.4-geo-experiments.md#4-estimation)
  and belongs to this family.

---

## 5. References

- **Abadie, Diamond & Hainmueller (2010).** "Synthetic Control Methods for Comparative Case Studies." *JASA.* — The foundation (§6.1).
- **Ben-Michael, Feller & Rothstein (2021).** "The Augmented Synthetic Control Method." *JASA.* — ASCM (§6.2).
- **Arkhangelsky, Athey, Hirshberg, Imbens & Wager (2021).** "Synthetic Difference-in-Differences." *AER.* — SDID (§6.2).
- **Athey, Bayati, Doudchenko, Imbens & Khosravi (2021).** "Matrix Completion Methods for Causal Panel Data Models." *JASA.* — Matrix completion (§6.3).
- **Abadie (2021).** "Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects." *JEL.* — The definitive practitioner survey across the family.
