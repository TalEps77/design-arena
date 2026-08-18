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

**Say the cost out loud before you start.** Twelve subagents each researching a
skill and writing a full HTML page is a large run — tens of minutes and a lot of
tokens. Tell the user that in one sentence and get a go-ahead before Step 3. If
they want something cheaper, offer a 4-agent arena (two skills × two tracks) —
the structure works at any even size.

---

## Step 0 — Preflight: skills must be installed

All twelve agents depend on the six skills above. **None of them ship with Claude
Code** — they are third-party skills, so a fresh install of design-arena will
normally find zero of them. Resolve them before spawning anything:

```bash
bash scripts/check_skills.sh
```

(Run it from this skill's directory, or by absolute path — see *Running the
bundled scripts* below.)

Cross-check against the skills roster in your own context: that roster is
authoritative for what the Skill tool can actually invoke, and the script is the
filesystem fallback. A skill that appears in one but not the other is a real
signal — usually a just-installed skill that needs a session restart.

**Record the resolved invoke-name for each skill**, not the bare name. A skill
installed as part of a plugin is invoked as `<plugin>:<skill>` (e.g.
`ui-ux-pro-max:ui-ux-pro-max`). Agents get the resolved name in their prompt; the
mockup filename stays the plain skill name.

If anything is `MISSING`, **stop and read `references/installing-skills.md`** —
it names the upstream repo and the exact install command for each of the six.
Then:

1. Tell the user which are missing and where they'd come from (name the repos —
   you are about to pull third-party code into their `~/.claude/`).
2. Offer to install them. You can run the `npx`/`npm` installers yourself with
   their permission; `/plugin …` commands must be typed by the user.
3. After installing, re-run the preflight. If a skill is on disk but still not
   invocable, have the user restart the session before continuing.

Don't silently drop a missing skill and run 10 agents — the user asked for a fair
six-skill field, and a missing skill quietly changes the competition. If the user
declines to install one, either substitute another design skill or run a smaller
field on purpose — and either way, state the final roster in the gallery so the
comparison is honest.

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
3. **Where the output goes.** `design-arena-output/` at the root of the user's
   project, unless they say otherwise. It is disposable scratch, not source: add
   it to the project's `.gitignore` (or use a scratch directory outside the repo)
   so twelve mockups don't land in their next commit.

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

**Check the blind brief for leaks before you spawn** — the cheapest possible
audit, and the one thing that invalidates half the arena if you skip it:

```bash
grep -nEi '#[0-9a-f]{3,8}\b|rgba?\(|oklch|--[a-z-]+:|font-family|px\b|rem\b|tailwind|class=|currently looks' \
  design-arena-output/_context/blind-brief.md
```

Any hit is a leak unless it is a genuine functional constraint (a fixed viewport
size, a required logo colour the *brand* mandates). Rewrite and re-check.

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

Use this exact prompt template. Fill `{SKILL}` (the **resolved invoke-name** from
Step 0), `{FILE}` (the plain skill name, used in paths), `{TRACK}`, and the
track-specific block.

