# 03. Observational Methods

When you can't run an experiment and the world hasn't handed you a
clean quasi-experimental design, you fall back to **selection on
observables**: assume that conditional on a rich enough feature set
`X`, treatment is as-good-as-random.

The identifying assumption — **unconfoundedness**
`{Y(1), Y(0)} ⊥ T | X` — is untestable. Sensitivity analysis (§6) is
mandatory.

This is the weakest of the three identification regimes (experimental
> quasi-experimental > observational), but it covers the vast
majority of industry causal questions where rich behavioral logs are
available.

---

## The industry default: Double / Debiased ML (DML)

Reach for DML first in any observational ATE setting with high-
dimensional `X`. It uses ML for the nuisance components, gives
√n-consistent estimates of `τ`, and has honest confidence intervals.

### Setup — partially linear model

```
Y  =  τ · T  +  g(X)  +  ε        (outcome equation)
T  =  m(X)  +  v                  (treatment / propensity equation)
```

with `E[ε | X] = E[v | X] = 0`.

### Algorithm

1. **Fit nuisances with ML** on a held-out fold:
   - `ĝ(X) ≈ E[Y | X]`
   - `m̂(X) ≈ P(T = 1 | X)` (the propensity)
   Use LightGBM, neural nets, lasso — whatever fits the data.
2. **Residualize on the other fold:**
   - `Ỹ = Y − ĝ(X)`
   - `T̃ = T − m̂(X)`
3. **Final stage:** OLS of `Ỹ` on `T̃`:
   ```
   τ̂  =  ( Σ T̃ Ỹ )  /  ( Σ T̃² )
   ```
4. **Cross-fit** (swap folds, average) to eliminate same-data bias.

### Why this works

The score function for `τ` is constructed so that
`∂_η E[ψ(W; τ, η)] = 0` at the true `τ` — **first-order insensitive
to nuisance error**. Combined with cross-fitting, this gives
`√n`-consistent `τ̂` even when `ĝ`, `m̂` converge at the slower
`n^(1/4)` rate that flexible ML achieves under sample-complexity
bounds. This is the **Neyman-orthogonality** property.

### Worked example

*Effect of attending a marketing email on 30-day GMV.* Several
hundred behavioral controls (browsing history, prior order recency
/ frequency / monetary, device features, segment membership).
Logistic regression for propensity is too rigid; gradient boosting
inside DML gives an honest ATE.

```python
from econml.dml import LinearDML
from lightgbm import LGBMRegressor, LGBMClassifier

dml = LinearDML(
    model_y=LGBMRegressor(),
    model_t=LGBMClassifier(),
    cv=5,
)
dml.fit(Y, T, X=X_features)
ate = dml.coef_[0]
ci = dml.coef__interval()
```

### Sanity check

- **Overlap / positivity.** Histogram `m̂(X)`. Mass at 0 or 1 means
  you're extrapolating; trim or report on the trimmed sample.
- **Nuisance OOS quality.** `ĝ(X)` and `m̂(X)` should have
  reasonable OOS R² / AUC. Degenerate nuisance → ATE unidentified
  from `X`.
- **Cross-fit fold sensitivity.** Re-run at 2, 5, 10 folds.
  Sensitivity flags too-small `n` or unstable fits.
- **Compare to OLS with the same controls.** Large divergence
  highlights where ML is finding nonlinear confounding structure
  that OLS missed.

### When to use

- Many observable confounders, willing to assume unconfoundedness.
- Want one number — the ATE — with honest inference.
- Have at least a few thousand observations (DML's asymptotic
  properties kick in with reasonable `n`).

---

## The classical baselines — when and why they still matter

DML is the modern default, but its predecessors are still useful
when you need interpretability, are working with small samples, or
need to communicate to stakeholders trained in classical methods.

### Propensity-score matching (Rosenbaum-Rubin 1983)

Reduce matching from multi-dimensional `X` to a 1-D propensity
`ê(x) = P(T = 1 | X = x)`. Match each treated unit to one or more
controls with similar `ê(x)`; compute ATT as the average outcome
difference on matched pairs.

**When to use.** Small `n` and you need an interpretable matched-
pairs ATT for stakeholders.

**Sanity check.**
- **Overlap** — histogram `ê(X)` by treatment group.
- **Balance** — standardized mean difference (SMD) < 0.1 on every
  covariate after matching.
