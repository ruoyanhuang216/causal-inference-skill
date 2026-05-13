# 00. Foundations

The shared vocabulary. Read this once; the rest of the playbook
assumes it.

---

## Potential outcomes

For unit `i` and binary treatment `T_i ∈ {0, 1}`:

```
Y_i  =  T_i · Y_i(1)  +  (1 − T_i) · Y_i(0)
```

You only ever observe one of `{Y_i(1), Y_i(0)}` for any unit. The
other is the **counterfactual**. Every causal estimator is a strategy
for filling in the missing one.

---

## The six estimands

Different methods estimate different things. Naming the right one is
half the staff-level interview.

| Estimand | Definition | Industry use case |
| --- | --- | --- |
| **ATE** | `E[Y(1) − Y(0)]` | Population-level decision: "should we ship to everyone?" |
| **ATT** | `E[Y(1) − Y(0) \| T = 1]` | Effect on those treated — most policy evaluations |
| **CATE** | `τ(x) = E[Y(1) − Y(0) \| X = x]` | Targeting / personalization |
| **LATE** | `E[Y(1) − Y(0) \| compliers]` | IV designs and fuzzy RDD (effect on the people whose treatment status responds to the instrument) |
| **ITT** | `E[Y \| assigned] − E[Y \| not assigned]` | RCT primary readout under non-compliance |
| **CACE** | LATE for the compliant subpopulation | RCT with imperfect take-up; equivalent to LATE |

**Naming-the-estimand rule:** if you can't say which of these your
stakeholder cares about, the analysis isn't ready. ATE vs. CATE
matters when you have a budget; LATE vs. ATE matters when you
generalize beyond compliers.

---

## The assumption stack

Every method rests on one or more of these. Knowing *which* assumption
your method needs is the difference between "ran the model" and
"defended the estimate."

| Assumption | What it says | Needed by |
| --- | --- | --- |
| **SUTVA** | One unit's outcome doesn't depend on another's treatment | Almost everything; explicitly violated in marketplaces and networks |
| **Ignorability / unconfoundedness** | `{Y(1), Y(0)} ⊥ T \| X` | Matching, IPW, DML, causal forests |
| **Overlap / positivity** | `0 < P(T=1 \| X) < 1` for all `X` | Same as above; fails at the propensity tails |
| **Parallel trends** | Treated and control would have moved in parallel absent treatment | DiD family |
| **Continuity at the cutoff** | `E[Y(0) \| X = c]` continuous at the cutoff | RDD |
| **Exclusion restriction** | Instrument affects `Y` only through `T` | IV, fuzzy RDD |
| **Monotonicity** | No "defiers" (units that take treatment iff ineligible) | IV-based LATE estimation |

Identification is choosing the assumption you're willing to defend.
There's no assumption-free causal inference.

---

## When OLS captures the causal effect

`β` from `Y = α + βT + γX + ε` is the causal effect of `T` on `Y` when:

1. Unconfoundedness holds given `X`, AND
2. The functional form `γX` correctly captures confounding (no
   nonlinear interactions missed).

Most modern methods relax (2) by using flexible ML for nuisance
estimation (Section 3) or relax (1) by exploiting design (Section 1,
Section 2).

---

## The four-question sanity framework

Apply this to every causal estimate before reporting it. The
methodology section isn't done until all four are answered.

1. **What is the identifying assumption?** (parallel trends?
   ignorability? continuity? exclusion?) What does the real-world DGP
   do to that assumption?
2. **What is the falsification test?** (pre-trends? McCrary?
   placebo treatments?) Does it pass?
3. **What is the magnitude of bias** if the assumption is off by a
   realistic amount? (Run a sensitivity analysis — see §6.)
4. **What is the estimand** you're reporting (ATE / ATT / LATE /
   CATE), and is it the right one for the decision the stakeholder
   is making?

This framework is what separates a junior write-up from a staff one.
Memorize it.

---

## Vocabulary you should never mix up

- **Effect vs. estimand vs. estimator.** *Effect* = the thing in the
  world. *Estimand* = the population quantity you're targeting
  (ATE, CATE, etc.). *Estimator* = the procedure that produces a
  number (OLS, DML, causal forest).
- **Bias vs. variance.** Bias = systematic offset from the true
  effect. Variance = how much the estimate would change on a new
  sample.
- **Identification vs. estimation.** *Identification* = can the
  effect be recovered from infinite data under your assumptions?
  *Estimation* = how do you recover it from finite data?
- **ITT vs. CACE.** ITT measures the effect of *being assigned* to
  treatment regardless of compliance. CACE / LATE measures the
  effect on those who actually complied. ITT is what ships; CACE
  is what the mechanism is.
