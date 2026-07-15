#!/usr/bin/env python3
"""Génère le site GitHub Pages (site/index.html) depuis data/cv.yaml.

Page unique, autonome (CSS/JS inline), bilingue FR/EN avec bascule, et
boutons de téléchargement des 4 PDF. Les PDF présents dans build/ sont
copiés dans site/ pour être servis par Pages.

Usage :
    python scripts/build.py       # d'abord générer les PDF
    python scripts/gen_site.py    # puis le site
"""
from __future__ import annotations

import html
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Le paquet 'pyyaml' est manquant. Installez-le : pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "cv.yaml"
BUILD = ROOT / "build"
SITE = ROOT / "site"

MONTHS = {
    "fr": ["janv.", "févr.", "mars", "avr.", "mai", "juin",
           "juil.", "août", "sept.", "oct.", "nov.", "déc."],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}
UI = {
    "fr": {"profile": "Profil", "skills": "Compétences", "experience": "Expériences",
           "education": "Formation", "certifications": "Certifications",
           "languages": "Langues", "interests": "Centres d'intérêt",
           "context": "Contexte", "achievements": "Réalisations",
           "stack": "Environnement technique", "present": "aujourd'hui",
           "updated": "Mis à jour le", "download": "Télécharger",
           "pdf_design": "PDF design", "pdf_classic": "PDF classique"},
    "en": {"profile": "Profile", "skills": "Skills", "experience": "Experience",
           "education": "Education", "certifications": "Certifications",
           "languages": "Languages", "interests": "Interests",
           "context": "Context", "achievements": "Achievements",
           "stack": "Technical environment", "present": "present",
           "updated": "Updated on", "download": "Download",
           "pdf_design": "Design PDF", "pdf_classic": "Classic PDF"},
}


def tr(v, lang):
    if isinstance(v, dict) and "fr" in v and "en" in v:
        return v.get(lang, v["fr"])
    return v


def esc(s):
    return html.escape(str(s))


def fmt_date(s, lang):
    if not s:
        return ""
    if s == "present":
        return UI[lang]["present"]
    parts = str(s).split("-")
    if len(parts) >= 2:
        m = int(parts[1])
        if 1 <= m <= 12:
            return f"{MONTHS[lang][m - 1]} {parts[0]}"
    return parts[0]


def daterange(start, end, lang):
    a, b = fmt_date(start, lang), fmt_date(end, lang)
    return a if not b else f"{a} – {b}"


