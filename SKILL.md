---
name: design-arena
description: >-
  Run a 12-way design competition ("bake-off") on a UI. Spins up 12 subagents —
  6 INFORMED (see the current design, make it better) and 6 BLIND (see only what
  the product DOES, design from scratch, never seeing the current look) — each
  invoking one of six design skills (gpt-taste, ui-ux-pro-max,
  high-end-visual-design, impeccable, design-taste-frontend, brandkit). Every
  agent ships a real self-contained HTML mockup. Output: one HTML gallery brief
  with all 12 live previews (tagged blind/informed + skill) plus a per-design
  markdown apply-plan, so the user picks a winner to apply. Use WHENEVER the user
  wants to redesign or explore visual directions for a UI and wants OPTIONS to
  compare — "design competition", "design bake-off", "design arena", "give me
  several redesigns to pick from", "have agents redesign this", "blind vs
  informed designs", "compete designs", "which look is best". Prefer over a
  single-shot redesign when the user wants to compare multiple takes.
---

# Design Arena

A design competition. Twelve subagents redesign the same target screen; the user
picks the winner from a live-preview gallery; the winning skill + its plan are
then applied to the real project.

Two tracks, six skills each:

- **Informed (6):** each agent sees the *current* visual design and tries to make
  it better. One agent per skill.
- **Blind (6):** each agent sees only a *functional* spec — what the product is
  and does — and never sees the current look. It designs from scratch. One agent
  per skill.

Because each of the six skills runs once blind and once informed, the gallery
lets the user compare not just skill-vs-skill but also "polish the existing
direction" vs "start clean" for the same taste engine. That contrast is the whole
point: sometimes the current design is a local maximum and only a blind agent
escapes it.

The six skills: `gpt-taste`, `ui-ux-pro-max`, `high-end-visual-design`,
`impeccable`, `design-taste-frontend`, `brandkit`.

---

## Step 0 — Preflight: skills must be installed

All twelve agents depend on the six skills above. Before spawning anything,
confirm each is installed (they live in `~/.claude/skills/<name>/` or a plugin
skills dir):

```bash
for s in gpt-taste ui-ux-pro-max high-end-visual-design impeccable design-taste-frontend brandkit; do
  d=$(ls -d ~/.claude/skills/"$s" 2>/dev/null)
  echo "$s -> ${d:-MISSING}"
done
```

If any are `MISSING`, stop and tell the user which ones, then offer to install
them via the `find-skills` skill (or a plugin marketplace). Don't silently drop a
missing skill and run 10 agents — the user asked for a fair six-skill field, and a
missing skill quietly changes the competition. Get confirmation, then continue.

---

## Step 1 — Scope the arena

A competition is only meaningful if all twelve agents design **the same thing at
the same fidelity**. Pin these down before spawning:

1. **The target screen.** One page/view is the unit of competition (landing page,
   dashboard home, settings, the main app shell — whatever matters most). If the
   product has many screens and it's not obvious which one, ask the user to pick
   one. Designing "the whole app" 12 times produces incomparable mush; one strong
   screen produces a clean decision.
