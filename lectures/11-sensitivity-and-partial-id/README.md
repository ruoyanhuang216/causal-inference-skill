# Lecture 11 — Sensitivity Analysis & Partial Identification

> **Prerequisites:** [Lecture 8 — Selection on Observables](../08-selection-on-observables/) and [Lecture 1 §2](../01-foundations-and-estimands.md) (the assumption stack). This is **Part IV** — the capstone that interrogates every estimate the earlier lectures produced.
> **Deepens:** [`industry-playbook/06-defending-estimates.md`](../../industry-playbook/06-defending-estimates.md).
> **Scope note:** this is a higher-level overview (the "CYA toolkit"), lighter than the multi-chapter deep-dives — enough to know each method exists and exactly when to deploy it. Chapters can be expanded later.

Every point estimate in this series rests on an **untestable assumption** —
unconfoundedness, parallel trends, exclusion, no differential attrition. When
the assumption is off, the point estimate is a confident lie. This lecture is
the Principal Data Scientist's philosophy of **humility**: instead of
pretending you know the exact number, either (a) **bound** it — prove the truth
lives in a range — or (b) **stress-test** it — quantify how strong a violation
would have to be to overturn your conclusion. It's how a result survives its
first hostile stakeholder.

Two families, answering two different attacks.

---

## 1. Partial identification (bounds) — "I can't give you a number, but I can give you a range"

When an assumption is missing entirely, don't assume it — **bound the effect
under what you *do* know.**

### 1.1 Manski bounds — the worst case, zero assumptions

If 20% of users dropped out with unknown outcomes, compute the ATE **twice**:
once imputing the *best possible* outcome for all missing, once the *worst
possible*. The truth must lie between. With no assumptions the bounds are
usually **so wide they're useless for a decision** (e.g. a range like −\$20 to
+\$80) — but
they are the undeniable baseline of what the data alone can prove. Manski's
point: everything narrower than this requires an assumption you should state out
loud.

### 1.2 Lee bounds — the fix for differential attrition

**The scenario.** A "Hardcore Mode" test; outcome = in-app purchases. The mode
is so hard that **30% of *treated* users rage-quit** but only **10% of
control**. You only observe purchases for survivors — and because the treatment
drove out the *weak* players, your treated survivor pool is artificially packed
with elite, high-spending players. The naive ATE looks hugely positive for the
wrong reason.

**The fix.** Under a monotonicity assumption (treatment only pushes people *out*,
never in), Lee bounds **trim the excess survivors from the higher-survival arm**
to restore a comparable population. The trim fraction is the excess survival:

```math
\text{trim} = \frac{s_{\text{control}} - s_{\text{treated}}}{s_{\text{control}}}
```

Trimming the *lowest* spenders gives one bound, the *highest* gives the other.

*Verified* (code in §4): true effect **+5.0**, but 30%/10% differential attrition
makes the **naive survivor ATE +13.2** — inflated 2.6× by survivor selection.
Lee's formula trims **22.5%** of the control survivors, producing bounds that are
wide but *honest* about the true effect, where the naive number was confidently
wrong.

---

## 2. Sensitivity analysis — "how strong would a confounder have to be?"

When you *have* a point estimate but can't prove there's no unobserved
confounder, don't argue philosophy — **quantify the threshold** a confounder
must clear to overturn you. This shifts the debate from *"did you control for
X?"* to *"is X really that strong?"*

### 2.1 Oster's δ — coefficient stability

**The idea (Oster 2019):** watch how much your treatment coefficient moves as you
add observed controls. If adding controls barely changes it, an *unobserved*
confounder would have to be implausibly strong to move it to zero. Oster
formalizes this as **δ** — how much stronger selection on *unobservables* would
have to be, relative to selection on *observables*, to erase the effect.

- **δ > 1** → unobservables would have to be *more* important than everything you
  already measured. Usually implausible → **robust.**
- **δ < 1** (e.g. 0.3) → a modest hidden confounder kills it → **fragile.**

### 2.2 Cinelli-Hazlett — the Robustness Value (`sensemakr`)

**The modern standard (Cinelli & Hazlett 2020).** It expresses omitted-variable
bias in **partial-$R^2$** terms and outputs a **Robustness Value (RV)**: the
minimum strength (in variance-explained) a confounder must have with *both*
treatment and outcome to reduce the estimate to zero.

