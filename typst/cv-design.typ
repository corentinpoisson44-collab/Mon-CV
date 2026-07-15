// =============================================================================
//  cv-design.typ — version « design » du dossier de compétences
//  Parti pris éditorial monochrome (noir & blanc) : masthead centré en
//  capitales espacées, sections numérotées, filets fins, puces sobres.
// =============================================================================
#import "lib.typ": data, lang, tr, L, daterange

// -- Palette monochrome -------------------------------------------------------
#let ink   = rgb("#111111") // texte principal, quasi noir
#let mid   = rgb("#454545") // texte secondaire
#let muted = rgb("#8a8a8a") // méta, dates, filets typés
#let hair  = rgb("#d9d9d9") // filets fins
#let wash  = rgb("#f3f3f3") // fond des étiquettes

#set document(
  title: tr(data.profile.title) + " — " + data.profile.name,
  author: data.profile.name,
)

#set page(
  paper: "a4",
  margin: (x: 1.9cm, top: 1.6cm, bottom: 1.5cm),
  footer: context [
    #line(length: 100%, stroke: 0.5pt + hair)
    #v(0.35em)
    #set text(7.5pt, fill: muted, tracking: 0.04em)
    #smallcaps(data.profile.name)
    #h(1fr)
    #L.updated #data.meta.updated
    #h(1fr)
    #counter(page).display("1 / 1", both: true)
  ],
)

#set text(font: "DejaVu Sans", size: 9.5pt, fill: ink, lang: lang)
#set par(justify: true, leading: 0.6em)

// -- Section numérotée --------------------------------------------------------
#let sec-counter = counter("section")
#let section(title) = {
  sec-counter.step()
  v(0.75em)
  block(sticky: true, grid(
    columns: (auto, auto, 1fr),
    align: (left + horizon, left + horizon, left + horizon),
    column-gutter: 0.7em,
    context {
      let n = sec-counter.get().first()
      let s = if n < 10 { "0" + str(n) } else { str(n) }
      text(8.5pt, fill: muted, weight: "bold", tracking: 0.05em)[#s]
    },
    text(10.5pt, weight: "bold", fill: ink, tracking: 0.2em)[#upper(title)],
    line(length: 100%, stroke: 0.6pt + hair),
  ))
  v(0.45em)
}

// -- Étiquette de compétence (monochrome) -------------------------------------
#let chip(txt) = box(
  fill: wash,
  inset: (x: 0.6em, y: 0.34em),
  radius: 2pt,
  text(8.5pt, fill: ink, txt),
)

// -- Marqueurs de liste -------------------------------------------------------
#let bullet = text(fill: mid, baseline: -0.02em)[–]
#let arrow  = text(fill: ink, weight: "bold")[→]

// =============================================================================
//  MASTHEAD
// =============================================================================
#let contacts = (
  data.profile.email,
  if data.profile.at("phone", default: "") != "" { data.profile.phone },
  tr(data.profile.location),
).filter(x => x != none and x != "")
#let contact-links = data.profile.at("links", default: ())

#align(center)[
  #text(24pt, weight: "bold", tracking: 0.28em)[#upper(data.profile.name)]
  #v(0.5em)
  #line(length: 16%, stroke: 0.9pt + ink)
  #v(0.5em)
  #text(9pt, fill: mid, tracking: 0.3em)[#upper(tr(data.profile.title))]
  #v(0.75em)
  #block[
    #set text(8.3pt, fill: muted, tracking: 0.02em)
    #contacts.join("   ·   ")
    #if contact-links.len() > 0 [
      #linebreak()
      #v(0.15em)
      #contact-links.map(l => link(l.url, text(fill: ink)[#l.label #text(fill: muted)[↗]])).join("   ·   ")
    ]
  ]
]

