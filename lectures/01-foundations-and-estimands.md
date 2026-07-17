# Lecture 1 — Foundations of Causal Inference & Treatment Effects

> **Prerequisites:** none. This is the entry point.
> **Deepens:** [`industry-playbook/00-foundations.md`](../industry-playbook/00-foundations.md) (the vocabulary table) and Phase 1 of [`skills/causal-inference/SKILL.md`](../skills/causal-inference/SKILL.md) (problem framing).
> **Next:** Lecture 2 — Randomization and the Experimental Ideal.

---

## 1. The question this lecture answers

> *"We ran the test. Revenue went up. How much of that did we cause?"*

Every causal question is a comparison between something that happened and something that didn't. The something-that-didn't is the problem: it is not in your data, it is not recoverable by collecting more data, and no amount of model complexity conjures it. This lecture builds the framework that makes the missing half of the comparison *explicit*, then shows that the choice of **which** average effect you report is not a technicality — it can reverse a business decision.

The punchline, stated up front so you know where we're going: **an estimand is a claim about a policy you could actually execute.** Pick the estimand that matches the lever your stakeholder can pull. Most bad causal analyses in industry are not estimation failures. They are estimand failures — the math is right and it answers a question nobody asked.

---

## 2. The fundamental problem of causal inference

### 2.1 Potential outcomes (the Rubin Causal Model)

Fix a unit $i$ — a user, an account, a store, a market. Fix a binary treatment. Define two numbers:

- $Y_i(1)$ — the outcome that *would* occur if unit $i$ receives treatment.
- $Y_i(0)$ — the outcome that *would* occur if unit $i$ does not.

Both are properties of the unit. They exist before you assign anything, in the same sense that a coin has a weight before you weigh it. The **individual treatment effect** is their difference:

$$\tau_i = Y_i(1) - Y_i(0)$$

Now the trap. Let $D_i \in \{0,1\}$ record what actually happened. What you observe is:

$$Y_i^{\text{obs}} = D_i \cdot Y_i(1) + (1 - D_i) \cdot Y_i(0)$$

Read that equation slowly, because it is the whole lecture. It says: **treatment does not create the outcome, it selects which pre-existing potential outcome becomes visible.** The other one doesn't get destroyed. It just never surfaces. That unobserved value is the **counterfactual**.

This is the *fundamental problem of causal inference* (Holland, 1986): $\tau_i$ is never identified for any single $i$, in any dataset, ever. It is a missing-data problem where exactly 50% of the required data is missing by construction, and the missingness is total for every row.

> **Why this framing earns its keep.** Notice we defined the causal effect *without mentioning a regression, a model, or a dataset.* The estimand is defined in the world; the estimator comes later. Junior analysts define effects by the coefficient they ran. Staff analysts define the effect first and then ask what procedure recovers it. Every method in this repo — DiD, RDD, IV, DML — is a strategy for imputing the missing column of this table, and nothing more.

### 2.2 The science table

Here's the data God would give you:

| Unit | $Y_i(0)$ | $Y_i(1)$ | $\tau_i$ | $D_i$ | $Y_i^{\text{obs}}$ |
|------|----------|----------|----------|-------|--------------------|
| 1 | 10 | 14 | +4 | 1 | 14 |
| 2 | 8 | 8 | 0 | 0 | 8 |
| 3 | 12 | 9 | −3 | 1 | 9 |
| 4 | 15 | 20 | +5 | 0 | 15 |

And here's your actual dataset — the same table with a cloth thrown over it:

| Unit | $Y_i(0)$ | $Y_i(1)$ | $\tau_i$ | $D_i$ | $Y_i^{\text{obs}}$ |
|------|----------|----------|----------|-------|--------------------|
| 1 | **?** | 14 | **?** | 1 | 14 |
| 2 | 8 | **?** | **?** | 0 | 8 |
| 3 | **?** | 9 | **?** | 1 | 9 |
| 4 | 15 | **?** | **?** | 0 | 15 |

Two facts fall out immediately, and they organize everything that follows.

**Fact 1: the $\tau_i$ column is gone and it is not coming back.** So we retreat to averages. Averages of $\tau_i$ over well-chosen *groups* can be recovered even though no individual entry can. Which group you average over is precisely the choice of estimand — Section 4.

