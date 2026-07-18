# Lecture 9 — Double / Debiased Machine Learning

> **Prerequisites:** [Lecture 8 — Selection on Observables](../08-selection-on-observables/) (unconfoundedness, overlap, AIPW) and [Lecture 5 — Instrumental Variables](../05-instrumental-variables/) (the DML-IV finale in §9.3 merges the two). DML is what you reach for when the confounding is real, unconfoundedness is plausible, and the relationship between confounders and outcome is **too complex for OLS or a propensity model.**
> **Deepens:** [`industry-playbook/03-observational.md`](../../industry-playbook/03-observational.md).

Lecture 8 estimated observational effects with parametric nuisance models — a
logistic propensity, a regression outcome. But what if you have **500
confounders** and the relationship between them and the outcome is wildly
nonlinear? OLS chokes on the dimensions; a hand-specified propensity model is
hopeless. You want to throw a flexible ML model at the nuisances — but naively
regressing $Y$ on $D$ and $X$ with XGBoost **regularizes the treatment
coefficient toward zero**, destroying the causal estimate. ML is built for
*prediction*, and prediction demands shrinkage; causal estimation demands the
opposite.

**Double Machine Learning** (Chernozhukov et al. 2018) resolves the tension by
*separating the ML prediction task from the causal estimation task.* It is the
modern default for high-dimensional observational causal inference, and it's
the natural culmination of this series — it inherits AIPW's doubly-robust
structure (Lecture 8) and, in its IV form, absorbs the Judge-IV design (Lecture
5).

---

## 1. The core idea: Frisch-Waugh-Lovell on steroids

DML rests on a century-old result, the **Frisch-Waugh-Lovell (FWL) theorem**.
FWL says you can isolate the effect of $D$ on $Y$ by *partialling out* the
covariates $X$ from both, then regressing the leftovers:

1. Regress $Y$ on $X$; keep the residual $\tilde{Y}$ (variation in $Y$ not
   explained by $X$).
2. Regress $D$ on $X$; keep the residual $\tilde{D}$.
3. Regress $\tilde{Y}$ on $\tilde{D}$. **The slope is the causal effect** $\theta$.

Classical FWL does steps 1–2 with OLS — which assumes $X$ affects $Y$ and $D$
*linearly*. **DML's one move:** do steps 1–2 with *flexible ML* (random
forests, gradient boosting, neural nets) to capture arbitrary nonlinearity,
then do step 3 with dead-simple OLS. You've compared the *surprise in treatment*
against the *surprise in outcome*, after ML has vacuumed up everything the
confounders explain.

---

## 2. Two enemies, two defenses

Throwing ML at the nuisances introduces two biases that DML is engineered to
kill. Knowing which mechanic defeats which bias is the whole lecture.

| Bias | Where it comes from | The defense |
|---|---|---|
| **Regularization bias** | ML shrinks its estimates, so $\hat g$ and $\hat m$ are never exactly right | **Neyman orthogonality** — the residual-on-residual score is *locally insensitive* to small nuisance errors |
| **Overfitting bias** | ML fit and evaluated on the same data memorizes noise → residuals too small | **Cross-fitting** — fit nuisances on other folds, residualize out-of-sample |

- **Neyman orthogonality** (§9.1): because you partialled $X$ out of *both* $Y$
  and $D$, the final estimate's sensitivity to nuisance error is *first-order
  zero*. XGBoost can be a little wrong about $g$ and $m$ and $\hat\theta$
  survives. This is the same structural property that makes AIPW doubly robust
  (Lecture 8 §4).
- **Cross-fitting** (§9.1): fit the nuisance models on $K-1$ folds, compute
  residuals on the held-out fold, rotate. Without it, in-sample overfitting
  shrinks the residuals, the standard errors collapse, and you ship a
  confident false positive (§9.1's probe).

---

## 3. The chapters

| # | Chapter | Covers | Read when |
|---|---|---|---|
| **9.1** | [The DML Core](./9.1-dml-core.md) | FWL, the partially linear model, Neyman orthogonality, cross-fitting, the skip-cross-fitting probe | The confounders are high-dimensional / nonlinear |
| **9.2** | [Applied DML & the Two Gotchas](./9.2-applied-dml.md) | The enterprise-SaaS walkthrough end-to-end; feature importance ≠ causality; overlap still bites | You're building a real DML pipeline |
| **9.3** | [DML-IV (PLIV)](./9.3-dml-iv.md) | Merging Judge-IV with DML: the collection-agent design, standard-DML ITT vs. DML-IV, the LOO instrument | Treatment is endogenous *and* high-dimensional |

---

## 4. Through-lines

**DML separates prediction from estimation.** The ML models are *nuisances* —
mathematical vacuums that suck up confounding variance. Only the final $\theta$
is causal. Reading feature importances off the nuisance models for "business
insight" is the classic blunder (§9.2). §1.

**The two biases have two distinct fixes.** Neyman orthogonality handles
regularization bias (the ML being slightly wrong); cross-fitting handles
overfitting bias (the ML memorizing noise). Confusing them — or skipping
cross-fitting to save compute — is where production DML dies. §2, §9.1.

**DML is still selection-on-observables.** It crushes *observed* confounding
with ML, but an unobserved confounder breaks it exactly as in Lecture 8. And
overlap still bites: if the ML predicts $D$ perfectly, $\tilde{D} \to 0$ and the
final regression divides by zero. Magic-feeling, not magic. §9.2.

**AIPW + cross-fitting = DML.** The doubly-robust estimator of Lecture 8 §8.4,
with ML nuisances fit out-of-fold, *is* DML for the ATE. This lecture is that
idea taken seriously and extended to IV. §9.1.

---

## 5. References

- **Chernozhukov, Chetverikov, Demirer, Duflo, Hansen, Newey & Robins (2018).** "Double/Debiased Machine Learning for Treatment and Structural Parameters." *Econometrics Journal.* — The founding paper.
- **Frisch & Waugh (1933); Lovell (1963).** The partialling-out theorem behind §1.
- **Chernozhukov, Hansen, Spindler & others** — the `DoubleML` package papers (Python/R).
- **Syrgkanis et al.** — the `EconML` package (Microsoft), including DML-IV / PLIV.
- **Athey & Wager (2019).** "Estimating Treatment Effects with Causal Forests." — the CATE cousin (Lecture 10).
