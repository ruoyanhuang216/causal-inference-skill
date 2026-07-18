# Lectures in Causal Inference

A deep-dive lecture series. Where [`skills/causal-inference/`](../skills/causal-inference/)
tells you *what to run* and [`industry-playbook/`](../industry-playbook/)
tells you *what to do Monday morning*, these lectures tell you **why any
of it works** — and, just as often, why the obvious thing doesn't.

Each lecture derives the identification argument rather than asserting
it, works one realistic example end-to-end with numbers, and closes with
the misreadings that survive into production.

---

## The three layers of this repo

| Layer | Question it answers | Read it when |
| --- | --- | --- |
| [`skills/causal-inference/`](../skills/causal-inference/) | *What method, and what code?* | You're doing the analysis |
| [`industry-playbook/`](../industry-playbook/) | *What do I do before the GM review?* | You have a deadline |
| **`lectures/`** (you are here) | *Why does this identify anything?* | You want to understand it, teach it, or defend it under attack |

The layers cross-reference each other. A lecture ends with pointers to
the playbook chapter and skill reference that operationalize it.

---

## Series structure

The series moves along one axis: **how much the world does the identification
for you.** Five parts, from most-designed to least.

| Part | Theme | Lectures |
| --- | --- | --- |
| **I** | Foundations & design-based ID *(the world randomizes something)* | 1 Foundations · 2 Experimentation · 3 DiD · 4 RDD · 5 IV ✅ |
| **II** | Comparative-case & panel *(build the counterfactual)* | **6 Synthetic Control ✅** · 7 Panel Data *(planned)* |
| **III** | Selection on observables & ML *(assume you measured the confounders)* | **8 Selection on Observables ✅** · 9 ML for Average Effects · 10 Heterogeneity & Uplift *(planned)* |
| **IV** | Defending & interrogating estimates | 11 Sensitivity & Partial ID · 12 Mediation · 13 DAGs & Discovery *(planned)* |
| **V** | Structural | 14 Structural Estimation *(planned)* |

---

## Lectures

| # | Lecture | Core idea | Deepens |
| --- | --- | --- | --- |
| **1** | [Foundations & Treatment Effects](./01-foundations-and-estimands.md) | The counterfactual is missing by construction. ATE / ATT / CATE / ITT / LATE differ only in *whom you average over* — and that choice can flip a ship/no-ship decision. | [`00-foundations.md`](../industry-playbook/00-foundations.md) |
| **2** | [Experimentation](./02-experimentation/) | Run the simplest experiment that satisfies SUTVA without destroying power. Every design is a trade between the two, and **N is the number of randomization units — never the number of users.** | [`01-experiments-first.md`](../industry-playbook/01-experiments-first.md) |
| **3** | [Difference-in-Differences](./03-difference-in-differences/) | Difference twice to kill fixed confounders and common trends. The estimate is causal only under **parallel trends — untestable by construction** — and the danger is timing variation, not sample size. | [`02-quasi-experimental.md`](../industry-playbook/02-quasi-experimental.md) |
| **4** | [Regression Discontinuity](./04-regression-discontinuity/) | A business rule's arbitrary cutoff is a natural experiment: units just above vs. just below are as-good-as-randomized. Cleanest identification in observational work, **narrowest estimand** (a LATE at the cutoff), and it dies on one thing — **manipulation of the running variable.** | [`02-quasi-experimental.md`](../industry-playbook/02-quasi-experimental.md) |
| **5** | [Instrumental Variables](./05-instrumental-variables/) | When treatment is confounded and no design exists, find a lever that moves treatment without touching the confounder. IV **swaps** unconfoundedness for the **untestable exclusion restriction** — and dies on weak instruments or backdoor channels. Estimand: LATE / ACR for compliers. | [`02-quasi-experimental.md`](../industry-playbook/02-quasi-experimental.md) |
| **6** | [Synthetic Control & Counterfactual Estimators](./06-synthetic-control/) | One or a few treated units, non-parallel controls: **build** the counterfactual from a weighted blend of donors. Convex hull is a feature until it's a wall — then escalate to SDID (subtract the level) or matrix completion (impute messy rollouts). Inference is by **permutation, not standard errors.** | [`02-quasi-experimental.md`](../industry-playbook/02-quasi-experimental.md) |
| **8** | [Selection on Observables](./08-selection-on-observables/) | No design at all — assume you measured every confounder, then match or weight. The pivot to the observational world. **PSM solves the curse of dimensionality, not selection bias**; overlap is where it dies; **doubly-robust (AIPW) is the default** — unbiased if *either* model is right. | [`03-observational.md`](../industry-playbook/03-observational.md) |

### Lecture 2 chapters