**Fact 2: unit 3 has a negative effect.** In the observed table, unit 3 looks like a middling outcome (9) among the treated. The treatment *hurt* them, and no inspection of the observed data reveals this. This is why "the treated group did well" is not evidence of anything, and why **heterogeneity is the normal case, not an edge case**. An ATE of zero is fully consistent with the treatment helping half your users a lot and hurting the other half a lot.

### 2.3 SUTVA: the assumption hiding in the notation

Writing $Y_i(1)$ and $Y_i(0)$ already smuggled in an assumption, and it's easy to miss because it's encoded in what we *didn't* write. We gave unit $i$ two potential outcomes, indexed only by $i$'s own treatment. In full generality, $i$'s outcome could depend on the entire assignment vector $\mathbf{D} = (D_1, \dots, D_n)$ — that's $2^n$ potential outcomes per unit.

**SUTVA** (Stable Unit Treatment Value Assumption) is what collapses $2^n$ down to $2$. It has two parts:

1. **No interference.** Unit $i$'s outcome doesn't depend on unit $j$'s treatment. This is violated constantly in the settings we care about: marketplaces (your treated buyers bid up prices for control buyers), social products (treated users invite control users), ad auctions (treated campaigns exhaust shared budget), and — see Section 6 — **B2B SaaS, where the unit of randomization is the user but the unit of behavior is the account.**
2. **No hidden variations of treatment.** "Received the dashboard" must mean one thing. If half the compliers glanced at it once and half rebuilt their workflow around it, $Y_i(1)$ isn't well-defined, and your "effect" is an average over an undefined mixture.

When SUTVA fails, you haven't made an estimation error. You've made a *definition* error: the quantity you're estimating doesn't exist. That is a much worse place to be, and no robustness check will find it for you — it's not in the data. It's in the notation you chose on line one.

---

## 3. The causal graph

A DAG is a picture of your assumptions about the data-generating process. Its power isn't the drawing — it's that **the absent arrows are the assumptions**, and drawing forces you to state them.

### 3.1 The standard experimental setup with non-compliance

```
                    ┌───────────────┐
                    │       X       │
                    │  Confounders  │
                    │  (tenure,     │
                    │   platform,   │
                    │   firm size)  │
                    └───────────────┘
                       │         │
                       │         │
             ┌─────────┘         └─────────┐
             │                             │
             ▼                             ▼
  ┌──────┐        ┌───────────┐        ┌─────────┐
  │  Z   │───────▶│     D     │───────▶│    Y    │
  │      │        │           │        │         │
  │Assign│        │ Treatment │        │ Outcome │
  │-ment │        │ RECEIVED  │        │(revenue)│
  │(email│        │ (opened   │        │         │
  │ sent)│        │ dashboard)│        │         │
  └──────┘        └───────────┘        └─────────┘
      ╎                                     ▲
      ╎                                     ╎
      └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
         EXCLUSION RESTRICTION: this arrow
         must NOT exist. Z may affect Y only
         by way of D. (Dashed = assumed absent.)
```

Read the graph as four claims:

| Structure | Claim |
|-----------|-------|
| $Z \rightarrow D$ | **Relevance.** Assignment moves take-up. Testable — it's the first stage, and you can see it in the logs. |
| $D \rightarrow Y$ | The causal effect we want. |
| $X \rightarrow D$, $X \rightarrow Y$ | **Confounding.** $X$ is a common cause, opening the back-door path $D \leftarrow X \rightarrow Y$. This is why $E[Y \mid D=1] - E[Y \mid D=0]$ is not causal: it mixes the effect with the fact that different kinds of people take treatment. |
| **No** $X \rightarrow Z$ | **Randomization.** Nothing causes assignment. This is the one arrow you get to delete by *design* rather than by argument, and it's the entire value of running an experiment. |
| **No** $Z \rightarrow Y$ direct | **Exclusion restriction.** Assignment affects the outcome only through take-up. Assumed, **never testable**, and in this scenario it is the assumption most likely to be false (Section 6.6). |

### 3.2 What confounding actually is

The naive comparison decomposes exactly:

```math
\underbrace{E[Y \mid D=1] - E[Y \mid D=0]}_{\text{what you can compute}}
= \underbrace{E[Y(1) - Y(0) \mid D=1]}_{\text{ATT, the causal part}}
+ \underbrace{E[Y(0) \mid D=1] - E[Y(0) \mid D=0]}_{\text{selection bias}}
```

