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

# Canonical skill order so the gallery reads consistently and pairs line up.
SKILL_ORDER = [
    "gpt-taste",
    "ui-ux-pro-max",
    "high-end-visual-design",
    "impeccable",
    "design-taste-frontend",
    "brandkit",
]


def collect(track_dir: Path):
    """Return {skill_stem: html_path} for one track directory."""
    found = {}
    if track_dir.is_dir():
        for p in sorted(track_dir.glob("*.html")):
            found[p.stem] = p
    return found


def ordered_skills(informed, blind):
    """Known skills first (canonical order), then any extras alphabetically."""
    keys = set(informed) | set(blind)
    known = [s for s in SKILL_ORDER if s in keys]
    extra = sorted(k for k in keys if k not in SKILL_ORDER)
    return known + extra


def card(skill, track, mockup: Path, plan: Path, out_dir: Path):
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

    return f"""
      <article class="card">
        <header><span class="skill">{label}</span>
          <span class="badge {badge_cls}">{badge_txt}</span></header>
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
    informed = collect(out_dir / "informed")
    blind = collect(out_dir / "blind")
    plans = out_dir / "plans"
    skills = ordered_skills(informed, blind)

    total = len(informed) + len(blind)

    rows = []
    for skill in skills:
        inf = card(skill, "informed", informed.get(skill),
                   plans / f"informed-{skill}.md", out_dir)
        bli = card(skill, "blind", blind.get(skill),
                   plans / f"blind-{skill}.md", out_dir)
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
</style>
</head>
<body>
  <div class="top">
    <h1>Design Arena</h1>
    <p>{total} designs · 6 skills · each run once <b>informed</b> (saw the current
    design, improved it) and once <b>blind</b> (functional spec only, built from
    scratch). Click any preview to open it full-size; read its apply-plan below.
    Pick a winner and I'll apply it.</p>
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
    brief = out_dir / "competition-brief.html"
    brief.write_text(render(out_dir), encoding="utf-8")
    inf = len(collect(out_dir / "informed"))
    bli = len(collect(out_dir / "blind"))
    print(f"wrote {brief}  ({inf} informed + {bli} blind = {inf + bli} designs)")


if __name__ == "__main__":
    main()
