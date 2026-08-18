# 🏟️ Design Arena

**A 12-way design competition for any UI screen — run inside [Claude Code](https://claude.com/claude-code).**

One screen. Twelve subagents. Six design skills, each run **twice**: once *informed* (sees your current design and tries to beat it) and once *blind* (sees only what the product **does**, and designs from scratch). Every agent ships a real, self-contained HTML mockup. You get a single gallery page with all twelve live previews and pick a winner — then the winning direction gets applied to your actual codebase.

---

## Why blind vs informed

Most AI redesigns polish what's already there. That's useful — until the current design is a *local maximum* and no amount of polish escapes it.

| Track | Sees | Job |
|---|---|---|
| **Informed** (6 agents) | Screenshots, source, CSS, tokens, brand notes | Keep what works, fix what's cheap, raise the ceiling |
| **Blind** (6 agents) | A functional spec only — copy, actions, hierarchy, constraints. **No colors, fonts, layout, or screenshots.** | Invent the strongest direction from nothing |

Because each of the six skills runs once on each track, the gallery lets you compare **skill vs skill** *and* **polish vs start-clean for the same taste engine**. That contrast is the whole point.

If a blind agent could reconstruct your current design from its brief, the brief leaked — and the skill tells the orchestrator to rewrite it.

---

## The six taste engines

Each agent is required to invoke exactly one design skill and design in its voice:

- `gpt-taste`
- `ui-ux-pro-max`
- `high-end-visual-design`
- `impeccable`
- `design-taste-frontend`
- `brandkit`

A preflight step checks all six are installed before spawning anything — a missing skill silently turns a 12-way field into a 10-way one, and that quietly changes the competition.

---

## How it runs

```
Step 0  Preflight ......... verify all six design skills are installed
Step 1  Scope ............. pin ONE target screen + fidelity (single self-contained HTML)
Step 2  Two briefs ........ build informed-brief.md and blind-brief.md (visuals stripped)
Step 3  Spawn ............. 12 agents in parallel, one skill each
Step 4  Assemble .......... build_brief.py renders the live-preview gallery
Step 5  Judge ............. you open the gallery and name a winner
Step 6  Apply ............. winning skill + its plan applied to the real code, verified visually
```

Every agent writes exactly two files: its **mockup** (`.html`) and its **apply-plan** (`.md`) — design direction, token set, which real files change, fonts/assets, motion notes, risks. Someone can execute the plan without having watched the agent work.

---

## Output layout

```
design-arena-output/
├── _context/
│   ├── informed-brief.md      # full visual + functional brief
│   ├── blind-brief.md         # functional-only, visuals stripped
│   └── shots/                 # current-design screenshots (informed only)
├── informed/                  # 6 mockups, one per skill
├── blind/                     # 6 mockups, same six filenames
├── plans/                     # 12 apply-plans
└── competition-brief.html     # the gallery you judge
```

---

## Install

Drop the skill into your Claude Code skills directory:

```bash
git clone https://github.com/TalEps77/design-arena.git ~/.claude/skills/design-arena
```

Or copy just the two files (`SKILL.md` and `scripts/build_brief.py`) into `~/.claude/skills/design-arena/`.

Then make sure the six design skills above are installed too — Claude Code's `find-skills` skill can locate them.

---

## Use

Just ask, in plain language:

> "run a design arena on my dashboard"
> "design bake-off for the landing page"
> "give me several redesigns to pick from"
> "blind vs informed designs for the settings screen"

The skill auto-triggers on those. Or invoke it directly:

```
/design-arena
```

---

## The gallery script

`scripts/build_brief.py` is deterministic and standalone — no dependencies beyond Python 3:

```bash
python3 scripts/build_brief.py design-arena-output
```

It scans both track directories, embeds each mockup as a scaled live `<iframe>`, tags every card with its skill and blind/informed badge, pairs blind-vs-informed for the same skill side by side, links each card to its full-size mockup and its apply-plan, and writes `competition-brief.html`.

---

## Notes

- **One screen, not the whole app.** Designing "everything" twelve times produces incomparable mush. One strong screen produces a clean decision.
- **Twelve parallel agents is heavy.** If the environment struggles, run two waves of six — but keep the briefs identical.
- **A failed agent doesn't block the round.** Respawn that one, or mark it absent in the gallery.
- **Applied means verified.** A redesign isn't done until the real screen renders it and you've seen a screenshot.

---

## License

MIT