The second term compares the treated and untreated groups **in the same state of the world** — both untreated. If they'd have differed anyway, that difference contaminates your estimate one-for-one. Power users adopt the analytics dashboard *and* spend more regardless; the selection bias term is large and positive, and it doesn't shrink with sample size. This decomposition is worth committing to memory: it says the enemy is not noise. Adding data makes noise vanish and leaves bias untouched.

---

## 4. The estimands

All five are averages of the same $\tau_i$. They differ **only in whom you average over**, and that is exactly why they answer different questions.

### ATE — Average Treatment Effect

$$\text{ATE} = E[Y_i(1) - Y_i(0)]$$

Average over *everyone*. Answers: **"What if we forced the whole population into treatment, versus forced nobody?"**

The word *forced* is doing real work. ATE is the effect of a hypothetical intervention where compliance is universal — it is a statement about a world in which every user opens the dashboard. If you cannot execute that intervention, ATE is not a decision-relevant quantity, however much it feels like the "real" answer. It is the default estimand of an RCT with full compliance, and only then.

### ATT — Average Treatment Effect on the Treated

$$\text{ATT} = E[Y_i(1) - Y_i(0) \mid D_i = 1]$$

Average over those who actually got treated. Answers: **"For the people who took it, how much did it help them relative to their own counterfactual?"**

Note carefully what the conditioning bar does *not* do: it does not compare treated to untreated people. Both potential outcomes are still evaluated *for the same treated units*. The counterfactual $Y_i(0) \mid D_i = 1$ — how treated users would have done untreated — remains unobserved. ATT is the natural estimand for program evaluation and for observational work, since "what would have happened to the enrollees" is usually the policy question.

### CATE — Conditional Average Treatment Effect

$$\tau(x) = E[Y_i(1) - Y_i(0) \mid X_i = x]$$

Average within a covariate cell. Answers: **"Whom should we treat?"**

CATE is a *function*, not a number — the one estimand on this list that returns a curve. Averaging it back gives you the others: $\text{ATE} = E[\tau(X)]$. It's the foundation of targeting and uplift (Lecture 8; [`industry-playbook/04-heterogeneity-and-targeting.md`](../industry-playbook/04-heterogeneity-and-targeting.md)).

### ITT — Intention-To-Treat

$$\text{ITT} = E[Y_i \mid Z_i = 1] - E[Y_i \mid Z_i = 0]$$

The effect of **assignment**, compliance be damned. Answers: **"What happens if we launch this?"**

ITT is the odd one out in an important way: it is defined on *observable* quantities. Both terms are things you can compute from data. Under randomization it needs no assumptions beyond SUTVA — no exclusion, no monotonicity, no unconfoundedness. It is the most credible number in the entire framework and, in industry, usually the most decision-relevant, because **a launch is an offer, not an installation.** You ship the email. You do not ship the opening of the email.

Non-compliance mechanically drags ITT toward zero relative to the effect on users who engage. That attenuation is not a bug to be corrected away. It is a real feature of the policy you'd actually be shipping.

### LATE / CACE — Local Average Treatment Effect

$$\text{LATE} = E[Y_i(1) - Y_i(0) \mid i \text{ is a complier}]$$

Average over **compliers** only. Identified via the Wald ratio:

$$
\text{LATE} = \frac{E[Y \mid Z=1] - E[Y \mid Z=0]}{E[D \mid Z=1] - E[D \mid Z=0]} = \frac{\text{ITT}}{\text{first stage}}
$$

> **Note on your source notes.** Your paste rendered this as `LATE = E[D|Z=1] − E[D|Z=0]ITT`, which garbles it. The structure to hold onto: **LATE is ITT divided by the compliance rate.** Since the denominator is a probability in $(0, 1]$, LATE is always *larger in magnitude* than ITT. It has to be — you're attributing the entire assignment effect to the fraction of people who responded to assignment.

**Who are the compliers?** Assignment $Z$ and take-up $D$ partition the population into four latent types, defined by how a unit *would* behave under each assignment:

