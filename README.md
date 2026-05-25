# Knuth-Bendix Completion (Web Interface)

A single self-contained HTML page that runs Knuth-Bendix completion entirely
in the browser via [Pyodide](https://pyodide.org). Works on Chrome, Firefox,
and Safari with no installation.

Enter equations, declare any associative-commutative operators, pick the
algorithm, and get back a confluent set of rewrite rules — or an explanation
of why the algorithm couldn't finish.

## Try it

- **GitHub Pages:** `https://<your-username>.github.io/<repo-name>/`
  (enable Pages on the `main` branch, `/` root)
- **Locally:** open `index.html` directly, or
  ```sh
  python -m http.server 8000
  ```
  and visit <http://localhost:8000/index.html>.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | The whole interface — UI, embedded Python sources, Pyodide loader. Nothing else is required at runtime. |
| `knuth_bendix.py` | Standalone reference implementation: Robinson unification, LPO with lexicographic status, Huet-style completion. |
| `ac_knuth_bendix.py` | AC variant: AC matching, enumerative AC unification, extension rules, AC-compatible RPO with multiset status under AC heads. |
| `unfailing_knuth_bendix.py` | Unfailing (ordered) completion à la Bachmair-Dershowitz-Plaisted/Hsiang-Rusinowitch: keeps unorientable equations and uses them by ordered rewriting (strictly decreasing instances only). Output is `(rules, equations)`. |
| `.claude/launch.json` | Optional — config used by Claude Code's preview panel to serve the page on `localhost:8765`. |

The two `.py` files are inlined into `index.html`; you only need them if you
want to run the algorithms directly from a Python REPL or modify them.

## Using the interface

```
m(e, x)       = x
m(i(x), x)    = e
m(m(x, y), z) = m(x, m(y, z))
```

- One equation per line, `lhs = rhs`. `#` starts a comment.
- Identifiers starting with `u v w x y z` are variables. Everything else is
  a function symbol or (if nullary) a constant.
- **AC operators**: comma-separated list, e.g. `p, plus`.
- **Precedence**: comma-separated, **highest first**, e.g. `i, m, e`. Symbols
  you don't list get rank 0.

Built-in presets demonstrate the free group (standard), the abelian group (AC),
and an idempotent AC semigroup.

## Algorithms

Both algorithms use a **recursive path ordering (RPO)** parameterised by your
precedence:

- **Standard KB** — LPO with lexicographic status for every symbol.
  Huet-style completion: orient each equation, simplify rules with the new
  rule (compose/collapse), then add all critical pairs as fresh equations.
- **AC KB** — RPO with **multiset status under AC heads** (required so that
  `f(a, b)` and `f(b, a)` are ordered the same way). AC subterms are
  flattened and canonically sorted; rewriting uses AC matching; critical
  pairs use AC unification; for every AC-rooted rule an extension rule
  `f(l, X) → f(r, X)` is added to catch overlaps below the root.
- **Unfailing KB** — independently introduced by Bachmair, Dershowitz &
  Plaisted ("Completion without failure", 1989) and by Hsiang & Rusinowitch
  ("On word problems in equational theories", ICALP 1987 / JACM 1991).
  Same LPO, but equations the precedence can't orient are kept as
  unoriented pairs. Rewriting with an equation `l = r` is only allowed when
  the matched instance `σ(l)` is strictly greater than `σ(r)`. The output
  is `(rules, equations)`; if the equation list is empty the system is
  fully confluent, otherwise it is **ground-confluent** — every pair of
  equal *ground* terms still has a common normal form.

## Limitations

- Completion is **semi-decidable**. If a finite confluent system exists and
  the precedence orients every generated equation, the procedure finds it.
  Otherwise it fails with "cannot orient" or never saturates.
- RPO is silent on equations like `f(x, y) = f(y, x)`. Those can only be
  handled by declaring `f` AC and switching to AC mode, or by switching to
  Unfailing mode (which keeps them as unorientable equations).
- AC unification here is **enumerative** and assumes every variable binds
  to a **non-empty** term — unit elements absorbed into AC operators are
  not supported.
- No conditional rules, no built-in equality predicate, no sorts.
- AC unification is worst-case exponential; the iteration limit is the
  only brake.

## When it fails

| Message | Meaning | What to try |
| --- | --- | --- |
| `Cannot orient: s = t` | RPO can't compare the two sides. | Reorder the precedence so the intended LHS's head symbol comes earlier; if both heads coincide on the same argument multiset, declare it AC, or switch to *Unfailing* mode (keeps the equation as-is). |
| `did not saturate in N iterations` | Critical pairs kept coming. | Raise *Max iterations*. If still failing, try a different precedence — the theory may have no finite confluent presentation. |
| parse error | Bad syntax. | One `=` per non-blank line; check parens. |
| recursion-limit error | A generated term blew Python's stack. | Usually a divergent system — try a coarser precedence or fewer iterations. |
