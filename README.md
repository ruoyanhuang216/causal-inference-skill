# Causal Inference Workflow Skill for Claude Code

An interactive [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that guides researchers through the complete causal inference workflow — from research question formulation to method selection, assumption diagnostics, and implementation with code.

Designed for social scientists, economists, political scientists, epidemiologists, marketing scientists, and applied researchers working on causal questions — covering both reduced-form and structural approaches.

## What It Does

When you invoke `/causal-inference`, the skill starts an interactive conversation that walks you through 5 phases:

| Phase | What Happens |
|-------|--------------|
| **1. Problem Framing** | Identify your research question, treatment, outcome, and target estimand (ATE, ATT, LATE, CATE) |
| **2. Data & Assignment** | Characterize your data structure, treatment assignment mechanism, timing, and confounders |
| **3. Method Selection** | Navigate a decision tree across reduced-form and structural approaches to find the right method(s) |
| **4. Assumption Diagnostics** | Walk through method-specific checklists to validate your identification strategy |
| **5. Implementation** | Get Python code templates, key packages, and reporting guidance |
| **6. Robustness Checks** | Interactive, layered robustness workflow: identification threats, specification sensitivity, sample robustness, inference checks, sensitivity to unobservables, placebo tests, cross-method comparison, and publication-ready output |

## Methods Covered

The skill covers the full landscape of modern causal inference methods:

- **Experimental**: RCT, Cluster RCT, Stratified Randomization, Adaptive Experiments
- **Difference-in-Differences**: Classic 2x2, Staggered DiD (Callaway-Sant'Anna, Sun-Abraham, de Chaisemartin-D'Haultfoeuille, Borusyak-Jaravel-Spiess, Gardner, Wooldridge), Triple Differences
- **Regression Discontinuity**: Sharp RD, Fuzzy RD, Regression Kink, Geographic RD, Multi-cutoff RD
- **Instrumental Variables**: 2SLS, LIML, GMM, Shift-Share/Bartik, Judge/Examiner IV, Mendelian Randomization
- **Synthetic Control**: Classic SCM, Augmented SCM, Penalized SCM, Matrix Completion, Synthetic DiD (SDID)
- **Selection on Observables**: OLS, PSM, CEM, Mahalanobis Matching, IPW, AIPW/Doubly Robust, Entropy Balancing, Overlap Weighting
- **ML-Enhanced**: Double/Debiased ML, Causal Forest, BART, TMLE, Meta-Learners (S/T/X/R/DR-learner)
- **DAG/Structural**: Back-door/Front-door criteria, do-calculus, SEM, Causal Mediation
- **Structural Estimation**: BLP Demand, Nested/Mixed Logit, Dynamic Discrete Choice (Rust, Hotz-Miller, MPEC), Nash-Bertrand Pricing, Merger Simulation, Entry Models, Consumer Search (Weitzman), Bayesian Learning (Erdem-Keane), Latent Class Models
- **Panel Methods**: Two-Way FE, Correlated Random Effects, Arellano-Bond/Blundell-Bond GMM
- **Time Series**: Interrupted Time Series, Comparative ITS, CausalImpact (Bayesian Structural)
- **Sensitivity & Bounds**: Oster's delta, Rosenbaum bounds, Manski bounds, Lee bounds, Cinelli-Hazlett, E-value
- **Causal Discovery**: PC Algorithm, GES, NOTEARS

## Installation

### Option 1: Personal Skill (Available in All Projects)

Copy the skill folder into your Claude Code personal skills directory:

```bash
# Clone the repo
git clone https://github.com/<your-username>/causal-inference-skill.git

# Copy to Claude Code skills directory
cp -r causal-inference-skill/skills/causal-inference ~/.claude/skills/
```

### Option 2: Project-Level Skill (Available in One Project)

Copy the skill into your project's `.claude/skills/` directory:

```bash
# From your project root
mkdir -p .claude/skills
cp -r /path/to/causal-inference-skill/skills/causal-inference .claude/skills/
```

### Verify Installation

Open Claude Code and type `/causal-inference` — it should appear in the autocomplete menu.

## Usage

### Basic: Start the Interactive Workflow

```
/causal-inference
```

The skill will ask you a series of questions to understand your research problem and guide you to the right method.

### With Context: Provide Your Research Question Upfront

```
/causal-inference I want to estimate the effect of a minimum wage increase on employment using county-level panel data
```

```
/causal-inference Does access to microfinance improve household welfare? I have an RCT with non-compliance
```

```
/causal-inference I'm studying whether a state-level policy reduced crime using data from all 50 states over 20 years
```

```
/causal-inference I need to simulate how a merger between two consumer goods firms would change prices and consumer welfare
```

## Example Sessions

See the [`examples/`](examples/) directory for full example conversations:

| Example | Scenario | Method Selected |
|---------|----------|-----------------|
| [Minimum Wage](examples/minimum-wage-did.md) | Policy evaluation with staggered state adoption | Staggered DiD (Callaway-Sant'Anna) |
| [Class Size](examples/class-size-rdd.md) | Effect of class size on test scores with an enrollment cutoff | Fuzzy RDD |
| [Immigration & Wages](examples/immigration-iv.md) | Effect of immigration on wages with a shift-share instrument | Shift-Share IV |
| [California Smoking Ban](examples/smoking-ban-scm.md) | Single treated state, donor pool of other states | Synthetic Control |
| [Job Training](examples/job-training-ml.md) | Heterogeneous treatment effects from an RCT | Causal Forest + DML |
| [Cereal Demand](examples/cereal-demand-blp.md) | Pricing and merger simulation in consumer packaged goods | BLP Demand + Merger Simulation |

## Skill File Structure

```
skills/causal-inference/
├── SKILL.md               # Main skill: interactive workflow + decision tree
├── methods-reference.md   # Detailed reference for all methods
├── diagnostics.md         # Assumption testing checklists per method
└── code-templates.md      # Python code templates
```

| File | Purpose | Contents |
|------|---------|----------|
| `SKILL.md` | Entry point — loaded when skill is invoked | 5-phase interactive workflow, method decision tree, special topics |
| `methods-reference.md` | Deep reference — loaded on demand | Definitions, assumptions, estimands, key references for 40+ methods (reduced-form + structural) |
| `diagnostics.md` | Validation checklists — loaded during Phase 4 | Per-method diagnostic tests, robustness checks, sensitivity analysis |
| `code-templates.md` | Implementation — loaded during Phase 5 | Python code templates, package recommendations |

## Contributing

Contributions are welcome! Some areas where help is appreciated:

- Additional code templates for specialized methods
- More example sessions covering different research scenarios
- Translations of the skill to other languages
- Additional methods or updated references
- Integration with specific datasets or teaching materials

Please open an issue or submit a pull request.

## References

This skill draws on the following key textbooks and survey articles:

- Angrist & Pischke (2009). *Mostly Harmless Econometrics*
- Angrist & Pischke (2014). *Mastering 'Metrics*
- Cunningham (2021). *Causal Inference: The Mixtape*
- Huntington-Klein (2021). *The Effect: An Introduction to Research Design and Causality*
- Imbens & Rubin (2015). *Causal Inference for Statistics, Social, and Biomedical Sciences*
- Morgan & Winship (2015). *Counterfactuals and Causal Inference*
- Pearl (2009). *Causality: Models, Reasoning, and Inference*
- Hernan & Robins (2020). *Causal Inference: What If*
- Roth, Sant'Anna, Bilinski & Poe (2023). "What's Trending in Difference-in-Differences?"
- Abadie (2021). "Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects"
- Cattaneo, Idrobo & Titiunik (2019). *A Practical Introduction to Regression Discontinuity Designs*
- Berry, Levinsohn & Pakes (1995). "Automobile Prices in Market Equilibrium"
- Nevo (2000). "A Practitioner's Guide to Estimation of Random-Coefficients Logit Models of Demand"
- Train (2009). *Discrete Choice Methods with Simulation*
- Conlon & Gortmaker (2020). "Best Practices for Differentiated Products Demand Estimation with PyBLP"
- Rust (1987). "Optimal Replacement of GMC Bus Engines: An Empirical Model of Harold Zurcher"
- Aguirregabiria & Mira (2010). "Dynamic Discrete Choice Structural Models: A Survey"
- Erdem & Keane (1996). "Decision-Making Under Uncertainty: Capturing Dynamic Brand Choice Processes in Turbulent Consumer Goods Markets"

## License

MIT License. See [LICENSE](LICENSE) for details.