| Type | $D(Z{=}0)$ | $D(Z{=}1)$ | Description |
|------|-----------|-----------|-------------|
| **Complier** | 0 | 1 | Takes it iff offered. |
| **Never-taker** | 0 | 0 | Ignores the offer. |
| **Always-taker** | 1 | 1 | Gets it regardless. |
| **Defier** | 1 | 0 | Takes it iff *not* offered. Perverse. |

**Monotonicity** is the assumption that defiers don't exist. Combined with exclusion, it's what makes the Wald ratio equal a complier average rather than an uninterpretable mixture.

Here is the thing everyone gets wrong: **complier status is a latent trait, not an observed group.** You cannot filter your dataframe to compliers. In the treated arm you see who took it, but in the control arm compliers and never-takers are indistinguishable — both have $D = 0$. LATE identifies an average over a subpopulation you can *count* but cannot *name*. Which means:

- **LATE is defined by your instrument.** Change the email subject line and you change the complier population, and hence the estimand. A more aggressive nudge recruits more marginal users, and LATE moves — not because the treatment changed, but because *who complies* changed.
- **Compliers are self-selected.** They are, by construction, the people most responsive to being offered the thing. There is no reason to expect never-takers, if you could force them, to respond like compliers. Every reason to expect they wouldn't. That's what makes them never-takers.

---

## 5. The identification hierarchy

The estimands are not equally available. Here's what randomizing $Z$ buys you, and where it stops:

```
   Randomize Z
        │
        ├──▶ ITT ────── identified. Assumptions: randomization + SUTVA.
        │               CREDIBILITY: ★★★★★  ← nothing to argue about
        │
        ├──▶ LATE ───── identified. + exclusion + monotonicity + relevance.
        │               CREDIBILITY: ★★★☆☆  ← exclusion is untestable
        │
        └──▶ ATE ────── NOT identified. Requires extrapolating the effect
                        onto never-takers, who by definition never reveal
                        Y(1) to anyone, under any assignment you can run.
                        CREDIBILITY: ★☆☆☆☆  ← requires a modeling assumption
                                              the design cannot support
```

Sit with the bottom row. **A perfectly executed 50k/50k randomized experiment does not identify the ATE if compliance is partial.** No sample size fixes it. The never-takers' $Y(1)$ is not rare in your data — it is *structurally absent*, because the only lever you have is $Z$, and they don't respond to $Z$. To get ATE you'd need a stronger instrument (one that makes them comply, i.e. a different experiment) or a homogeneity assumption ("never-takers respond like compliers") that the design gives you no way to check and that common sense says is false.

This is the single most under-appreciated fact in industry experimentation, and it's why the CFO's question in Section 6 has a subtle answer.

---

## 6. Worked example: the SaaS analytics dashboard

### 6.1 Setup

A SaaS company tests an **Advanced Analytics Dashboard**.

| | Control ($Z=0$) | Treatment ($Z=1$) |
|---|---|---|
| Users | 50,000 | 50,000 |
| Offer | none | email invitation |
| Access to dashboard | **impossible** | via email click-through |
| Actually used it ($D=1$) | 0 | 10,000 |

Full user base: 5,000,000. Feature cost: **\$50,000/month** in cloud compute.

### 6.2 The structural fact that drives everything

Control users **cannot access the dashboard at all**. Therefore:

$$P(D = 1 \mid Z = 0) = 0$$

This is **one-sided non-compliance**, and it has two consequences that most treatments of this problem skip:

**(a) There are no always-takers.** Nobody gets the dashboard without the offer. The population contains only compliers (20%) and never-takers (80%).

**(b) Monotonicity holds by construction — it is not an assumption here.** A defier would need $D(Z{=}0) = 1$, i.e. use a product they cannot reach. The design makes defiance physically impossible. One of the two load-bearing IV assumptions comes free. (Exclusion does not — see §6.6.)

### 6.3 The collapse: LATE = ATT

Now the payoff, and the reason your notes list ATT and LATE as separate answers when here they are the same number.

$\text{ATT} = E[\tau_i \mid D_i = 1]$ conditions on *actually treated* users. Who are they? Only users with $Z=1$ **and** complier type — because $Z=0$ forecloses $D=1$, and never-takers don't take. So conditioning on $D = 1$ **is** conditioning on complier status:

$$
\text{ATT} = E[\tau_i \mid D_i = 1] = E[\tau_i \mid \text{complier}, Z_i = 1] = E[\tau_i \mid \text{complier}] = \text{LATE}
$$

