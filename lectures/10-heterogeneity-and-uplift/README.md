# Lecture 10 — Heterogeneous Effects & Uplift

> **Prerequisites:** [Lecture 1 §4 — CATE](../01-foundations-and-estimands.md), [Lecture 9 — DML](../09-double-machine-learning/) (causal forests use DML-style local centering), and any randomized or unconfounded design to estimate on.
> **Deepens:** [`industry-playbook/04-heterogeneity-and-targeting.md`](../../industry-playbook/04-heterogeneity-and-targeting.md).

Every lecture until now chased a *single number* — the ATE, the effect
averaged over everyone. This lecture asks the question that actually drives a
budget: **whom should we treat?** The answer requires the **CATE** — the
effect for each *kind* of user — and it exposes the most expensive mistake in
applied ML: **targeting the users most likely to convert, instead of the users
whose conversion the treatment actually causes.** Those are different people,
and confusing them wastes the entire marketing budget on customers who'd have
converted anyway.

---

## 1. From ATE to CATE — predict the impact, not the outcome

The **Conditional Average Treatment Effect:**

```math
\tau(x) = E[Y(1) - Y(0) \mid X = x]
```

the treatment effect for users with covariates $x$. Contrast the two modeling
tasks that look identical and aren't:

| | Predicts | Answers | Ranks by |
|---|---|---|---|
| **Standard ML** (RF classifier) | the outcome $Y$ | "who will renew?" | $P(Y=1)$ |
| **Causal ML** (causal forest) | the *effect* $\tau$ | "who renews *because of* the call?" | $\tau(x)$ |

A churn model predicts *who will churn*. An uplift model predicts *how much a
$10 discount changes* their churn probability. **The gap between these two
rankings is the whole lecture**, and §10.2's probe shows it costs a call
center its entire budget.

---

## 2. The uplift quadrant

Sort every user into one of four types by their treatment response. This is
the diagram to draw on any interview whiteboard:

```
                    Would convert WITHOUT treatment?
                         NO              YES
                   ┌──────────────┬──────────────┐
   Would convert   │ PERSUADABLES │  SURE THINGS │
   WITH treatment? │   τ > 0 ✅   │   τ ≈ 0 ❌   │
             YES   │   TARGET     │ convert anyway│
                   ├──────────────┼──────────────┤
                   │ LOST CAUSES  │ SLEEPING DOGS│
             NO    │   τ ≈ 0 ❌   │   τ < 0 ☠️   │
                   │ leave anyway │ treatment     │
                   │              │ backfires     │
                   └──────────────┴──────────────┘
```

- **Sure things** — convert with *or* without treatment. $\tau \approx 0$.
  Treating them is pure waste. **Standard ML targets these.**
- **Lost causes** — convert under neither. $\tau \approx 0$. Also waste.
- **Sleeping dogs** — the treatment makes them *worse* (a reminder email
  annoys a happy customer into churning). $\tau < 0$. **Treating them destroys
  value.**
- **Persuadables** — convert *only if* treated. $\tau > 0$. **The only group
  worth targeting.** Causal ML finds these.

The entire value of causal ML over standard ML is that it separates the
persuadables from the sure things — a distinction the outcome model is blind
to.

---

## 3. The chapters

| # | Chapter | Covers | Read when |
|---|---|---|---|
| **10.1** | [Causal Forests & CATE](./10.1-causal-forests.md) | How a causal tree splits (both arms in every leaf), honesty, local centering / DML, the min-leaf constraint | You need per-user effect estimates |
| **10.2** | [Uplift & Targeting](./10.2-uplift-and-targeting.md) | The quadrant, the sure-things trap (the telecom probe), ROI-threshold targeting, Qini / AUUC evaluation | You have a budget and must choose whom to treat |
| **10.3** | [Policy Learning](./10.3-policy-learning.md) | From black-box scores to interpretable rules: single honest tree vs. surrogate policy tree; deploying an IF/ELSE | The business needs a rule, not a model |
| **10.4** | [Meta-Learners](./10.4-meta-learners.md) | S/T/X/R/DR — architectural recipes turning any ML into a CATE estimator; the two failure modes (extrapolation, unobserved confounding); the selection matrix | You want to use XGBoost/LightGBM for uplift |

---

## 4. Through-lines

**Predict the impact, not the outcome.** Standard ML ranks by $Y$ (who
converts); causal ML ranks by $\tau$ (who converts *because of* treatment).
Verified (§10.2): targeting the top decile by predicted outcome generates
**~0 causal lift** (all sure things), while targeting by CATE generates a
large lift. §1.

**Every leaf is a local A/B test.** A causal tree needs *both* treated and
control units in every node — it splits to maximize heterogeneity in $\tau$,
not in $Y$, and estimates each leaf's effect as a within-leaf treated-minus-
control difference. **Honesty** (separate samples for splitting and
estimating) is what keeps the confidence intervals valid. §10.1.

**Target persuadables, and only above the ROI threshold.** A positive $\tau$
isn't enough — treatment costs money. Call iff $\hat\tau_i > c$. And beware
sleeping dogs ($\tau < 0$), whom a naive positive-uplift filter correctly
excludes but a "treat everyone likely to convert" policy hits. §10.2.

**Scores become rules.** A forest gives an accurate but black-box per-user
CATE. Distill it into a shallow **surrogate policy tree** for a human-readable
IF/ELSE the business can hardcode — no ML model in the serving path. Verified:
the surrogate recovers the true persuadable rule. §10.3.

---

## 5. References

- **Athey & Imbens (2016).** "Recursive Partitioning for Heterogeneous Causal Effects." *PNAS.* — Causal trees and honesty (§10.1).
- **Wager & Athey (2018).** "Estimation and Inference of Heterogeneous Treatment Effects using Random Forests." *JASA.* — Causal forests with valid confidence intervals.
- **Athey, Tibshirani & Wager (2019).** "Generalized Random Forests." *Annals of Statistics.* — The `grf` framework; local centering.
- **Radcliffe & Surry (2011); Gutierrez & Gérardy (2017).** — Uplift modeling and the Qini curve (§10.2).
- **Athey & Wager (2021).** "Policy Learning with Observational Data." *Econometrica.* — Optimal policy trees (§10.3).
- **Künzel, Sekhon, Bickel & Yu (2019).** "Metalearners for Estimating Heterogeneous Treatment Effects." *PNAS.* — S/T/X-learners (a complementary CATE toolkit).
