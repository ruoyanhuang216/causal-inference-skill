# Example: Effect of Minimum Wage on Employment (Staggered DiD)

This example shows how the `/causal-inference` skill guides a researcher studying the employment effects of state-level minimum wage increases.

---

## Conversation

### User
```
/causal-inference I want to estimate the effect of minimum wage increases on employment. Different US states raised their minimum wage at different times between 2010 and 2020. I have quarterly county-level panel data on employment in the restaurant sector.
```

### Phase 1: Problem Framing

**Skill asks:**
> Let me clarify your research setup:
>
> 1. **Research question**: Does raising the state minimum wage reduce restaurant employment?
> 2. **Treatment**: State-level minimum wage increase (binary: did the state raise MW above federal level?)
> 3. **Outcome**: Restaurant sector employment (level? log? employment-to-population ratio?)
> 4. **Unit of analysis**: County-quarter
> 5. **Estimand**: Are you interested in the ATT (effect on states that raised MW)? Or the ATE (effect if all states were to raise MW)?
>
> A few follow-ups:
> - Is the treatment a one-time increase or do some states raise MW multiple times?
> - Do you want to estimate the overall average effect, or trace out dynamic effects over time?

### User responds:
> - Outcome is log employment.
> - ATT is my target — I want the effect on states that actually raised their MW.
> - Some states raised MW multiple times. I'm treating the first increase as the treatment event.
> - I want both the overall average effect and dynamic effects (event study).

---

### Phase 2: Data & Assignment

**Skill asks:**
> Good. Let me characterize your data:
>
> 1. **Data structure**: Panel (county-quarter), confirmed.
> 2. **Sample size**: Roughly how many counties? How many treated states?
> 3. **Assignment mechanism**: States chose to raise MW — this is **not randomly assigned**. The key question is whether the *timing* of adoption is as good as random, conditional on fixed effects.
> 4. **Treatment timing**: Staggered — different states adopted at different times. This is critical for method selection.
> 5. **Confounders**: What might cause both MW increases and employment changes? State-level economic conditions, political composition, prior employment trends, cost of living...
>
> Are there states that **never** raised MW during your period? These "never-treated" units are valuable as a clean control group.

### User responds:
> About 3,000 counties across all 50 states. Around 30 states raised MW at some point. Yes, roughly 20 states never raised MW above federal level — those are my never-treated group.

---

### Phase 3: Method Selection

**Skill recommends:**
> Your setting — **staggered treatment adoption with panel data** — points clearly to **Difference-in-Differences**. However, there's a critical methodological issue:
>
> **Do NOT use standard Two-Way Fixed Effects (TWFE) as your primary specification.**
>
> With staggered adoption and potentially heterogeneous treatment effects, TWFE can produce biased estimates because it uses already-treated states as controls for later adopters (Goodman-Bacon 2021). The weights on different 2x2 comparisons can even be negative.
>
> **Recommended approach:**
>
> | Estimator | Why |
> |-----------|-----|
> | **Callaway & Sant'Anna (2021)** | Primary specification. Estimates clean group-time ATTs using never-treated as controls. Doubly robust option. Aggregates flexibly. |
> | **Sun & Abraham (2021)** | Robustness check. Interaction-weighted estimator. Easy to implement in `fixest`. |
> | **TWFE** | Report for comparison only — show readers how it differs from robust estimators. |
>
> For your **event study**, use the dynamic aggregation from Callaway & Sant'Anna, which provides clean pre-treatment and post-treatment coefficient estimates.
>
> **Key assumption to defend**: **Parallel trends** — in the absence of MW increases, employment trends in treated and never-treated states would have been similar. This is partially testable via pre-treatment dynamics.

---

### Phase 4: Diagnostics

**Skill provides checklist:**
> Before running your main analysis, validate these:
>
> **Parallel Trends**
> - [ ] Plot raw average log employment by treatment cohort over time. Do trends align pre-treatment?
> - [ ] Estimate event study with Callaway-Sant'Anna. Are pre-treatment coefficients individually and jointly insignificant?
> - [ ] Consider Roth (2022): even if pre-treatment coefficients pass, is your test powered to detect the violations that would matter?
>
> **Staggered DiD Specific**
> - [ ] Run Goodman-Bacon decomposition on TWFE to see which comparisons drive the estimate
> - [ ] Check for negative weights in TWFE
> - [ ] Compare results across at least two robust estimators
>
> **Robustness**
> - [ ] Placebo outcomes: Apply DiD to outcomes MW shouldn't affect (e.g., employment in non-MW-sensitive sectors)
> - [ ] Placebo timing: Pretend treatment happened 2 years earlier
> - [ ] Varying control group: Use "not-yet-treated" instead of "never-treated" as controls
> - [ ] Sensitivity: Rambachan & Roth honest confidence intervals allowing for non-linear pre-trends

---

### Phase 5: Implementation

**Skill provides code (R):**

```r
library(did)
library(fixest)
library(ggplot2)

# ── Data Preparation ──
# Ensure: unit_id (county), time (quarter), first_treat (quarter of first MW increase; 0 for never-treated), log_emp (outcome)

# ── Primary: Callaway & Sant'Anna ──
cs_out <- att_gt(
  yname = "log_emp",
  tname = "quarter",
  idname = "county_id",
  gname = "first_treat_quarter",  # 0 for never-treated
  data = df,
  control_group = "nevertreated",
  est_method = "dr",  # doubly robust
  xformla = ~ state_gdp_growth + pop_density,  # optional covariates
  clustervars = "state_id"  # cluster at state level (treatment level)
)

# Overall ATT
agg_simple <- aggte(cs_out, type = "simple")
summary(agg_simple)

# Event study (dynamic effects)
agg_dynamic <- aggte(cs_out, type = "dynamic", min_e = -8, max_e = 12)
ggdid(agg_dynamic) +
  geom_hline(yintercept = 0, linetype = "dashed") +
  labs(title = "Event Study: Minimum Wage and Restaurant Employment",
       x = "Quarters Relative to MW Increase",
       y = "ATT (log employment)")

# ── Robustness: Sun & Abraham via fixest ──
sa_model <- feols(log_emp ~ sunab(first_treat_quarter, quarter) | county_id + quarter,
                  data = df, cluster = ~state_id)
iplot(sa_model, main = "Sun & Abraham Event Study")

# ── Comparison: Standard TWFE (report but flag limitations) ──
twfe <- feols(log_emp ~ treat_post | county_id + quarter, data = df, cluster = ~state_id)
summary(twfe)

# ── Goodman-Bacon Decomposition ──
library(bacondecomp)
bacon_out <- bacon(log_emp ~ treat_post, data = df_state_level,
                   id_var = "state_id", time_var = "quarter")
ggplot(bacon_out) +
  aes(x = weight, y = estimate, color = type) +
  geom_point(size = 3) +
  geom_hline(yintercept = 0, linetype = "dashed") +
  labs(title = "Goodman-Bacon Decomposition")
```

> **Reporting checklist:**
> 1. Report Callaway-Sant'Anna ATT as primary estimate with confidence interval
> 2. Show event study plot with pre-treatment coefficients
> 3. Report Sun-Abraham and TWFE side-by-side for comparison
> 4. Show Goodman-Bacon decomposition to explain any TWFE vs. robust estimator discrepancy
> 5. Discuss parallel trends assumption qualitatively and via pre-treatment dynamics
> 6. Report at least one sensitivity analysis (e.g., Rambachan-Roth, or using not-yet-treated controls)