(The middle step drops $Z_i=1$ because $Z$ is randomized, hence independent of the latent type $\tau_i$.)

**Under one-sided non-compliance, ATT and LATE are the same estimand.** The "local" in LATE stops being a caveat about a weird subgroup and becomes a precise description of the treated population — which is exactly the group the VP is asking about. This is a genuinely lucky feature of the design, and it's worth recognizing on sight, because in two-sided non-compliance (where control users can get the feature some other way) it is **false**, and conflating ATT with LATE there is a real error.

### 6.4 The numbers

Suppose monthly revenue per user:

$$\bar{Y}_{Z=1} = \$12.05, \qquad \bar{Y}_{Z=0} = \$12.00, \qquad \text{sd}(Y) \approx \$2.00$$

**ITT:**

$$\widehat{\text{ITT}} = 12.05 - 12.00 = \$0.05 \text{ per assigned user per month}$$

$$\text{SE} = 2.00 \times \sqrt{\tfrac{1}{50{,}000} + \tfrac{1}{50{,}000}} \approx \$0.0126 \quad \Rightarrow \quad t \approx 4.0, \;\; \text{95\% CI } [\$0.025,\; \$0.075]$$

**First stage:**

$$\widehat{\pi} = P(D{=}1 \mid Z{=}1) - P(D{=}1 \mid Z{=}0) = 0.20 - 0 = 0.20$$

**LATE (= ATT here):**

$$\widehat{\text{LATE}} = \frac{0.05}{0.20} = \$0.25 \text{ per complier per month}$$

$$\text{SE} \approx \frac{0.0126}{0.20} \approx \$0.063 \quad \Rightarrow \quad \text{95\% CI } [\$0.13,\; \$0.37]$$

Note the SE inflated by the same $1/0.20 = 5\times$ factor as the point estimate. Rescaling by the first stage rescales your uncertainty too — there is no free precision in the Wald ratio. At $\pi = 0.20$ with $n = 50{,}000$ this is fine (the first-stage $F$ is enormous). Below roughly $\pi \approx 0.05$ you're in weak-instrument territory and the ratio's finite-sample behavior degrades badly — the sampling distribution gets fat tails and conventional CIs undercover.

### 6.5 Answering the two questions

#### Q1 — The VP: *"How much value does the dashboard provide when people actually use it?"*

**Answer: LATE = \$0.25/user/month.** And because of §6.3, that *is* the ATT — the effect on the treated — so the VP gets the mechanism question answered exactly.

Compute it as the Wald ratio, or equivalently 2SLS of $Y$ on $D$ instrumented by $Z$.

But hand it over with the caveat attached, because the VP will misuse it otherwise:

> This is the effect **for the 20% who chose to open it.** They self-selected on interest in analytics. They are almost certainly your power users — the ones with enough data in the product for a dashboard to say anything, and enough engagement to read email. The other 80% are not a random sample of "people who haven't tried it yet"; they are people who **revealed they don't want it.** \$0.25 is not what a never-taker would get if you forced the dashboard on them, and this experiment cannot tell you what that number is.

If the VP responds *"fine, then let's make everyone use it"* — that's a request for the ATE, and §5 says you don't have it. Say so. The honest answer is: run a stronger instrument (a more aggressive nudge, an in-product forced surface) and see whether LATE moves as compliance rises. If LATE stays flat as you pull in more marginal users, that's evidence of homogeneity. If it drops, you've learned the effect is concentrated in the enthusiasts and further push has poor returns. **That sequence — instrument strength as a probe of heterogeneity — is the actual answer to "what about everyone else," and it's a roadmap item, not a query.**

#### Q2 — The CFO: *"\$50k/month in compute. Roll out to all 5M?"*

**Answer: ITT = \$0.05/user/month.** Not LATE. Here's the reasoning chain, and it's the whole lecture in miniature.

**Match the estimand to the executable policy.** The CFO isn't buying a dashboard-usage event. They're buying *the launch* — ship the feature, send the email, pay the compute for everyone the system serves. Under that policy, the realized uptake will be about 20%, exactly as in the test. **ITT is the estimand whose defining intervention is the one the CFO can actually authorize.** LATE's defining intervention — "make 5M people be compliers" — is not on the menu.

