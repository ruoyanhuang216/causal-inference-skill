# 01. Experiments First

**The rule:** if you can randomize, randomize. Every method in
Sections 2–5 of this playbook is a *workaround* for not being able to
run an experiment. The workarounds are powerful but always weaker than
the design they substitute for.

This chapter covers the experimental playbook for industry: A/B,
switchback, compliance / ITT, cluster designs for interference, and
trigger analysis for low-incidence treatments.

---

## The simplest case: user-level A/B test

```
1. Randomize users to treatment (T = 1) or control (T = 0)
   at the user_uuid level.
2. Choose ONE primary metric agreed with the stakeholder in advance.
3. Compute  τ̂ = Ȳ_T − Ȳ_C.  Standard error via the two-sample formula.
4. Compare τ̂ ± 1.96 · SE  to zero. Pre-register the MDE.
```

That's the whole story when treatments are independent across users
and the unit you randomize on is the unit whose outcomes you measure.

**Sanity check before shipping the analysis.**

- **Randomization-unit / metric-unit alignment.** If you randomize at
  user level but measure session-level outcomes, your SEs are wrong.
  Either re-aggregate to user level or cluster SEs at user level.
- **Sample Ratio Mismatch (SRM).** If the treated/control ratio
  deviates from the intended split by more than a chi-squared-test
  level, the randomization is broken. Find the bug before reading
  the readout.
- **Peeking / sequential testing.** Don't read out before the
  pre-registered duration. If you must, use sequential testing
  (Always-Valid p-values; mSPRT) — not naive z-tests at every
  midpoint.
- **Pre-experiment balance** on key covariates. Significant imbalance
  → recheck randomization or use CUPED-style variance reduction.

---

## When users are not independent: SUTVA violations

A/B test results assume each unit's outcome doesn't depend on other
units' treatment status. In **marketplaces, social networks, and
two-sided platforms**, this is wrong by construction:

- Treating sellers affects untreated sellers via competition.
- Treating users with a recommender change affects the items shown
  to other users (shared item pool).
- A discount given to one rider raises driver supply, helping
  untreated riders.

Two design responses:

### Switchback (time-cluster randomization)

Randomize the **policy state of the marketplace** in short time
windows. Buyers and sellers in the same window see the same policy;
cross-window contamination is small.

**When to use.** Continuous-marketplace experiments where SUTVA
violation is large within a session.

**Example.** *Surge-pricing experiment.* Every 60 minutes the surge
algorithm flips between treatment (new curve) and control (old).
Block-level GMV is the outcome; block-level differences-in-means
is the estimator.

**Sanity check.**
- **Carryover** — drop the first 5–15 minutes after each policy flip.
  If estimates shift materially, lengthen blocks.
- **Block-length sensitivity** — re-run at 30 / 60 / 120 min. Large
  drift signals either carryover or treatment-effect dynamics.
- **Time balance** — assignment should be ≈ balanced across daypart
  and DOW; if not, add time fixed effects.
- **Cluster SE at block level** — within-block autocorrelation will
  inflate significance.

### Cluster randomization

Randomize whole clusters (geographic markets, friend groups, item
categories). SUTVA holds *between* clusters; within-cluster
interference is absorbed.

**When to use.** When the natural interference boundary is a
geography or a social cluster.

**Example.** *City-level pricing change in a ride-hail app.*
Randomize cities into treatment / control. Effect estimated on
city-aggregate metrics with cluster SE.

**Spillover-magnitude back-of-envelope:** estimate the share of
control-unit interactions with treated units. <5% → SUTVA-assuming
estimate is probably fine; 20%+ → cluster-randomize.

---

## When some users don't comply: ITT vs. CACE

Real RCTs have non-compliance. A user assigned to "see new banner"
may close it before reading; a user assigned to "free shipping"
might never use it.

**Two estimands, two different decisions.**

- **ITT (intention-to-treat):** effect of *assignment*. What ships
  on average; the policy-level estimate.