```
You are competing in a design bake-off. Your entire job is to produce ONE
outstanding design for a single screen.

MANDATORY FIRST ACTION: invoke the `{SKILL}` skill via the Skill tool and follow
it. Your design must reflect that skill's taste and method — that is what you are
here to represent. Do not design generically. If the Skill tool cannot load
`{SKILL}`, stop and report that instead of designing without it — a mockup that
didn't use its skill is not a valid entry.

TARGET SCREEN: {one-line description of the screen}

{TRACK-SPECIFIC BLOCK — see below}

DELIVERABLES (write both, exact paths):
1. design-arena-output/{TRACK}/{FILE}.html
   - One self-contained HTML file. Inline CSS. Inline JS only for motion/interaction.
   - No build step, no external JS deps. Google Fonts <link> is allowed.
   - Must open in a browser and look finished and intentional on its own.
   - Design at ~1440px desktop width; it's fine to also make it responsive.
   - Use realistic content/copy from the brief — no lorem ipsum.
2. design-arena-output/plans/{TRACK}-{FILE}.md
   - A concrete plan to apply THIS design to the real project if it wins:
     the design direction in 2-3 sentences; the token set (colors, type scale,
     spacing, radius, shadows); which real files/components would change and how;
     fonts/assets to add; motion notes; and any risks or effort flags.
     Someone should be able to execute it without having watched you work.

Do not modify any file outside design-arena-output/ — this is a mockup, not an
implementation. Return a 2-3 sentence summary of your design's concept and what
makes it distinct.
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

This is a hard constraint, not a framing device: do not open, grep, screenshot or
otherwise inspect the project's source, stylesheets, design tokens, README,
_context/informed-brief.md, or _context/shots/. If you learn what the product
currently looks like, your entry is disqualified. The blind brief plus your own
judgement is the whole input.

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

It scans `informed/` and `blind/`, embeds each mockup as a scaled live `<iframe>`
preview in a responsive grid, tags each card with its skill + blind/informed
badge, links each to its full-size mockup and its apply-plan, and writes
`design-arena-output/competition-brief.html`. It pairs blind vs informed for the
same skill side by side so the contrast is easy to read. It prints a per-track
summary and exits non-zero if it found no mockups at all — read that output
instead of assuming the gallery is complete.

If the script is unavailable for any reason, hand-build an equivalent HTML gallery
of `<iframe src>` previews — but prefer the script; it's deterministic and keeps
every card consistent.

### Running the bundled scripts

The paths above are relative to **this skill's directory**, not the user's
project. Resolve it once and reuse it:

```bash
ARENA=$(ls -d ~/.claude/skills/design-arena .claude/skills/design-arena 2>/dev/null | head -1)
python3 "$ARENA/scripts/build_brief.py" design-arena-output
bash "$ARENA/scripts/check_skills.sh"
```

If the skill lives somewhere else (a plugin directory, a clone elsewhere), use its
actual absolute path.

---

## Step 5 — Present and let the user pick

Open the brief — the command differs per platform, so pick the one that fits, and
always print the path too in case none of them work:

```bash
open design-arena-output/competition-brief.html   # macOS
xdg-open design-arena-output/competition-brief.html   # Linux
start design-arena-output/competition-brief.html      # Windows
```

If the previews come up blank, the browser is refusing to frame `file://` pages.
Serve the directory instead and open the printed URL:

```bash
python3 -m http.server 8123 --directory design-arena-output
```

Say plainly: twelve designs, six skills each run blind and informed, click any
preview to open it full-size, read the plan link under each. The card previews are
scaled screenshots of the top ~1000px — tell the user to open a design full-size
before judging it, since a preview crops long pages. Ask them to name a winner
(e.g. "informed / high-end-visual-design" or "blind / brandkit"). Don't push your
own favorite unless asked — the whole apparatus exists so *they* choose.

---

## Step 6 — Apply the winner

Once the user picks:

1. Invoke the **winning skill** via the Skill tool — using the resolved
   invoke-name from Step 0 — so the application work carries that skill's taste,
   matching the mockup.
2. Read the winner's plan: `design-arena-output/plans/{track}-{skill}.md`.
3. Apply it to the real project — surgically, following the plan's file list and
   token set. Match the mockup; don't drift.
4. Verify visually before calling it done: run the app / open the changed screen
   and screenshot it, or diff against the winning mockup. A redesign is not
   "applied" until the real screen shows it.

The eleven losing mockups stay on disk for reference. Ask before deleting
`design-arena-output/` — the user may want to revisit a runner-up.

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

## Skill layout (reference)

```
design-arena/
├── SKILL.md
├── references/
│   └── installing-skills.md   # where each of the six design skills comes from
└── scripts/
    ├── check_skills.sh        # Step 0 preflight — resolves invoke-names
    └── build_brief.py         # Step 4 gallery builder
```
