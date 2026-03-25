# Example: California Tobacco Control Program (Synthetic Control)

This example replicates the classic Abadie, Diamond & Hainmueller (2010) analysis of California's Proposition 99.

---

## Conversation

### User
```
/causal-inference California passed a large tobacco tax and control program (Proposition 99) in 1988. I want to estimate its effect on per-capita cigarette sales. I have state-level annual data for all 50 states from 1970-2000.
```

### Phase 1-2: Problem Framing & Data

**Skill identifies:**
> - **Research question**: Did California's Proposition 99 reduce cigarette consumption?
> - **Treatment**: Proposition 99 (comprehensive tobacco control program)
> - **Treated unit**: California (1 unit)
> - **Outcome**: Per-capita cigarette sales (packs)
> - **Time**: 1970-2000 (18 pre-treatment years, 12 post-treatment years)
> - **Donor pool**: Other US states that did NOT implement similar large programs during this period
>
> **Why DiD won't work well here**: With only 1 treated unit, there's no obvious single comparison state. Any individual state comparison is arbitrary — "Why New York and not Texas?"
>
> **This is a textbook Synthetic Control setting**: single treated unit, many potential donors, long pre-treatment period.

---

### Phase 3: Method Selection

**Skill recommends:**

> **Synthetic Control Method (Abadie, Diamond & Hainmueller 2010)**
>
> The idea: construct a weighted combination of donor states that closely reproduces California's pre-1988 cigarette sales trajectory. This "Synthetic California" serves as the counterfactual. The treatment effect = actual California - synthetic California after 1988.
>
> **Donor pool considerations:**
> - Exclude states that implemented their own large tobacco programs during the study period
> - Exclude states with unusual cigarette tax changes
> - Standard donor pool: ~38 states after exclusions
>
> **Also consider as robustness:**
>
> | Method | Why |
> |--------|-----|
> | **Augmented SCM** | If pre-treatment fit is imperfect, ASCM adds a bias-correction term |
> | **SDID** | Synthetic DiD — reweights both units AND time periods |

---

### Phase 4: Diagnostics

> **Pre-treatment fit**: The synthetic California must closely track actual California before 1988. Report RMSPE. If fit is poor, consider Augmented SCM.
>
> **Inference via placebo tests**:
> 1. Apply SCM to every donor state (pretending each was "treated" in 1988)
> 2. Compute post/pre RMSPE ratio for each
> 3. California's ratio should be an outlier — the p-value is its rank / number of states
>
> **Robustness**:
> - Leave-one-out: drop each major donor state and re-estimate
> - In-time placebo: pretend treatment happened in 1983 — effect should be ~0 before 1988
> - Backdating: shift treatment date and verify effect appears only at actual date

---

### Phase 5: Implementation

```r
library(Synth)
library(augsynth)

# ── Classic Synthetic Control ──
dataprep_out <- dataprep(
  foo = df,
  predictors = c("lnincome", "beer", "age15to24", "retprice"),
  predictors.op = "mean",
  special.predictors = list(
    list("cigsale", 1975, "mean"),
    list("cigsale", 1980, "mean"),
    list("cigsale", 1988, "mean")
  ),
  dependent = "cigsale",
  unit.variable = "state_id",
  time.variable = "year",
  treatment.identifier = 3,  # California
  controls.identifier = donor_ids,
  time.predictors.prior = 1970:1988,
  time.optimize.ssr = 1970:1988,
  time.plot = 1970:2000
)

synth_out <- synth(dataprep_out)

# ── Path plot (actual vs synthetic) ──
path.plot(synth_out, dataprep_out,
          Ylab = "Per-Capita Cigarette Sales (packs)",
          Xlab = "Year",
          Legend = c("California", "Synthetic California"),
          Main = "California vs. Synthetic California")
abline(v = 1988, lty = 2)

# ── Gap plot (treatment effect over time) ──
gaps.plot(synth_out, dataprep_out,
          Ylab = "Gap in Cigarette Sales",
          Xlab = "Year",
          Main = "Effect of Proposition 99")
abline(v = 1988, lty = 2)

# ── Donor weights ──
synth.tables <- synth.tab(dataprep.res = dataprep_out, synth.res = synth_out)
print(synth.tables$tab.w)  # which states contribute to synthetic CA?
print(synth.tables$tab.pred)  # predictor balance

# ── Pre-treatment RMSPE ──
pre_gaps <- dataprep_out$Y1plot[1:19] - (dataprep_out$Y0plot[1:19, ] %*% synth_out$solution.w)
rmspe_pre <- sqrt(mean(pre_gaps^2))
cat(sprintf("Pre-treatment RMSPE: %.2f\n", rmspe_pre))

# ── Placebo tests (permutation inference) ──
# Run SCM for each donor state
placebo_gaps <- list()
for (donor in donor_ids) {
  tryCatch({
    dp <- dataprep(foo = df, ..., treatment.identifier = donor,
                   controls.identifier = setdiff(c(3, donor_ids), donor), ...)
    sp <- synth(dp)
    placebo_gaps[[as.character(donor)]] <- dp$Y1plot - (dp$Y0plot %*% sp$solution.w)
  }, error = function(e) NULL)
}
# Plot all placebo gaps + California gap
# Calculate post/pre RMSPE ratios and rank California

# ── Augmented SCM (if pre-fit is imperfect) ──
ascm_out <- augsynth(cigsale ~ treat, unit = state_id, time = year,
                     data = df, progfunc = "ridge", scm = TRUE)
summary(ascm_out)
plot(ascm_out)

# ── Synthetic DiD ──
library(synthdid)
setup <- panel.matrices(df, unit = "state_id", time = "year",
                        outcome = "cigsale", treatment = "treat")
sdid_est <- synthdid_estimate(setup$Y, setup$N0, setup$T0)
plot(sdid_est)
```

> **Key results to report:**
> 1. Path plot: actual CA vs. synthetic CA — clear divergence after 1988
> 2. Gap plot: treatment effect grows over time (cumulative effect of sustained program)
> 3. Donor weights: which states form synthetic CA (typically CO, CT, MT, NV, UT)
> 4. Placebo test: CA has the largest post/pre RMSPE ratio → p-value ~ 0.03
> 5. Robustness: leave-one-out donors, ASCM, SDID estimates
