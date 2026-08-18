#!/usr/bin/env bash
# design-arena preflight: resolve the design skills the arena needs.
#
# Reads the roster from ../roster.txt (single source of truth) unless skills are
# named on the command line. Prints one line per skill:
#   <skill>  OK  <invoke-name>  <path>
#   <skill>  MISSING
# and exits 1 if any are missing, 0 otherwise.
#
# <invoke-name> is what to pass to the Skill tool. For a skill that arrived as
# part of a plugin it is "<plugin>:<skill>", not the bare name — pass the printed
# invoke-name to the agents, not the skill name.
#
# Usage:
#   bash check_skills.sh                    # the roster
#   bash check_skills.sh apple-design       # only these
#
# This is a filesystem check. The authoritative list is the skills roster in the
# orchestrator's own context — if a skill is listed there, it is available even
# if this script cannot find it on disk (and vice versa).

set -u

HERE=$(cd -- "$(dirname -- "$0")" && pwd)
ROSTER="$HERE/../roster.txt"

if [ "$#" -gt 0 ]; then
  SKILLS="$*"
elif [ -f "$ROSTER" ]; then
  # Strip comments (whole-line and trailing notes) and blank lines.
  SKILLS=$(sed 's/#.*//' "$ROSTER" | tr -d '\r' | awk 'NF {print $1}')
else
  echo "error: no roster at $ROSTER and no skills given on the command line" >&2
  exit 2
fi

if [ -z "${SKILLS// /}" ]; then
  echo "error: roster is empty — $ROSTER lists no skills" >&2
  exit 2
fi

missing=0

for s in $SKILLS; do
  found=""
  invoke=""

  # Plain skill dirs: project scope first (it wins on name collisions), then user
  # scope, then any nested layout under the skills root (e.g. .../skills/synced/<name>).
  for root in "$PWD/.claude/skills" "$HOME/.claude/skills"; do
    [ -d "$root" ] || continue
    hit=$(find "$root" -maxdepth 3 -type f -path "*/$s/SKILL.md" 2>/dev/null | head -1)
    if [ -n "$hit" ]; then
      found=$(dirname "$hit")
      invoke="$s"
      break
    fi
  done

  # Plugin-provided skills: <plugin-root>/skills/<name>/SKILL.md -> "<plugin>:<name>"
  if [ -z "$found" ] && [ -d "$HOME/.claude/plugins" ]; then
    hit=$(find "$HOME/.claude/plugins" -maxdepth 8 -type f -path "*/skills/$s/SKILL.md" 2>/dev/null | head -1)
    if [ -n "$hit" ]; then
      found=$(dirname "$hit")
      plugin=$(basename "$(dirname "$(dirname "$found")")")
      invoke="$plugin:$s"
    fi
  fi

  if [ -n "$found" ]; then
    printf '%-24s OK       %-32s %s\n' "$s" "$invoke" "$found"
  else
    printf '%-24s MISSING\n' "$s"
    missing=$((missing + 1))
  fi
done

if [ "$missing" -gt 0 ]; then
  echo
  echo "$missing skill(s) missing — see references/installing-skills.md for where each one comes from."
  exit 1
fi
