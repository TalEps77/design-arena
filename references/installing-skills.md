# Installing the six design skills

Read this only when Step 0 preflight reports a skill as `MISSING`. It lists where
each of the six skills comes from and the exact command that installs it.

Verified sources (all six are third-party, MIT/open-source skills — none ship with
Claude Code, so a fresh clone of design-arena will almost always be missing all of
them):

| Skill | Upstream | Install |
|---|---|---|
| `gpt-taste` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `npx skills add` |
| `design-taste-frontend` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `npx skills add` |
| `high-end-visual-design` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `npx skills add` |
| `brandkit` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `npx skills add` |
| `impeccable` | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | `npx impeccable install` |
| `ui-ux-pro-max` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | `uipro init` or plugin marketplace |

## Who runs what

You (the orchestrator) can run every `npx` / `npm` command below yourself, with the
user's permission — they are ordinary shell commands. You **cannot** run
`/plugin marketplace add …`; slash commands are typed by the user into their own
session. So: prefer the CLI installers, and only fall back to asking the user to
type a slash command when the CLI route fails.

Always ask before installing. These commands download and write third-party code
into the user's `~/.claude/` (or the project's `.claude/`) — that is the user's
call, not yours. Name the repos you're about to pull from.

## 1 — the four taste-skill skills (one command)

`gpt-taste`, `design-taste-frontend`, `high-end-visual-design` and `brandkit` all
live in the same repo, installed with the Agent Skills CLI:

```bash
npx -y skills add Leonxlnx/taste-skill \
  --skill gpt-taste design-taste-frontend high-end-visual-design brandkit \
  --agent claude-code --global --yes
```

- `--global` writes to `~/.claude/skills/<name>/` (available in every project).
  Drop it to install into this project's `.claude/skills/` instead — do that if
  the user prefers not to touch their home directory.
- Install only the ones reported `MISSING`; re-installing an existing skill
  overwrites the user's copy, which may be customized.

## 2 — impeccable

```bash
npx -y impeccable install
```

It detects the `.claude` folder and installs itself there. The upstream README
also documents `/plugin marketplace add pbakaus/impeccable` (user-typed) and a
manual copy of `dist/claude-code/.claude` as fallbacks. `impeccable` has an
optional `/impeccable init` step that records design context for the project;
the arena does not require it — the mockup agents get their context from the
briefs instead.

## 3 — ui-ux-pro-max

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
may not be mid-turn. Re-run the preflight check; if the shell says a skill is on
disk but you still cannot invoke it with the Skill tool, tell the user to restart
the session (or run `/plugin` once) before starting the arena. Spawning twelve
agents that then fail to load their skill is the expensive failure mode.

## Substituting a skill

The field is six skills because six taste engines produce a readable spread, not
because these exact six are sacred. `Leonxlnx/taste-skill` also ships
`minimalist-ui`, `industrial-brutalist-ui`, `stitch-design-taste` and
`redesign-existing-projects`; other design skills work equally well. If the user
declines one of the six, offer a substitute rather than dropping to five — and
whatever the final roster is, name it in the gallery so the comparison is honest.