$$\text{Incremental revenue} = 5{,}000{,}000 \times \$0.05 = \$250{,}000/\text{month}$$

$$\text{Net} = \$250{,}000 - \$50{,}000 = +\$200{,}000/\text{month} \quad \Rightarrow \quad \textbf{ship}$$

Breakeven ITT is $\$50{,}000 / 5\text{M} = \$0.01$/user/month. The observed \$0.05 clears it 5×, and the CI lower bound (\$0.025) clears it 2.5×. The decision is robust to sampling error — which is the check that makes this a recommendation rather than a point estimate.

**Now the trap.** Suppose you'd handed the CFO the LATE, because it's the bigger number and it "isolates the true effect":

$$5{,}000{,}000 \times \$0.25 = \$1{,}250{,}000/\text{month} \quad \text{(WRONG — 5× overstated)}$$

This forecast asserts that all 5M users will behave like compliers. 80% of them will never open the thing. You've multiplied a per-complier effect by a population count, which is a units error dressed up as an analysis — the *per*-denominators don't match.

Here it happens not to flip the decision: both numbers say ship. **That's the dangerous case, not the safe one** — the error passes review because the conclusion was right, and it survives to be repeated. Watch where it bites:

| Monthly cost | ITT verdict (correct) | Naive LATE verdict | Agree? |
|---|---|---|---|
| \$50,000 | Ship (+\$200k) | Ship (+\$1.2M) | ✓ — but for the wrong reason |
| \$400,000 | **Don't ship** (−\$150k) | Ship (+\$850k) | ✗ **flips** |
| \$1,000,000 | **Don't ship** (−\$750k) | Ship (+\$250k) | ✗ **flips** |
| \$2,000,000 | Don't ship | Don't ship | ✓ |

**There is a \$250k–\$1.25M/month band where the choice of estimand, not the data, determines whether you ship.** Same experiment, same clean randomization, same correctly-computed statistics — opposite decisions. This is what "estimand failure" means concretely, and why §4's framing (an estimand is a claim about a policy you could execute) is the load-bearing idea in this lecture.

**When ITT is the wrong answer for the CFO:** if the compute cost were *per active user* rather than a flat platform fee, the economics change — you'd only pay for the 20% who use it, so compare per-complier value (\$0.25) against per-complier cost. The rule isn't "always report ITT to finance." The rule is **match the estimand's denominator to the cost's denominator.** Flat cost over the population → population-average effect (ITT). Cost per user served → effect per user served (LATE). Getting this right is just dimensional analysis, and it catches most real-world versions of this mistake.

### 6.6 What would break this analysis

The estimates above are only as good as the assumptions. Four threats, roughly in order of how much they should worry you:

**1. Exclusion restriction (the serious one).** The email itself may move revenue for people who never open the dashboard — a subject line reading "New: Advanced Analytics" reminds a lapsed user the product exists, and they log in and do something unrelated. Then $Z \rightarrow Y$ directly, the dashed arrow in §3.1 is real, and the Wald ratio attributes the *entire* ITT to the 20% who complied when part of it belongs to the other 80%. **LATE is biased away from zero, and the bias is amplified by $1/\pi = 5\times$.** This is untestable by construction, but it is *bound-able*: if never-takers respond to the email at all, you can partially identify LATE, and a placebo email (same send, no dashboard behind it) measures the direct channel directly. **Note that ITT is completely immune to this** — "the effect of sending the email" includes the reminder effect, and if the reminder effect is part of what you'd ship, it *belongs* in the number. That immunity is the deep reason ITT is the CFO's estimand and not merely the conservative choice.

**2. SUTVA / interference.** This is B2B SaaS. Users sit in accounts. A complier exports the dashboard to a Slack channel, and their untreated colleague — possibly randomized to control — acts on it. Control is contaminated, the ITT is attenuated toward zero, and you're *understating* the effect. Fix by randomizing at the **account** level and clustering the SEs there (Lecture 3). If the assignment unit and the behavior unit differ, the design is wrong before any estimation happens.

**3. Hidden variations of treatment.** "Used the dashboard" pools one accidental click with daily power use. $Y_i(1)$ isn't well-defined across that range, so LATE averages over an undefined mixture. Sharpen $D$ to a meaningful threshold — but note that thresholding on a *post-treatment* behavior re-introduces selection. Define it in the pre-registration, not after looking.

