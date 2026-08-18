# Installing the roster's design skills

Read this when Step 0 preflight reports a skill as `MISSING`. It maps every
default roster entry to its upstream and the exact command that installs it.

**None of these ship with Claude Code.** `frontend-design` is Anthropic-maintained
but still installed separately; the other five are third-party. A fresh clone of
design-arena will normally find zero of them installed.

| Skill | Upstream | Install |
|---|---|---|
| `frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) | `npx skills add` |
| `design-taste-frontend` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `npx skills add` |
| `impeccable` | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | `npx impeccable install` |
| `ui-ux-pro-max` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | `uipro init` or plugin marketplace |
| `apple-design` | [emilkowalski/skills](https://github.com/emilkowalski/skills) | `npx skills add` |
| `superdesign` | [superdesigndev/superdesign-skill](https://github.com/superdesigndev/superdesign-skill) | `npx skills add` |

## Who runs what

You (the orchestrator) can run every `npx` / `npm` command below yourself, with the
user's permission — they are ordinary shell commands. You **cannot** run
`/plugin marketplace add …`; slash commands are typed by the user into their own
session. So: prefer the CLI installers, and only fall back to asking the user to
type a slash command when the CLI route fails.

Always ask before installing. These commands download and write third-party code
into the user's `~/.claude/` (or the project's `.claude/`) — that is the user's
call, not yours. Name the repos you're about to pull from.

`--global` writes to `~/.claude/skills/<name>/` (available in every project). Drop
it to install into the current project's `.claude/skills/` instead — do that if the
user prefers not to touch their home directory. Install only what the preflight
reported `MISSING`: re-installing an existing skill overwrites the user's copy,
which may be customized.

## The four `npx skills add` skills

```bash
# frontend-design — Anthropic's baseline / control entry
npx -y skills add anthropics/skills --skill frontend-design \
  --agent claude-code --global --yes

# design-taste-frontend
npx -y skills add Leonxlnx/taste-skill --skill design-taste-frontend \
  --agent claude-code --global --yes

# apple-design
npx -y skills add emilkowalski/skills --skill apple-design \
  --agent claude-code --global --yes

# superdesign
npx -y skills add superdesigndev/superdesign-skill \
  --agent claude-code --global --yes
```

`superdesign` is also distributed as a plugin, in which case it is invoked as
`superdesign:superdesign`. The preflight resolves whichever form is installed —
use the invoke-name it prints.

## impeccable

```bash
npx -y impeccable install
```

It detects the `.claude` folder and installs itself there. The upstream README
also documents `/plugin marketplace add pbakaus/impeccable` (user-typed) and a
manual copy of `dist/claude-code/.claude` as fallbacks. `impeccable` has an
optional `/impeccable init` step that records design context for the project;
the arena does not require it — the mockup agents get their context from the
briefs instead.

## ui-ux-pro-max

CLI route (runnable by you, installs into the current project):

```bash
npm install -g ui-ux-pro-max-cli && uipro init --ai claude
```

Plugin route (must be typed by the user, two lines):

```
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
/plugin install ui-ux-pro-max@ui-ux-pro-max-skill
```

If it arrives as a **plugin**, its invocable name is `<plugin>:<skill>` (e.g.
`ui-ux-pro-max:ui-ux-pro-max`), not the bare name. Re-run the preflight after any
install so the arena passes the *resolved* name to the agents.

## After installing

Newly installed skills are picked up when the skills list is next loaded — that
may not be mid-turn. Re-run the preflight. If the shell says a skill is on disk
but you still cannot invoke it with the Skill tool, tell the user to restart the
session (or run `/plugin` once) before starting the arena. Spawning twelve agents
that then fail to load their skill is the expensive failure mode.

## Substituting or extending the roster

Edit `roster.txt`; nothing else hardcodes the list. One rule when you do: **keep
the lineages distinct** — several skills forked from the same upstream measure one
taste engine repeatedly, which is the failure mode the arena exists to avoid.

Known-good substitutes, and why they aren't in the default six:

| Candidate | Source | Note |
|---|---|---|
| `high-end-visual-design` | Leonxlnx/taste-skill | Good, but shares its lineage with `design-taste-frontend`. |
| `gpt-taste` | Leonxlnx/taste-skill | Explicitly the GPT/Codex-tuned variant of `design-taste-frontend` — near-duplicate. |
| `minimalist-ui`, `industrial-brutalist-ui` | Leonxlnx/taste-skill | Same lineage, but style-committed enough to add real spread if you want an 8-skill field. |
| `brandkit` | Leonxlnx/taste-skill | Produces a 3×3 brand board, not a screen — wrong deliverable for a one-screen arena. Better used as a pre-step that fixes one brand direction for all agents. |

Reviewer-style skills (e.g. Vercel's Web Interface Guidelines) do not belong in
the field — they critique rather than design. They'd fit a judging stage, which
this skill doesn't have.
