// =============================================================================
//  cv-classic.typ — version « classique » du dossier de compétences
//  Sobre, mono-colonne, police type Arial (Liberation Sans), sans couleur.
//  Objectif : contenu propre et neutre, facile à ré-habiller par un cabinet.
// =============================================================================
#import "lib.typ": data, lang, tr, L, daterange

#set document(
  title: tr(data.profile.title) + " — " + data.profile.name,
  author: data.profile.name,
)

#set page(
  paper: "a4",
  margin: (x: 2cm, top: 1.8cm, bottom: 1.6cm),
  footer: context [
    #set text(8pt, fill: luma(40%))
    #data.profile.name #h(1fr) #L.updated #data.meta.updated #h(1fr) #counter(page).display("1 / 1", both: true)
  ],
)

#set text(font: "Liberation Sans", size: 10.5pt, fill: black, lang: lang)
#set par(justify: false, leading: 0.6em)

// -- Titre de section : simple, majuscules, filet fin -----------------------
#let section(title) = {
  v(0.6em)
  text(11pt, weight: "bold", upper(title))
  v(0.1em)
  line(length: 100%, stroke: 0.5pt + black)
  v(0.25em)
}

// =============================================================================
//  EN-TÊTE
// =============================================================================
#align(center)[
  #text(18pt, weight: "bold", data.profile.name) \
  #v(-0.35em)
  #text(12pt, tr(data.profile.title))
]
#v(0.3em)

#let contacts = (
  data.profile.email,
  if data.profile.at("phone", default: "") != "" { data.profile.phone },
  tr(data.profile.location),
).filter(x => x != none and x != "")
#let contact-links = data.profile.at("links", default: ()).map(l => l.url)

#align(center, text(9pt, (contacts + contact-links).join("  |  ")))

// =============================================================================
//  PROFIL
// =============================================================================
#section(L.profile)
#tr(data.profile.summary)

// =============================================================================
//  COMPÉTENCES
// =============================================================================
#section(L.skills)
#for group in data.at("skills", default: ()) {
  block[
    #text(weight: "bold", tr(group.category)) : #group.items.map(it => tr(it)).join(", ")
  ]
  v(0.15em)
}

// =============================================================================
//  EXPÉRIENCES
// =============================================================================
#section(L.experience)
#for exp in data.at("experiences", default: ()) {
  block(breakable: false, width: 100%, {
    grid(
      columns: (1fr, auto),
      align: (left, right),
      text(weight: "bold", tr(exp.role) + " — " + exp.company),
      text(9.5pt, daterange(exp.start, exp.end)),
    )
    if exp.at("location", default: none) != none {
      text(9.5pt, style: "italic", tr(exp.location))
    }
    v(0.2em)
    if exp.at("context", default: none) != none {
      block[#text(weight: "bold", L.ctx + " : ")#tr(exp.context)]
      v(0.1em)
    }
    for m in exp.at("missions", default: ()) {
      grid(columns: (1em, 1fr), "•", tr(m))
    }
    let achs = exp.at("achievements", default: ())
    if achs.len() > 0 {
      v(0.15em)
      text(weight: "bold", L.achievements + " : ")
      for a in achs { grid(columns: (1em, 1fr), "•", tr(a)) }
    }
    let st = exp.at("stack", default: ())
    if st.len() > 0 {
      v(0.15em)
      block[#text(weight: "bold", L.stack + " : ")#st.join(", ")]
    }
  })
  v(0.5em)
}

// =============================================================================
//  FORMATION
// =============================================================================
#if data.at("education", default: ()).len() > 0 {
  section(L.education)
  for ed in data.education {
    grid(
      columns: (1fr, auto),
      align: (left, right),
      [#text(weight: "bold", tr(ed.degree))#if ed.at("field", default: none) != none [ — #tr(ed.field)], #ed.school#if ed.at("location", default: none) != none [ (#tr(ed.location))]],
      text(9.5pt, daterange(ed.start, ed.at("end", default: ""))),
    )
    v(0.2em)
  }
}

// =============================================================================
//  CERTIFICATIONS
// =============================================================================
#if data.at("certifications", default: ()).len() > 0 {
  section(L.certifications)
  for c in data.certifications {
    grid(columns: (1em, 1fr), "•",
      [#text(weight: "bold", c.name) — #c.issuer#if c.at("year", default: none) != none [ (#c.year)]])
  }
}

// =============================================================================
//  LANGUES
// =============================================================================
#if data.at("languages", default: ()).len() > 0 {
  section(L.languages)
  for lg in data.languages {
    grid(columns: (1em, 1fr), "•",
      [#text(weight: "bold", tr(lg.name)) : #tr(lg.level)])
  }
}
