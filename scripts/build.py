#!/usr/bin/env python3
"""Compile les PDF du dossier de compétences depuis les gabarits Typst.

Génère, dans build/, le produit croisé { design, classic } x { fr, en } :
    build/cv-design-fr.pdf   build/cv-design-en.pdf
    build/cv-classic-fr.pdf  build/cv-classic-en.pdf

Usage :
    python scripts/build.py                 # tout compiler
    python scripts/build.py --theme classic # un seul thème
    python scripts/build.py --lang fr       # une seule langue

Dépendance : le paquet officiel `typst` (pip install typst) qui embarque
le compilateur natif — aucun binaire externe requis.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import typst
except ImportError:
    sys.exit("Le paquet 'typst' est manquant. Installez-le : pip install typst")

ROOT = Path(__file__).resolve().parent.parent
TYPST_DIR = ROOT / "typst"
BUILD_DIR = ROOT / "build"

THEMES = {
    "design": TYPST_DIR / "cv-design.typ",
    "classic": TYPST_DIR / "cv-classic.typ",
}
LANGS = ("fr", "en")


def build_one(theme: str, lang: str) -> Path:
    src = THEMES[theme]
    out = BUILD_DIR / f"cv-{theme}-{lang}.pdf"
    typst.compile(
        str(src),
        output=str(out),
        root=str(ROOT),
        sys_inputs={"lang": lang},
    )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", choices=list(THEMES), help="Limiter à un thème.")
    parser.add_argument("--lang", choices=LANGS, help="Limiter à une langue.")
    args = parser.parse_args()

    themes = [args.theme] if args.theme else list(THEMES)
    langs = [args.lang] if args.lang else list(LANGS)

    BUILD_DIR.mkdir(exist_ok=True)

    failures = 0
    for theme in themes:
        for lang in langs:
            try:
                out = build_one(theme, lang)
                size_kb = out.stat().st_size / 1024
                print(f"  ✓ {out.relative_to(ROOT)}  ({size_kb:.0f} Ko)")
            except Exception as exc:  # noqa: BLE001 — on veut le message brut de Typst
                failures += 1
                print(f"  ✗ {theme}/{lang} : {exc}", file=sys.stderr)

    if failures:
        print(f"\n{failures} échec(s) de compilation.", file=sys.stderr)
        return 1
    print("\nTous les PDF ont été générés dans build/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
