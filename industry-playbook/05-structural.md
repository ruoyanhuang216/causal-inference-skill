# 05. Structural Estimation

Reduced-form methods (§1–4) answer "what is the effect of *this
specific* intervention?" Structural methods estimate the **parameters
of an economic model** — preferences, elasticities, marginal costs —
and let you *simulate counterfactual worlds*: merger effects, new
products, price-cap regulations, demand under a competitor entry.

The industry rule: **reduced-form for shipping; structural for
strategy.** If the decision is "should we run this campaign?",
reduced-form answers it. If the decision is "what should the price
schedule look like across the full demand curve?", you need
structural.

---

## The identification problem: simultaneous equations

Price and quantity are jointly determined. OLS of `Q ~ P` is biased
because both move together with supply / demand shocks:

```
Demand:   Q^d_t  =  α  −  β · P_t   +  γ_d · X_t  +  ε^d_t
Supply:   Q^s_t  =  δ  +  ζ · P_t   +  γ_s · Z_t  +  ε^s_t
Equilibrium:  Q^d_t = Q^s_t
```

**IV identifies the demand curve:** an instrument that shifts supply
without shifting demand recovers `β` (the slope of the demand curve).

Standard industry IV candidates:

- **Hausman instruments** — prices of the same product in *other
  markets* (correlated through common costs, uncorrelated with local
  demand shocks).
- **Cost shifters** — input prices, exchange rates, weather (for
  agricultural goods).
- **BLP instruments** — characteristics of *rival* products in the
  same market (competitive landscape shifts markups).

---

## Random-utility foundations (the workhorse abstraction)

Underlies BLP, conjoint, and most demand modeling. Consumer `i` picks
alternative `j` from choice set `J_i` to maximize utility:

```
u_ij  =  X_j · β  +  ξ_j  +  ε_ij
```

With iid Type-I extreme-value `ε_ij`, this gives the **multinomial
logit (MNL)**:

```
P_ij  =  exp(X_j β + ξ_j)  /  Σ_{k ∈ J_i}  exp(X_k β + ξ_k)
```

**MNL's pathology: IIA** (Independence of Irrelevant Alternatives) —
the red-bus / blue-bus problem. Standard fixes: **nested logit**
(correlated shocks within nests) or **random-coefficients logit**
(`β_i ~ F(·; θ)`, used in BLP). Mixed logit / random-coefficients
logit is the modern default.

---

## §5.1 BLP — the differentiated-products workhorse

Use when: estimating demand and pricing for a category with many
heterogeneous products (consumer packaged goods, cars, financial
products, retail).

**Demand side: random-coefficients logit.**

```
u_ijt  =  X_jt · β_i  −  α_i · P_jt  +  ξ_jt  +  ε_ijt
```

with `(β_i, α_i) ~ F(·; θ)` capturing taste heterogeneity. Aggregate
market share:

```
s_jt(θ; X, P, ξ)  =  ∫ exp(...)  /  (1 + Σ exp(...))  dF(β_i, α_i; θ)
```

**Estimation: GMM** matching predicted shares to observed shares.
Instruments enter via `ξ_jt`.

**Supply side: Bertrand-Nash pricing.** Multi-product firms set
prices to maximize profits given the demand system. The first-order
condition implies a markup depending on demand elasticities; jointly
estimating supply and demand recovers marginal costs.

### Worked example

*Pricing strategy for a new financial product entering a market.*
Use BLP on existing-market data to estimate own- and cross-price
elasticities by user segment; simulate entering with the new product
at various price points to estimate take-up, revenue, and competitor
cannibalization.

### Sanity check

- **Own-price elasticity** negative; for differentiated products
  typically |elasticity| in 2–10. |e| < 1 implies firms aren't
  profit-maximizing → model misspecified.
- **Cross-price elasticity** positive for same-category substitutes,
  ≈ 0 for unrelated categories.
