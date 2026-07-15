// =============================================================================
//  lib.typ — données + helpers partagés par les gabarits Typst
// =============================================================================
//
//  Compilation paramétrée via --input :
//    typst compile --input lang=fr  typst/cv-design.typ
//    typst compile --input lang=en  typst/cv-classic.typ
//
//  `lang` vaut "fr" (défaut) ou "en".
// =============================================================================

// -- Chargement de la source unique de vérité --------------------------------
#let data = yaml("../data/cv.yaml")

// -- Langue courante ----------------------------------------------------------
#let default-lang = data.meta.at("default_lang", default: "fr")
#let lang = sys.inputs.at("lang", default: default-lang)

// -- tr(v) : résout un champ éventuellement bilingue -------------------------
//  { fr: …, en: … }  -> la variante de la langue courante
//  toute autre valeur -> renvoyée telle quelle
#let tr(v) = {
  if type(v) == dictionary and "fr" in v and "en" in v {
    v.at(lang, default: v.at("fr"))
  } else {
    v
  }
}

// -- Libellés d'interface (selon la langue) ----------------------------------
#let i18n = (
  fr: (
    profile: "Profil",
    skills: "Compétences",
    experience: "Expériences",
    education: "Formation",
    certifications: "Certifications",
    languages: "Langues",
    ctx: "Contexte",
    achievements: "Réalisations",
    stack: "Environnement technique",
    present: "aujourd'hui",
    updated: "Mis à jour le",
  ),
  en: (
    profile: "Profile",
    skills: "Skills",
    experience: "Experience",
    education: "Education",
    certifications: "Certifications",
    languages: "Languages",
    ctx: "Context",
    achievements: "Achievements",
    stack: "Technical environment",
    present: "present",
    updated: "Updated on",
  ),
)
#let L = i18n.at(lang)

// -- Noms de mois abrégés -----------------------------------------------------
#let month-names = (
  fr: ("janv.", "févr.", "mars", "avr.", "mai", "juin",
       "juil.", "août", "sept.", "oct.", "nov.", "déc."),
  en: ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
)

// -- fmt-date("2023-01") -> "janv. 2023" ; "present" -> "aujourd'hui" ---------
#let fmt-date(s) = {
  if s == none or s == "" { return "" }
  if s == "present" { return L.present }
  let parts = str(s).split("-")
  if parts.len() >= 2 {
    let m = int(parts.at(1))
    if m >= 1 and m <= 12 {
      return month-names.at(lang).at(m - 1) + " " + parts.at(0)
    }
  }
  // année seule
  parts.at(0)
}

// -- daterange(start, end) -> "janv. 2023 – aujourd'hui" ---------------------
#let daterange(start, end) = {
  let a = fmt-date(start)
  let b = fmt-date(end)
  if b == "" { a } else { a + " – " + b }
}
