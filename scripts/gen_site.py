#!/usr/bin/env python3
"""Génère le site GitHub Pages (site/index.html) depuis data/cv.yaml.

Page unique, autonome (CSS/JS inline), bilingue FR/EN avec bascule, et
boutons de téléchargement des PDF. Les PDF présents dans build/ sont
copiés dans site/ pour être servis par Pages.

Design : « International Typographic Style » (école suisse).
Grille modulaire stricte, Inter + monospace pour le méta-technique,
noir & blanc franc, un seul accent (vermillon) employé avec parcimonie,
angles vifs, hairlines et filets épais. Sobre, professionnel, précis.

Usage :
    python scripts/build.py       # d'abord générer les PDF
    python scripts/gen_site.py    # puis le site
"""
from __future__ import annotations

import html
import json
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
           "context": "Contexte", "achievements": "Réalisation",
           "stack": "Environnement technique", "present": "aujourd'hui",
           "updated": "Mis à jour le", "download": "Télécharger",
           "pdf_design": "PDF design", "pdf_classic": "PDF classique",
           "kicker": "Curriculum Vitæ", "loc_label": "Localisation",
           "contact_label": "Contact", "links_label": "Liens",
           "theme": "Thème", "colophon": "Composé à la grille · Inter"},
    "en": {"profile": "Profile", "skills": "Skills", "experience": "Experience",
           "education": "Education", "certifications": "Certifications",
           "languages": "Languages", "interests": "Interests",
           "context": "Context", "achievements": "Achievement",
           "stack": "Technical environment", "present": "present",
           "updated": "Updated on", "download": "Download",
           "pdf_design": "Design PDF", "pdf_classic": "Classic PDF",
           "kicker": "Curriculum Vitæ", "loc_label": "Location",
           "contact_label": "Contact", "links_label": "Links",
           "theme": "Theme", "colophon": "Set to a grid · Inter"},
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
    return a if not b else f"{a} — {b}"


class Counter:
    """Numérotation séquentielle des sections (01, 02, …)."""

    def __init__(self):
        self.n = 0

    def next(self):
        self.n += 1
        return f"{self.n:02d}"


def section(num, title, body_html):
    return f"""
    <section class="section reveal">
      <div class="section-head">
        <span class="section-num">{num}</span>
        <h2 class="section-title">{esc(title)}</h2>
      </div>
      <div class="section-body">{body_html}</div>
    </section>"""