2. **Fidelity target.** A single self-contained HTML file per agent: inline CSS,
   inline JS only if it adds motion/interaction, no external deps, no CDN, fonts
   via system stack or `@font-face` data-URIs / Google Fonts `<link>` (allowed
   here since these open in a normal browser, not a CSP'd artifact). It must open
   and look finished on its own.

---

## Step 2 — Build the two context packages

This is the most important step. The blind/informed split only works if you
prepare **two genuinely different** briefs. Gather inputs flexibly — use whatever
is available:

- **Local project files** (default): read the target screen's source — markup,
  styles/tokens, component files, copy/content, routes.
- **Screenshots** (if Chrome tools are available and the app runs, or the user
  provides images): capture the current screen at desktop width. Great for the
  informed package.
- **Live URL** (if provided and reachable): fetch it / screenshot it.

Then assemble:

### Informed package (given to the 6 informed agents)
Everything about how it looks *and* works:
- Screenshots of the current screen (if you have them).
- The relevant source: HTML/JSX, CSS/tokens/theme, key component code.
- The URL, if any.
- A short note: brand, audience, what's good and what feels off today.

The informed agent's job: **keep what works, fix what doesn't, raise the ceiling.**

### Blind package (given to the 6 blind agents)
A **functional spec with every visual signal stripped out.** Include:
- What the product is and who it's for.
- What this screen must let the user do (features, primary actions).
- The content and real copy that must appear (headlines, labels, data, sections).
- Information architecture / hierarchy of importance (what's primary vs secondary).
- Hard constraints (must fit these nav items, this data table has N columns, etc.).

Do **not** include: current colors, fonts, spacing, layout, screenshots, CSS,
class names, or "it currently looks like…". If a blind agent can reconstruct the
present design from your brief, the brief leaked — rewrite it. The reason to be
strict: a blind agent that peeks just polishes the status quo, and you already get
that from the informed track. Blind's value is a design that owes nothing to the
current one.

Write both packages to disk so every agent reads an identical brief:
- `design-arena-output/_context/informed-brief.md`
- `design-arena-output/_context/blind-brief.md`
- put any screenshots in `design-arena-output/_context/shots/`.

---

## Step 3 — Spawn the 12 agents

Create the output tree first:

```bash
mkdir -p design-arena-output/{informed,blind,plans,_context/shots}
```

Spawn **all 12 in parallel** (one message, twelve `Agent` tool calls) so the
round finishes together. Use the `general-purpose` agent type. Each agent invokes
exactly one skill and writes exactly two files: its HTML mockup and its apply-plan.

Use this exact prompt template. Fill `{SKILL}`, `{TRACK}`, and the track-specific
block.

```
You are competing in a design bake-off. Your entire job is to produce ONE
outstanding design for a single screen.

MANDATORY FIRST ACTION: invoke the `{SKILL}` skill via the Skill tool and follow
it. Your design must reflect that skill's taste and method — that is what you are
here to represent. Do not design generically.

TARGET SCREEN: {one-line description of the screen}

{TRACK-SPECIFIC BLOCK — see below}

DELIVERABLES (write both, exact paths):
1. design-arena-output/{TRACK}/{SKILL}.html
   - One self-contained HTML file. Inline CSS. Inline JS only for motion/interaction.
   - No build step, no external JS deps. Google Fonts <link> is allowed.
   - Must open in a browser and look finished and intentional on its own.
   - Design at ~1440px desktop width; it's fine to also make it responsive.
   - Use realistic content/copy from the brief — no lorem ipsum.
2. design-arena-output/plans/{TRACK}-{SKILL}.md
   - A concrete plan to apply THIS design to the real project if it wins:
     the design direction in 2-3 sentences; the token set (colors, type scale,
     spacing, radius, shadows); which real files/components would change and how;
     fonts/assets to add; motion notes; and any risks or effort flags.
     Someone should be able to execute it without having watched you work.

Return a 2-3 sentence summary of your design's concept and what makes it distinct.
```

**Informed track block** (`{TRACK}` = `informed`):
```
You CAN see the current design. Read design-arena-output/_context/informed-brief.md
and any screenshots in _context/shots/. Your goal is to make the CURRENT design
meaningfully better — sharpen hierarchy, fix what feels cheap or generic, raise
the craft — while respecting what already works and the product's brand. This is a
redesign of something real, not a blank canvas.
```

**Blind track block** (`{TRACK}` = `blind`):
```
You must design FROM SCRATCH. Read ONLY design-arena-output/_context/blind-brief.md.
You have NOT seen the current design and must not ask for it — that's deliberate.
Interpret the product's function and invent the strongest visual direction you can.
Owe nothing to how it looks today.
```

Notes:
- If a subagent returns without writing its file (skill error, ran out of room),
  note it and either respawn that one agent or mark it absent in the brief — don't
  let one failure block the other eleven.
- Twelve parallel agents is heavy; if the environment struggles, run them in two
  waves of six (all informed, then all blind), but keep the briefs identical.

---

## Step 4 — Assemble the competition brief

Once the mockups exist, build the gallery with the bundled script:

```bash
python3 scripts/build_brief.py design-arena-output
```

(Path is relative to this skill's directory — run it as
`python3 ~/.claude/skills/design-arena/scripts/build_brief.py design-arena-output`
or with the absolute skill path.)

It scans `informed/` and `blind/`, embeds each mockup as a scaled live `<iframe>`
preview in a responsive grid, tags each card with its skill + blind/informed
badge, links each to its full-size mockup and its apply-plan, and writes
`design-arena-output/competition-brief.html`. It pairs blind vs informed for the
same skill side by side so the contrast is easy to read.

If the script is unavailable for any reason, hand-build an equivalent HTML gallery
of `<iframe src>` previews — but prefer the script; it's deterministic and keeps
every card consistent.

---

## Step 5 — Present and let the user pick

Open the brief and tell the user to judge:

```bash
open design-arena-output/competition-brief.html
```

Say plainly: twelve designs, six skills each run blind and informed, click any
preview to open it full-size, read the plan link under each. Ask them to name a
winner (e.g. "informed / high-end-visual-design" or "blind / brandkit"). Don't
push your own favorite unless asked — the whole apparatus exists so *they* choose.

---

## Step 6 — Apply the winner

Once the user picks:

1. Invoke the **winning skill** via the Skill tool (so the application work
   carries that skill's taste, matching the mockup).
2. Read the winner's plan: `design-arena-output/plans/{track}-{skill}.md`.
3. Apply it to the real project — surgically, following the plan's file list and
   token set. Match the mockup; don't drift.
4. Verify visually before calling it done: run the app / open the changed screen
   and screenshot it, or diff against the winning mockup. A redesign is not
   "applied" until the real screen shows it.

---

## Output layout (reference)

```
design-arena-output/
├── _context/
│   ├── informed-brief.md      # full visual + functional brief
│   ├── blind-brief.md         # functional-only, visuals stripped
│   └── shots/                 # current-design screenshots (informed only)
├── informed/                  # 6 mockups (one per skill)
│   ├── gpt-taste.html
│   ├── ui-ux-pro-max.html
│   ├── high-end-visual-design.html
│   ├── impeccable.html
│   ├── design-taste-frontend.html
│   └── brandkit.html
├── blind/                     # 6 mockups (one per skill), built from scratch
│   └── … (same six filenames)
├── plans/                     # 12 apply-plans
│   ├── informed-gpt-taste.md
│   ├── blind-gpt-taste.md
│   └── …
└── competition-brief.html     # generated gallery — the thing the user judges
```