- **Caliper sensitivity** — re-run at multiple caliper widths.

### Inverse Propensity Weighting (IPW)

Re-weight the sample to balance treatment:

```
τ̂_IPW  =  (1/n) · Σ  [ T_i · Y_i / ê(X_i)  −  (1 − T_i) · Y_i / (1 − ê(X_i)) ]
```

Hájek-stabilized version normalizes the weights.

**When to use.** Full-sample ATE with classical (logistic-regression)
propensity model.

**Sanity check.** Extreme weights (`1 / ê → ∞`) inflate variance.
Trim at 1st / 99th percentile or stabilize.

### Augmented IPW (AIPW / Doubly Robust)

Combine outcome model `ĝ(X, t)` with propensity `ê(X)`:

```
τ̂_AIPW  =  (1/n) · Σ  [ ĝ(X_i, 1) − ĝ(X_i, 0)
                  +  T_i · (Y_i − ĝ(X_i, 1)) / ê(X_i)
                  −  (1 − T_i) · (Y_i − ĝ(X_i, 0)) / (1 − ê(X_i)) ]
```

**Doubly robust** — consistent if *either* `ĝ` or `ê` is correctly
specified. This is the **direct predecessor of DML**: replace
parametric `ĝ, ê` with ML + cross-fitting and you get DML.

### The lineage you should be able to articulate

```
OLS  →  Matching / IPW (classical)
     →  AIPW (doubly robust, classical nuisances)
     →  DML (ML nuisances + cross-fit, √n-efficient)
```

A staff-level interview question is "why DML over AIPW?" Answer:
ML nuisances + cross-fitting buy you flexibility for high-dim `X`
while preserving honest inference. With low-dim `X` and simple
nonlinear structure, AIPW with logistic + GAM is the right answer.

---

## TMLE (Targeted Maximum Likelihood Estimation)

The biostatistics cousin of DML. Same doubly-robust target, same
flexible-nuisance machinery. Different community, different
software (`tmle3`, `lmtp` in R). One key difference: TMLE updates
the outcome model with a "clever covariate" that targets the ATE
parameter directly, making the estimator the MLE of a re-weighted
likelihood.

**Use TMLE when** publishing in epidemiology / biostatistics, or
when you want the explicit doubly-robust property in a single
estimator.

**Use DML when** working in tech / econometrics / industry — the
software ecosystem (`econml`, `doubleml`) is more mature.

Both target the same `τ̂` and converge to similar numbers in
practice.

---

## When unconfoundedness fails

DML / matching / IPW all rely on `{Y(1), Y(0)} ⊥ T | X`. If a
critical confounder is unobserved, the estimate is biased.

The defense, in order:

1. **Argue for unconfoundedness from domain knowledge.** Make
   explicit which confounders `X` covers; identify ones you can't
   measure.
2. **Run sensitivity analysis** (Cinelli-Hazlett RV in §6).
3. **If you can't defend (1) and (2)**, you don't have an
   observational identification — escalate to quasi-experimental
   (§2) or structural (§5).

The skill of senior observational causal inference is not "fit a
DML and report the number." It's "argue why the identifying
assumption holds in this setting, then fit DML, then quantify how
much the assumption could be wrong."

---

## Decision matrix

| Situation | Method |
| --- | --- |
| High-dim `X`, want ATE, can assume unconfoundedness | DML (default) |
| Small `n`, want interpretable matched-pairs ATT | Propensity-score matching |
| Mid-dim `X`, want full-sample ATE with classical nuisances | AIPW |
| Same as DML but publishing in biostatistics | TMLE |
| Can't defend unconfoundedness even with sensitivity analysis | Escalate to §2 or §5 |

---

## Common pitfalls

- **Post-treatment controls.** Conditioning on a variable that's
  affected by `T` blocks the causal pathway. Drop all features
  measured after the treatment.
- **M-bias** (collider bias). Conditioning on a common effect of two
  unrelated variables induces association. Draw the DAG before
  choosing controls.
- **Selection into the sample.** If `Y` is only observed for a
  selected subset, you have a selection model, not a clean ATE.
- **High-VIF features.** Multicollinearity doesn't bias `τ̂` but
  inflates SE. Trim or use regularized nuisance models (DML's
  built-in advantage).
- **Treatment heterogeneity.** If treatment effects vary across `X`,
  the ATE is a weighted average — see §4 for CATE methods.
