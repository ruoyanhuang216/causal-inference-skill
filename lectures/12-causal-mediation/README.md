# Lecture 12 — Causal Mediation Analysis

> **Prerequisites:** [Lecture 1](../01-foundations-and-estimands.md) (potential outcomes) and [Lecture 8 §8.1](../08-selection-on-observables/8.1-propensity-and-unconfoundedness.md) (unconfoundedness, post-treatment bias). Part IV.
> **Deepens:** [`industry-playbook/`](../../industry-playbook/).
> **Scope note:** a higher-level overview (per the lighter-notes request) — the mechanism, the danger, and the toolkit. Chapters can be expanded later.

Everything so far answered *"did the treatment $D$ affect the outcome $Y$?"*
Mediation answers the next question the PM always asks: **"*why*? Through what
mechanism?"** It decomposes a total effect into the part that flows *through* an
intermediate variable and the part that doesn't. It's the most useful — and most
statistically treacherous — question in the book.

---

## 1. The question — direct vs. indirect

**The Spotify example.** An email campaign $D$ (offer a 1-month free trial) raises
6-month retention $Y$ by **+5%**. *Why?*

- Did the email work because users liked the free month — a **direct effect**?
- Or did the email cause them to **download the mobile app** $M$, and *having the
  app* is what actually drove retention — an **indirect effect** through $M$?

The business consequence is opposite: if it's the app, stop sending emails and
just push app downloads.

```
              ┌──────────── direct effect (NDE) ─────────────┐
              │                                              ▼
   Email (D) ─┼──► App download (M) ──► Retention (Y)
              └──────── indirect effect (NIE) ───────────────┘
```

---

## 2. NDE and NIE

- **Natural Direct Effect (NDE):** the effect of $D$ on $Y$ **holding the
  mediator at whatever it *would naturally have been*** — the email's effect *not*
  routed through the app.
- **Natural Indirect Effect (NIE):** the effect of $D$ on $Y$ **strictly through
  the change in $M$** — the retention gain that exists *only because* the email
  moved app downloads.

Under standard conditions, **Total Effect = NDE + NIE.** Splitting the +5%
into these two is the whole deliverable.

---

## 3. The danger — post-treatment bias

Mediation is treacherous because of **one brutal fact**: even with a *perfectly
randomized* A/B test of the email $D$, **you did not randomize the mediator
$M$.** Whether a user downloads the app is a *choice* — and the people who chose
to are structurally different from those who didn't.

So to identify the NIE you must assume **sequential ignorability**: *no
unobserved confounders between the mediator $M$ and the outcome $Y$.* But
"downloads the app" and "retains" almost certainly share hidden common causes —
underlying engagement, intent, device loyalty. Conditioning on the mediator opens
a **collider / post-treatment-bias path** (the same trap as
[Lecture 2 §README.3.4](../02-experimentation/README.md) and
[Lecture 1's "filter to compliers"](../01-foundations-and-estimands.md)).

The assumption is **strong, untestable, and usually violated** — which is why
mediation results deserve heavy skepticism and a sensitivity analysis
([Lecture 11](../11-sensitivity-and-partial-id/)) attached to the NIE.

There's a further, subtler assumption — **no treatment-induced mediator-outcome
confounding** (the "cross-world" condition): the treatment must not create a
variable that then confounds the $M \to Y$ relationship. It's the reason NDE/NIE
are harder to identify than they first look.

---

## 4. The toolkit

- **Never use Baron-Kenny (1986).** The classic "run three regressions, multiply
  the coefficients" recipe assumes **everything is linear and there is no
  treatment-mediator interaction.** It silently misleads with binary outcomes or
  when the email only works *if* you download the app *and* you're on iOS.
- **Use Imai, Keele & Tingley (2010)** — the `mediation` package (R) — which
  identifies NDE/NIE **non-parametrically**, handles interactions, and ships with
  a **built-in sensitivity analysis** (a parameter $\rho$ = the correlation of the
  mediator and outcome residuals) for exactly the §3 violation.
- **Or VanderWeele's framework (2015)** — the most comprehensive treatment,
  explicitly allowing treatment-mediator interaction, and connecting mediation to
  the sensitivity/E-value machinery of Lecture 11.

---

## 5. When (and whether) to reach for it

Mediation is worth it when the **mechanism changes the decision** (email vs. app
push). But respect the ladder of credibility:

1. **Best:** *experimentally manipulate the mediator too.* If you can randomly
   encourage app downloads (an encouragement design / IV — Lecture 5, Lecture 8
   §8.1), you sidestep the mediator-outcome confounding entirely. This is far
   stronger than any mediation formula on observational $M$.
2. **Acceptable:** Imai/VanderWeele mediation **with a reported sensitivity
   analysis** on the NIE.
3. **Never:** Baron-Kenny coefficients presented as clean causal mechanism.

The honest one-liner for leadership: *"We can estimate how much of the email's
effect runs through app downloads, but that number assumes no hidden confounder
between downloading and retaining — an assumption we can't test, so here's how
fragile it is."*

---

## 6. References

- **Imai, Keele & Tingley (2010).** "A General Approach to Causal Mediation Analysis." *Psychological Methods.* — the `mediation` package; non-parametric NDE/NIE + sensitivity.
- **VanderWeele (2015).** *Explanation in Causal Inference: Methods for Mediation and Interaction.* — the comprehensive modern reference.
- **Pearl (2001).** "Direct and Indirect Effects." *UAI.* — the natural direct/indirect effect definitions.
- **Baron & Kenny (1986).** "The Moderator-Mediator Variable Distinction..." *JPSP.* — the classic method, included to know *why not* to use it.
- **VanderWeele (2016).** "Mediation Analysis: A Practitioner's Guide." *Annual Review of Public Health.* — the readable how-to.