| # | Chapter | Core idea |
| --- | --- | --- |
| 2.1 | [RCT & Assumptions](./02-experimentation/2.1-rct-and-assumptions.md) | Randomization buys one assumption of four. SUTVA, attrition, and compliance are still yours — and SUTVA fails silently. |
| 2.2 | [Power & Multi-Arm](./02-experimentation/2.2-power-and-multi-arm.md) | The inverse-square law: halving the MDE quadruples runtime. Four arms turn a 10-day test into 35 days. |
| 2.3 | [Cluster Randomization](./02-experimentation/2.3-cluster-randomization.md) | Cluster on the graph the treatment *interferes* along, not the graph you have. Effective N → K/ρ. |
| 2.4 | [Geo Experiments & iROAS](./02-experimentation/2.4-geo-experiments.md) | iROAS **is** a Wald ratio — a local derivative, not an average return. 210 DMAs are worth ~13 effective units. |
| 2.5 | [Switchbacks](./02-experimentation/2.5-switchbacks.md) | The window must exceed the washout. Optimal designs throw away most of the data, and that's correct. |
| 2.6 | [Ramp-Up & Bandits](./02-experimentation/2.6-ramp-up-and-bandits.md) | Change enrolled traffic freely; change the T:C ratio never. A homogeneous +1.0 effect reads as +4.81 if you break that rule. |

### Lecture 3 chapters

| # | Chapter | Core idea |
| --- | --- | --- |
| 3.1 | [Classic 2×2 & Geo-Controls](./03-difference-in-differences/3.1-classic-did-and-geo-controls.md) | δ is the interaction coefficient; a 2-period design has *zero* testable pre-trends, so the Miami tourist trap needs a historical placebo, not an event study. |
| 3.2 | [Synthetic Control](./03-difference-in-differences/3.2-synthetic-control.md) *(bridge)* | The weighted-control idea in one screen; full treatment in [Lecture 6](./06-synthetic-control/). |
| 3.3 | [Staggered DiD: The TWFE Trap and Its Fixes](./03-difference-in-differences/3.3-staggered-did.md) | TWFE uses already-treated units as controls (a true +3.98 effect reports as −1.24). Then the fix: every modern estimator implements "never control on the already-treated," and CS assumes *absorbing* treatment — for a toggle-able feature you pivot to de Chaisemartin-D'Haultfœuille. |
| 3.4 | [Triple Differences](./03-difference-in-differences/3.4-triple-differences.md) | A second control dimension differences out a shock. Verified: a naive DiD reports +28 for a true +8; DDD recovers +8.3. |

### Lecture 4 chapters

| # | Chapter | Core idea |
| --- | --- | --- |
| 4.1 | [Sharp RDD](./04-regression-discontinuity/4.1-sharp-rdd.md) | Local randomization at an arbitrary cutoff. Why you center `X−c`: verified, the D coefficient is the jump (5.03) centered, garbage (−69.9) uncentered. |
| 4.2 | [Fuzzy RDD](./04-regression-discontinuity/4.2-fuzzy-rdd.md) | The cutoff as an instrument; a local Wald/LATE for compliers. The 10% shadowban effect is for the *borderline* users only — not always-takers or never-takers. |
| 4.3 | [Regression Kink Design](./04-regression-discontinuity/4.3-regression-kink.md) | The policy changes *slope*, not level. Effect = ratio of slope-changes (α₂/γ₂); verified 0.79 vs true 0.8. |
| 4.4 | [Geographic RD](./04-regression-discontinuity/4.4-geographic-rd.md) | A border is the cutoff; distance is the running variable. The placebo-border test separates policy-gaming from natural spatial clustering. |

### Lecture 5 chapters

| # | Chapter | Core idea |
| --- | --- | --- |
| 5.1 | [Standard 2SLS](./05-instrumental-variables/5.1-standard-2sls.md) | 2SLS = reduced form ÷ first stage (verified: OLS biased 2.84, IV recovers 2.01). Weak instruments bias you back toward OLS *and* explode SEs. |
| 5.2 | [Shift-Share / Bartik](./05-instrumental-variables/5.2-shift-share-bartik.md) | Shares × shocks. Identification is share-based (GPSS) *or* shock-based (BHJ) — you must pick. Shopify/iOS 14.5 → shock-based is the only defensible one. |
| 5.3 | [Judge / Examiner IV](./05-instrumental-variables/5.3-judge-examiner-iv.md) | Leave-one-out leniency; many-dummy 2SLS biased 19% toward OLS, LOO fixes it. The Ramp probes + a full review of the collection-agent IV (an ACR, with a within-call exclusion threat). |

### Lecture 6 chapters

| # | Chapter | Core idea |
| --- | --- | --- |
| 6.1 | [Classic Synthetic Control](./06-synthetic-control/6.1-classic-scm.md) | Convex-hull weights, permutation inference (rank by post/pre RMSPE ratio), leave-one-out robustness. Verified: recovers 0.59 Boston + 0.41 Austin, ATT 15.3 vs. true 15. |
| 6.2 | [Augmented SCM & Synthetic DiD](./06-synthetic-control/6.2-ascm-and-sdid.md) | When the treated unit is a level outlier, classic SCM flatlines (17,184 for a true 500). SDID absorbs the gap with a fixed effect (recovers 497); ASCM extrapolates with ridge — riskier. |
| 6.3 | [Matrix Completion](./06-synthetic-control/6.3-matrix-completion.md) | Causal inference as a missing-data problem: delete treated cells, impute via low-rank. Handles staggered + toggling + many treated units; verified 2.05 vs true 2.0. |

