<!-- BEGIN:CV -->
# Corentin Poisson

**Consultant — [intitulé de poste à préciser]**

EXEMPLE — Consultant avec X années d'expérience sur [domaine]. Spécialisé en [expertise clé], j'accompagne mes clients de la [phase amont] jusqu'à la [phase aval]. À remplacer par votre pitch réel.

✉️ corentinpoisson44@gmail.com · 📍 France · [LinkedIn](https://www.linkedin.com/in/…) · [GitHub](https://github.com/corentinpoisson44-collab)

## Compétences

- **Compétences métier** : Cadrage de projet, Recueil du besoin, Conduite du changement
- **Compétences techniques** : Python, SQL, Docker, CI/CD
- **Méthodologies** : Agile / Scrum, Kanban, Gestion de projet

## Expériences

### Consultant [rôle] — [Client / Employeur]
*janv. 2023 – aujourd'hui*

> EXEMPLE — Contexte de la mission : secteur, enjeu, taille d'équipe.

- Réalisation de [livrable / action] ayant permis [résultat].
- Pilotage de [périmètre] auprès de [parties prenantes].

`Python` · `PostgreSQL` · `Airflow`

### Consultant junior — [Client / Employeur précédent]
*sept. 2021 – déc. 2022*

> EXEMPLE — Deuxième expérience à remplacer.

- Description d'une mission clé.

`Excel` · `Power BI`

## Formation

- **Diplôme (ex. Master)** — Spécialité, [École / Université] · *2018 – 2021*

## Langues

- **Français** : Langue maternelle
- **Anglais** : Courant (C1)

*Mis à jour le 2026-07-15.*
<!-- END:CV -->

---

## 🗂️ À propos de ce dépôt

Ce dépôt **versionne mon dossier de compétences** (CV étendu). Toute
l'information vit dans **une seule source de vérité** — [`data/cv.yaml`](data/cv.yaml) —
d'où sont dérivés automatiquement :

| Sortie | Description | Commande |
| --- | --- | --- |
| **Résumé README** | La fiche ci-dessus | `python scripts/gen_readme.py` |
| **PDF design** | Rendu soigné, couleur d'accent | `python scripts/build.py --theme design` |
| **PDF classique** | Sobre et neutre, réadaptable par un cabinet de conseil | `python scripts/build.py --theme classic` |

Chaque PDF est généré en **français et en anglais** (`--lang fr` / `--lang en`).

### Structure

```
Mon-CV/
├── data/
│   └── cv.yaml           ← SOURCE UNIQUE À ÉDITER (bilingue FR/EN)
├── typst/
│   ├── lib.typ           ← données + helpers partagés
│   ├── cv-design.typ     ← gabarit « design »
│   └── cv-classic.typ    ← gabarit « classique » (neutre)
├── scripts/
│   ├── build.py          ← compile les PDF
│   └── gen_readme.py     ← régénère le résumé ci-dessus
└── build/                ← PDF générés (ignorés par git)
```

### Prise en main

```bash
# 1. Installer les dépendances (compilateur Typst + YAML, sans binaire externe)
pip install typst pyyaml

# 2. Éditer le contenu
$EDITOR data/cv.yaml

# 3. Régénérer le README et les 4 PDF
python scripts/gen_readme.py
python scripts/build.py
```

Les PDF se retrouvent dans `build/` :
`cv-design-fr.pdf`, `cv-design-en.pdf`, `cv-classic-fr.pdf`, `cv-classic-en.pdf`.

### Éditer le contenu

Tout se passe dans [`data/cv.yaml`](data/cv.yaml). Convention bilingue :

```yaml
# Champ traduisible :
title: { fr: "Consultant data", en: "Data Consultant" }
# Champ neutre (date, techno, nom propre) :
company: "ACME"
start: "2023-01"        # format AAAA-MM ; "present" = en cours
```

Après chaque modification, relancer `gen_readme.py` et `build.py`. Un
[workflow GitHub Actions](.github/workflows/build.yml) recompile aussi les PDF
à chaque push et les publie en artefacts.