def render(data, lang):
    ui = UI[lang]
    p = data["profile"]
    h = []

    # En-tête
    contacts = [esc(p["email"])]
    if p.get("phone"):
        contacts.append(esc(p["phone"]))
    if p.get("location"):
        contacts.append(esc(tr(p["location"], lang)))
    links = "".join(
        f'<a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["label"])} ↗</a>'
        for l in p.get("links", [])
    )
    h.append(f"""
    <header class="hero">
      <h1>{esc(p['name'])}</h1>
      <p class="title">{esc(tr(p['title'], lang))}</p>
    </header>
    <p class="contacts">{' · '.join(contacts)}</p>
    <p class="links">{links}</p>
    """)

    # Profil
    h.append(f'<section><h2>{ui["profile"]}</h2><p class="summary">{esc(tr(p["summary"], lang))}</p></section>')

    # Compétences
    if data.get("skills"):
        rows = ""
        for g in data["skills"]:
            chips = "".join(f'<span class="chip">{esc(tr(it, lang))}</span>' for it in g["items"])
            rows += f'<div class="skill-row"><div class="skill-cat">{esc(tr(g["category"], lang))}</div><div class="chips">{chips}</div></div>'
        h.append(f'<section><h2>{ui["skills"]}</h2>{rows}</section>')

    # Expériences
    if data.get("experiences"):
        items = ""
        for e in data["experiences"]:
            period = daterange(e["start"], e.get("end", ""), lang)
            loc = f'<div class="loc">{esc(tr(e["location"], lang))}</div>' if e.get("location") else ""
            ctx = f'<p class="ctx">{esc(tr(e["context"], lang))}</p>' if e.get("context") else ""
            miss = "".join(f"<li>{esc(tr(m, lang))}</li>" for m in e.get("missions", []))
            miss = f"<ul>{miss}</ul>" if miss else ""
            achs = e.get("achievements", [])
            ach_html = ""
            if achs:
                lis = "".join(f"<li>{esc(tr(a, lang))}</li>" for a in achs)
                ach_html = f'<p class="ach-label">{ui["achievements"]}</p><ul class="ach">{lis}</ul>'
            stack = ""
            if e.get("stack"):
                tags = "".join(f'<span class="tag">{esc(s)}</span>' for s in e["stack"])
                stack = f'<div class="stack"><span class="stack-label">{ui["stack"]} :</span> {tags}</div>'
            items += f"""
      <article class="exp">
        <div class="exp-head">
          <div class="exp-role">{esc(tr(e['role'], lang))} <span class="at">— {esc(e['company'])}</span></div>
          <div class="exp-date">{esc(period)}</div>
        </div>
        {loc}{ctx}{miss}{ach_html}{stack}
      </article>"""
        h.append(f'<section><h2>{ui["experience"]}</h2>{items}</section>')

    # Formation
    if data.get("education"):
        items = ""
        for ed in data["education"]:
            period = daterange(ed["start"], ed.get("end", ""), lang)
            field = tr(ed.get("field", ""), lang)
            field = f" — {esc(field)}" if field else ""
            loc = f' · {esc(tr(ed["location"], lang))}' if ed.get("location") else ""
            items += f"""
      <article class="edu">
        <div class="exp-head">
          <div><strong>{esc(tr(ed['degree'], lang))}</strong>{field}</div>
          <div class="exp-date">{esc(period)}</div>
        </div>
        <div class="loc">{esc(ed['school'])}{loc}</div>
      </article>"""
        h.append(f'<section><h2>{ui["education"]}</h2>{items}</section>')

    # Certifications + Langues côte à côte
    cols = ""
    if data.get("certifications"):
        lis = "".join(
            f"<li><strong>{esc(c['name'])}</strong> — {esc(c.get('issuer',''))}"
            + (f" ({esc(c['year'])})" if c.get("year") else "") + "</li>"
            for c in data["certifications"]
        )
        cols += f'<section class="half"><h2>{ui["certifications"]}</h2><ul class="plain">{lis}</ul></section>'
    if data.get("languages"):
        lis = "".join(
            f"<li><strong>{esc(tr(lg['name'], lang))}</strong> — {esc(tr(lg['level'], lang))}</li>"
            for lg in data["languages"]
        )
        cols += f'<section class="half"><h2>{ui["languages"]}</h2><ul class="plain">{lis}</ul></section>'
    if cols:
        h.append(f'<div class="two-col">{cols}</div>')

    # Centres d'intérêt
    if data.get("interests"):
        chips = "".join(f'<span class="chip">{esc(tr(it, lang))}</span>' for it in data["interests"])
        h.append(f'<section><h2>{ui["interests"]}</h2><div class="chips">{chips}</div></section>')

    h.append(f'<p class="updated">{ui["updated"]} {esc(data["meta"]["updated"])}</p>')
    return "\n".join(h)


