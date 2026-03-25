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

```python
from rdrobust import rdrobust, rdplot
from rddensity import rddensity
import pandas as pd

# Center running variable at cutoff
df['enroll_centered'] = df['enrollment'] - 40
df['above_cutoff'] = (df['enrollment'] > 40).astype(int)

# ── Fuzzy RD estimate ──
frd = rdrobust(Y=df['test_scores'], X=df['enroll_centered'],
               fuzzy=df['class_size'], c=0)
print(frd)

# ── First stage: class size discontinuity ──
first_stage = rdrobust(Y=df['class_size'], X=df['enroll_centered'], c=0)
print('First Stage:')
print(first_stage)

# ── Reduced form: test score discontinuity ──
reduced_form = rdrobust(Y=df['test_scores'], X=df['enroll_centered'], c=0)
print('Reduced Form:')
print(reduced_form)

# ── Plots ──
rdplot(y=df['test_scores'], x=df['enroll_centered'], c=0,
       title='Test Scores at Enrollment Cutoff',
       x_label='Enrollment - 40', y_label='Average Test Score')

rdplot(y=df['class_size'], x=df['enroll_centered'], c=0,
       title='First Stage: Class Size at Enrollment Cutoff',
       x_label='Enrollment - 40', y_label='Average Class Size')

# ── Manipulation test ──
density_test = rddensity(X=df['enroll_centered'], c=0)
print(density_test)

# ── Covariate balance ──
for cov in ['pct_disadvantaged', 'teacher_experience', 'school_age']:
    print(f'\n=== {cov} ===')
    print(rdrobust(Y=df[cov], X=df['enroll_centered'], c=0))

# ── Bandwidth sensitivity ──
opt_bw = frd.bws.values[0, 0]
for mult in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
    est = rdrobust(Y=df['test_scores'], X=df['enroll_centered'],
                   fuzzy=df['class_size'], c=0, h=opt_bw * mult)
    coef = est.coef.values[0]
    se = est.se.values[2]
    pv = est.pv.values[2]
    print(f'BW={opt_bw*mult:.1f} ({mult:.2f}x): Estimate={coef:.3f}, SE={se:.3f}, p={pv:.3f}')
```