- **First-stage F across `ξ_jt`-instrumented prices.**
- **Outside-good share stability** when excluding small markets.
- **Counterfactual sanity** — perturb a price by 1%; predicted
  quantity should move in a reasonable magnitude.

**Software.** `PyBLP` (Conlon-Gortmaker) is the modern standard.

---

## §5.2 Conjoint analysis — pricing a product that doesn't exist yet

Use when: launching a new product / feature bundle and there's no
revealed-preference data to estimate elasticities from.

**Setup.** Generate hypothetical product profiles by varying feature
levels (fee, interest rate, feature toggles) according to an
orthogonal-array or D-optimal design. Survey respondents rank or
choose among profile bundles.

**Estimation.** Same MNL / random-coefficients-logit machinery as
BLP, fit to **stated** choice data instead of **revealed** market
data. Recover part-worth utilities `β_k` per feature level.

### Worked example

*Pricing a new financial-product bundle.* Conjoint survey with
1,000 users on 12 hypothetical profiles (fee tier × rate × feature
toggles). MNL estimation gives part-worths; structural simulation
predicts take-up and revenue at proposed price-feature combinations
against competitor benchmarks.

### Sanity check

- **Hold-out task accuracy** — train on N − 1 tasks per respondent,
  predict the held-out one. Aim for ≥ 60% most-preferred-alternative
  accuracy.
- **Stated-vs-revealed calibration** — survey respondents overstate
  willingness-to-pay by 30–50% on average. Calibrate elasticities
  downward before porting to real pricing decisions.
- **Within-respondent rationality** — flag respondents who violate
  IIA or transitivity at high rates; their data is noise.

---

## §5.3 Hedonic pricing — implicit feature valuation

Use when: estimating the implicit market price of bundled product
attributes — housing (bedrooms, school district), labor compensation
(skills, education), ad inventory (audience × placement),
financial-product features (rate × term × covenants).

**Setup.** Regress price on feature vector:

```
P_j  =  α  +  β · X_j  +  ε_j
```

Each `β_k` is the **implicit price** of feature `k` (Rosen 1974).

**Identification challenge.** Confounders correlated with the feature
of interest. Two houses differ in renovation status but also in
unobservable neighborhood quality. Standard mitigations:

- **DML** with high-dim ML controls (§3).
- **IV** with exogenous variation in the feature.
- **Quasi-experimental** designs (DiD on policy changes).

### Worked example

*Real-time ad-slot pricing.* Estimate the marginal value of audience
attributes (age bucket, geography, device, daypart) in auction-
clearing prices via DML-augmented hedonic regression on impression-
level data. Output feeds the pricing floor in real-time bidding.

### Sanity check

