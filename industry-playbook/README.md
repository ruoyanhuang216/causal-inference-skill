# Industry Playbook for Causal Inference

A concise, opinionated, decision-tree-first playbook for **industry data
scientists** doing causal inference. Complements the formal skill at
[`skills/causal-inference/`](../skills/causal-inference/), which is
more comprehensive and academically rigorous; this playbook is the
**pragmatic counterpart**: what to actually do on Monday morning.

If you're choosing between two methods at 5 PM the day before a GM
review, this is the resource. If you're writing for the *Journal of
Economic Methods*, use the formal skill.

---

## The single decision tree

```
                   Can I randomize? ──────────────────► YES → §1 Experiments
                          │
                          │ NO
                          ▼
       Did the world hand me a natural experiment? ───► YES → §2 Quasi-experiments
       (policy rollout, eligibility cutoff, external               (DiD / RDD / IV)
        instrument)
                          │
                          │ NO
                          ▼
        Are observable confounders enough? ───────────► YES → §3 Observational
        (rich features, defensible unconfoundedness)              (DML by default)
                          │
                          │ "yes but I also want to know WHO responds"
                          ▼
                   Heterogeneous effects ───────────────► §4 Heterogeneity & targeting
                   (CATE / uplift)                          (causal forest, R-learner)
                          │
                          │ "I need to extrapolate to a policy that hasn't been tried"
                          ▼
                   Structural model ───────────────────► §5 Structural
                   (pricing, demand, credit, real options)
                          │
                          ▼
        Defending the estimate to stakeholders ───────► §6 Defending estimates
        (sensitivity, robustness, pre-trends, reporting)
```

---

## Files

| File | What it covers | Read when |
| --- | --- | --- |
| [`00-foundations.md`](./00-foundations.md) | Potential outcomes, the 6 estimands, the assumption stack, the four-question sanity framework | Always start here if new to causal inference |
| [`01-experiments-first.md`](./01-experiments-first.md) | A/B, switchback, ITT vs. CACE, cluster randomization, trigger analysis | Anything you can randomize |
| [`02-quasi-experimental.md`](./02-quasi-experimental.md) | DiD (simple → staggered), RDD (sharp → fuzzy), IV (2SLS → modern) | Policy rollouts, eligibility cutoffs, external instruments |
| [`03-observational.md`](./03-observational.md) | DML (default), Matching/IPW (lineage), TMLE (cousin) | Rich observational data, no design exploitable |
| [`04-heterogeneity-and-targeting.md`](./04-heterogeneity-and-targeting.md) | CATE estimation, uplift modeling, mediation | "Whom to treat" or "what mechanism" |
| [`05-structural.md`](./05-structural.md) | BLP, conjoint, hedonic, Merton credit, dynamic discrete choice | When the policy is a *curve*, not a point |
| [`06-defending-estimates.md`](./06-defending-estimates.md) | Sensitivity (Cinelli-Hazlett RV), pre-trends, placebo, reporting templates | Before any stakeholder review |

---

## How to use this playbook

1. **Read [`00-foundations.md`](./00-foundations.md)** once. It's the
   shared vocabulary for everything else.
2. **Identify your situation in the decision tree above** and jump to
   the relevant chapter.
3. **Each chapter follows the same pattern:**
   - The industry question it answers
   - The simplest viable method first (with one worked example +
     sanity check)
   - "Escalate to X if Y" pointers to advanced variants
   - Decision matrix at the end
4. **Always finish with [`06-defending-estimates.md`](./06-defending-estimates.md)**
   before presenting. Sensitivity analysis is not optional in industry —
   it's how you survive the first stakeholder pushback.

---

## What this playbook is opinionated about

- **DML is the default for observational ATE.** Matching / IPW exist;
  use them when you need interpretable matched pairs.
- **Causal forest is the default for CATE.** Meta-learners (R / X / DR)
  are the right answer when the forest function class is wrong.
- **Synthetic DiD is the modern default for single-treated-unit panels.**
  Vanilla synthetic control is the predecessor; SDiD dominates in most
  industrial settings.
- **Cinelli-Hazlett RV is the sensitivity-analysis default.** Rosenbaum
  for matched designs, E-value for risk-ratio framings.
- **Switchback for marketplaces with interference.** Not user-level A/B.
- **Trigger analysis for low-incidence experiments.** Not full-population
  effect size.

---

## What this playbook intentionally leaves out

Pointers to the formal skill for these:
- Honest RDD, design-based RDD (academic rigor)
- Borusyak-Jaravel-Spiess imputation (use Callaway-Sant'Anna in practice)
- Mendelian randomization, draft-lottery, judge-leniency
  (epidemiology / academic)
- Causal discovery (PC, NOTEARS) — different paradigm; rarely actionable
  in industry decisions
- Bayesian Causal Forest beyond a one-paragraph mention
- Full structural macroeconomic models (Rust, MPEC)

These are all covered in the formal skill at
[`skills/causal-inference/methods-reference.md`](../skills/causal-inference/methods-reference.md).