PAGE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — {title}</title>
<meta name="description" content="{title} — {name}">
<style>
  :root {{ --accent:#1f6feb; --ink:#1a1a1a; --muted:#5b6570; --hair:#e3e7ec; --bg:#f6f8fa; --card:#fff; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --ink:#e6edf3; --muted:#9aa4ae; --hair:#30363d; --bg:#0d1117; --card:#161b22; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
    font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }}
  .wrap {{ max-width:820px; margin:0 auto; padding:24px 20px 64px; }}
  .toolbar {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center;
    position:sticky; top:0; background:var(--bg); padding:12px 0; z-index:5; }}
  .toolbar .spacer {{ flex:1; }}
  .btn {{ border:1px solid var(--hair); background:var(--card); color:var(--ink);
    padding:7px 12px; border-radius:8px; font-size:13px; cursor:pointer;
    text-decoration:none; display:inline-flex; align-items:center; gap:6px; }}
  .btn:hover {{ border-color:var(--accent); color:var(--accent); }}
  .btn.primary {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
  .btn.primary:hover {{ filter:brightness(1.06); color:#fff; }}
  .lang-switch .btn.active {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
  .hero {{ background:var(--accent); color:#fff; border-radius:12px; padding:22px 24px; margin-top:8px; }}
  .hero h1 {{ margin:0; font-size:30px; }}
  .hero .title {{ margin:4px 0 0; opacity:.92; font-size:16px; }}
  .contacts {{ color:var(--muted); margin:14px 0 2px; font-size:14px; }}
  .links a {{ color:var(--accent); text-decoration:none; margin-right:12px; font-size:14px; }}
  .links a:hover {{ text-decoration:underline; }}
  section {{ margin-top:26px; }}
  h2 {{ font-size:14px; letter-spacing:.06em; text-transform:uppercase; color:var(--accent);
    border-bottom:1px solid var(--hair); padding-bottom:6px; margin:0 0 12px; }}
  .summary {{ margin:0; }}
  .skill-row {{ display:grid; grid-template-columns:190px 1fr; gap:10px; margin-bottom:10px; align-items:start; }}
  .skill-cat {{ font-weight:700; }}
  .chips {{ display:flex; flex-wrap:wrap; gap:6px; }}
  .chip {{ background:color-mix(in srgb, var(--accent) 12%, transparent); color:var(--accent);
    padding:3px 9px; border-radius:6px; font-size:13px; }}
  .exp, .edu {{ margin-bottom:18px; }}
  .exp-head {{ display:flex; justify-content:space-between; gap:12px; align-items:baseline; flex-wrap:wrap; }}
  .exp-role {{ font-weight:700; font-size:15.5px; }}
  .exp-role .at {{ color:var(--accent); font-weight:700; }}
  .exp-date {{ color:var(--muted); font-size:13px; white-space:nowrap; }}
  .loc {{ color:var(--muted); font-size:13px; font-style:italic; }}
  .ctx {{ color:var(--muted); font-style:italic; margin:6px 0; }}
  ul {{ margin:8px 0; padding-left:20px; }}
  li {{ margin:3px 0; }}
  .ach-label {{ font-weight:700; color:var(--accent); margin:8px 0 2px; font-size:13.5px; }}
  ul.ach {{ margin-top:2px; }}
  .stack {{ margin-top:8px; font-size:13px; color:var(--muted); }}
  .stack-label {{ font-weight:700; }}
  .tag {{ display:inline-block; border:1px solid var(--hair); border-radius:5px;
    padding:1px 7px; margin:2px 3px 2px 0; font-size:12.5px; }}
  .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; }}
  ul.plain {{ list-style:none; padding:0; }}
  ul.plain li {{ margin:5px 0; }}
  .updated {{ color:var(--muted); font-size:12.5px; font-style:italic; margin-top:28px; }}
  .cv[data-active="false"] {{ display:none; }}
  @media (max-width:640px) {{
    .skill-row {{ grid-template-columns:1fr; gap:4px; }}
    .two-col {{ grid-template-columns:1fr; gap:0; }}
  }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="toolbar">
      <div class="lang-switch">
        <button class="btn active" data-lang="fr" onclick="setLang('fr')">FR</button>
        <button class="btn" data-lang="en" onclick="setLang('en')">EN</button>
      </div>
      <div class="spacer"></div>
      <a class="btn primary" id="dl-design" href="cv-design-fr.pdf" download>⬇ {design_label_fr}</a>
      <a class="btn" id="dl-classic" href="cv-classic-fr.pdf" download>⬇ {classic_label_fr}</a>
    </div>

    <div class="cv" data-lang="fr" data-active="true">{body_fr}</div>
    <div class="cv" data-lang="en" data-active="false">{body_en}</div>
  </div>

<script>
  var LABELS = {{
    fr: {{ design: "{design_label_fr}", classic: "{classic_label_fr}" }},
    en: {{ design: "{design_label_en}", classic: "{classic_label_en}" }}
  }};
  function setLang(l) {{
    document.querySelectorAll('.cv').forEach(function(c) {{
      c.setAttribute('data-active', c.getAttribute('data-lang') === l ? 'true' : 'false');
    }});
    document.querySelectorAll('.lang-switch .btn').forEach(function(b) {{
      b.classList.toggle('active', b.getAttribute('data-lang') === l);
    }});
    document.getElementById('dl-design').setAttribute('href', 'cv-design-' + l + '.pdf');
    document.getElementById('dl-design').textContent = '⬇ ' + LABELS[l].design;
    document.getElementById('dl-classic').setAttribute('href', 'cv-classic-' + l + '.pdf');
    document.getElementById('dl-classic').textContent = '⬇ ' + LABELS[l].classic;
    document.documentElement.setAttribute('lang', l);
  }}
</script>
</body>
</html>
"""


def main() -> int:
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    SITE.mkdir(exist_ok=True)

    page = PAGE.format(
        lang="fr",
        name=esc(data["profile"]["name"]),
        title=esc(tr(data["profile"]["title"], "fr")),
        body_fr=render(data, "fr"),
        body_en=render(data, "en"),
        design_label_fr=UI["fr"]["pdf_design"], classic_label_fr=UI["fr"]["pdf_classic"],
        design_label_en=UI["en"]["pdf_design"], classic_label_en=UI["en"]["pdf_classic"],
    )
    (SITE / "index.html").write_text(page, encoding="utf-8")

    # Copie des PDF disponibles
    copied = 0
    for pdf in BUILD.glob("cv-*.pdf"):
        shutil.copy2(pdf, SITE / pdf.name)
        copied += 1
    if copied == 0:
        print("  ! Aucun PDF dans build/ — lancez d'abord 'python scripts/build.py'.", file=sys.stderr)

    print(f"Site généré dans site/ (index.html + {copied} PDF).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
