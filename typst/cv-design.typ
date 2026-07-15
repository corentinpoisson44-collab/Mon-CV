// =============================================================================
//  cv-design.typ — version « design » du dossier de compétences
//  Rendu soigné : bandeau d'en-tête, couleur d'accent, puces, filets.
// =============================================================================
#import "lib.typ": data, lang, tr, L, daterange

// -- Palette ------------------------------------------------------------------
#let accent = rgb("#1f6feb")
#let ink = rgb("#1a1a1a")
#let muted = rgb("#5b6570")
#let hair = rgb("#e3e7ec")

#set document(
  title: tr(data.profile.title) + " — " + data.profile.name,
  author: data.profile.name,
)

#set page(
  paper: "a4",
  margin: (x: 1.6cm, top: 1.4cm, bottom: 1.4cm),
  footer: context [
    #set text(8pt, fill: muted)
    #data.profile.name
    #h(1fr)
    #L.updated #data.meta.updated
    #h(1fr)
    #counter(page).display("1 / 1", both: true)
  ],
)

#set text(font: "DejaVu Sans", size: 9.5pt, fill: ink, lang: lang)
#set par(justify: true, leading: 0.62em)

// -- Titre de section ---------------------------------------------------------
#let section(title) = {
  v(0.7em)
  block(
    grid(
      columns: (auto, 1fr),
      align: (left + horizon, left + horizon),
      column-gutter: 0.6em,
      text(11pt, weight: "bold", fill: accent, upper(title)),
      line(length: 100%, stroke: 0.6pt + hair),
    ),
  )
  v(0.15em)
}

// -- Puce de compétence -------------------------------------------------------
#let chip(txt) = box(
  fill: accent.lighten(88%),
  inset: (x: 0.55em, y: 0.3em),
  radius: 4pt,
  text(8.5pt, fill: accent.darken(15%), txt),
)

// =============================================================================
//  EN-TÊTE
// =============================================================================
#block(
  fill: accent,
  width: 100%,
  inset: (x: 1.1em, y: 0.9em),
  radius: 6pt,
  [
    #set text(fill: white)
    #text(19pt, weight: "bold", data.profile.name) \
    #v(-0.3em)
    #text(11.5pt, fill: white.darken(6%), tr(data.profile.title))
  ],
)

#v(0.4em)
// Ligne de contact
#let contacts = (
  data.profile.email,
  if data.profile.at("phone", default: "") != "" { data.profile.phone },
  tr(data.profile.location),
).filter(x => x != none and x != "")
#let contact-links = data.profile.at("links", default: ())

#block[
  #set text(8.8pt, fill: muted)
  #contacts.join("  ·  ")
  #if contact-links.len() > 0 [
    #linebreak()
    #contact-links.map(l => link(l.url, text(fill: accent, l.label + " ↗"))).join("  ·  ")
  ]
]

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
  block(
    grid(
      columns: (5.5cm, 1fr),
      column-gutter: 0.6em,
      row-gutter: 0.4em,
      text(weight: "bold", tr(group.category)),
      box(width: 100%, {
        for it in group.items {
          chip(tr(it))
          h(0.35em)
        }
      }),
    ),
  )
  v(0.2em)
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
      [
        #text(10.5pt, weight: "bold", tr(exp.role)) — #text(10.5pt, fill: accent, exp.company)
      ],
      text(8.5pt, fill: muted, daterange(exp.start, exp.end)),
    )
    if exp.at("location", default: none) != none {
      text(8.5pt, fill: muted, style: "italic", tr(exp.location))
    }
    v(0.25em)
    if exp.at("context", default: none) != none {
      block(text(9pt, fill: muted, style: "italic", tr(exp.context)))
      v(0.15em)
    }
    for m in exp.at("missions", default: ()) {
      grid(columns: (0.9em, 1fr),
        text(fill: accent, "▪"), tr(m))
    }
    let achs = exp.at("achievements", default: ())
    if achs.len() > 0 {
      v(0.2em)
      text(8.8pt, weight: "bold", fill: accent, L.achievements + " : ")
      for a in achs {
        grid(columns: (0.9em, 1fr), text(fill: accent, "→"), tr(a))
      }
    }
    let st = exp.at("stack", default: ())
    if st.len() > 0 {
      v(0.25em)
      text(8.5pt, fill: muted, weight: "bold", L.stack + " : ")
      text(8.5pt, fill: muted, st.join(" · "))
    }
  })
  v(0.55em)
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
      [
        #text(weight: "bold", tr(ed.degree))#if ed.at("field", default: none) != none [ — #tr(ed.field)] \
        #text(9pt, fill: muted, ed.school)#if ed.at("location", default: none) != none [ · #tr(ed.location)]
      ],
      text(8.5pt, fill: muted, daterange(ed.start, ed.at("end", default: ""))),
    )
    v(0.3em)
  }
}

// =============================================================================
//  CERTIFICATIONS + LANGUES (deux colonnes)
// =============================================================================
#let certs = data.at("certifications", default: ())
#let langs = data.at("languages", default: ())
#if certs.len() > 0 or langs.len() > 0 {
  grid(
    columns: (1fr, 1fr),
    column-gutter: 1.2em,
    if certs.len() > 0 [
      #section(L.certifications)
      #for c in certs [
        - #text(weight: "bold", c.name) — #text(fill: muted, c.issuer) #if c.at("year", default: none) != none [(#c.year)]
      ]
    ],
    if langs.len() > 0 [
      #section(L.languages)
      #for lg in langs [
        - #text(weight: "bold", tr(lg.name)) — #text(fill: muted, tr(lg.level))
      ]
    ],
  )
}
