#!/usr/bin/env python3
"""Régénère le résumé du dossier de compétences dans README.md.

Le contenu est injecté entre les marqueurs :
    <!-- BEGIN:CV --> … <!-- END:CV -->
Tout le reste du README (documentation d'usage) est préservé.

Usage :
    python scripts/gen_readme.py            # langue par défaut (data.meta.default_lang)
    python scripts/gen_readme.py --lang en
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Le paquet 'pyyaml' est manquant. Installez-le : pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "cv.yaml"
README = ROOT / "README.md"
BEGIN, END = "<!-- BEGIN:CV -->", "<!-- END:CV -->"

LABELS = {
    "fr": {
        "skills": "Compétences", "experience": "Expériences",
        "education": "Formation", "languages": "Langues",
        "interests": "Centres d'intérêt",
        "present": "aujourd'hui", "updated": "Mis à jour le",
        "contact": "Contact",
    },
    "en": {
        "skills": "Skills", "experience": "Experience",
        "education": "Education", "languages": "Languages",
        "interests": "Interests",
        "present": "present", "updated": "Updated on",
        "contact": "Contact",
    },
}
MONTHS = {
    "fr": ["janv.", "févr.", "mars", "avr.", "mai", "juin",
           "juil.", "août", "sept.", "oct.", "nov.", "déc."],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}


def tr(v, lang):
    if isinstance(v, dict) and "fr" in v and "en" in v:
        return v.get(lang, v["fr"])
    return v


def fmt_date(s, lang):
    if not s:
        return ""
    if s == "present":
        return LABELS[lang]["present"]
    parts = str(s).split("-")
    if len(parts) >= 2:
        m = int(parts[1])
        if 1 <= m <= 12:
            return f"{MONTHS[lang][m - 1]} {parts[0]}"
    return parts[0]


def daterange(start, end, lang):
    a, b = fmt_date(start, lang), fmt_date(end, lang)
    return a if not b else f"{a} – {b}"


def build_summary(data: dict, lang: str) -> str:
    lb = LABELS[lang]
    p = data["profile"]
    out: list[str] = []

    out.append(f"# {p['name']}")
    out.append("")
    if p.get("page_url"):
        out.append(f"Github Page : {p['page_url']}")
        out.append("")
    out.append(f"**{tr(p['title'], lang)}**")
    out.append("")
    out.append(tr(p["summary"], lang).strip())
    out.append("")

    # Contact
    bits = [f"✉️ {p['email']}"]
    if p.get("phone"):
        bits.append(f"📞 {p['phone']}")
    if p.get("location"):
        bits.append(f"📍 {tr(p['location'], lang)}")
    for link in p.get("links", []):
        bits.append(f"[{link['label']}]({link['url']})")
    out.append(" · ".join(bits))
    out.append("")

    # Compétences
    if data.get("skills"):
        out.append(f"## {lb['skills']}")
        out.append("")
        for g in data["skills"]:
            items = ", ".join(tr(it, lang) for it in g["items"])
            out.append(f"- **{tr(g['category'], lang)}** : {items}")
        out.append("")

    # Expériences
    if data.get("experiences"):
        out.append(f"## {lb['experience']}")
        out.append("")
        for e in data["experiences"]:
            period = daterange(e["start"], e.get("end", ""), lang)
            out.append(f"### {tr(e['role'], lang)} — {e['company']}")
            out.append(f"*{period}*")
            out.append("")
            if e.get("context"):
                out.append(f"> {tr(e['context'], lang)}")
                out.append("")
            for m in e.get("missions", []):
                out.append(f"- {tr(m, lang)}")
            if e.get("stack"):
                out.append("")
                out.append("`" + "` · `".join(e["stack"]) + "`")
            out.append("")

    # Formation
    if data.get("education"):
        out.append(f"## {lb['education']}")
        out.append("")
        for ed in data["education"]:
            period = daterange(ed["start"], ed.get("end", ""), lang)
            field = f" — {tr(ed['field'], lang)}" if ed.get("field") else ""
            out.append(f"- **{tr(ed['degree'], lang)}**{field}, {ed['school']} · *{period}*")
        out.append("")

    # Langues
    if data.get("languages"):
        out.append(f"## {lb['languages']}")
        out.append("")
        for lg in data["languages"]:
            out.append(f"- **{tr(lg['name'], lang)}** : {tr(lg['level'], lang)}")
        out.append("")

    # Centres d'intérêt
    if data.get("interests"):
        out.append(f"## {lb['interests']}")
        out.append("")
        out.append(" · ".join(tr(it, lang) for it in data["interests"]))
        out.append("")

    out.append(f"*{lb['updated']} {data['meta']['updated']}.*")
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=("fr", "en"))
    args = parser.parse_args()

    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    lang = args.lang or data["meta"].get("default_lang", "fr")
    summary = build_summary(data, lang)

    text = README.read_text(encoding="utf-8") if README.exists() else ""
    if BEGIN in text and END in text:
        head = text.split(BEGIN)[0]
        tail = text.split(END)[1]
        new = f"{head}{BEGIN}\n{summary}{END}{tail}"
    else:
        # Pas de marqueurs : on crée un README minimal encadré.
        new = f"{BEGIN}\n{summary}{END}\n"

    README.write_text(new, encoding="utf-8")
    print(f"README.md régénéré (langue : {lang}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
