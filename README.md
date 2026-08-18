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

**None of the six ship with Claude Code** — they're third-party skills, so a fresh clone of Design Arena will find zero of them installed. A preflight step (`scripts/check_skills.sh`) resolves each one before spawning anything, and `references/installing-skills.md` tells the agent exactly where each comes from and which command installs it. A missing skill silently turns a 12-way field into a 10-way one, and that quietly changes the competition.

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

### 1. The arena itself

```bash
git clone https://github.com/TalEps77/design-arena.git ~/.claude/skills/design-arena
```

The directory name must be `design-arena` (it has to match the skill's `name:`). Keep `SKILL.md`, `scripts/` and `references/` together — the skill reads all three.

### 2. The six design skills

Four of them live in one repo, so most of the work is a single command:

```bash
# gpt-taste, design-taste-frontend, high-end-visual-design, brandkit
npx -y skills add Leonxlnx/taste-skill \
  --skill gpt-taste design-taste-frontend high-end-visual-design brandkit \
  --agent claude-code --global --yes

# impeccable
npx -y impeccable install
```

`ui-ux-pro-max` installs either from the CLI or as a plugin:

```bash
npm install -g ui-ux-pro-max-cli && uipro init --ai claude
```

```
# …or, typed in Claude Code:
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
/plugin install ui-ux-pro-max@ui-ux-pro-max-skill
```

| Skill | Upstream |
|---|---|
| `gpt-taste`, `design-taste-frontend`, `high-end-visual-design`, `brandkit` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) |
| `impeccable` | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) |
| `ui-ux-pro-max` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |

Then verify — this is exactly what the skill runs at Step 0:

```bash
bash ~/.claude/skills/design-arena/scripts/check_skills.sh
```

It prints `OK` plus the **invoke-name** for each skill (a plugin-provided skill is invoked as `plugin:skill`, not by its bare name) or `MISSING`, and exits non-zero if anything is absent. If you skip this, the skill will run it for you and offer to install what's missing — see [`references/installing-skills.md`](references/installing-skills.md).

The roster isn't sacred: `Leonxlnx/taste-skill` also ships `minimalist-ui`, `industrial-brutalist-ui` and others, and any design skill can take a slot. Just tell the arena which six you want.

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

## Repo layout

```
design-arena/
├── SKILL.md                      # the skill itself — the 6-step procedure
├── references/
│   └── installing-skills.md      # where each design skill comes from (read on preflight failure)
└── scripts/
    ├── check_skills.sh           # Step 0 preflight — resolves skills + invoke-names
    └── build_brief.py            # Step 4 — builds the gallery
```

## The gallery script

`scripts/build_brief.py` is deterministic and standalone — no dependencies beyond Python 3:

```bash
python3 scripts/build_brief.py design-arena-output
```

It scans both track directories, embeds each mockup as a scaled live `<iframe>`, tags every card with its skill and blind/informed badge, pairs blind-vs-informed for the same skill side by side, links each card to its full-size mockup and its apply-plan, and writes `competition-brief.html`. It also reports which mockups and plans never showed up, and exits non-zero if nothing was produced at all — so a half-finished round can't quietly look like a complete one.

---

## Notes

- **One screen, not the whole app.** Designing "everything" twelve times produces incomparable mush. One strong screen produces a clean decision.
- **Twelve parallel agents is heavy.** If the environment struggles, run two waves of six — but keep the briefs identical.
- **A failed agent doesn't block the round.** Respawn that one, or mark it absent in the gallery.
- **Applied means verified.** A redesign isn't done until the real screen renders it and you've seen a screenshot.
- **It's an expensive run.** Twelve agents each researching a skill and writing a full page costs real time and tokens. The skill says so before it spawns; a smaller arena (two skills × two tracks) works the same way.
- **Blank previews?** Your browser is refusing to frame `file://` pages. `python3 -m http.server 8123 --directory design-arena-output` and open the printed URL.

---

## License

MIT