**4. Weak first stage.** Not a problem at $\pi = 0.20$. Would be at $\pi = 0.02$, where the Wald denominator is near zero, the ratio's distribution is non-normal, and conventional CIs badly undercover.

---

## 7. Estimation in Python

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.iv import IV2SLS

# df columns: Z (assigned), D (used dashboard), Y (monthly revenue)

# ---- ITT: assignment -> outcome. Requires only randomization. ----
itt = sm.OLS(df["Y"], sm.add_constant(df[["Z"]])).fit(cov_type="HC1")
print(itt.summary())          # coef on Z = ITT = 0.05

# ---- First stage: assignment -> take-up. Check relevance. ----
fs = sm.OLS(df["D"], sm.add_constant(df[["Z"]])).fit(cov_type="HC1")
pi = fs.params["Z"]           # 0.20
print(f"first stage = {pi:.3f}, F = {fs.tvalues['Z'] ** 2:.1f}")
# Rule of thumb: F > 10. Here F is in the thousands.

# ---- LATE: Wald ratio. Identical to 2SLS with one instrument. ----
late_wald = itt.params["Z"] / pi
print(f"LATE (Wald) = {late_wald:.3f}")   # 0.25

# ---- LATE via 2SLS: same point estimate, correct SEs for free. ----
# The Wald SE needs the delta method; 2SLS just gives it to you.
late_2sls = IV2SLS(
    dependent=df["Y"],
    exog=sm.add_constant(df[["Z"]])[["const"]],
    endog=df["D"],
    instruments=df["Z"],
).fit(cov_type="robust")
print(late_2sls.summary)      # coef on D = 0.25, SE = 0.063

# ---- If randomizing at the account level, cluster there. ----
# late_2sls = IV2SLS(...).fit(cov_type="clustered", clusters=df["account_id"])

# ---- The decision, in the estimand the decision actually requires. ----
N_USERS, MONTHLY_COST = 5_000_000, 50_000
lo, hi = itt.conf_int().loc["Z"]
print(f"ITT-based net:  ${N_USERS * itt.params['Z'] - MONTHLY_COST:>12,.0f}/mo")
print(f"  worst case:   ${N_USERS * lo - MONTHLY_COST:>12,.0f}/mo")
print(f"breakeven ITT:  ${MONTHLY_COST / N_USERS:.4f}/user/mo")