def render(data, lang):
    ui = UI[lang]
    p = data["profile"]
    c = Counter()
    h = []

    # ------------------------------------------------------------- Masthead
    ident = []
    ident.append(
        f'<div class="ident-row"><dt>{esc(ui["loc_label"])}</dt>'
        f'<dd>{esc(tr(p["location"], lang))}</dd></div>'
    )
    contact_bits = [f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>']
    if p.get("phone"):
        contact_bits.append(esc(p["phone"]))
    ident.append(
        f'<div class="ident-row"><dt>{esc(ui["contact_label"])}</dt>'
        f'<dd>{" · ".join(contact_bits)}</dd></div>'
    )
    if p.get("links"):
        link_bits = "".join(
            f'<a href="{esc(l["url"])}" target="_blank" rel="noopener">'
            f'{esc(l["label"])} <span class="arw">↗</span></a>'
            for l in p["links"]
        )
        ident.append(
            f'<div class="ident-row"><dt>{esc(ui["links_label"])}</dt>'
            f'<dd class="ident-links">{link_bits}</dd></div>'
        )

    h.append(f"""
    <header class="masthead" id="top">
      <p class="kicker">{esc(ui["kicker"])} <span class="kicker-yr">— {esc(data["meta"]["updated"][:4])}</span></p>
      <h1 class="name">{esc(p["name"])}</h1>
      <p class="role">{esc(tr(p["title"], lang))}</p>
      <dl class="ident">{"".join(ident)}</dl>
    </header>""")

    # -------------------------------------------------------------- Profil
    h.append(section(
        c.next(), ui["profile"],
        f'<p class="lede">{esc(tr(p["summary"], lang))}</p>'
    ))

    # --------------------------------------------------------- Compétences
    if data.get("skills"):
        groups = ""
        for g in data["skills"]:
            tags = "".join(
                f'<li class="tag">{esc(tr(it, lang))}</li>' for it in g["items"]
            )
            groups += (
                '<div class="skill-group">'
                f'<h3 class="subhead">{esc(tr(g["category"], lang))}</h3>'
                f'<ul class="tags">{tags}</ul></div>'
            )
        h.append(section(c.next(), ui["skills"], groups))

    # ---------------------------------------------------------- Expériences
    if data.get("experiences"):
        entries = ""
        for e in data["experiences"]:
            period = daterange(e["start"], e.get("end", ""), lang)
            ongoing = " is-now" if e.get("end") == "present" else ""
            place = (
                f'<span class="place">{esc(tr(e["location"], lang))}</span>'
                if e.get("location") else ""
            )
            ctx = (
                f'<p class="entry-ctx">{esc(tr(e["context"], lang))}</p>'
                if e.get("context") else ""
            )
            miss = "".join(
                f'<li>{esc(tr(m, lang))}</li>' for m in e.get("missions", [])
            )
            miss = f'<ul class="missions">{miss}</ul>' if miss else ""
            ach_html = ""
            for a in e.get("achievements", []):
                ach_html += (
                    '<div class="ach">'
                    f'<span class="ach-label">{esc(ui["achievements"])}</span>'
                    f'<span class="ach-text">{esc(tr(a, lang))}</span></div>'
                )
            stack = ""
            if e.get("stack"):
                st = "".join(f'<li>{esc(s)}</li>' for s in e["stack"])
                stack = (
                    '<div class="stack"><span class="stack-label">Stack</span>'
                    f'<ul class="stack-list">{st}</ul></div>'
                )
            entries += f"""
        <article class="entry{ongoing}">
          <div class="entry-meta">
            <span class="period">{esc(period)}</span>
            {place}
          </div>
          <div class="entry-main">
            <h3 class="entry-role">{esc(tr(e["role"], lang))}<span class="co">{esc(e["company"])}</span></h3>
            {ctx}{miss}{ach_html}{stack}
          </div>
        </article>"""
        h.append(section(c.next(), ui["experience"], entries))

    # ------------------------------------------------------------ Formation
    if data.get("education"):
        entries = ""
        for ed in data["education"]:
            period = daterange(ed["start"], ed.get("end", ""), lang)
            field = tr(ed.get("field", ""), lang)
            field = f'<span class="edu-field"> — {esc(field)}</span>' if field else ""
            loc = f' · {esc(tr(ed["location"], lang))}' if ed.get("location") else ""
            entries += f"""
        <article class="entry">
          <div class="entry-meta"><span class="period">{esc(period)}</span></div>
          <div class="entry-main">
            <h3 class="entry-role">{esc(tr(ed["degree"], lang))}{field}</h3>
            <p class="edu-school">{esc(ed["school"])}{loc}</p>
          </div>
        </article>"""
        h.append(section(c.next(), ui["education"], entries))

    # --------------------------------------------- Certifications + Langues
    if data.get("certifications"):
        rows = "".join(
            '<div class="ident-row">'
            f'<dt>{esc(c_["name"])}</dt><dd>{esc(c_.get("issuer", ""))}'
            + (f' · {esc(c_["year"])}' if c_.get("year") else "")
            + "</dd></div>"
            for c_ in data["certifications"]
        )
        h.append(section(c.next(), ui["certifications"], f'<dl class="deflist">{rows}</dl>'))

    if data.get("languages"):
        rows = "".join(
            '<div class="ident-row">'
            f'<dt>{esc(tr(lg["name"], lang))}</dt>'
            f'<dd>{esc(tr(lg["level"], lang))}</dd></div>'
            for lg in data["languages"]
        )
        h.append(section(c.next(), ui["languages"], f'<dl class="deflist">{rows}</dl>'))

    # ------------------------------------------------------ Centres d'intérêt
    if data.get("interests"):
        tags = "".join(
            f'<li class="tag ghost">{esc(tr(it, lang))}</li>' for it in data["interests"]
        )
        h.append(section(c.next(), ui["interests"], f'<ul class="tags">{tags}</ul>'))

    return "\n".join(h)


# =============================================================================
#  Feuille de style — International Typographic Style
# =============================================================================
STYLE = """
/* ---- Reset & tokens ------------------------------------------------------ */
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
body, h1, h2, h3, p, dl, dd, ul, figure { margin: 0; }
ul { list-style: none; padding: 0; }

:root {
  --paper:   #ffffff;
  --panel:   #fafafa;
  --ink:     #101010;
  --ink-2:   #333333;
  --muted:   #6a6a6a;
  --faint:   #9a9a9a;
  --rule:    #101010;   /* filets structurants forts */
  --hair:    #e4e4e4;   /* séparateurs légers */
  --accent:  #e3120b;   /* vermillon — signal, employé avec parcimonie */
  --sel:     #ffe1df;
  --sans: "Inter", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  --gap: clamp(24px, 4vw, 56px);
  --rail: minmax(150px, 210px);
}
:root[data-theme="dark"] {
  --paper:  #0d0d0d;
  --panel:  #151515;
  --ink:    #ededea;
  --ink-2:  #c9c9c4;
  --muted:  #9a9a94;
  --faint:  #6f6f6a;
  --rule:   #ededea;
  --hair:   #262626;
  --accent: #ff4b3e;
  --sel:    #40100c;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper:  #0d0d0d;
    --panel:  #151515;
    --ink:    #ededea;
    --ink-2:  #c9c9c4;
    --muted:  #9a9a94;
    --faint:  #6f6f6a;
    --rule:   #ededea;
    --hair:   #262626;
    --accent: #ff4b3e;
    --sel:    #40100c;
  }
}

::selection { background: var(--sel); color: var(--ink); }

body {
  background: var(--paper);
  color: var(--ink);
  font-family: var(--sans);
  font-size: 16px;
  line-height: 1.5;
  font-feature-settings: "kern" 1, "liga" 1, "cv05" 1, "ss01" 1, "tnum" 1;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

a { color: inherit; }

/* ---- Barre supérieure ---------------------------------------------------- */
.bar {
  position: sticky; top: 0; z-index: 20;
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px;
  padding: 12px clamp(18px, 5vw, 64px);
  background: color-mix(in srgb, var(--paper) 86%, transparent);
  backdrop-filter: saturate(140%) blur(10px);
  -webkit-backdrop-filter: saturate(140%) blur(10px);
  border-bottom: 1px solid var(--hair);
}
.bar-ident {
  font-family: var(--mono);
  font-size: 11px; letter-spacing: .16em; text-transform: uppercase;
  text-decoration: none; color: var(--ink); white-space: nowrap;
}
.bar-ident b { color: var(--accent); font-weight: 600; }
.bar-actions { display: flex; align-items: center; gap: clamp(10px, 2vw, 22px); flex-wrap: wrap; justify-content: flex-end; }

.seg { display: inline-flex; border: 1px solid var(--rule); }
.seg button {
  font-family: var(--mono); font-size: 11px; letter-spacing: .12em;
  background: transparent; color: var(--ink); border: 0; cursor: pointer;
  padding: 6px 11px; line-height: 1; transition: background .15s, color .15s;
}
.seg button + button { border-left: 1px solid var(--rule); }
.seg button.on { background: var(--ink); color: var(--paper); }
.seg button:not(.on):hover { background: var(--panel); }

.icon-btn {
  font-family: var(--mono); font-size: 12px; letter-spacing: .1em;
  background: transparent; border: 1px solid var(--rule); color: var(--ink);
  cursor: pointer; padding: 6px 10px; line-height: 1;
  display: inline-flex; align-items: center; gap: 7px; transition: background .15s;
}
.icon-btn:hover { background: var(--panel); }

.bar-dl { display: inline-flex; gap: 16px; }
.bar-dl a {
  font-family: var(--mono); font-size: 11px; letter-spacing: .06em;
  text-decoration: none; color: var(--muted); white-space: nowrap;
  border-bottom: 1px solid transparent; padding-bottom: 1px; transition: color .15s, border-color .15s;
}
.bar-dl a:hover { color: var(--accent); border-color: var(--accent); }
.bar-dl a::after { content: " ↓"; }
@media (max-width: 720px) { .bar-dl { display: none; } }

/* ---- Conteneur ----------------------------------------------------------- */
.wrap {
  max-width: 1160px;
  margin: 0 auto;
  padding: clamp(36px, 7vw, 96px) clamp(18px, 5vw, 64px) 40px;
}

/* ---- Masthead ------------------------------------------------------------ */
.masthead { padding-bottom: clamp(30px, 5vw, 56px); }
.kicker {
  font-family: var(--mono); font-size: 12px; letter-spacing: .22em;
  text-transform: uppercase; color: var(--muted);
}
.kicker-yr { color: var(--faint); }
.name {
  font-size: clamp(44px, 10vw, 104px);
  line-height: .94;
  letter-spacing: -0.03em;
  font-weight: 800;
  margin: clamp(14px, 3vw, 26px) 0 0;
  text-transform: uppercase;
}
.role {
  font-size: clamp(17px, 2.4vw, 23px);
  color: var(--ink-2); font-weight: 500;
  letter-spacing: -0.01em;
  margin-top: clamp(12px, 2vw, 18px);
  max-width: 40ch;
}

.ident {
  margin-top: clamp(26px, 4vw, 40px);
  display: grid; gap: 0;
  border-top: 1px solid var(--hair);
}
.ident-row {
  display: grid;
  grid-template-columns: var(--rail) 1fr;
  gap: var(--gap);
  padding: 11px 0;
  border-bottom: 1px solid var(--hair);
  align-items: baseline;
}
.ident-row dt {
  font-family: var(--mono); font-size: 11px; letter-spacing: .16em;
  text-transform: uppercase; color: var(--faint);
}
.ident-row dd { font-size: 15px; color: var(--ink); }
.ident-links { display: flex; flex-wrap: wrap; gap: 4px 22px; }
.ident-row dd a { text-decoration: none; border-bottom: 1px solid var(--hair); padding-bottom: 1px; transition: border-color .15s, color .15s; }
.ident-row dd a:hover { color: var(--accent); border-color: var(--accent); }
.arw { color: var(--accent); font-size: .85em; }

/* ---- Sections (module label + corps) ------------------------------------ */
.section {
  display: grid;
  grid-template-columns: var(--rail) 1fr;
  gap: var(--gap);
  padding: clamp(30px, 4.5vw, 52px) 0;
  border-top: 2px solid var(--rule);
}
.section-head { position: relative; }
.section-num {
  display: block;
  font-family: var(--mono); font-size: 12px; letter-spacing: .12em;
  color: var(--accent); margin-bottom: 10px;
}
.section-title {
  font-size: 13px; font-weight: 600;
  letter-spacing: .18em; text-transform: uppercase;
  color: var(--ink);
}
@media (min-width: 861px) {
  .section-head { position: sticky; top: 76px; align-self: start; }
}

/* ---- Profil -------------------------------------------------------------- */
.lede {
  font-size: clamp(19px, 2.5vw, 24px);
  line-height: 1.5; letter-spacing: -0.01em;
  color: var(--ink); font-weight: 400;
  max-width: 46ch; text-wrap: balance;
}

/* ---- Compétences --------------------------------------------------------- */
.skill-group { padding: 16px 0; border-bottom: 1px solid var(--hair); }
.skill-group:first-child { padding-top: 0; }
.skill-group:last-child { border-bottom: 0; padding-bottom: 0; }
.subhead {
  font-family: var(--mono); font-size: 11px; letter-spacing: .12em;
  text-transform: uppercase; color: var(--muted); font-weight: 500;
  margin-bottom: 12px;
}
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag {
  font-size: 13px; line-height: 1;
  padding: 7px 11px;
  border: 1px solid var(--hair);
  color: var(--ink-2);
  transition: border-color .15s, color .15s, background .15s;
}
.tag:hover { border-color: var(--ink); color: var(--ink); }
.tag.ghost { color: var(--muted); }

/* ---- Entrées (expériences / formation) ---------------------------------- */
.entry {
  display: grid;
  grid-template-columns: minmax(120px, 168px) 1fr;
  gap: var(--gap);
  padding: 26px 0;
  border-bottom: 1px solid var(--hair);
}
.entry:first-child { padding-top: 0; }
.entry:last-child { border-bottom: 0; padding-bottom: 0; }
.entry-meta { display: flex; flex-direction: column; gap: 5px; }
.period {
  font-family: var(--mono); font-size: 12px; letter-spacing: .04em;
  color: var(--ink); font-variant-numeric: tabular-nums;
}
.entry.is-now .period { color: var(--accent); }
.entry.is-now .period::after {
  content: ""; display: inline-block; width: 6px; height: 6px;
  margin-left: 7px; background: var(--accent); vertical-align: middle;
}
.place {
  font-family: var(--mono); font-size: 11px; letter-spacing: .04em;
  color: var(--faint);
}
.entry-role {
  font-size: clamp(18px, 2.2vw, 22px); font-weight: 700;
  letter-spacing: -0.015em; line-height: 1.2;
}
.entry-role .co {
  display: block; font-size: 13px; font-weight: 600;
  letter-spacing: .05em; text-transform: uppercase;
  color: var(--accent); margin-top: 5px;
}
.entry-role .edu-field { font-weight: 400; color: var(--muted); letter-spacing: 0; }
.entry-ctx {
  color: var(--muted); font-size: 14.5px; margin-top: 10px;
  max-width: 62ch;
}
.edu-school { color: var(--muted); font-size: 14px; margin-top: 8px; }

.missions { margin-top: 14px; display: grid; gap: 9px; }
.missions li {
  position: relative; padding-left: 22px;
  font-size: 14.5px; color: var(--ink-2); max-width: 66ch;
}
.missions li::before {
  content: ""; position: absolute; left: 0; top: .62em;
  width: 11px; height: 1px; background: var(--accent);
}

.ach {
  margin-top: 16px; padding: 12px 16px;
  border-left: 2px solid var(--accent); background: var(--panel);
  display: grid; gap: 4px;
}
.ach-label {
  font-family: var(--mono); font-size: 10px; letter-spacing: .18em;
  text-transform: uppercase; color: var(--accent);
}
.ach-text { font-size: 14.5px; color: var(--ink); max-width: 64ch; }

.stack { margin-top: 16px; display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.stack-label {
  font-family: var(--mono); font-size: 10px; letter-spacing: .16em;
  text-transform: uppercase; color: var(--faint);
}
.stack-list { display: flex; flex-wrap: wrap; gap: 6px 14px; }
.stack-list li {
  font-family: var(--mono); font-size: 12px; color: var(--muted);
  letter-spacing: .01em;
}
.stack-list li::before { content: "/ "; color: var(--faint); }

/* ---- Deflist (langues / certifs) ---------------------------------------- */
.deflist { display: grid; }
.deflist .ident-row:first-child { border-top: 0; }
.deflist .ident-row {
  grid-template-columns: minmax(140px, 220px) 1fr;
  border-bottom: 1px solid var(--hair);
}
.deflist .ident-row:last-child { border-bottom: 0; }
.deflist dt { color: var(--ink); font-family: var(--sans); font-size: 15px; letter-spacing: 0; text-transform: none; font-weight: 600; }
.deflist dd { color: var(--muted); }

/* ---- Pied de page -------------------------------------------------------- */
.colophon {
  border-top: 2px solid var(--rule);
  margin-top: 8px; padding-top: 20px;
  display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px;
  font-family: var(--mono); font-size: 11px; letter-spacing: .08em;
  color: var(--faint); text-transform: uppercase;
}

/* ---- Révélation au défilement ------------------------------------------- */
.js .reveal { opacity: 0; transform: translateY(14px); }
.js .reveal.in { opacity: 1; transform: none; transition: opacity .6s ease, transform .6s cubic-bezier(.2,.7,.2,1); }
@media (prefers-reduced-motion: reduce) {
  .js .reveal { opacity: 1; transform: none; }
}

/* ---- Bascule de langue --------------------------------------------------- */
.cv[data-active="false"] { display: none; }

/* ---- Responsive ---------------------------------------------------------- */
@media (max-width: 860px) {
  .ident-row, .section, .entry, .deflist .ident-row {
    grid-template-columns: 1fr; gap: 8px;
  }
  .section { gap: 18px; }
  .section-head { display: flex; align-items: baseline; gap: 12px; }
  .section-num { margin-bottom: 0; }
  .entry-meta { flex-direction: row; gap: 14px; align-items: baseline; }
}

/* ---- Impression ---------------------------------------------------------- */
@media print {
  .bar { display: none; }
  .wrap { max-width: none; padding: 0; }
  body { background: #fff; color: #000; font-size: 11px; }
  .js .reveal { opacity: 1 !important; transform: none !important; }
  .section, .entry { break-inside: avoid; }
  a { color: #000; }
}
"""


PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><!--NAME--> — <!--TITLE--></title>
<meta name="description" content="<!--TITLE--> — <!--NAME-->">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0d0d0d" media="(prefers-color-scheme: dark)">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style><!--STYLE--></style>
</head>
<body>
  <script>document.documentElement.classList.add('js');</script>
  <div class="bar">
    <a class="bar-ident" href="#top"><b>◆</b> <!--NAME--></a>
    <div class="bar-actions">
      <div class="seg lang-switch" role="group" aria-label="Language">
        <button class="on" data-lang="fr" onclick="setLang('fr')">FR</button>
        <button data-lang="en" onclick="setLang('en')">EN</button>
      </div>
      <button class="icon-btn" id="theme-btn" onclick="toggleTheme()" aria-label="Theme"><span id="theme-ico">◐</span></button>
      <span class="bar-dl">
        <a id="dl-design" href="cv-design-fr.pdf" download><!--DL_DESIGN--></a>
        <a id="dl-classic" href="cv-classic-fr.pdf" download><!--DL_CLASSIC--></a>
      </span>
    </div>
  </div>

  <main class="wrap">
    <div class="cv" data-lang="fr" data-active="true"><!--BODY_FR--></div>
    <div class="cv" data-lang="en" data-active="false"><!--BODY_EN--></div>
    <footer class="colophon">
      <span id="colo-left"><!--COLOPHON--></span>
      <span id="colo-right"><!--UPDATED--> <!--UPDATED_DATE--></span>
    </footer>
  </main>

<script>
  var LABELS = <!--LABELS-->;
  function applyLangText(l) {
    document.getElementById('dl-design').textContent = LABELS[l].design;
    document.getElementById('dl-classic').textContent = LABELS[l].classic;
    document.getElementById('dl-design').setAttribute('href', 'cv-design-' + l + '.pdf');
    document.getElementById('dl-classic').setAttribute('href', 'cv-classic-' + l + '.pdf');
    document.getElementById('colo-left').textContent = LABELS[l].colophon;
    document.getElementById('colo-right').textContent = LABELS[l].updated + ' ' + LABELS[l].date;
  }
  function setLang(l) {
    document.querySelectorAll('.cv').forEach(function (c) {
      c.setAttribute('data-active', c.getAttribute('data-lang') === l ? 'true' : 'false');
    });
    document.querySelectorAll('.lang-switch button').forEach(function (b) {
      b.classList.toggle('on', b.getAttribute('data-lang') === l);
    });
    document.documentElement.setAttribute('lang', l);
    applyLangText(l);
    observeReveals();
  }

  function currentTheme() {
    return document.documentElement.getAttribute('data-theme')
      || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }
  function paintThemeIcon() {
    document.getElementById('theme-ico').textContent = currentTheme() === 'dark' ? '☀' : '☾';
  }
  function toggleTheme() {
    var next = currentTheme() === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('cv-theme', next); } catch (e) {}
    paintThemeIcon();
  }
  (function initTheme() {
    var saved = null;
    try { saved = localStorage.getItem('cv-theme'); } catch (e) {}
    if (saved) document.documentElement.setAttribute('data-theme', saved);
    paintThemeIcon();
  })();

  var io;
  function observeReveals() {
    if (!('IntersectionObserver' in window)) {
      document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('in'); });
      return;
    }
    if (!io) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    }
    document.querySelectorAll('.cv[data-active="true"] .reveal:not(.in)').forEach(function (el) {
      io.observe(el);
    });
  }
  observeReveals();