- **Irrelevant-feature placebo** — include a feature you have strong
  prior is irrelevant (e.g., the unit's serial number); its
  coefficient should be near zero.
- **Functional-form robustness** — log-price vs level-price; basis
  expansions for key features. Implicit prices should be stable up
  to scale.
- **DML diagnostics** if using ML controls.

---

## §5.4 Structural credit risk: Merton (1974)

Use when: estimating default probability for firms with sparse
default history; bank stress testing; counterparty risk.

**The idea.** Treat firm equity as a call option on firm assets,
struck at debt face value `D`, expiring at debt maturity `T`. Default
occurs when asset value at `T` falls below `D`. Black-Scholes:

```
V_t  =  A_t · N(d_1)  −  D · e^{-rT} · N(d_2)
```

where:

- `A_t` = firm asset value (unobservable)
- `V_t` = market equity value (observable from market cap)
- `σ_A` = asset volatility (unobservable)
- `σ_V` = equity volatility (observable from options / returns)
- `d_1 = ( ln(A_t / D) + (r + σ_A² / 2) T ) / (σ_A √T)`
- `d_2 = d_1 − σ_A √T`

**Joint identification.** Two equations link observable `(V_t, σ_V)`
to unobservable `(A_t, σ_A)`:

1. Merton call equation above
2. Black-Scholes delta: `σ_V = (A_t / V_t) · N(d_1) · σ_A`

Solve jointly (Newton-Raphson / fixed point) for `(A_t, σ_A)`.

**Output — distance to default and PD:**

```
DD  =  ( ln(A_t / D)  +  (μ_A − σ_A² / 2) T )  /  ( σ_A √T )
PD  =  N(−DD)
```

**Commercial implementation.** Moody's KMV (now EDF) calibrates `PD`
empirically to default frequencies rather than using theoretical
`N(−DD)`.

### Sanity check

- **Empirical-vs-theoretical PD calibration** — theoretical Merton
  understates tail defaults (lognormal thin tails). Calibrate to
  observed default rates by rating bucket, or use jump diffusion.
- **Joint solve stability** — Newton-Raphson can fail at extreme
  leverage; check convergence.
- **Walk-forward backtest** — predicted PD at horizon `T` vs.
  realized defaults.

### Modern ML-augmented variant

Use ML to predict structural parameters (asset volatility, drift,
effective `D`) from accounting + market data, then run the Merton
fixed point. Preserves structural interpretation while escaping
accounting-ratio rigidity.

---

## §5.5 Dynamic discrete choice (brief)

Use when: sequential decisions matter — subscription renewals,
investment timing, equipment replacement, life-cycle labor supply,
real options.

**Bellman setup:**

```
V_t(s)  =  max_a  [ u(s, a; θ)  +  β · E_t[ V_{t+1}(s') | s, a ] ]
```

Two estimation paths:

- **Nested fixed point (Rust 1987).** Solve Bellman inside the
  likelihood. Computationally heavy.
- **Hotz-Miller (1993) CCP inversion.** Estimate choice
  probabilities reduced-form from data, invert via the CCP
  representation to recover utility parameters. Practical default.

### Worked example

*Subscription churn under price elasticity.* Each month, user `i`
decides renew vs. cancel. State `s_t = (price, tenure, recent usage)`.
Estimate `θ` via Hotz-Miller; use the estimated model to simulate
counterfactual churn under a 10% price hike.

### Sanity check

- **State-space adequacy** — heatmap `P(renew | s)`; flat regions
  mean those state dimensions don't matter.
- **Discount factor `β` identification** — `β` is hard to identify
  separately from current-period utility. Fix from external data
  (typical Rust approach, often 0.95 / yr) or argue from data why
  it's separately identified.
- **Counterfactual reasonableness** — small policy perturbations
  should produce reasonable behavior changes.
- **Out-of-time prediction** — train on first 70% of time series,
  predict last 30%.

---

## Decision matrix — reduced-form vs. structural

| Question | Reduced-form | Structural |
| --- | --- | --- |
| Effect of *this specific* price change? | ✓ | overkill |
| Effect of *all possible* price changes (a curve)? |  | ✓ |
| Welfare effect of a merger? |  | ✓ |
| Did the campaign work? | ✓ |  |
| Consumer-surplus-maximizing price? |  | ✓ |
| Need a number this quarter for the GM | ✓ | not in time |
| Need to predict default for a brand-new IPO firm | reduced-form proxy possible | Merton structural is the right primitive |
| Subscription pricing across the full demand curve |  | Dynamic discrete choice |

---

## When structural is the wrong tool

- **Specific A/B testable interventions** — running an experiment is
  faster and more credible than building a structural model.
- **Insufficient data to identify structural parameters** —
  identification needs variation in the choice set / prices / cohort
  state; without it, structural is just imposing assumptions.
- **Hours-to-days deadline** — BLP and dynamic discrete choice take
  weeks to specify, estimate, and validate. Reduced-form ships in
  days.

The right time to invest in structural is when the same kind of
counterfactual question gets asked repeatedly and reduced-form
answers can't scale — pricing, demand simulation, capacity planning,
merger evaluation.
