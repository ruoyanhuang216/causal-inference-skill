# Lecture 14 — Structural Estimation

> **Prerequisites:** [Lecture 1](../01-foundations-and-estimands.md) and [Lecture 5 — IV](../05-instrumental-variables/) (BLP is GMM-IV at its core). Part V.
> **Deepens:** [`industry-playbook/05-structural.md`](../../industry-playbook/05-structural.md).
> **Scope note:** BLP demand (§14.1) and the supply side (§14.2) are done step-by-step; the dynamic / search / learning families (§14.3) are a lighter survey — enough to know they exist and when to reach for them.

Every lecture until now estimated **the effect of something that happened** — a
launch, a rollout, a price change you observed. Structural estimation answers the
question those cannot: **"what would happen under a change we've *never*
observed?"** A merger between two firms. A brand-new product. A 20% price hike in
a market where prices never moved that much. You cannot A/B test a merger. So you
write down the *economic model* — consumers maximizing utility, firms maximizing
profit — estimate its **parameters** from the data you have, and then *simulate*
the counterfactual.

That's the trade: structural methods buy **extrapolation to unseen policies**, at
the cost of **strong modeling assumptions.** Reduced-form causal inference
(Lectures 1–13) is credible but local; structural is assumption-heavy but can
answer questions no experiment can.

---

## 1. What "structural" means

1. **Economic theory specifies the optimization.** Consumers choose the product
   that maximizes utility; firms set prices that maximize profit; agents solve a
   dynamic program.
2. **Estimate by matching model-implied moments to data** — market shares, choice
   probabilities, prices — usually via GMM or simulated likelihood.
3. **The estimated parameters enable counterfactual simulation** beyond observed
   variation: change the ownership matrix (a merger), add a product, shift a cost,
   and re-solve the model for the new equilibrium.

**The non-negotiable principle: structural estimation does *not* bypass
identification.** Every parameter must be identified from *variation in the data*
— the price coefficient needs price instruments (Lecture 5), preference
heterogeneity needs substitution variation across markets, search costs need
variation in how many options consumers examine. A structural model with no
identifying variation is a calibration, not an estimate.

---

## 2. The chapters

| # | Chapter | Covers | Depth |
|---|---|---|---|
| **14.1** | [Discrete Choice & BLP Demand](./14.1-discrete-choice-and-blp.md) | Logit → IIA problem → mixed logit → **BLP step-by-step** (contraction mapping, price IVs, GMM); nested logit, latent class | Detailed |
| **14.2** | [Supply Side & Merger Simulation](./14.2-supply-and-mergers.md) | Nash-Bertrand FOCs, backing out marginal costs, **merger simulation** step-by-step; entry models | Detailed |
| **14.3** | [Dynamic, Search & Learning Models](./14.3-dynamic-search-learning.md) | Rust NFXP, Hotz-Miller CCP, MPEC, dynamic games; Weitzman search; Bayesian learning | Survey (TBA) |

---

## 3. Through-lines

**Structural is for counterfactuals you can't observe.** If the policy you care
about *happened*, use reduced-form (Lectures 1–13) — it's more credible. Reach
for structural only when you must simulate the *un*-observed: a merger, a new
product, a price outside the historical range. §1.

**IIA is why BLP exists.** Plain logit forces *proportional* substitution — remove
a product and its share redistributes in fixed ratios, no matter how similar the
alternatives (verified in §14.1). Random coefficients (BLP) break IIA so a
luxury car's buyers flow to other luxury cars, not to economy cars. §14.1.

**Price is endogenous — instrument it.** Firms set high prices for high-quality
(high-$\xi$) products, so price correlates with the unobserved quality in the
error. BLP is, at its heart, **GMM-IV** (Lecture 5): the contraction inverts
shares to mean utility, then instruments handle the price endogeneity. §14.1.

**Demand estimates power supply counterfactuals.** Once you have the demand
elasticities, the Nash-Bertrand first-order conditions **back out marginal
costs** from observed prices — and then you change the ownership matrix and
re-solve for post-merger prices. Demand → costs → counterfactual is the whole
industrial-organization pipeline. §14.2.

---

## 4. References

- **Berry, Levinsohn & Pakes (1995).** "Automobile Prices in Market Equilibrium." *Econometrica.* — BLP (§14.1).
- **Nevo (2000).** "A Practitioner's Guide to Estimation of Random-Coefficients Logit Models of Demand." *J. Economics & Management Strategy.* — the readable how-to.
- **Conlon & Gortmaker (2020).** "Best Practices for Differentiated Products Demand Estimation with PyBLP." *RAND J. Economics.* — the modern implementation (`pyblp`).
- **Train (2009).** *Discrete Choice Methods with Simulation.* — logit / mixed logit foundations.
- **Aguirregabiria & Mira (2010).** "Dynamic Discrete Choice Structural Models: A Survey." *J. Econometrics.* — §14.3.
