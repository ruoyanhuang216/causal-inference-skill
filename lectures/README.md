# Lectures in Causal Inference

A deep-dive lecture series. Where [`skills/causal-inference/`](../skills/causal-inference/)
tells you *what to run* and [`industry-playbook/`](../industry-playbook/)
tells you *what to do Monday morning*, these lectures tell you **why any
of it works** — and, just as often, why the obvious thing doesn't.

Each lecture derives the identification argument rather than asserting
it, works one realistic example end-to-end with numbers, and closes with
the misreadings that survive into production.

---

## The three layers of this repo

| Layer | Question it answers | Read it when |
| --- | --- | --- |
| [`skills/causal-inference/`](../skills/causal-inference/) | *What method, and what code?* | You're doing the analysis |
| [`industry-playbook/`](../industry-playbook/) | *What do I do before the GM review?* | You have a deadline |
| **`lectures/`** (you are here) | *Why does this identify anything?* | You want to understand it, teach it, or defend it under attack |

The layers cross-reference each other. A lecture ends with pointers to
the playbook chapter and skill reference that operationalize it.

---

## Lectures

| # | Lecture | Core idea | Deepens |
| --- | --- | --- | --- |
| **1** | [Foundations & Treatment Effects](./01-foundations-and-estimands.md) | The counterfactual is missing by construction. ATE / ATT / CATE / ITT / LATE differ only in *whom you average over* — and that choice can flip a ship/no-ship decision. | [`00-foundations.md`](../industry-playbook/00-foundations.md) |
| **2** | [Experimentation](./02-experimentation/) | Run the simplest experiment that satisfies SUTVA without destroying power. Every design is a trade between the two, and **N is the number of randomization units — never the number of users.** | [`01-experiments-first.md`](../industry-playbook/01-experiments-first.md) |

### Lecture 2 chapters

| # | Chapter | Core idea |
| --- | --- | --- |
| 2.1 | [RCT & Assumptions](./02-experimentation/2.1-rct-and-assumptions.md) | Randomization buys one assumption of four. SUTVA, attrition, and compliance are still yours — and SUTVA fails silently. |
| 2.2 | [Power & Multi-Arm](./02-experimentation/2.2-power-and-multi-arm.md) | The inverse-square law: halving the MDE quadruples runtime. Four arms turn a 10-day test into 35 days. |
| 2.3 | [Cluster Randomization](./02-experimentation/2.3-cluster-randomization.md) | Cluster on the graph the treatment *interferes* along, not the graph you have. Effective N → K/ρ. |
| 2.4 | [Geo Experiments & iROAS](./02-experimentation/2.4-geo-experiments.md) | iROAS **is** a Wald ratio — a local derivative, not an average return. 210 DMAs are worth ~13 effective units. |
| 2.5 | [Switchbacks](./02-experimentation/2.5-switchbacks.md) | The window must exceed the washout. Optimal designs throw away most of the data, and that's correct. |
| 2.6 | [Ramp-Up & Bandits](./02-experimentation/2.6-ramp-up-and-bandits.md) | Change enrolled traffic freely; change the T:C ratio never. A homogeneous +1.0 effect reads as +4.81 if you break that rule. |

*More lectures to come — the series is written topic by topic.*

---

## The shape of a lecture

Every lecture follows the same nine-part structure, so the set reads as
one book rather than a pile of notes:

1. **The question it answers** — and why the naive answer fails
2. **Setup and notation** — potential outcomes, consistent across lectures
3. **The identification argument** — derived, not asserted
4. **What the assumptions buy you** — and how each one breaks
5. **The identification hierarchy** — what's available, what isn't, at what credibility
6. **Worked example** — realistic, with numbers, end-to-end
7. **Estimation in Python** — runnable, with the wrong way shown and labeled
8. **Common misreadings** — the errors that pass code review
9. **Summary + references** — with section-level pointers, not just citations

---

## Conventions

- **Math** is LaTeX (`$...$` inline, `$$...$$` display). Renders natively
  on GitHub; converts cleanly to Jupyter, Quarto, PDF, or a static site.
- **Currency is always escaped: `\$50,000`, never `$50,000`.** GitHub reads
  `$...$` as inline math, so two bare amounts on one line — `$250k–$1.25M`
  — make the parser treat `250k–` as math and swallow it. Inside a `$$`
  block, `\$` is already correct LaTeX. Run **`python3 check-math.py`**
  before committing; it flags currency-shaped inline spans and ignores
  real math like `$i$`, `$2^n$`, and `$1/\pi = 5\times$`.
- **DAGs** are ASCII box-and-arrow, so they diff in git, need no build
  step, and never rot. Assumed-absent arrows are drawn dashed and
  labeled — because in a DAG, the missing arrows *are* the assumptions.
- **Code** is Python, matching the packages in
  [`code-templates.md`](../skills/causal-inference/code-templates.md).
- **Notation** is stable across lectures: $Z$ assignment, $D$ treatment
  received, $X$ covariates, $Y$ outcome, $\tau$ treatment effect.

---

## How to read

If you're new: **read Lecture 1**, then jump to whichever lecture matches
your design. The lectures after 1 are largely independent — they all
assume the potential-outcomes vocabulary and nothing else.

If you're preparing for an interview: the *Common misreadings* section of
each lecture is the highest-yield page in this repo. Those are the
answers that separate a senior response from a staff one.

If you're defending an estimate: read the lecture for your method, then
[`06-defending-estimates.md`](../industry-playbook/06-defending-estimates.md).