#v(0.9em)
#line(length: 100%, stroke: 0.8pt + ink)

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
  block(breakable: false, grid(
    columns: (5.2cm, 1fr),
    column-gutter: 0.8em,
    row-gutter: 0.4em,
    par(justify: false, text(weight: "bold", size: 9pt, hyphenate: false, tr(group.category))),
    box(width: 100%, par(leading: 0.8em, {
      for it in group.items {
        chip(tr(it))
        h(0.35em)
      }
    })),
  ))
  v(0.28em)
}

// =============================================================================
//  EXPÉRIENCES
// =============================================================================
#section(L.experience)
#for exp in data.at("experiences", default: ()) {
  block(breakable: false, width: 100%, {
    grid(
      columns: (1fr, auto),
      column-gutter: 0.8em,
      align: (left + top, right + top),
      [
        #text(10.5pt, weight: "bold", tr(exp.role))
        #text(10.5pt, fill: mid)[ — #exp.company]
      ],
      text(8pt, fill: muted, tracking: 0.03em, daterange(exp.start, exp.end)),
    )
    if exp.at("location", default: none) != none {
      text(8.5pt, fill: muted, style: "italic", tr(exp.location))
    }
    v(0.28em)
    if exp.at("context", default: none) != none {
      block(text(9pt, fill: mid, style: "italic", tr(exp.context)))
      v(0.18em)
    }
    for m in exp.at("missions", default: ()) {
      grid(columns: (1em, 1fr), column-gutter: 0.2em, bullet, tr(m))
    }
    let achs = exp.at("achievements", default: ())
    if achs.len() > 0 {
      v(0.25em)
      text(8.5pt, weight: "bold", fill: ink, tracking: 0.12em)[#upper(L.achievements)]
      v(0.15em)
      for a in achs {
        grid(columns: (1em, 1fr), column-gutter: 0.2em, arrow, tr(a))
      }
    }
    let st = exp.at("stack", default: ())
    if st.len() > 0 {
      v(0.3em)
      text(8pt, fill: muted, weight: "bold", tracking: 0.08em)[#upper(L.stack) ]
      text(8.5pt, fill: mid, st.join("  ·  "))
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
    let field = tr(ed.at("field", default: ""))
    grid(
      columns: (1fr, auto),
      column-gutter: 0.8em,
      align: (left + top, right + top),
      [
        #text(weight: "bold", tr(ed.degree))#if field != "" [ — #field] \
        #text(9pt, fill: mid, ed.school)#if ed.at("location", default: none) != none [ · #tr(ed.location)]
      ],
      text(8pt, fill: muted, tracking: 0.03em, daterange(ed.start, ed.at("end", default: ""))),
    )
    v(0.35em)
  }
}

// =============================================================================
//  CERTIFICATIONS + LANGUES (deux colonnes)
// =============================================================================
#let certs = data.at("certifications", default: ())
#let langs = data.at("languages", default: ())
#let render-certs = [
  #section(L.certifications)
  #for c in certs [
    #grid(columns: (1em, 1fr), column-gutter: 0.2em, bullet,
      [#text(weight: "bold", c.name) — #text(fill: mid, c.issuer)#if c.at("year", default: none) != none [ (#c.year)]])
  ]
]
#let render-langs = [
  #section(L.languages)
  #for lg in langs [
    #grid(columns: (1em, 1fr), column-gutter: 0.2em, bullet,
      [#text(weight: "bold", tr(lg.name)) — #text(fill: mid, tr(lg.level))])
  ]
]
#if certs.len() > 0 and langs.len() > 0 {
  grid(columns: (1fr, 1fr), column-gutter: 1.4em, render-certs, render-langs)
} else if certs.len() > 0 {
  render-certs
} else if langs.len() > 0 {
  render-langs
}

// =============================================================================
//  CENTRES D'INTÉRÊT
// =============================================================================
#let interests = data.at("interests", default: ())
#if interests.len() > 0 {
  section(L.interests)
  box(width: 100%, par(leading: 0.8em, {
    for it in interests {
      chip(tr(it))
      h(0.35em)
    }
  }))
}
