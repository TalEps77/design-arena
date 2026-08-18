#!/usr/bin/env python3
"""Assemble the design-arena competition brief.

Scans <output_dir>/informed and <output_dir>/blind for *.html mockups, embeds
each as a scaled live <iframe> preview in a responsive gallery, tags each card
with its skill + blind/informed badge, and links to the full mockup and the
matching apply-plan under plans/. Writes <output_dir>/competition-brief.html.

Usage:
    python3 build_brief.py <output_dir>        # default: design-arena-output
"""

import html
import sys
from pathlib import Path

ROSTER = Path(__file__).resolve().parent.parent / "roster.txt"


def load_roster(path: Path = ROSTER):
    """Read roster.txt -> ([skill, ...], {skill: note}).

    One skill per line, in gallery order. Blank lines and lines starting with #
    are ignored; text after a "#" on a skill line is a note shown on that skill's
    cards. Returns an empty roster if the file is absent — the gallery then falls
    back to whatever the agents actually produced.
    """
    order, notes = [], {}
    if not path.is_file():
        return order, notes
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, _, note = line.partition("#")
        name = name.strip()
        if not name:
            continue
        order.append(name)
        if note.strip():
            notes[name] = note.strip()
    return order, notes


def collect(track_dir: Path):
    """Return {skill_stem: html_path} for one track directory."""
    found = {}
    if track_dir.is_dir():
        for p in sorted(track_dir.glob("*.html")):
            found[p.stem] = p
    return found


def ordered_skills(informed, blind, roster):
    """Roster skills first (roster order), then anything unexpected, alphabetically.

    A roster entry with no mockup on either track is dropped rather than rendered
    as a pair of empty cards — it was never in this run.
    """
    keys = set(informed) | set(blind)
    known = [s for s in roster if s in keys]
    extra = sorted(k for k in keys if k not in roster)
    return known + extra


def card(skill, track, mockup: Path, plan: Path, out_dir: Path, note=""):
    """Build one gallery card (or an 'absent' placeholder)."""
    label = html.escape(skill)
    badge_cls = "informed" if track == "informed" else "blind"
    badge_txt = track.upper()

    if mockup is None:
        return f"""
      <article class="card missing">
        <header><span class="skill">{label}</span>
          <span class="badge {badge_cls}">{badge_txt}</span></header>
        <div class="preview empty">no mockup produced</div>
      </article>"""

    rel = mockup.relative_to(out_dir).as_posix()
    plan_link = ""
    if plan and plan.exists():
        prel = plan.relative_to(out_dir).as_posix()
        plan_link = f'<a href="{prel}" target="_blank">apply-plan ↗</a>'
    else:
        plan_link = '<span class="noplan">no plan</span>'

    note_html = f'<p class="note">{html.escape(note)}</p>' if note else ""

    return f"""
      <article class="card">
        <header><span class="skill">{label}</span>
          <span class="badge {badge_cls}">{badge_txt}</span></header>
        {note_html}
        <div class="preview">
          <iframe src="{rel}" loading="lazy" scrolling="no"
                  sandbox="allow-scripts allow-same-origin"></iframe>
        </div>
        <footer>
          <a href="{rel}" target="_blank">open full ↗</a>
          {plan_link}
        </footer>
      </article>"""


def render(out_dir: Path) -> str:
    roster, notes = load_roster()
    informed = collect(out_dir / "informed")
    blind = collect(out_dir / "blind")
    plans = out_dir / "plans"
    skills = ordered_skills(informed, blind, roster)

    total = len(informed) + len(blind)
    n_skills = len(skills)

    rows = []
    for skill in skills:
        note = notes.get(skill, "")
        inf = card(skill, "informed", informed.get(skill),
                   plans / f"informed-{skill}.md", out_dir, note)
        bli = card(skill, "blind", blind.get(skill),
                   plans / f"blind-{skill}.md", out_dir, note)
        rows.append(f"""
    <section class="pair">
      <h2>{html.escape(skill)}</h2>
      <div class="row">{inf}{bli}</div>
    </section>""")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Design Arena — competition brief</title>