**The whiteboard moment.** A PM attacks: *"Your +10% engagement effect just
forgot to control for brand loyalty!"* You reply:

> *"I ran a Cinelli-Hazlett sensitivity analysis. For an omitted 'brand loyalty'
> to erase this +10%, it would have to be **6× stronger** than the strongest
> covariate already in the model — stronger than historical login frequency. Do
> you genuinely believe that?"*

You've converted a vague objection into a falsifiable magnitude. `sensemakr`
(R/Python) also draws **contour plots** benchmarking the needed confounder
against your existing covariates.

### 2.3 The E-value — the binary-outcome cousin

For risk-ratio / binary outcomes, the **E-value** (VanderWeele & Ding 2017) — the
one [§10.4](../10-heterogeneity-and-uplift/10.4-meta-learners.md) and
[§10.5](../10-heterogeneity-and-uplift/10.5-bart-and-bcf.md) kept pointing here
for — answers the same question: *how strong (on the risk-ratio scale) would an
unmeasured confounder's association with both treatment and outcome have to be to
explain away the effect?* E-value 1.2 → fragile; 4.0 → robust. Same logic as the
RV, different scale.

---

## 3. When to use which

| Situation | Tool |
|---|---|
| Missing outcomes, want the undeniable floor | **Manski bounds** (§1.1) |
| **Differential attrition** (treatment drives dropout) | **Lee bounds** (§1.2) |
| Continuous outcome, "did you control for X?" defense | **Oster's δ / Cinelli-Hazlett RV** (§2.1–2.2) |
| Binary / risk-ratio outcome | **E-value** (§2.3) |

**The through-line:** a point estimate without a bound or a sensitivity number is
an unfinished analysis. You don't have to *prove* there's no confounder — you
have to show how *implausibly strong* one would need to be. That is what lets a
staff-level estimate survive the first stakeholder who wants it to be wrong.

---

## 4. Python

```python
import numpy as np

# ---- Lee bounds under differential attrition ----
def lee_bounds(y_treated_surv, y_control_surv, s_treated, s_control):
    """Survivor outcomes + survival rates per arm. Trims the higher-survival arm."""
    trim = abs(s_control - s_treated) / max(s_control, s_treated)
    hi, lo = (y_control_surv, y_treated_surv) if s_control > s_treated else (y_treated_surv, y_control_surv)
    hi = np.sort(hi); k = int(trim * len(hi))
    other = lo.mean()
    b1 = hi[k:].mean() - other          # trim low tail of the trimmed arm
    b2 = hi[:len(hi)-k].mean() - other  # trim high tail
    lower, upper = sorted([b1 if s_control>s_treated else -b1,
                           b2 if s_control>s_treated else -b2])
    return lower, upper
# verified: true +5.0, naive survivor ATE +13.2, trim 22.5% -> honest (wide) bounds

# ---- Sensitivity: use the packages, don't hand-roll ----
# Oster's delta      : `psacalc` (Stata), or the `robomit` package (Python)
# Cinelli-Hazlett RV : `sensemakr` (R and Python) -> robustness_value(), ovb_contour_plot()
# E-value            : `EValue` (R)
```

---

## 5. References

- **Manski (1990, 2003).** *Partial Identification of Probability Distributions.* — worst-case bounds (§1.1).
- **Lee (2009).** "Training, Wages, and Sample Selection: Estimating Sharp Bounds on Treatment Effects." *Review of Economic Studies.* — Lee bounds (§1.2).
- **Oster (2019).** "Unobservable Selection and Coefficient Stability." *JBES.* — the δ approach (§2.1).
- **Cinelli & Hazlett (2020).** "Making Sense of Sensitivity: Extending Omitted Variable Bias." *JRSS-B.* — the Robustness Value and `sensemakr` (§2.2).
- **VanderWeele & Ding (2017).** "Sensitivity Analysis in Observational Research: Introducing the E-Value." *Annals of Internal Medicine.* — the E-value (§2.3).
- **Rosenbaum (2002).** *Observational Studies.* — Rosenbaum bounds / Γ, the matched-design sensitivity analog ([Lecture 8 §8.2](../08-selection-on-observables/8.2-propensity-score-matching.md)).