- **CACE / LATE (complier average causal effect):** effect on the
  *compliers* — users whose treatment status actually changed with
  assignment. The mechanism-level estimate.

Computing CACE is just IV (§2) with random assignment as the
instrument:

```
τ̂_CACE  =  (Ȳ_assigned − Ȳ_not-assigned)  /  (compliance_rate_assigned − compliance_rate_not-assigned)
```

**Default reporting rule.** Show ITT to the GM; show CACE if a
follow-up question is "is the *feature* effective for people who
actually engage with it?"

---

## When the treatment fires rarely: trigger analysis

In risk / fraud / discount experiments, *most users never trigger
the policy* (e.g., 95% of deposits aren't flagged by either model).
A full-population A/B reading dilutes the metric.

**Trigger analysis.** Restrict the comparison to the
subpopulation where treatment and control *would have made
different decisions*. The difference among those users is the
*counterfactually relevant* effect.

**Pipeline.**

1. Log the decisions of both control and treatment in real-time
   (counterfactual logging — treatment's decision is logged for
   control users and vice versa).
2. Identify the subpopulation where the two models disagreed.
3. Compute treatment effect only on that subpopulation.

**Why this matters.** Detecting a 2-cent ARPU effect on full
traffic requires 6 months of experiment; trigger analysis can detect
the same effect in 2 months because it removes the 95% of users
where the two policies are indistinguishable.

---

## Ramp protocol and rollback

Industry experiments rarely jump straight to 50/50. Standard ramp:

| Phase | Allocation | Duration | Rollback trigger |
| --- | --- | --- | --- |
| Canary | 1% / 99% | 1–2 days | any error / FP spike |
| Pilot | 5% / 95% | 2–3 days | guardrail-metric breach |
| Half-ramp | 30% / 70% | 3 days | same |
| Full A/B | 50% / 50% | Pre-registered duration | same |
| Ramp to 100% | Post-readout | — | — |

Define **auto-rollback bars** in advance (e.g., flag-rate > 2× control,
single-user-loss > $5K, error rate > 1%). Make the rollback automatic;
don't trust humans to pull the cord at 2 AM.

---

## Variance reduction (when you have observational priors)

A/B SEs can be tightened by ~30–60% with two cheap moves:

- **CUPED** (Deng-Xu-Kohavi-Walker 2013) — regress the post-period
  metric on the same metric from the pre-period; experiment runs on
  the residual. The pre-period coefficient ≈ 1 in most settings, so
  the residual has much lower variance.
- **Stratification at randomization** — pre-stratify on a strong
  predictor of the outcome (e.g., deciles of past spend) before
  random assignment within strata.

Both are essentially "use known prior structure to reduce noise."
Always check what fraction of variance the pre-period explains
before reporting smaller MDEs.

---

## Decision matrix: which experimental design?

| Situation | Design |
| --- | --- |
| Independent user-level outcomes | User-level A/B |
| Some users won't comply with assignment | A/B + report both ITT and CACE |
| Marketplace / social network interference | Switchback or cluster randomization |
| Outcome only realized for a small subpopulation | Counterfactual logging + trigger analysis |
| Treatment is risky or revenue-sensitive | Ramp protocol with auto-rollback |
| Want tighter SEs with a noisy outcome | Add CUPED with pre-period covariate |

---

## When you can't randomize — what next?

Three families of workarounds, in rough order of how much they
"feel like" an experiment:

1. **Quasi-experimental designs** (§2) — when the world hands you a
   discontinuity, a policy date, or an external shifter. Often the
   second-best after randomization.
2. **Observational + selection on observables** (§3) — assume rich
   features capture confounding; lean on DML. Weaker than (1) but
   more general.
3. **Structural modeling** (§5) — needed when the policy is a curve,
   not a point.

Always start at (1) and only escalate to (2) or (3) if no natural
experiment is available.
