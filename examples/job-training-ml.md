# Example: Heterogeneous Effects of Job Training (Causal Forest + DML)

This example shows the skill guiding a researcher who has experimental data and wants to understand who benefits most from a job training program.

---

## Conversation

### User
```
/causal-inference I have data from a randomized job training experiment (like the JTPA or NSW). Treatment was randomly assigned. I want to go beyond the average effect and understand which types of participants benefit most from the training. I have rich baseline covariates: age, education, prior earnings, race, marital status, etc.
```

### Phase 1-2: Problem Framing & Data

**Skill identifies:**
> Great — you're in a strong position because you have experimental data, so the ATE is cleanly identified. Your goal is to estimate **heterogeneous treatment effects (CATE)**.
>
> - **Research question**: Who benefits most from job training?
> - **Treatment**: Random assignment to job training (binary)
> - **Outcome**: Post-program earnings (or employment)
> - **Estimand**: CATE — E[Y(1) - Y(0) | X = x] — the treatment effect conditional on individual characteristics
> - **Data**: Cross-sectional (one observation per individual, post-randomization)
>
> Since treatment is randomized, the **unconfoundedness assumption is satisfied by design**. The challenge is statistical — estimating a high-dimensional function CATE(x) with valid inference.

---

### Phase 3: Method Selection

**Skill recommends:**

> For CATE estimation with experimental data and rich covariates, I recommend a **multi-method approach**:
>
> | Method | Role | Strength |
> |--------|------|----------|
> | **Causal Forest** (Wager & Athey 2018) | Primary CATE estimator | Nonparametric; pointwise CIs; variable importance; built-in calibration test |
> | **DML** (Chernozhukov et al. 2018) | ATE/ATT as benchmark | Rigorous inference for average effects; cross-fitted; agnostic to ML method |
> | **Best Linear Projection** | Interpretable summary | Projects nonparametric CATE onto linear function of key covariates |
> | **Sorted Effects** (Chernozhukov et al. 2018) | Visualization | Rank individuals by predicted CATE; show distribution of effects |
>
> **Workflow:**
> 1. Estimate ATE via DML as a benchmark (should match simple difference-in-means)
> 2. Estimate CATE via Causal Forest
> 3. Run calibration test — does the forest detect real heterogeneity?
> 4. Examine variable importance — which covariates drive heterogeneity?
> 5. Use Best Linear Projection to summarize heterogeneity in interpretable terms
> 6. Characterize the most- and least-affected subgroups (CLAN analysis)
> 7. Optionally: estimate optimal treatment assignment policy

---

### Phase 4: Diagnostics

> **For Causal Forest:**
> - [ ] **Calibration test**: `test_calibration(cf)` — tests whether predicted CATEs are well-calibrated. The "mean forest prediction" coefficient should be significant (there IS heterogeneity) and close to 1 (predictions are well-calibrated).
> - [ ] **Out-of-bag honesty**: The forest uses separate samples for splitting and estimation — verify this is enabled (default in `grf`).
> - [ ] **Overlap**: Even with randomization, check that propensity scores are bounded away from 0 and 1 in all subgroups.
>
> **For DML:**
> - [ ] **Cross-fitting**: Use K=5 folds; show stability across different random splits.
> - [ ] **Nuisance model fit**: Report out-of-fold R-squared for outcome model.
>
> **General:**
> - [ ] **Overfitting check**: Compare in-sample vs. out-of-sample predictions. If using CATE for targeting, evaluate on a held-out sample.
> - [ ] **Pre-registered subgroups**: If you had pre-specified subgroups of interest, test those first and report ML-discovered heterogeneity as exploratory.

---

### Phase 5: Implementation