</script>
</body>
</html>
"""


def main() -> int:
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    SITE.mkdir(exist_ok=True)

    updated = data["meta"]["updated"]
    labels = {
        lng: {
            "design": UI[lng]["pdf_design"],
            "classic": UI[lng]["pdf_classic"],
            "updated": UI[lng]["updated"],
            "colophon": UI[lng]["colophon"],
            "date": updated,
        }
        for lng in ("fr", "en")
    }

    replacements = {
        "<!--STYLE-->": STYLE,
        "<!--NAME-->": esc(data["profile"]["name"]),
        "<!--TITLE-->": esc(tr(data["profile"]["title"], "fr")),
        "<!--BODY_FR-->": render(data, "fr"),
        "<!--BODY_EN-->": render(data, "en"),
        "<!--DL_DESIGN-->": esc(UI["fr"]["pdf_design"]),
        "<!--DL_CLASSIC-->": esc(UI["fr"]["pdf_classic"]),
        "<!--COLOPHON-->": esc(UI["fr"]["colophon"]),
        "<!--UPDATED-->": esc(UI["fr"]["updated"]),
        "<!--UPDATED_DATE-->": esc(updated),
        "<!--LABELS-->": json.dumps(labels, ensure_ascii=False),
    }

    page = PAGE
    for token, value in replacements.items():
        page = page.replace(token, value)

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
