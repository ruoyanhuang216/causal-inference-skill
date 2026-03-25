# Example: Effect of Class Size on Test Scores (Fuzzy RDD)

This example shows how the skill guides a researcher exploiting Maimonides' Rule — a class size cap that creates a regression discontinuity.

---

## Conversation

### User
```
/causal-inference I'm studying whether smaller class sizes improve student test scores. In my country, schools must split a class into two when enrollment exceeds 40 students. I have school-level data on enrollment, average class size, and average test scores.
```

### Phase 1: Problem Framing

**Skill identifies:**
> Your setup matches a classic **Regression Discontinuity Design** — similar to Angrist & Lavy (1999) studying Maimonides' Rule in Israel.
>
> - **Research question**: Does reducing class size improve test scores?
> - **Treatment**: Smaller class size (continuous, but driven by a discrete split)
> - **Running variable**: School enrollment
> - **Cutoff**: 40 students — schools with enrollment just above 40 get two classes (~20 each), while those just below keep one class (~39-40)
> - **Outcome**: Average test scores
> - **Estimand**: LATE at the cutoff — the effect for schools near the 40-student threshold

**Key clarification:**
> This is a **Fuzzy RD**, not Sharp. Crossing the 40-student threshold increases the *probability* of a class split (and thus smaller classes) but may not guarantee it — some schools might get exemptions, or actual class size may not perfectly follow the rule. Is that correct?

### User confirms:
> Yes, it's fuzzy. Most schools follow the rule but not all. The compliance rate is about 85%.

---

### Phase 3: Method Selection

**Skill recommends:**

> **Fuzzy Regression Discontinuity Design**
>
> This is equivalent to an **IV strategy at the cutoff**:
> - **Instrument**: Indicator for enrollment > 40 (crossing the threshold)
> - **First stage**: Crossing the threshold → reduction in class size
> - **Reduced form**: Crossing the threshold → change in test scores
> - **Structural estimate**: Effect of class size on test scores (for compliers at the cutoff)
>
> **Implementation: Local polynomial with optimal bandwidth**
> - Use `rdrobust` package (Calonico, Cattaneo & Titiunik)
> - Local linear regression (polynomial order 1) is the standard choice
> - Triangular kernel weights (more weight to observations near cutoff)
> - MSE-optimal bandwidth selection

---

### Phase 4: Diagnostics

> **Validity checks (critical!):**
>
> 1. **Manipulation test**: Schools might strategically misreport enrollment to stay below 40. Run McCrary/rddensity test.
>    - If there's bunching just below 40, the RD is compromised
>    - Look for a "donut" — excess mass just below, missing mass just above
>
> 2. **Covariate smoothness**: Test that pre-determined characteristics (school location, teacher experience, student demographics) are continuous at the cutoff. Any jump suggests sorting.
>
> 3. **First stage strength**: The jump in class size at 40 must be substantial. Plot average class size against enrollment — you should see a clear sawtooth pattern.
>
> 4. **Bandwidth sensitivity**: Show estimates at 0.5x, 0.75x, 1x, 1.5x, 2x the optimal bandwidth.

---

### Phase 5: Implementation

```r
library(rdrobust)
library(rddensity)

# Center running variable at cutoff
df$enroll_centered <- df$enrollment - 40
df$above_cutoff <- as.numeric(df$enrollment > 40)

# ── Fuzzy RD estimate ──
frd <- rdrobust(y = df$test_scores, x = df$enroll_centered,
                fuzzy = df$class_size, c = 0)
summary(frd)

# ── First stage: class size discontinuity ──
first_stage <- rdrobust(y = df$class_size, x = df$enroll_centered, c = 0)
summary(first_stage)

# ── Reduced form: test score discontinuity ──
reduced_form <- rdrobust(y = df$test_scores, x = df$enroll_centered, c = 0)
summary(reduced_form)

# ── Plots ──
rdplot(y = df$test_scores, x = df$enroll_centered, c = 0,
       title = "Test Scores at Enrollment Cutoff",
       x.label = "Enrollment - 40",
       y.label = "Average Test Score")

rdplot(y = df$class_size, x = df$enroll_centered, c = 0,
       title = "First Stage: Class Size at Enrollment Cutoff",
       x.label = "Enrollment - 40",
       y.label = "Average Class Size")

# ── Manipulation test ──
dens <- rddensity(X = df$enroll_centered, c = 0)
summary(dens)
rdplotdensity(dens, df$enroll_centered,
              title = "McCrary Density Test at Cutoff")

# ── Covariate balance ──
covariates <- c("pct_disadvantaged", "teacher_experience", "school_age")
for (cov in covariates) {
  cat("\n===", cov, "===\n")
  print(summary(rdrobust(y = df[[cov]], x = df$enroll_centered, c = 0)))
}

# ── Bandwidth sensitivity ──
opt_bw <- frd$bws[1, 1]
for (mult in c(0.5, 0.75, 1, 1.25, 1.5, 2)) {
  est <- rdrobust(y = df$test_scores, x = df$enroll_centered,
                  fuzzy = df$class_size, c = 0, h = opt_bw * mult)
  cat(sprintf("BW=%.1f (%.1fx): Estimate=%.3f, SE=%.3f, p=%.3f\n",
              opt_bw * mult, mult, est$coef[1], est$se[3], est$pv[3]))
}
```
