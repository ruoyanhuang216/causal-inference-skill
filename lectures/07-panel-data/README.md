# Lecture 7 — Panel Data Methods

> **Prerequisites:** [Lecture 1](../01-foundations-and-estimands.md), and [Lecture 3 — Difference-in-Differences](../03-difference-in-differences/) (DiD *is* a panel FE method; the standard-error and staggered-treatment discussions carry straight over).
> **Deepens:** [`industry-playbook/`](../../industry-playbook/).

You have the same units observed **over time** — 100,000 users across 30 days,
1M advertisers across their whole history. That repeated structure is a gift:
each unit becomes **its own control.** Subtract a user from their own historical
baseline and every fixed, unobservable thing about them — intelligence, brand
loyalty, socioeconomic status — cancels to zero, for free, without ever
measuring it. This lecture is the panel toolkit that exploits that, and the ways
it breaks.

This chapter also **closes Part II** (comparative-case & panel): where synthetic
control (Lecture 6) built a counterfactual for *one* treated unit, panel methods
use *every* unit's own history as its counterfactual.

---

## 1. The core idea — each unit is its own control

The panel model:

```math
Y_{it} = \alpha_i + \beta X_{it} + \epsilon_{it}
```

$\alpha_i$ is the unit's **time-invariant unobserved confounder** — everything
stable and unmeasured about user $i$. The moment $\alpha_i$ correlates with the
treatment $X_{it}$ (power users adopt the feature *and* engage more), a
cross-sectional comparison is hopelessly confounded.

The **within-transformation** disposes of it. Average each unit over time, then
subtract:

```math
(Y_{it} - \bar Y_i) = \beta\,(X_{it} - \bar X_i) + (\epsilon_{it} - \bar\epsilon_i)
```

$\alpha_i - \alpha_i = 0$. **The confounder is gone** — not modeled, not
measured, *differenced away*. What's left is pure within-unit variation: "on days
this user was above their *own* average treatment, was their outcome above their
*own* average?" That's the causal question, stripped of every stable
between-user difference.

---

## 2. The four methods, and what each fixes

Each method patches a failure of the one before:

```
   Fixed Effects (§7.1) ──── kills TIME-INVARIANT confounders (within)
        │
        │ "but FE destroys my time-invariant variables (gender, OS)!"
        ▼
   Mundlak / CRE (§7.2) ──── recover FE's beta AND keep static coefficients
        │
        │ "but my outcome depends on its own lag (habit)!"
        ▼
   Arellano-Bond GMM (§7.3) ── fix Nickell bias with first-diff + lag instruments
        │
        │ "but I have millions of tiny groups (advertisers)!"
        ▼
   Empirical Bayes (§7.4) ──── adaptive shrinkage by each group's own sample size
```

| # | Chapter | Fixes | Read when |
|---|---|---|---|
| **7.1** | [Fixed Effects](./7.1-fixed-effects.md) | time-invariant confounding | treatment toggles on/off within a unit over time |
| **7.2** | [Correlated Random Effects (Mundlak)](./7.2-correlated-random-effects.md) | FE erases static variables | you need FE's β *and* coefficients on gender/OS/cohort |
| **7.3** | [Dynamic Panel GMM (Arellano-Bond)](./7.3-dynamic-panel-gmm.md) | Nickell bias from lagged $Y$ | the outcome is habit-forming; short panel (big $N$, small $T$) |
| **7.4** | [Empirical Bayes / Partial Pooling](./7.4-empirical-bayes.md) | small-sample noise across many groups | estimating a rate for millions of sparse groups |

---

## 3. Through-lines

**The within-transformation is free, but only for *time-invariant* confounders.**
It cancels anything stable about a unit — and *nothing* that varies over time. A
confounder that moves with the treatment (a motivation spike the week someone
subscribes) survives untouched. FE is not a cure for confounding; it's a cure for
*stable* confounding. §7.1.

**FE and Mundlak give the identical β.** Mundlak just adds each unit's *group
mean* $\bar X_i$ as a control — and the treatment coefficient comes out *exactly*
equal to FE (verified to machine precision), while you also recover the
time-invariant coefficients FE destroyed. It's FE without the amnesia. §7.2.

**A lagged dependent variable breaks FE.** When $Y_t$ depends on $Y_{t-1}$, the
within-transformation correlates the lag with the error (**Nickell bias**), and
it's severe when $T$ is small. First-difference and instrument the lag with
deeper lags (Arellano-Bond). §7.3.

**Cluster your standard errors at the unit.** The same unit over time has
serially-correlated errors; naive OLS SEs are far too narrow. This is the
*identical* clustering lesson as [Lecture 3 §3.1](../03-difference-in-differences/3.1-classic-did-and-geo-controls.md#3-inference-the-standard-error-is-where-did-dies)
— DiD is a panel FE method, so it inherits the same rule. §7.1.

**Relationship to DiD.** Two-way fixed effects (unit + time) *is* the DiD
estimator ([Lecture 3](../03-difference-in-differences/)). Everything there about
staggered treatment and the TWFE trap ([§3.3](../03-difference-in-differences/3.3-staggered-did.md))
applies to panel FE with staggered adoption — this lecture covers the general
machinery and defers that failure mode to Lecture 3.

---

## 4. References

- **Wooldridge (2010).** *Econometric Analysis of Cross Section and Panel Data.* — the definitive reference for all four methods.
- **Mundlak (1978).** "On the Pooling of Time Series and Cross Section Data." *Econometrica.* — §7.2.
- **Arellano & Bond (1991).** "Some Tests of Specification for Panel Data." *Review of Economic Studies.* — §7.3.
- **Efron & Morris (1975).** "Data Analysis Using Stein's Estimator and Its Generalizations." *JASA.* — the shrinkage foundation of §7.4.
- **Angrist & Pischke (2009).** *Mostly Harmless Econometrics*, Ch. 5 — fixed effects and its assumptions.