```r
library(grf)
library(DoubleML)
library(mlr3)
library(mlr3learners)
library(ggplot2)

# ── Setup ──
covariates <- c("age", "education", "prior_earnings", "race",
                "married", "hispanic", "nodegree")
X <- as.matrix(df[, covariates])
Y <- df$earnings
W <- df$treatment

# ═══════════════════════════════════════════
# Step 1: ATE via DML (benchmark)
# ═══════════════════════════════════════════
dml_data <- DoubleMLData$new(df, y_col = "earnings", d_cols = "treatment",
                              x_cols = covariates)

ml_l <- lrn("regr.ranger", num.trees = 500)
ml_m <- lrn("classif.ranger", num.trees = 500)

dml_plr <- DoubleMLPLR$new(dml_data, ml_l = ml_l, ml_m = ml_m, n_folds = 5)
dml_plr$fit()
cat("DML ATE estimate:\n")
print(dml_plr$summary())

# Simple difference-in-means for comparison
ate_simple <- mean(Y[W == 1]) - mean(Y[W == 0])
cat(sprintf("Simple DiM: %.2f\n", ate_simple))

# ═══════════════════════════════════════════
# Step 2: Causal Forest for CATE
# ═══════════════════════════════════════════
cf <- causal_forest(X, Y, W,
                    num.trees = 4000,
                    honesty = TRUE,
                    tune.parameters = "all")

# ── ATE from forest ──
ate_cf <- average_treatment_effect(cf, target.sample = "all")
cat(sprintf("Causal Forest ATE: %.2f (SE: %.2f)\n", ate_cf[1], ate_cf[2]))

# ═══════════════════════════════════════════
# Step 3: Calibration test
# ═══════════════════════════════════════════
cal <- test_calibration(cf)
print(cal)
# "mean.forest.prediction" should be significant and coef ~ 1
# "differential.forest.prediction" significant → heterogeneity detected

# ═══════════════════════════════════════════
# Step 4: Variable importance
# ═══════════════════════════════════════════
varimp <- variable_importance(cf)
varimp_df <- data.frame(variable = covariates, importance = as.numeric(varimp))
varimp_df <- varimp_df[order(-varimp_df$importance), ]

ggplot(varimp_df, aes(x = reorder(variable, importance), y = importance)) +
  geom_col() + coord_flip() +
  labs(title = "Variable Importance for Treatment Effect Heterogeneity",
       x = "", y = "Importance")

# ═══════════════════════════════════════════
# Step 5: Best Linear Projection
# ═══════════════════════════════════════════
blp <- best_linear_projection(cf, X)
print(blp)
# Shows which covariates linearly predict larger/smaller treatment effects

# ═══════════════════════════════════════════
# Step 6: CLAN — Characterize subgroups
# ═══════════════════════════════════════════
cate_pred <- predict(cf)$predictions

# Split into quintiles of predicted CATE
df$cate_quintile <- cut(cate_pred, breaks = quantile(cate_pred, probs = 0:5/5),
                        labels = 1:5, include.lowest = TRUE)

# Average characteristics by quintile
for (v in covariates) {
  cat(sprintf("\n%s by CATE quintile:\n", v))
  print(tapply(df[[v]], df$cate_quintile, mean))
}

# Average treatment effect by quintile (using forest's doubly-robust scores)
for (q in 1:5) {
  ate_q <- average_treatment_effect(cf, target.sample = "all",
                                     subset = df$cate_quintile == q)
  cat(sprintf("Quintile %d: GATE = %.2f (%.2f)\n", q, ate_q[1], ate_q[2]))
}

# ═══════════════════════════════════════════
# Step 7: Distribution of treatment effects
# ═══════════════════════════════════════════
ggplot(data.frame(cate = cate_pred), aes(x = cate)) +
  geom_histogram(bins = 50, fill = "steelblue", alpha = 0.7) +
  geom_vline(xintercept = ate_cf[1], linetype = "dashed", color = "red") +
  labs(title = "Distribution of Predicted Treatment Effects",
       x = "Conditional Average Treatment Effect (CATE)",
       y = "Count") +
  annotate("text", x = ate_cf[1], y = Inf, label = sprintf("ATE = %.0f", ate_cf[1]),
           vjust = 2, hjust = -0.1, color = "red")

# ═══════════════════════════════════════════
# Optional: Optimal policy learning
# ═══════════════════════════════════════════
library(policytree)

# Train a shallow policy tree (interpretable)
policy <- policy_tree(X, cf$W.hat, predict(cf)$predictions, depth = 2)
plot(policy)

# Who should be treated under optimal policy?
df$optimal_treat <- predict(policy, X)
table(df$optimal_treat)
```

> **Reporting recommendations:**
> 1. Report ATE from simple DiM, DML, and Causal Forest — should agree closely (validating the methods)
> 2. Report calibration test results — evidence for/against heterogeneity
> 3. Show variable importance and BLP — which characteristics predict larger effects
> 4. Present GATE (Group Average Treatment Effects) by CATE quintile with CIs
> 5. Show CLAN table — who are the high-benefit vs. low-benefit individuals?
> 6. Caveat: CATE estimates are noisier than ATE. Heterogeneity findings should be treated as exploratory unless pre-specified.
> 7. If relevant, discuss optimal policy implications — but note the gap between statistical targeting and real-world implementation.