# WRONG — do not do this. Multiplies a per-complier effect by a
# population count. The denominators don't match.
# print(N_USERS * late_wald - MONTHLY_COST)
```

**Two notes.** (i) Never hand-roll the Wald SE by dividing the ITT's SE by $\hat\pi$ — that treats $\hat\pi$ as known when it's estimated. It's a decent approximation at high compliance (which is why §6.4's back-of-envelope is fine) and wrong when compliance is low. 2SLS handles the delta method for you. (ii) With one instrument and one endogenous regressor the system is *just-identified*, so 2SLS = Wald = IV exactly. With multiple instruments they diverge, and 2SLS becomes an efficiency-weighted combination — a different estimand, weighted by each instrument's complier population.

---

## 8. Common misreadings

**"ITT is the conservative/watered-down estimate; LATE is the real effect."**
No. They are answers to different questions, and neither is a degraded version of the other. ITT answers *what does launching do*; LATE answers *what does using do*. Calling ITT conservative implies LATE is the truth ITT approximates — it isn't. If your policy is a launch, ITT **is** the effect, full stop, and LATE is the one that doesn't describe any policy you can run.

**"Just filter to compliers and compare them to control."**
This is the single most common blown interview answer. Comparing the 10,000 who opened against the 50,000 controls is not causal — it's the selection bias term of §3.2 in its purest form. You've conditioned on a **post-treatment variable**, so the groups differ in enthusiasm as well as treatment. And you can't fix it by finding compliers in control: in the control arm compliers and never-takers are *observationally identical*. That's not a data-collection gap. It's the definition of the latent type.

**"With a big enough sample we can estimate ATE."**
$n$ has nothing to do with it. ATE isn't unidentified because it's noisy; it's unidentified because never-takers' $Y(1)$ is structurally unobservable under any $Z$ you can assign. Identification is a question about infinite data. This one fails there too.

**"LATE = ATT, so the local caveat doesn't matter."**
True *here*, because of one-sided non-compliance (§6.3). Generically false. Add always-takers — control users who reach the feature another way — and the treated group is compliers *plus* always-takers, so ATT ≠ LATE, and the Wald ratio recovers only the complier piece.

**"We have a DAG, so we've handled confounding."**
A DAG is a set of assumptions you drew, not evidence. Its value is forcing you to state which arrows you claim are absent. Randomizing $Z$ genuinely deletes $X \rightarrow Z$; nothing about drawing the picture deletes $Z \rightarrow Y$.

**"CATE is just ATE with subgroups."**
CATE is a function, ATE is its mean: $\text{ATE} = E[\tau(X)]$. Estimating $\tau(\cdot)$ well requires machinery built for it (Lecture 8) — running your ATE regression inside 20 subgroups is a multiple-testing generator, not a CATE estimator.

---

## 9. Summary

| Estimand | Averages over | Answers | Identified by randomizing $Z$? |
|---|---|---|---|
| **ATE** | everyone | "force everyone vs. nobody" | **No**, not under partial compliance |
| **ATT** | the treated | "did it help the takers" | Yes — *if* one-sided (then = LATE) |
| **CATE** | an $X$-cell | "whom to treat" | Yes, for ITT/LATE conditional on $X$ |
| **ITT** | everyone assigned | "**what does launching do**" | **Yes** — cheapest assumptions on the list |
| **LATE** | compliers | "**what does using do**" | Yes, + exclusion + monotonicity |

Three things to carry into Lecture 2:

1. **The counterfactual is missing by construction, not by neglect.** Every method is an imputation strategy. Judge methods by the credibility of the assumption doing the imputing, not the sophistication of the estimator.
2. **Estimand before estimator.** The estimand is a claim about an intervention. If nobody can execute that intervention, the number is trivia — no matter how well-estimated.
3. **Match the denominator to the decision.** Flat cost over a population → ITT. Cost per user served → LATE. Multiplying a per-complier effect by a population headcount is a units error, and §6.5 shows it flipping a real ship/no-ship call.

---

## 10. References

- **Holland, P. (1986).** "Statistics and Causal Inference." *JASA* 81(396), 945–960. — Names the fundamental problem. §2 of this lecture is §2 of that paper.
- **Rubin, D. (1974).** "Estimating Causal Effects of Treatments in Randomized and Nonrandomized Studies." *J. Educational Psychology* 66(5), 688–701. — Origin of the potential-outcomes framework.
- **Imbens, G. & Angrist, J. (1994).** "Identification and Estimation of Local Average Treatment Effects." *Econometrica* 62(2), 467–475. — The LATE theorem; source of the complier/never-taker/always-taker/defier typology and of monotonicity.
- **Angrist, Imbens & Rubin (1996).** "Identification of Causal Effects Using Instrumental Variables." *JASA* 91(434), 444–455. — The canonical treatment; §5 of the paper works a draft-lottery example structurally identical to §6 here (one-sided non-compliance).
- **Imbens & Rubin (2015).** *Causal Inference for Statistics, Social, and Biomedical Sciences.* Ch. 1–2 (potential outcomes, SUTVA), Ch. 23–24 (non-compliance, LATE).
- **Angrist & Pischke (2009).** *Mostly Harmless Econometrics.* §4.4.1 (LATE), §4.4.3 (LATE vs. ATT under one-sided non-compliance).
- **Pearl, J. (2009).** *Causality.* Ch. 3 — the DAG machinery behind §3; back-door criterion.
- **Hernán, M. & Robins, J. (2020).** *Causal Inference: What If.* Ch. 1–3 — the clearest free treatment of the estimand/estimator distinction.

**In this repo:**
- [`industry-playbook/00-foundations.md`](../industry-playbook/00-foundations.md) — the compressed version: estimand table, assumption stack, four-question sanity framework.
- [`industry-playbook/01-experiments-first.md`](../industry-playbook/01-experiments-first.md) — ITT vs. CACE in practice, cluster randomization, trigger analysis.
- [`skills/causal-inference/methods-reference.md`](../skills/causal-inference/methods-reference.md) — IV/2SLS reference and the estimand each method targets.
