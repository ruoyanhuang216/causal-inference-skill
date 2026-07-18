# Lecture 5 — Instrumental Variables

> **Prerequisites:** [Lecture 1 — Foundations & Estimands](../01-foundations-and-estimands.md) (LATE, compliers, monotonicity, the Wald ratio) and [Lecture 4 §4.2 — Fuzzy RDD](../04-regression-discontinuity/4.2-fuzzy-rdd.md) (which *is* an IV). IV is the general machine those two are special cases of.
> **Deepens:** [`industry-playbook/02-quasi-experimental.md`](../../industry-playbook/02-quasi-experimental.md).

Everywhere else in this series, identification came from a *design* — you
randomized, you found a rollout, you found a cutoff. Instrumental variables
is what you reach for when there is **no clean design and the treatment is
confounded**: motivated users adopt the feature *and* retain better, so OLS
can't separate the feature from the motivation. IV finds a lever — an
**instrument** — that moves the treatment *without* touching the confounder,
and uses only that slice of variation. It is the most powerful and the most
easily abused tool in the observational toolkit.

---

## 1. The core idea

The problem: treatment $D$ is correlated with the error term — with the
unobserved confounders in $Y$. OLS of $Y$ on $D$ is hopelessly biased,
because it attributes the confounder's effect to $D$.

The fix: find an instrument $Z$ that (a) **moves $D$**, and (b) is otherwise
**disconnected from everything in $Y$'s error**. Then $Z$ acts as a *filter*:
it isolates only the part of $D$ that came from $Z$'s exogenous variation,
and throws away the confounded part. Regress $Y$ on that filtered treatment
and you recover the causal effect — for the units the instrument actually
moves.

```
   Confounded reality:              IV isolates the clean variation:

     U (unobserved)                   Z ──────► D ──────► Y
    ╱          ╲                      (instrument moves D,
   D ─────────► Y                      but reaches Y ONLY through D)
   (OLS blames D                          │
    for U's effect)                       U ──────► Y
                                      (U still confounds D, but Z
                                       doesn't touch U — so the
                                       Z-driven part of D is clean)
```

The whole game is finding a $Z$ that genuinely satisfies (b), because (b)
is **untestable** and (a) is where you get punished for being greedy.

---

## 2. The four assumptions

IV lives or dies on four conditions. Two you can check; two you must argue.

| # | Assumption | Statement | Testable? |
|---|---|---|---|
| 1 | **Relevance** | $\text{Cov}(Z, D) \neq 0$ — the instrument moves treatment | ✅ Yes — first-stage F |
| 2 | **Exclusion** | $Z$ affects $Y$ *only* through $D$ — no direct or backdoor path | ❌ **No — argue it** |
| 3 | **Independence** | $Z$ is as-good-as-randomly assigned (maybe given covariates $X$) | ~ Partly (balance tests) |
| 4 | **Monotonicity** | $Z$ moves $D$ the same direction for everyone — no defiers | ❌ Mostly — argue it |

**The exclusion restriction is where every IV dies.** Relevance you can
measure. Independence you can partly check with balance tests. But exclusion
— that the instrument has *no other path* to the outcome — is a claim about
the absence of a channel you can't see, and no statistic proves it. Every IV
critique in this lecture (the Zoom call, the auto-pay setup, the consulting
call) is an exclusion attack, and the defense is always business logic, never
a p-value.

---

## 3. The estimand: LATE, or ACR for continuous treatment

IV does **not** give the ATE. With a **binary** treatment it gives the
**LATE** — the effect for *compliers*, the units whose treatment status the
instrument actually flips (Lecture 1 §4). Always-takers and never-takers are
invisible: the instrument doesn't move them, so the data carries no
information about their effect.

With a **continuous** treatment (dollars of credit, dollars collected), 2SLS
gives the **Average Causal Response (ACR)** — a weighted average of the
per-unit marginal effect $E[Y(d) - Y(d-1)]$ across the treatment
distribution, weighted by how many compliers the instrument moves across each
margin (Angrist & Imbens 1995). The interpretation shifts from "the effect of
being treated" to "the effect of the marginal dollar, for the units whose
dollars respond to the instrument." §5.3's collection-agent design is an ACR,
and naming it correctly is a staff-level distinction.

Either way: **name the complier population.** "IV says X" is incomplete;
"IV says X for the units the instrument moves" is the honest claim.

---

## 4. The family

Three ways to find an instrument, three chapters:

| # | Chapter | The instrument is… | Canonical use |
|---|---|---|---|
| **5.1** | [Standard 2SLS](./5.1-standard-2sls.md) | any variable satisfying the four assumptions | the general machine; weak-instrument diagnostics |
| **5.2** | [Shift-Share / Bartik](./5.2-shift-share-bartik.md) | local exposure shares × global shocks | one endogenous regressor, a structural exposure |
| **5.3** | [Judge / Examiner IV](./5.3-judge-examiner-iv.md) | the leniency of a randomly-assigned human decider | human-in-the-loop decisions (loans, moderation, courts) |

They're the same machine (§5.1) with different sources of the exogenous
variation. Shift-share manufactures an instrument from structure; judge IV
harvests one from the randomness of case routing.

---

## 5. Through-lines

**IV moves the untestable assumption, it doesn't remove it.** Unconfoundedness
methods need you to observe the confounders. IV frees you from that — and
charges you the exclusion restriction instead, which is *also* untestable.
You've swapped "I've measured every confounder" for "my instrument has no
other channel." Choose the one you can defend. §2.

**Two failure modes dominate every IV.** *Weak instruments* (relevance too
weak → estimate biased back toward OLS, standard errors explode) and
*exclusion violations* (a backdoor channel → bias, undetectable). Every IV
diagnostic targets one of these. §5.1.

**2SLS = reduced form ÷ first stage.** If the instrument has no raw
relationship with the outcome (a null reduced form), the IV is dead — no
amount of 2SLS machinery revives it. Look at the reduced form *first*. §5.1.

**Name the compliers.** IV is a LATE (or ACR). It speaks only for the units
the instrument moves, never the whole population. §3.

---

## 6. References

- **Angrist & Krueger (2001).** "Instrumental Variables and the Search for Identification." *Journal of Economic Perspectives.* — The gentle, intuition-first introduction.
- **Imbens & Angrist (1994).** "Identification and Estimation of Local Average Treatment Effects." *Econometrica.* — The LATE theorem.
- **Angrist & Imbens (1995).** "Two-Stage Least Squares Estimation of Average Causal Effects in Models with Variable Treatment Intensity." *JASA.* — The ACR of §3.
- **Angrist, Imbens & Rubin (1996).** "Identification of Causal Effects Using Instrumental Variables." *JASA.* — The four assumptions, formally.
- **Angrist & Pischke (2009).** *Mostly Harmless Econometrics*, Ch. 4. — The definitive practitioner treatment.
