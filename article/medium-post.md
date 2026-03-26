# I Built a Claude Code Skill That Guides You Through the Entire Causal Inference Workflow — Here's How It Works

*An interactive AI assistant for choosing the right causal method, running diagnostics, stress-testing your results, and generating publication-ready reports.*

---

If you've ever stared at your dataset and wondered, "Should I use DiD or synthetic control? Is my instrument strong enough? Did I check enough robustness specifications?" — this skill is for you.

I built a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill called `/causal-inference` that interactively walks you through the entire causal inference pipeline: from framing your research question to selecting the right method, checking assumptions, running robustness tests, and producing a structured report with inline charts and a presentation deck.

In this post, I'll walk through a complete session using a real-world example — estimating the effect of minimum wage increases on restaurant employment.

**GitHub repo**: [causal-inference-skill](https://github.com/ruoyanhuang216/causal-inference-skill)

---

## Why I Built This

Causal inference is hard. Not because the math is complicated (though it can be), but because the *workflow* is complicated:

1. You need to match your **research question** to the right **identification strategy**
2. The right method depends on your **data structure**, **treatment assignment**, and **assumptions** you can defend
3. Once you pick a method, there are **dozens of robustness checks** — and knowing which ones matter most for your specific method is non-trivial
4. Modern methods (staggered DiD, ML-enhanced causal methods, structural estimation) require specialized code that most researchers don't have at their fingertips
5. Reviewers will ask hard questions — and you need to anticipate them

I wanted a tool that could guide a researcher through this entire process interactively, like having a methodologist sitting next to you.

---

## What the Skill Covers

The skill includes **40+ methods** across the full causal inference landscape:

| Category | Methods |
|----------|---------|
| **Experimental** | RCT, Cluster RCT, Adaptive Experiments |
| **Difference-in-Differences** | Classic, Staggered (Callaway-Sant'Anna, Sun-Abraham, de Chaisemartin, Borusyak, Gardner, Wooldridge) |
| **Regression Discontinuity** | Sharp, Fuzzy, Kink, Geographic, Multi-cutoff |
| **Instrumental Variables** | 2SLS, Shift-Share/Bartik, Judge IV |
| **Synthetic Control** | Classic SCM, Augmented SCM, SDID |
| **Selection on Observables** | PSM, CEM, IPW, AIPW, Entropy Balancing |
| **ML-Enhanced** | Double ML, Causal Forest, BART, TMLE, Meta-Learners |
| **Structural Estimation** | BLP Demand, Dynamic Discrete Choice, Merger Simulation, Consumer Search |
| **Sensitivity & Bounds** | Oster's delta, Cinelli-Hazlett, Rosenbaum bounds, Lee bounds |

And it produces all code in **Python** using modern packages: `pyfixest`, `rdrobust`, `econml`, `doubleml`, `pyblp`, and more.

---

## The 7-Phase Workflow

Here's the full pipeline the skill walks you through:

```
Phase 1: Problem Framing      → What's your causal question?
Phase 2: Data & Assignment     → What does your data look like?
Phase 3: Method Selection      → Decision tree → right method
Phase 4: Assumption Diagnostics → Can you defend the assumptions?
Phase 5: Implementation        → Python code + packages
Phase 6: Robustness Checks     → 7-layer stress test
Phase 7: Report & Presentation → Publication-ready output
```

Let me show each phase in action.

---

## Live Walkthrough: Minimum Wage and Restaurant Employment

### Starting the Skill

I type:

```
/causal-inference I want to estimate the effect of minimum wage increases
on employment. Different US states raised their minimum wage at different
times between 2010 and 2020. I have quarterly county-level panel data on
employment in the restaurant sector.
```

The skill immediately picks up the key elements and starts Phase 1.

---

### Phase 1: Problem Framing

The skill asks targeted questions to nail down the research setup:

> **Research question**: Does raising the state minimum wage reduce restaurant employment?
> **Treatment**: State-level minimum wage increase (binary)
> **Outcome**: Restaurant sector employment — level? log? employment-to-population ratio?
> **Estimand**: ATT or ATE?
>
> A few follow-ups:
> - Is the treatment a one-time increase or do some states raise MW multiple times?
> - Do you want the overall average effect, or dynamic effects over time?

I answer: log employment, ATT, first increase as treatment event, want both average and dynamic effects.

**What's happening**: The skill is disambiguating the estimand (ATT vs ATE — they answer different questions) and the outcome measurement (levels vs logs — matters for interpretation). These seemingly simple choices have downstream consequences for which estimator is appropriate.

---

### Phase 2: Data & Assignment

The skill characterizes my data:

> **Data structure**: Panel (county-quarter) ✓
> **Assignment mechanism**: Self-selected — states chose to raise MW. This is **not randomly assigned**. The key question is whether the *timing* is as good as random.
> **Treatment timing**: Staggered — different states adopted at different times. **This is critical for method selection.**
>
> Are there states that **never** raised MW? These "never-treated" units are valuable.

I confirm: 3,000 counties, 29 treated states, 21 never-treated states.

**What's happening**: The skill identified two crucial features — (1) staggered adoption and (2) a clean never-treated control group — that directly determine which method track to follow.

---

### Phase 3: Method Selection

This is where the decision tree kicks in. The skill routes me to **Track B1: Staggered Difference-in-Differences** and immediately flags the TWFE problem:

> **Do NOT use standard Two-Way Fixed Effects (TWFE) as your primary specification.**
>
> With staggered adoption and potentially heterogeneous treatment effects, TWFE can produce biased estimates because it uses already-treated states as controls for later adopters (Goodman-Bacon 2021).
>
> **Recommended:**
>
> | Estimator | Role |
> |-----------|------|
> | **Callaway & Sant'Anna (2021)** | Primary. Clean group-time ATTs, doubly robust. |
> | **Sun & Abraham (2021)** | Robustness check. |
> | **TWFE** | Report for comparison only. |

**What's happening**: Five years ago, everyone used TWFE for staggered DiD. Now we know it can be biased. The skill ensures you're using modern estimators and explains *why* TWFE is problematic — not just telling you to avoid it.

---

### Phase 4: Assumption Diagnostics

Before writing any code, the skill walks through what needs to hold:

> **Parallel trends**: Would treated and control states have followed the same employment trajectory absent the MW increase?
>
> Tests to run:
> - [ ] Plot raw means by treatment cohort over time
> - [ ] Event study with Callaway-Sant'Anna — are pre-treatment coefficients insignificant?
> - [ ] Consider Roth (2022): even if pre-treatment coefficients pass, is the test *powered* to detect violations that matter?

**What's happening**: The skill doesn't just list the assumption — it tells you how to *test* it, what failure looks like, and flags a subtle point (Roth 2022) that most textbooks don't cover: passing a pre-trend test doesn't prove parallel trends.

---

### Phase 5: Implementation

The skill generates Python code:

```python
from csdid import att_gt
import pyfixest as pf

# Primary: Callaway & Sant'Anna
cs_out = att_gt(
    data=df, yname='log_emp', tname='quarter',
    idname='county_id', gname='first_treat_quarter',
    control_group='nevertreated', est_method='dr'
)
agg = cs_out.aggregate('simple')
print(agg.summary())

# Event study
agg_dyn = cs_out.aggregate('dynamic')
agg_dyn.plot()

# Robustness: Sun & Abraham
sa = pf.feols(
    'log_emp ~ sunab(first_treat_quarter, quarter) | county_id + quarter',
    data=df, vcov={'CRV1': 'state_id'}
)
```

**Main result**: ATT = -0.0147, 95% CI [-0.025, -0.004], p = 0.007. Restaurant employment fell by ~1.5%.

![Main result with headline estimate](https://github.com/ruoyanhuang216/causal-inference-skill/blob/main/examples/sample-output/figures/main_result.png?raw=true)

The event study shows no pre-trends and a gradual emergence of the negative effect:

![Event study — pre-treatment coefficients near zero, post-treatment negative](https://github.com/ruoyanhuang216/causal-inference-skill/blob/main/examples/sample-output/figures/event_study.png?raw=true)

---

### Phase 6: The 7-Layer Robustness Gauntlet

This is where the skill really shines. It walks through robustness checks **interactively, one layer at a time**, generating code and helping interpret results.

#### Layer 1: Identification Threats

> "Let's start with the tests that could overturn your result."

| Test | Result | Status |
|------|--------|--------|
| Parallel pre-trends (joint F) | F = 0.87, p = 0.54 | ✓ Pass |
| Individual pre-treatment coefficients | All \|t\| < 1.2 | ✓ Pass |
| Goodman-Bacon decomposition | 89% clean comparisons | ✓ Pass |

#### Layer 2: Specification Sensitivity

The skill generates a **specification curve** — the same estimate computed 48 different ways:

![Specification curve — 48 specifications sorted by estimate, preferred highlighted in red](https://github.com/ruoyanhuang216/causal-inference-skill/blob/main/examples/sample-output/figures/specification_curve.png?raw=true)

Across 48 specifications varying the outcome (levels, logs, IHS), controls, fixed effects, clustering, and estimator — **all 48 are negative, and 88% are statistically significant**. The result is not fragile.

#### Layers 3 & 4: Sample & Inference Robustness

No single state drives the result. Dropping California (the most influential state) shifts the estimate from -0.0147 to -0.0134 — barely a change. Significance holds under wild cluster bootstrap (p=0.014) and randomization inference (p=0.008), even with only 50 clusters.

#### Layer 5: Sensitivity to Unobservables

This is the "how much hidden bias would it take?" layer:

- **Oster's delta = 2.34** — unobservables would need 2.3x the explanatory power of all observed controls to explain away the result
- **Robustness Value = 0.089** — exceeds the strongest observed confounder (GDP growth, partial R² = 0.041)

![Sensitivity cards — Oster's delta and Robustness Value](https://github.com/ruoyanhuang216/causal-inference-skill/blob/main/examples/sample-output/figures/sensitivity_cards.png?raw=true)

![Sensitivity contour plot — Cinelli & Hazlett with covariate benchmarks](https://github.com/ruoyanhuang216/causal-inference-skill/blob/main/examples/sample-output/figures/sensitivity_contour.png?raw=true)

#### Layer 6: Placebo Tests

![Placebo outcomes and timing tests](https://github.com/ruoyanhuang216/causal-inference-skill/blob/main/examples/sample-output/figures/placebo_outcomes.png?raw=true)

Applying the same DiD to mining, finance, and government employment yields null results. The method only "finds" an effect where one should exist. All 6 placebo tests pass.

#### Layer 7: Cross-Method Comparison

![Forest plot — 5 identification strategies all agree](https://github.com/ruoyanhuang216/causal-inference-skill/blob/main/examples/sample-output/figures/cross_method_forest.png?raw=true)

Five methods with different identifying assumptions all agree: the effect is negative, in the range [-0.016, -0.009], and statistically significant.

And the skill compiles it all into a robustness dashboard:

![Robustness dashboard — all 7 dimensions pass](https://github.com/ruoyanhuang216/causal-inference-skill/blob/main/examples/sample-output/figures/robustness_dashboard.png?raw=true)

---

### Phase 7: Report & Presentation

After the analysis is complete, the skill compiles everything into two deliverables:

**1. A structured analysis report** (markdown + PDF) with:
- Executive summary and hypothesis-driven narrative
- Main results with tables and figures
- All 7 robustness layers documented
- A robustness dashboard:

| Category | Status | Evidence |
|----------|--------|----------|
| Identification | ✓ | Pre-trends insignificant (F=0.87, p=0.54) |
| Specification stability | ✓ | 48 specs, all negative, 88% significant |
| Sample robustness | ✓ | No single state drives result |
| Inference | ✓ | Significant under wild bootstrap + RI |
| Sensitivity | ✓ | Oster's δ = 2.34, RV = 0.089 |
| Placebo tests | ✓ | 6/6 passed |
| Cross-method | ✓ | 5 methods agree |

> **Verdict: STRONG** — robust across all 7 dimensions.

- Limitations section (honest, specific, informed by what the checks actually found)
- Reproduction code in collapsible appendix

**2. A 10-slide HTML presentation** (zero dependencies, runs in any browser):

Title → Motivation → Research Design → Data → Main Result → Heterogeneity → Robustness Dashboard → Sensitivity → Limitations → Conclusion

You can see the full sample outputs in the [GitHub repo](https://github.com/ruoyanhuang216/causal-inference-skill/tree/main/examples/sample-output).

---

## Beyond Reduced-Form: Structural Estimation

The skill doesn't stop at reduced-form causal inference. It includes a full **structural estimation track** (Track G) covering the methods dominant in marketing science and industrial organization:

- **BLP demand estimation** with PyBLP — including instruments, elasticity computation, and marginal cost recovery
- **Merger simulation** — change the ownership matrix, solve for new equilibrium prices, compute consumer surplus changes
- **Dynamic discrete choice** — Rust (1987) NFXP, Hotz-Miller CCP estimation
- **Consumer search models**, **Bayesian learning**, **latent class models**

The skill guides you through the key trade-off: *when do you need structural vs. reduced-form?*

| | Reduced-Form | Structural |
|--|-------------|-----------|
| **Strength** | Credible identification, minimal assumptions | Out-of-sample counterfactuals, welfare, mechanisms |
| **Weakness** | Limited to in-sample variation | Requires strong functional form assumptions |
| **Use when** | Estimating a credible causal effect | Predicting effects of policies never observed |

---

## How to Install

```bash
# Clone
git clone https://github.com/ruoyanhuang216/causal-inference-skill.git

# Copy to your Claude Code skills directory
cp -r causal-inference-skill/skills/causal-inference ~/.claude/skills/

# Verify: open Claude Code and type /causal-inference
```

That's it. The skill auto-registers and appears in your `/` menu.

---

## What's Inside

```
skills/causal-inference/
├── SKILL.md              # Main workflow (7 phases, decision tree, interaction logic)
├── methods-reference.md  # Deep reference for 40+ methods
├── diagnostics.md        # Per-method assumption testing checklists
└── code-templates.md     # Python templates for everything
```

The skill is modular: `SKILL.md` is the interactive brain, and the supporting files are loaded on demand as reference material.

---

## Try It

Here are some prompts to get started:

```
/causal-inference

/causal-inference I want to evaluate the effect of a job training program
on earnings. Treatment was randomly assigned but there was non-compliance.

/causal-inference I need to simulate how a merger between two consumer goods
firms would change prices and consumer welfare.

/causal-inference I'm studying whether a state-level policy reduced crime
using data from all 50 states over 20 years.
```

The skill adapts to your problem — whether it's a clean RCT, a messy observational study, a regression discontinuity, or a structural demand model.

---

## What I Learned Building This

1. **The decision tree is the hard part.** The methods themselves are well-documented. What's missing is the *routing* — "given my data and question, which method should I use?" That's what the skill's Phase 3 decision tree solves.

2. **Robustness is more than a checklist.** Researchers often run a grab-bag of robustness checks without prioritizing. The 7-layer structure forces you to start with the checks that matter most (identification threats) before moving to nice-to-haves (cross-method comparison).

3. **The report writes itself if you track results along the way.** Phase 7 works because the skill accumulates findings throughout Phases 1-6. By the end, compiling the report is just stitching together what you already have.

4. **Structural and reduced-form belong in the same framework.** In practice, many top papers combine both. The skill treats them as tracks you can switch between, not competing paradigms.

---

## Links

- **GitHub**: [github.com/ruoyanhuang216/causal-inference-skill](https://github.com/ruoyanhuang216/causal-inference-skill)
- **Sample report (PDF)**: [report.pdf](https://github.com/ruoyanhuang216/causal-inference-skill/blob/main/examples/sample-output/report.pdf)
- **Sample presentation**: [presentation.html](https://github.com/ruoyanhuang216/causal-inference-skill/blob/main/examples/sample-output/presentation.html)

If you find it useful, star the repo or open an issue with suggestions. Contributions welcome — especially additional example sessions and specialized code templates.

---

*Built with [Claude Code](https://docs.anthropic.com/en/docs/claude-code). The skill leverages Claude's knowledge of econometrics, biostatistics, marketing science, and computational social science to guide researchers through causal analysis workflows interactively.*