<style>
  :root {{
    --bg:#0b0c0f; --panel:#14161c; --line:#262a33; --ink:#e8eaf0;
    --muted:#8b90a0; --informed:#4ade80; --blind:#60a5fa;
    --scale:0.34;                 /* iframe 1440 -> ~490px card */
    --fw:1440px; --fh:1000px;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
    font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }}
  .top {{ padding:40px 40px 8px; }}
  .top h1 {{ margin:0 0 6px; font-size:30px; letter-spacing:-0.02em; }}
  .top p {{ margin:0; color:var(--muted); max-width:70ch; }}
  .legend {{ display:flex; gap:20px; margin-top:16px; font-size:13px; color:var(--muted); }}
  .legend .dot {{ display:inline-block; width:10px; height:10px; border-radius:50%;
    margin-right:6px; vertical-align:middle; }}
  .dot.informed {{ background:var(--informed); }}
  .dot.blind {{ background:var(--blind); }}
  .pair {{ padding:8px 40px 24px; }}
  .pair h2 {{ font-size:15px; text-transform:lowercase; letter-spacing:0.02em;
    color:var(--muted); font-weight:600; margin:24px 0 12px;
    border-top:1px solid var(--line); padding-top:20px; }}
  .row {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:20px; }}
  @media (max-width:1040px) {{ .row {{ grid-template-columns:1fr; }} }}
  .card {{ background:var(--panel); border:1px solid var(--line);
    border-radius:14px; overflow:hidden; }}
  .card header {{ display:flex; align-items:center; justify-content:space-between;
    padding:12px 16px; }}
  .card .skill {{ font-weight:600; }}
  .badge {{ font-size:11px; font-weight:700; letter-spacing:0.06em;
    padding:3px 8px; border-radius:999px; }}
  .badge.informed {{ color:#052e12; background:var(--informed); }}
  .badge.blind {{ color:#04204a; background:var(--blind); }}
  .preview {{ position:relative; width:100%;
    height:calc(var(--fh) * var(--scale)); overflow:hidden;
    border-top:1px solid var(--line); border-bottom:1px solid var(--line);
    background:#fff; }}
  .preview iframe {{ position:absolute; top:0; left:0;
    width:var(--fw); height:var(--fh); border:0;
    transform:scale(var(--scale)); transform-origin:top left; }}
  .preview.empty {{ display:flex; align-items:center; justify-content:center;
    background:var(--panel); color:var(--muted); font-style:italic;
    height:120px; }}
  .card.missing {{ opacity:0.6; }}
  .card footer {{ display:flex; gap:16px; padding:12px 16px; font-size:13px; }}
  .card footer a {{ color:var(--ink); text-decoration:none;
    border-bottom:1px solid var(--line); }}
  .card footer a:hover {{ border-color:var(--ink); }}
  .noplan {{ color:var(--muted); }}
  .note {{ margin:0; padding:0 16px 12px; font-size:12.5px; line-height:1.45;
    color:var(--muted); }}
</style>
</head>
<body>
  <div class="top">
    <h1>Design Arena</h1>
    <p>{total} designs · {n_skills} skills · each run once <b>informed</b> (saw the
    current design, improved it) and once <b>blind</b> (functional spec only, built
    from scratch). Previews are scaled and cropped to the top of each page — open
    one full-size before judging it, and read its apply-plan below. Pick a winner
    and I'll apply it.</p>
    <div class="legend">
      <span><span class="dot informed"></span>informed — improved the real design</span>
      <span><span class="dot blind"></span>blind — designed from scratch</span>
    </div>
  </div>
  {''.join(rows)}
</body>
</html>"""


def main():
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "design-arena-output")
    if not out_dir.is_dir():
        sys.exit(f"error: {out_dir} is not a directory")

    informed = collect(out_dir / "informed")
    blind = collect(out_dir / "blind")
    if not informed and not blind:
        sys.exit(
            f"error: no mockups found under {out_dir}/informed or {out_dir}/blind — "
            "the agents wrote nothing. Nothing to build a gallery from."
        )

    brief = out_dir / "competition-brief.html"
    brief.write_text(render(out_dir), encoding="utf-8")
    print(f"wrote {brief}  "
          f"({len(informed)} informed + {len(blind)} blind = "
          f"{len(informed) + len(blind)} designs)")

    # Report gaps explicitly: a silently short field changes the competition.
    roster, _ = load_roster()
    if not roster:
        print(f"  note: no roster at {ROSTER} — gallery ordered by what was found")
    for track, found in (("informed", informed), ("blind", blind)):
        gaps = [s for s in roster if s not in found]
        if gaps:
            print(f"  missing {track}: {', '.join(gaps)}")
    missing_plans = [
        f"{t}-{s}"
        for t, found in (("informed", informed), ("blind", blind))
        for s in found
        if not (out_dir / "plans" / f"{t}-{s}.md").exists()
    ]
    if missing_plans:
        print(f"  missing plans: {', '.join(sorted(missing_plans))}")
    print("  if previews render blank, the browser is blocking file:// frames — "
          f"serve it: python3 -m http.server 8123 --directory {out_dir}")


if __name__ == "__main__":
    main()