### Lecture 8 chapters

| # | Chapter | Core idea |
| --- | --- | --- |
| 8.1 | [Propensity Score & Unconfoundedness](./08-selection-on-observables/8.1-propensity-and-unconfoundedness.md) | Rosenbaum-Rubin collapses 50 covariates to one score. The golden rule: PSM solves the curse of dimensionality, *not* selection bias. High AUC ≠ no confounders; "too high" kills overlap. The Spotify opt-in trap. |
| 8.2 | [Propensity Score Matching](./08-selection-on-observables/8.2-propensity-score-matching.md) | End-to-end DoorDash: estimate → overlap trim → caliper match → Love plot (SMD < 0.1) → ATT → Rosenbaum Γ. Matching → ATT is a difference of matched means. |
| 8.3 | [Inverse Probability Weighting](./08-selection-on-observables/8.3-inverse-probability-weighting.md) | Reweight into a pseudo-population. Treated weight = 1 for ATT (they *are* the target), 1/e(X) for ATE. Extreme propensities explode the variance. |
| 8.4 | [Doubly Robust / AIPW](./08-selection-on-observables/8.4-doubly-robust-aipw.md) | Two chances to be right — verified: unbiased if *either* model correct (bias +0.01 / +0.00), biased only if both wrong (+0.36). Weights hit residuals not raw outcomes (DoorDash: 2,000 vs 50,000). |
| 8.5 | [Advanced Matching & Weighting](./08-selection-on-observables/8.5-advanced-matching-and-weighting.md) | Beyond PSM (King-Nielsen). Entropy balancing = exact moment balance by construction (verified ~1e-6), for pipelines. CEM = stakeholder-verifiable pairs but prunes hard (500 survive at 4 covariates, 14% at 8). Mahalanobis for ≤8 continuous. |

*More lectures to come — the series is written topic by topic.*

---

## The shape of a lecture

Every lecture follows the same nine-part structure, so the set reads as
one book rather than a pile of notes:

1. **The question it answers** — and why the naive answer fails
2. **Setup and notation** — potential outcomes, consistent across lectures
3. **The identification argument** — derived, not asserted
4. **What the assumptions buy you** — and how each one breaks
5. **The identification hierarchy** — what's available, what isn't, at what credibility
6. **Worked example** — realistic, with numbers, end-to-end
7. **Estimation in Python** — runnable, with the wrong way shown and labeled
8. **Common misreadings** — the errors that pass code review
9. **Summary + references** — with section-level pointers, not just citations

---

## Conventions

- **Math** is LaTeX. Renders natively on GitHub; converts cleanly to
  Jupyter, Quarto, PDF, or a static site.
  - **Inline:** `$...$`.
  - **Display, single line:** `$$...$$` is fine.
  - **Display, multi-line: use a ```` ```math ```` fenced block — never
    `$$`.** GitHub does not reliably parse a multi-line `$$` block as
    math, and when it fails, markdown eats the body: `_` pairs become
    `<em>` (deleting your subscripts) and a leading `+ ` becomes a
    bullet list. The formula isn't just unrendered, it's *corrupted* —
    and it looks fine in every local previewer. Fenced blocks are immune
    because fenced code is never markdown-parsed.
- **Currency is always escaped: `\$50,000`, never `$50,000`.** GitHub reads
  `$...$` as inline math, so two bare amounts on one line — `$250k–$1.25M`
  — make the parser treat `250k–` as math and swallow it. Inside a math
  block, `\$` is already correct LaTeX.
- **Run `python3 check-math.py` before committing.** It catches both
  failure modes above — currency-shaped inline spans (while ignoring real
  math like `$i$`, `$2^n$`, `$1/\pi = 5\times$`) and multi-line `$$`
  blocks. Both render fine in local previewers and break only on GitHub,
  which is exactly why they need a checker and not a reviewer.
- **DAGs** are ASCII box-and-arrow, so they diff in git, need no build
  step, and never rot. Assumed-absent arrows are drawn dashed and
  labeled — because in a DAG, the missing arrows *are* the assumptions.
- **Code** is Python, matching the packages in
  [`code-templates.md`](../skills/causal-inference/code-templates.md).
- **Notation** is stable across lectures: $Z$ assignment, $D$ treatment
  received, $X$ covariates, $Y$ outcome, $\tau$ treatment effect.

---

## How to read

If you're new: **read Lecture 1**, then jump to whichever lecture matches
your design. The lectures after 1 are largely independent — they all
assume the potential-outcomes vocabulary and nothing else.

If you're preparing for an interview: the *Common misreadings* section of
each lecture is the highest-yield page in this repo. Those are the
answers that separate a senior response from a staff one.

If you're defending an estimate: read the lecture for your method, then
[`06-defending-estimates.md`](../industry-playbook/06-defending-estimates.md).
