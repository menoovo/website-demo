#!/usr/bin/env python3
"""Baut die statische HEIDEHOF-Website.

Aufruf:  python3 build.py
Erzeugt alle HTML-Seiten, sitemap.xml und robots.txt im Repo-Wurzelverzeichnis.
Inhalte, Speisekarte und Öffnungszeiten werden hier gepflegt.
Benötigt Python 3 und Pillow (für Bildmaße).
"""
import html
import json
import os
import re
from datetime import date

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://menoovo.github.io/website-demo/"
HEUTE = date.today().isoformat()

NAME = "HEIDEHOF"
NAME_LANG = "HEIDEHOF – Das Familienwirtshaus"
CLAIM = "Gut essen. Zusammen sein."
CLAIM_LANG = "Wo gutes Essen Menschen zusammenbringt."
STRASSE = "Am Heidehof 1"
PLZ = "21335"
ORT = "Lüneburg"
TEL_ANZEIGE = "04131 00 00 00"
TEL = "+494131000000"
MAIL = "hallo@heidehof-lueneburg.de"
GEO = (53.2272, 10.4031)
OSM = f"https://www.openstreetmap.org/?mlat={GEO[0]}&mlon={GEO[1]}#map=15/{GEO[0]}/{GEO[1]}"

NAV = [
    ("speisekarte/", "Speisekarte"),
    ("familien/", "Familien"),
    ("feiern/", "Feiern"),
    ("ausflug/", "Ausflug"),
    ("mittagstisch/", "Mittagstisch"),
    ("regionale-kueche/", "Unsere Küche"),
]

# ---------------------------------------------------------------- Öffnungszeiten
ZEITEN = [
    ("1", "Montag", "Ruhetag"),
    ("2,3,4,5", "Dienstag – Freitag", "11:30 – 14:30 Uhr <small>(Mittagstisch)</small><br>17:00 – 22:00 Uhr"),
    ("6", "Samstag", "11:30 – 22:30 Uhr durchgehend"),
    ("0", "Sonntag &amp; Feiertage", "09:30 – 21:00 Uhr<br><small>Heide-Frühstück bis 12:00 Uhr</small>"),
]
ZEITEN_SCHEMA = [
    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "11:30", "closes": "14:30"},
    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "17:00", "closes": "22:00"},
    {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "11:30", "closes": "22:30"},
    {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "09:30", "closes": "21:00"},
]

# ---------------------------------------------------------------- Speisekarte
# (id, Titel, Untertitel, [(Name, Beschreibung, Preis, [Etiketten])])
KARTE = [
    ("vorspeisen", "Vorspeisen &amp; Kleinigkeiten", "Zum Anfangen – oder zum Teilen mit dem ganzen Tisch.", [
        ("Heidekartoffelsuppe", "Cremig, mit gerösteten Speckwürfeln, Schnittlauch und Bauernbrot. Ohne Speck auch vegetarisch.", "7,90", ["Klassiker", "regional"]),
        ("Buchweizen-Blinis mit geräucherter Forelle", "Forelle aus der Heide, Meerrettich-Schmand, eingelegte Gurke und Dill.", "12,50", ["regional"]),
        ("Rote-Bete-Carpaccio", "Mit Ziegenfrischkäse vom Hof, Walnüssen, Heidehonig und Feldsalat.", "10,90", ["vegetarisch"]),
        ("Heidjer Brotzeitbrett", "Heidschnucken-Salami, Katenschinken, Bergkäse, Griebenschmalz, Gurken und Bauernbrot.", "16,90", ["zum Teilen"]),
        ("Kleiner Marktsalat", "Blattsalate der Saison, Kerne, Radieschen und Apfel-Senf-Dressing.", "6,90", ["vegan"]),
    ]),
    ("hauptgerichte", "Hauptgerichte", "Norddeutsche Klassiker, zeitgemäß gekocht – mit Zeit, Handwerk und guten Zutaten.", [
        ("Geschmorte Heidschnuckenkeule", "Sieben Stunden geschmort, Wacholderjus, Speckbohnen und Kartoffelgratin. Unser Hausgericht.", "28,50", ["Hausgericht", "regional"]),
        ("Heidschnucken-Burger", "Brioche, Bergkäse, Preiselbeer-Zwiebeln, Rauke und Rosmarin-Kartoffelspalten.", "19,90", ["regional"]),
        ("Kotelett vom Strohschwein", "Vom Hof aus der Nachbarschaft, mit knusprigen Bratkartoffeln und Gurkensalat.", "21,90", ["Klassiker"]),
        ("Rinderroulade nach Omas Rezept", "Mit Apfelrotkohl und Kartoffelklößen. Ja, mit ganz viel Soße.", "23,90", ["Klassiker"]),
        ("Lachsforelle in Senfrahm", "Aus Teichwirtschaft in der Heide, Petersilienkartoffeln und Gurken-Dill-Gemüse.", "22,50", ["regional"]),
        ("Wildgulasch", "Aus heimischer Jagd, mit Pilzen, Rotkohl und Spätzle. Von Oktober bis Februar.", "24,50", ["saisonal"]),
        ("Heidespargel (April bis Juni)", "Ein Pfund weißer Spargel, neue Kartoffeln, Sauce Hollandaise, wahlweise mit Katenschinken.", "26,90", ["saisonal", "regional"]),
    ]),
    ("vegetarisch", "Vegetarisch &amp; Vegan", "Kein Beiwerk, sondern Hauptsache.", [
        ("Graupotto mit Kürbis", "Perlgraupen wie Risotto gekocht, Ofenkürbis, Bergkäse, geröstete Kerne.", "17,90", ["vegetarisch"]),
        ("Ofengemüse-Bowl mit Buchweizen", "Saisongemüse aus dem Ofen, Buchweizen, Hummus, Kräuter und Leinsamen-Crunch.", "16,50", ["vegan"]),
        ("Käsespätzle", "Mit Bergkäse, Röstzwiebeln und kleinem Salat. Macht glücklich, wissenschaftlich unbelegt.", "15,90", ["vegetarisch", "Kinderliebling"]),
    ]),
    ("kinder", "Für kleine Heidjer", "Für Kinder bis 12 Jahre – gerne auch als halbe Portion von der großen Karte.", [
        ("Kleines Schnitzel", "Vom Strohschwein, mit Pommes oder Kartoffelpüree.", "8,90", ["Kinderliebling"]),
        ("Nudeln mit Tomatensoße", "Mit oder ohne Käse – Hauptsache Nudeln.", "6,50", ["vegetarisch"]),
        ("Fischstäbchen, selbst gemacht", "Aus Forellenfilet, mit Kartoffelpüree und Erbsen.", "7,90", ["Kinderliebling"]),
        ("Buchweizen-Pfannkuchen", "Mit Apfelmus und Zimtzucker.", "6,90", ["vegetarisch"]),
        ("Schnuckenfutter", "Gemüsesticks mit Kräuterdip – für Kinder kostenlos.", "0,00", ["vegan"]),
    ]),
    ("desserts", "Desserts &amp; Kuchen", "Ohne Nachtisch ist kein Essen fertig. Steht so im Familienrat-Protokoll.", [
        ("Heide-Buchweizentorte", "Der Klassiker der Region: Buchweizenboden, Preiselbeeren und Sahne.", "5,90", ["regional", "Klassiker"]),
        ("Rote Grütze", "Mit Vanillesoße – oder, für Mutige, mit beidem: Soße und Sahne.", "7,50", ["vegetarisch"]),
        ("Heidehonig-Parfait", "Mit Heidelbeeren und Haferkrokant.", "8,50", ["regional"]),
        ("Arme Ritter", "Vom eigenen Brioche, mit Apfelkompott und Zimt.", "7,90", ["vegetarisch"]),
    ]),
    ("fruehstueck", "Heide-Frühstück am Sonntag", "Sonntags 09:30 bis 12:00 Uhr – Buffet mit regionalen Produkten.", [
        ("Heide-Frühstück für Erwachsene", "Brot und Brötchen vom Bäcker, Rührei, Wurst und Käse aus der Region, Heidehonig, Müsli, Obst, Kaffee und Tee satt.", "24,90", ["regional"]),
        ("Heide-Frühstück für Kinder", "Pro Lebensjahr 1 Euro, Kinder unter 3 Jahren frühstücken gratis.", "1,00", ["Kinderliebling"]),
    ]),
    ("getraenke", "Getränke", "Eine Auswahl – die ganze Getränkekarte bekommst du am Tisch.", [
        ("Heide-Hell vom Fass", "Untergäriges Helles einer Brauerei aus der Region, 0,4 l.", "4,90", ["regional"]),
        ("Hausgemachte Limonade", "Holunder-Minze oder Rhabarber, 0,4 l.", "4,50", ["vegan"]),
        ("Apfelschorle von der Streuobstwiese", "Naturtrüber Saft aus der Region, 0,4 l.", "3,90", ["regional"]),
        ("Weinbegleitung", "Ausgewählte Weine von Familienweingütern – glasweise ab", "5,90", []),
        ("Kaffee &amp; Spezialitäten", "Bohnen von einer Rösterei aus Lüneburg – ab", "2,90", []),
    ]),
]

ETIKETT_DIAET = {"vegetarisch": "https://schema.org/VegetarianDiet", "vegan": "https://schema.org/VeganDiet"}

# ---------------------------------------------------------------- Hilfsfunktionen
_bildmasse = {}


def bildmasse(datei):
    if datei not in _bildmasse:
        with Image.open(os.path.join(ROOT, "assets", "img", datei)) as im:
            _bildmasse[datei] = im.size
    return _bildmasse[datei]


def img(name, alt, sizes="100vw", cls="", eager=False):
    """Responsives <img> mit srcset, Maßen und Lazy Loading."""
    if name.startswith("marke-"):
        w, h = bildmasse(f"{name}.webp")
        src = f"~/assets/img/{name}.webp"
        srcset = ""
    else:
        w, h = bildmasse(f"{name}-1600.webp")
        w8, _ = bildmasse(f"{name}-800.webp")
        src = f"~/assets/img/{name}-1600.webp"
        srcset = f' srcset="~/assets/img/{name}-800.webp {w8}w, ~/assets/img/{name}-1600.webp {w}w" sizes="{sizes}"'
    laden = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    klasse = f' class="{cls}"' if cls else ""
    return f'<img src="{src}"{srcset} width="{w}" height="{h}" alt="{alt}"{klasse}{laden}>'


def zweig(cls):
    return f'<img src="~/assets/img/heidezweig.svg" alt="" class="{cls}" width="80" height="305" aria-hidden="true">'


ICONS = {
    "kind": '<circle cx="12" cy="5" r="2.5"/><path d="M12 8v7m0 0-3 6m3-6 3 6M7 11l5-2 5 2"/>',
    "herz": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    "blatt": '<path d="M5 19c0-8 5-13 14-14 0 9-5 14-13 14z"/><path d="M5 19 13 11"/>',
    "glas": '<path d="M7 3h10l-1 7a4 4 0 0 1-8 0L7 3z"/><path d="M12 14v6m-4 0h8"/>',
    "rad": '<circle cx="6" cy="16" r="4"/><circle cx="18" cy="16" r="4"/><path d="m6 16 4-8h5l3 8M10 8 12 16h6M9 5h3"/>',
    "pfote": '<circle cx="7" cy="9" r="1.8"/><circle cx="11" cy="6" r="1.8"/><circle cx="15" cy="6" r="1.8"/><circle cx="18" cy="10" r="1.8"/><path d="M8 17c0-3 2-5 4.5-5S17 14 17 17c0 2-2 2.5-4.5 2.5S8 19 8 17z"/>',
    "uhr": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/>',
    "torte": '<path d="M4 20h16v-7H4zM4 15c2 1.5 4 1.5 5.3 0 1.4 1.5 4 1.5 5.4 0 1.3 1.5 3.3 1.5 5.3 0M12 13V8m0-4c1 1 1 2.5 0 4-1-1.5-1-3 0-4z"/>',
    "haus": '<path d="M4 11 12 4l8 7v9H4z"/><path d="M10 20v-5h4v5"/>',
    "buch": '<path d="M4 5c3-1 6-1 8 1 2-2 5-2 8-1v14c-3-1-6-1-8 1-2-2-5-2-8-1z"/><path d="M12 6v14"/>',
    "topf": '<path d="M4 10h16v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5zM2 10h20M9 6c0-1 1-1 1-2m4 2c0-1 1-1 1-2"/>',
    "sonne": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>',
    "stuhl": '<path d="M7 3v18M17 3v18M7 9h10M7 13h10M5 13h14"/>',
    "tasche": '<path d="M5 8h14l-1 12H6zM9 8V6a3 3 0 0 1 6 0v2"/>',
    "stern": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    "besteck": '<path d="M7 3v8m-2-8v5a2 2 0 0 0 4 0V3M7 11v10M17 3c-2 1-3 3-3 7h3v11"/>',
}


def icon(name):
    return f'<svg class="karte-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'


def karte(ic, titel, text, reveal_i=0):
    return f'<article class="karte" data-reveal style="--verz:{reveal_i * 0.08:.2f}s">{icon(ic)}<h3>{titel}</h3><p>{text}</p></article>'


def faq_html(fragen):
    teile = "".join(f"<details><summary>{q}</summary><div><p>{a}</p></div></details>" for q, a in fragen)
    return f'<div class="faq" data-reveal>{teile}</div>'


def faq_schema(fragen):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
            for q, a in fragen
        ],
    }


def strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def zeiten_tabelle():
    zeilen = "".join(f'<tr data-tage="{t}"><th scope="row">{tag}</th><td>{z}</td></tr>' for t, tag, z in ZEITEN)
    return f'<table class="zeiten"><caption class="visually-hidden">Öffnungszeiten</caption>{zeilen}</table>'


def adresse_html():
    return (f'<address><strong>{NAME_LANG}</strong><br>{STRASSE}<br>{PLZ} {ORT}<br><br>'
            f'Telefon: <a href="tel:{TEL}">{TEL_ANZEIGE}</a><br>E-Mail: <a href="mailto:{MAIL}">{MAIL}</a></address>')


KARTE_SVG = """<svg viewBox="0 0 400 250" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
<rect width="400" height="250" fill="#2c4a3a"/>
<path d="M-10 190 C 80 160, 150 210, 230 170 S 360 120, 420 140" stroke="#3f6b8a" stroke-width="10" fill="none" opacity=".7"/>
<g stroke="#d6c6b0" stroke-linecap="round" fill="none" opacity=".55"><path d="M0 70 H400" stroke-width="5"/><path d="M120 0 V250" stroke-width="4"/><path d="M0 230 L250 40 L400 30" stroke-width="3"/><path d="M260 250 L300 0" stroke-width="2.5"/><path d="M0 120 C 100 110, 200 130, 400 95" stroke-width="2"/></g>
<g fill="#7A4B73" opacity=".35"><circle cx="60" cy="30" r="22"/><circle cx="340" cy="200" r="30"/><circle cx="350" cy="70" r="16"/></g>
<g transform="translate(200 112)"><circle r="34" fill="#F6EDE0" opacity=".18"/><path d="M0 18 C -12 2, -16 -6, -16 -12 a16 16 0 0 1 32 0 c0 6 -4 14 -16 30z" fill="#F6EDE0"/><circle cy="-12" r="6" fill="#1F3B2D"/></g>
</svg>"""


def brotkrumen(teile):
    li = []
    for i, (url, name) in enumerate(teile):
        if i == len(teile) - 1:
            li.append(f'<li aria-current="page">{name}</li>')
        else:
            li.append(f'<li><a href="~/{url}">{name}</a></li>')
    return f'<nav class="brotkrumen" aria-label="Brotkrumen"><ol>{"".join(li)}</ol></nav>'


def brotkrumen_schema(teile):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": strip(n), "item": BASE + u}
            for i, (u, n) in enumerate(teile)
        ],
    }


def seiten_hero(bild, alt, kicker, h1, lead, krumen, extra=""):
    return f"""
<header class="seiten-hero">
  <div class="hero-bild">{img(bild, alt, "100vw", eager=True)}</div>
  <div class="wrap">
    {brotkrumen(krumen)}
    <p class="kicker">{kicker}</p>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
    {extra}
  </div>
</header>"""


def cta(titel="Wir halten dir einen Platz frei.", text="Reserviere online in einer Minute – oder ruf uns einfach an. Wir freuen uns auf dich, deine Familie und alle, die du mitbringst.", hell=False):
    return f"""
<section class="sektion {'sektion--sand' if hell else 'sektion--gruen'} cta">
  {zweig('zweig-l')}{zweig('zweig-r')}
  <div class="wrap wrap--schmal zentriert" data-reveal>
    <p class="kicker">Gut essen. Zusammen sein.</p>
    <h2>{titel}</h2>
    <p class="lead">{text}</p>
    <div class="btn-reihe">
      <a class="btn {'btn--gruen' if hell else 'btn--creme'}" href="~/reservieren/">Tisch reservieren</a>
      <a class="btn btn--linie" href="tel:{TEL}">{TEL_ANZEIGE}</a>
    </div>
  </div>
</section>"""


def restaurant_schema():
    return {
        "@context": "https://schema.org",
        "@type": "Restaurant",
        "@id": BASE + "#restaurant",
        "name": NAME_LANG,
        "alternateName": ["HEIDEHOF Lüneburg", "Heidehof Familienwirtshaus"],
        "slogan": CLAIM,
        "description": "Modernes Familienwirtshaus in Lüneburg mit regionaler, norddeutscher Küche aus der Lüneburger Heide, Spielecke für Kinder, Heidegarten und Räumen für Familienfeiern.",
        "url": BASE,
        "logo": BASE + "assets/logo/heidehof-logo.png",
        "image": [BASE + "assets/img/gemeinsam-am-tisch-1600.webp", BASE + "assets/img/schmorbraten-1600.webp", BASE + "assets/img/og-heidehof.jpg"],
        "telephone": TEL,
        "email": MAIL,
        "address": {"@type": "PostalAddress", "streetAddress": STRASSE, "postalCode": PLZ, "addressLocality": ORT, "addressRegion": "Niedersachsen", "addressCountry": "DE"},
        "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
        "hasMap": OSM,
        "areaServed": ["Lüneburg", "Landkreis Lüneburg", "Lüneburger Heide"],
        "servesCuisine": ["Regionale Küche", "Norddeutsche Küche", "Deutsche Küche", "Vegetarisch", "Vegan"],
        "priceRange": "€€",
        "currenciesAccepted": "EUR",
        "paymentAccepted": "Bargeld, EC-Karte, Kreditkarte",
        "acceptsReservations": True,
        "hasMenu": BASE + "speisekarte/",
        "openingHoursSpecification": ZEITEN_SCHEMA,
        "amenityFeature": [
            {"@type": "LocationFeatureSpecification", "name": n, "value": True}
            for n in ["Spielecke für Kinder", "Spielplatz im Garten", "Hochstühle", "Wickelraum", "Kinderkarte",
                      "Terrasse / Biergarten", "Barrierefreier Zugang", "Hunde willkommen", "Kostenlose Parkplätze",
                      "Fahrradstellplätze", "E-Bike-Ladestation", "Räume für Feiern", "Vegetarische und vegane Gerichte"]
        ],
        "knowsLanguage": ["de", "en"],
    }


def menu_schema():
    abschnitte = []
    for sid, titel, unter, speisen in KARTE:
        items = []
        for n, d, p, tags in speisen:
            item = {"@type": "MenuItem", "name": strip(n), "description": strip(d),
                    "offers": {"@type": "Offer", "price": p.replace(",", "."), "priceCurrency": "EUR"}}
            diaet = [ETIKETT_DIAET[t] for t in tags if t in ETIKETT_DIAET]
            if diaet:
                item["suitableForDiet"] = diaet if len(diaet) > 1 else diaet[0]
            items.append(item)
        abschnitte.append({"@type": "MenuSection", "name": strip(titel), "description": strip(unter), "hasMenuItem": items})
    return {"@context": "https://schema.org", "@type": "Menu", "@id": BASE + "speisekarte/#menu", "name": "Speisekarte HEIDEHOF Lüneburg",
            "inLanguage": "de", "mainEntityOfPage": BASE + "speisekarte/", "hasMenuSection": abschnitte}


# ---------------------------------------------------------------- Seitenrahmen
def kopf(seite, R):
    navlis = "".join(
        f'<li><a href="~/{u}"{" aria-current=\"page\"" if seite["pfad"] == u else ""}>{n}</a></li>' for u, n in NAV
    )
    return f"""<a class="skip-link" href="#inhalt">Zum Inhalt springen</a>
<header class="site-header">
  <div class="wrap">
    <a class="marke" href="~/" aria-label="HEIDEHOF – zur Startseite">
      <img class="marke-dunkel" src="~/assets/logo/heidehof-zeichen-gruen.svg" alt="" width="58" height="25">
      <img class="marke-hell" src="~/assets/logo/heidehof-zeichen-creme.svg" alt="" width="58" height="25">
      <span class="marke-text"><strong>HEIDEHOF</strong><small>Das Familienwirtshaus</small></span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="hauptnav">Menü <span aria-hidden="true"><i></i><i></i><i></i></span></button>
    <nav class="hauptnav" id="hauptnav" aria-label="Hauptnavigation">
      <ul>{navlis}<li><a class="btn btn--gruen" href="~/reservieren/">Reservieren</a></li></ul>
    </nav>
  </div>
</header>"""


def fuss():
    return f"""
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-raster">
      <div>
        <img class="footer-logo" src="~/assets/logo/heidehof-logo-creme.svg" alt="HEIDEHOF – Das Familienwirtshaus" width="220" height="150" loading="lazy">
        <p class="footer-claim">{CLAIM}</p>
        <p>Modernes Familienwirtshaus in Lüneburg – regionale Küche, herzlicher Service und Platz für alle Generationen.</p>
      </div>
      <div>
        <h2>Besuch uns</h2>
        <p>{STRASSE}<br>{PLZ} {ORT}<br><a href="tel:{TEL}">{TEL_ANZEIGE}</a><br><a href="mailto:{MAIL}">{MAIL}</a></p>
        <p><a href="{OSM}" rel="noopener" target="_blank">Route planen ↗</a></p>
      </div>
      <div>
        <h2>Öffnungszeiten</h2>
        <ul>
          <li>Mo: Ruhetag</li>
          <li>Di – Fr: 11:30 – 14:30 &amp; 17 – 22 Uhr</li>
          <li>Sa: 11:30 – 22:30 Uhr</li>
          <li>So: 09:30 – 21:00 Uhr</li>
        </ul>
      </div>
      <div>
        <h2>Entdecken</h2>
        <ul>
          <li><a href="~/speisekarte/">Speisekarte</a></li>
          <li><a href="~/familien/">Kinderfreundliches Restaurant</a></li>
          <li><a href="~/feiern/">Feiern &amp; Gruppen</a></li>
          <li><a href="~/ausflug/">Ausflugslokal Lüneburger Heide</a></li>
          <li><a href="~/mittagstisch/">Mittagstisch Lüneburg</a></li>
          <li><a href="~/regionale-kueche/">Regionale Küche &amp; Erzeuger</a></li>
          <li><a href="~/en/" hreflang="en" lang="en">English</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-unten">
      <p>© <span data-jahr>2026</span> HEIDEHOF – Das Familienwirtshaus · Demo-Projekt: Der HEIDEHOF ist ein fiktives Restaurant.</p>
      <ul><li><a href="~/impressum/">Impressum</a></li><li><a href="~/datenschutz/">Datenschutz</a></li></ul>
    </div>
  </div>
</footer>
<div class="mobil-cta"><a class="btn btn--creme" href="tel:{TEL}">Anrufen</a><a class="btn btn--gruen" href="~/reservieren/">Reservieren</a></div>"""


def seite_rendern(seite):
    pfad = seite["pfad"]
    tiefe = pfad.count("/")
    R = seite.get("R") or ("../" * tiefe if tiefe else "./")
    canonical = BASE + pfad
    titel = seite["titel"]
    beschreibung = seite["beschreibung"]
    lang = seite.get("lang", "de")
    og_bild = BASE + "assets/img/og-heidehof.jpg"
    schemas = seite.get("schema", [])
    ld = "\n".join(
        f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False, separators=(",", ":"))}</script>' for s in schemas
    )
    robots = "noindex, follow" if seite.get("noindex") else "index, follow, max-image-preview:large, max-snippet:-1"
    hreflang = ""
    if pfad in ("", "en/"):
        hreflang = (f'<link rel="alternate" hreflang="de" href="{BASE}">\n'
                    f'<link rel="alternate" hreflang="en" href="{BASE}en/">\n'
                    f'<link rel="alternate" hreflang="x-default" href="{BASE}">')
    preload = ""
    if seite.get("preload"):
        n = seite["preload"]
        preload = f'<link rel="preload" as="image" href="~/assets/img/{n}-1600.webp" imagesrcset="~/assets/img/{n}-800.webp 800w, ~/assets/img/{n}-1600.webp 1600w" imagesizes="100vw" fetchpriority="high">'
    body_cls = "hat-hero" if seite.get("hero", True) else ""
    doc = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titel}</title>
<meta name="description" content="{beschreibung}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
{hreflang}
<meta name="theme-color" content="#1F3B2D">
<meta name="geo.region" content="DE-NI">
<meta name="geo.placename" content="{ORT}">
<meta name="geo.position" content="{GEO[0]};{GEO[1]}">
<meta name="ICBM" content="{GEO[0]}, {GEO[1]}">
<meta property="og:type" content="{'restaurant.restaurant' if pfad == '' else 'website'}">
<meta property="og:site_name" content="{NAME_LANG}">
<meta property="og:locale" content="{'en_GB' if lang == 'en' else 'de_DE'}">
<meta property="og:title" content="{seite.get('og_titel', titel)}">
<meta property="og:description" content="{beschreibung}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_bild}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="HEIDEHOF – Das Familienwirtshaus in Lüneburg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="~/favicon.svg" type="image/svg+xml">
<link rel="icon" href="~/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="~/apple-touch-icon.png">
<link rel="manifest" href="~/site.webmanifest">
<link rel="preload" href="~/assets/fonts/montserrat.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="~/assets/fonts/merriweather.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<link rel="stylesheet" href="~/assets/css/style.css">
<script>document.documentElement.classList.add("js")</script>
{ld}
</head>
<body class="{body_cls}">
{kopf(seite, R)}
<main id="inhalt">
{seite['inhalt']}
</main>
{fuss()}
<script src="~/assets/js/main.js" defer></script>
</body>
</html>
"""
    doc = re.sub(r"\n{2,}", "\n", doc)
    doc = doc.replace("~/", R)
    ziel = os.path.join(ROOT, seite.get("datei") or os.path.join(pfad, "index.html"))
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    with open(ziel, "w", encoding="utf-8") as f:
        f.write(doc)
    return ziel


# ================================================================= SEITEN
SEITEN = []

# ---------------------------------------------------------------- Startseite
gerichte = [
    ("schmorbraten", "Geschmorte Heidschnuckenkeule mit Jus", "Geschmorte Heidschnuckenkeule", "Sieben Stunden im Ofen, Wacholderjus, Speckbohnen, Kartoffelgratin. Unser Hausgericht.", "28,50 €", ["Hausgericht", "regional"]),
    ("kotelett-bratkartoffeln", "Kotelett mit Bratkartoffeln", "Kotelett vom Strohschwein", "Vom Nachbarhof, mit knusprigen Bratkartoffeln und Gurkensalat.", "21,90 €", ["Klassiker"]),
    ("forelle-ofen", "Fischfilets in Senfrahm mit Zitrone", "Lachsforelle in Senfrahm", "Aus der Heide-Teichwirtschaft, Petersilienkartoffeln, Gurken-Dill-Gemüse.", "22,50 €", ["regional"]),
    ("vegetarische-bowl", "Bunte Gemüse-Bowl mit Getreide", "Ofengemüse-Bowl", "Saisongemüse, Buchweizen, Hummus und Kräuter. Kein Beiwerk, sondern Hauptsache.", "16,50 €", ["vegan"]),
    ("teilen-platte", "Brotzeitplatte zum Teilen mit Bier", "Heidjer Brotzeitbrett", "Heidschnucken-Salami, Katenschinken, Käse, Schmalz – für den ganzen Tisch.", "16,90 €", ["zum Teilen"]),
    ("dessert-gruetze", "Dessert im Glas mit Erdbeeren", "Rote Grütze", "Mit Vanillesoße. Oder mit Sahne. Oder – wir urteilen nicht – mit beidem.", "7,50 €", ["Klassiker"]),
]
scroller = "".join(
    f'<article class="gericht" data-reveal style="--verz:{i * 0.07:.2f}s"><figure>{img(n, alt, "(max-width: 600px) 85vw, 360px")}</figure>'
    f'<div class="gericht-text"><div>{"".join(f"<span class=etikett>{t}</span>" for t in tags)}</div><h3>{t1}</h3><p>{d}</p><span class="preis">{p}</span></div></article>'
    for i, (n, alt, t1, d, p, tags) in enumerate(gerichte)
)

startseite = f"""
<section class="hero">
  <div class="hero-bild">{img("gemeinsam-am-tisch", "Freunde und Familie sitzen gemeinsam an einer langen Tafel", "100vw", eager=True)}</div>
  {zweig('hero-zweig hero-zweig--l')}{zweig('hero-zweig hero-zweig--l2')}{zweig('hero-zweig hero-zweig--r')}{zweig('hero-zweig hero-zweig--r2')}
  <div class="hero-intro">
    <p class="offen-status" data-offen-status><i></i><span>Di – So geöffnet</span></p>
    <div class="hero-logo"><img src="~/assets/logo/heidehof-logo-creme.svg" alt="HEIDEHOF – Das Familienwirtshaus" width="2504" height="1709" fetchpriority="high"></div>
    <h1>Familienwirtshaus in Lüneburg</h1>
    <p class="hero-claim">{CLAIM}</p>
    <div>
      <p class="hero-text">Regionale Küche aus der Lüneburger Heide, ein Tisch für alle Generationen und ganz viel Herzlichkeit. Komm vorbei – und bring mit, wen du magst.</p>
      <div class="btn-reihe"><a class="btn btn--creme" href="~/reservieren/">Tisch reservieren</a><a class="btn btn--linie" href="~/speisekarte/">Zur Speisekarte</a></div>
    </div>
  </div>
  <a class="scroll-hinweis" href="#willkommen">Entdecken</a>
</section>

<section class="sektion papier" id="willkommen">
  <div class="wrap split">
    <div class="split-bild" data-reveal>
      {img("genuss-moment", "Liebevoll angerichteter Teller auf einem gedeckten Holztisch", "(max-width: 860px) 100vw, 50vw")}
      {img("schaf-portrait", "Neugieriges Schaf auf der Weide", "(max-width: 860px) 45vw, 22vw", "bild-klein")}
      {zweig('zweig-deko')}
    </div>
    <div data-reveal style="--verz:.15s">
      <p class="kicker">Willkommen im HEIDEHOF</p>
      <h2>{CLAIM_LANG}</h2>
      <p class="lead">Der HEIDEHOF steht für ehrliche, hochwertige Gastronomie mit regionalen Wurzeln und echter Herzlichkeit.</p>
      <p>Bei uns fühlen sich alle Generationen willkommen: Kinder dürfen Kinder sein, Erwachsene genießen entspannt. Wir verbinden die Tradition norddeutscher Gastlichkeit mit einem modernen, ungezwungenen Restauranterlebnis – mit norddeutschen Klassikern, zeitgemäßen Ideen und saisonalen Produkten aus der Lüneburger Heide.</p>
      <p>Natürliche Materialien, warmes Licht und aufmerksamer Service: Der HEIDEHOF ist ein Ort für Familien, Freunde, Paare und alle, die gutes Essen ernst nehmen und das Zusammensein genießen.</p>
      <a class="pfeil-link" href="~/regionale-kueche/">Unsere Küche &amp; Erzeuger</a>
    </div>
  </div>
</section>

<section class="sektion sektion--gruen" aria-label="Der HEIDEHOF in Zahlen">
  <div class="wrap zahlen">
    <div class="zahl" data-reveal><strong data-zahl="12">12</strong><span>Erzeuger aus der Region beliefern unsere Küche</span></div>
    <div class="zahl" data-reveal style="--verz:.1s"><strong data-zahl="50" data-nach=" km">50 km</strong><span>weiter reisen unsere Zutaten selten</span></div>
    <div class="zahl" data-reveal style="--verz:.2s"><strong data-zahl="180">180</strong><span>Plätze drinnen und im Heidegarten</span></div>
    <div class="zahl" data-reveal style="--verz:.3s"><strong data-zahl="1000" data-nach="+">1.000+</strong><span>Kinderbilder an unserer Malwand</span></div>
  </div>
</section>

<section class="sektion">
  <div class="wrap">
    <div class="sektion-kopf" data-reveal>
      <p class="kicker">Aus unserer Küche</p>
      <h2>Norddeutsch. Saisonal. Mit Liebe gekocht.</h2>
      <p class="lead">Klassiker, die wie früher schmecken – nur ein bisschen besser. Dazu vegetarische Gerichte, die niemand als Beilage bezeichnen würde.</p>
    </div>
    <div class="scroller" role="list">{scroller}</div>
    <p><a class="btn btn--gruen" href="~/speisekarte/">Ganze Speisekarte ansehen</a></p>
  </div>
</section>

<section class="sektion sektion--hell">
  <div class="wrap">
    <div class="sektion-kopf zentriert zentriert" data-reveal>
      <p class="kicker">Ein Tisch für alle Generationen</p>
      <h2>Wofür kommst du zu uns?</h2>
      <p class="lead">Ob Familienausflug, Geburtstag, schnelle Mittagspause oder Radtour durch die Heide – im HEIDEHOF ist für jeden Anlass ein Platz frei.</p>
    </div>
    <div class="kacheln">
      <a class="kachel kachel--breit" href="~/familien/" data-reveal>{img("kinder-spielen", "Kinder spielen fröhlich auf einer Wiese", "(max-width: 620px) 100vw, 50vw")}<div class="kachel-inhalt"><h3>Essen gehen mit Kindern</h3><p>Spielecke, Kinderkarte, Wickelraum – und Eltern, die in Ruhe aufessen.</p><span class="pfeil-link">Für Familien</span></div></a>
      <a class="kachel kachel--breit" href="~/feiern/" data-reveal style="--verz:.1s">{img("freunde-lachen", "Freunde lachen zusammen am Tisch", "(max-width: 620px) 100vw, 50vw")}<div class="kachel-inhalt"><h3>Feiern &amp; Gruppen</h3><p>Taufe, Geburtstag, Konfirmation oder Firmenfeier – bis 80 Gäste.</p><span class="pfeil-link">Feier planen</span></div></a>
      <a class="kachel" href="~/ausflug/" data-reveal>{img("abendlicht-feld", "Weite Landschaft im goldenen Abendlicht", "(max-width: 620px) 100vw, 33vw")}<div class="kachel-inhalt"><h3>Ausflug in die Heide</h3><p>Einkehr für Radler, Wanderer und Hunde.</p><span class="pfeil-link">Für Ausflügler</span></div></a>
      <a class="kachel" href="~/mittagstisch/" data-reveal style="--verz:.1s">{img("kueche-handwerk", "Koch schneidet frisches Gemüse", "(max-width: 620px) 100vw, 33vw")}<div class="kachel-inhalt"><h3>Mittagstisch</h3><p>Di – Fr, frisch gekocht, in 45 Minuten zurück im Büro.</p><span class="pfeil-link">Zur Wochenkarte</span></div></a>
      <a class="kachel" href="~/regionale-kueche/" data-reveal style="--verz:.2s">{img("heidschnucke", "Schaf auf einer sonnigen Weide", "(max-width: 620px) 100vw, 33vw")}<div class="kachel-inhalt"><h3>Für Genießer</h3><p>Heidschnucke, Heidespargel, Buchweizen: Region auf dem Teller.</p><span class="pfeil-link">Regionale Küche</span></div></a>
    </div>
  </div>
</section>

<section class="band" aria-label="Unser Versprechen">
  <div class="band-bild">{img("gastraum-theke", "Warm beleuchteter Gastraum mit Holztheke", "100vw")}</div>
  <blockquote data-reveal>„Hier wird gutes Essen ernst genommen – und das Zusammensein selbstverständlich gelebt.“<cite>Anna &amp; Jonas Brammer, Gastgeber</cite></blockquote>
</section>

<section class="sektion">
  <div class="wrap split">
    <div class="split-bild" data-reveal>{img("familie", "Vater trägt lachend zwei Kinder", "(max-width: 860px) 100vw, 50vw")}</div>
    <div data-reveal style="--verz:.15s">
      <p class="kicker">Kinderfreundliches Restaurant</p>
      <h2>Kinder dürfen Kinder sein.</h2>
      <p class="lead">Im „Schnuckenstall“ wird gespielt, gemalt und gebaut – in Sichtweite der Eltern, aber weit genug weg für ein Gespräch unter Erwachsenen.</p>
      <ul class="haken">
        <li>Spielecke drinnen und Spielplatz im Heidegarten</li>
        <li>Kinderkarte und halbe Portionen von der großen Karte</li>
        <li>Hochstühle, Wickelraum und Platz für Kinderwagen</li>
      </ul>
      <a class="pfeil-link" href="~/familien/">Alles für Familien</a>
    </div>
  </div>
</section>

<section class="sektion sektion--sand">
  <div class="wrap split split--umgekehrt">
    <div class="split-bild split-bild--quer" data-reveal>{img("fruehstueck", "Reich gedeckter Frühstückstisch von oben", "(max-width: 860px) 100vw, 50vw")}</div>
    <div data-reveal style="--verz:.15s">
      <p class="kicker">Jeden Sonntag</p>
      <h2>Heide-Frühstück für die ganze Familie</h2>
      <p class="lead">Sonntags von 09:30 bis 12:00 Uhr: Buffet mit Brot vom Bäcker, Rührei, Heidehonig, Wurst und Käse aus der Region – Kaffee und Tee so viel du magst.</p>
      <p><strong>24,90 € pro Person.</strong> Kinder zahlen 1 € pro Lebensjahr, unter 3 Jahren frühstücken sie gratis.</p>
      <a class="btn btn--gruen" href="~/reservieren/">Frühstückstisch reservieren</a>
    </div>
  </div>
</section>

<section class="sektion">
  <div class="wrap">
    <div class="sektion-kopf" data-reveal>
      <p class="kicker">Holz, Leinen, Keramik, warmes Licht</p>
      <h2>Ein Wirtshaus zum Wiederkommen</h2>
    </div>
    <div class="galerie">
      <figure class="hoch" data-reveal>{img("marke-sign", "Rundes HEIDEHOF-Wirtshausschild an der Fassade mit Heidekraut", "(max-width: 860px) 50vw, 25vw")}<figcaption>Unser Schild</figcaption></figure>
      <figure class="breit" data-reveal style="--verz:.1s">{img("gastraum-theke", "Gastraum mit Holztheke und warmem Licht", "(max-width: 860px) 100vw, 50vw")}<figcaption>Gastraum</figcaption></figure>
      <figure class="hoch" data-reveal style="--verz:.2s">{img("marke-menu", "In Leinen gebundene Speisekarte mit HEIDEHOF-Logo", "(max-width: 860px) 50vw, 25vw")}<figcaption>Speisekarte</figcaption></figure>
      <figure data-reveal>{img("bier-gezapft", "Frisch gezapftes Bier", "(max-width: 860px) 50vw, 25vw")}<figcaption>Heide-Hell</figcaption></figure>
      <figure data-reveal style="--verz:.1s">{img("marke-napkin", "Leinenserviette mit Heidezweig und Logo", "(max-width: 860px) 50vw, 25vw")}<figcaption>Liebe zum Detail</figcaption></figure>
    </div>
  </div>
</section>

<section class="sektion sektion--gruen" id="besuch">
  <div class="wrap">
    <div class="sektion-kopf" data-reveal>
      <p class="kicker">Besuch uns</p>
      <h2>Am südlichen Stadtrand von Lüneburg</h2>
      <p class="lead">Mit kostenlosen Parkplätzen, Fahrradständern und dem Heidegarten direkt vor der Tür.</p>
    </div>
    <div class="info-raster" data-reveal>
      <div><h3>Öffnungszeiten</h3>{zeiten_tabelle()}<p><small>Küche bis eine Stunde vor Schluss.</small></p></div>
      <div><h3>Adresse &amp; Kontakt</h3>{adresse_html()}<p style="margin-top:1.4em"><a class="btn btn--creme" href="~/reservieren/">Tisch reservieren</a></p></div>
      <div><h3>Anfahrt</h3><a class="karte-link" href="{OSM}" target="_blank" rel="noopener">{KARTE_SVG}<span>Route planen ↗</span></a><p style="margin-top:1em">40 kostenlose Parkplätze · Bushaltestelle in 3 Gehminuten · E-Bike-Ladestation</p></div>
    </div>
  </div>
</section>
{cta(hell=True)}
"""

SEITEN.append({
    "pfad": "",
    "titel": "HEIDEHOF Lüneburg – Familienwirtshaus mit regionaler Küche",
    "og_titel": "HEIDEHOF – Das Familienwirtshaus in Lüneburg · Gut essen. Zusammen sein.",
    "beschreibung": "Gut essen. Zusammen sein. Der HEIDEHOF in Lüneburg: regionale Küche aus der Heide, kinderfreundlich, mit Heidegarten und Räumen für Feiern. Jetzt reservieren!",
    "preload": "gemeinsam-am-tisch",
    "inhalt": startseite,
    "schema": [restaurant_schema(), {
        "@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "#website", "url": BASE, "name": NAME_LANG,
        "inLanguage": "de", "publisher": {"@id": BASE + "#restaurant"}}],
})

# ---------------------------------------------------------------- Speisekarte
def speise_html(n, d, p, tags):
    preis = "gratis" if p == "0,00" else (f"{p} €" if not d.endswith(" ab") else f"{p} €")
    et = "".join(f'<span class="etikett{" etikett--gruen" if t in ("vegetarisch", "vegan") else ""}">{t}</span>' for t in tags)
    return (f'<li class="speise"><div class="speise-kopf"><h3>{n}</h3><span class="punkte" aria-hidden="true"></span>'
            f'<span class="preis">{preis}</span></div><p>{d}</p>{f"<div class=etiketten>{et}</div>" if et else ""}</li>')


KURZ = {"vorspeisen": "Vorspeisen", "hauptgerichte": "Hauptgerichte", "vegetarisch": "Vegetarisch &amp; Vegan", "kinder": "Kinderkarte",
        "desserts": "Desserts", "fruehstueck": "Sonntagsfrühstück", "getraenke": "Getränke"}
karten_nav = "".join(f'<li><a href="#{sid}">{KURZ.get(sid, t)}</a></li>' for sid, t, _, _ in KARTE)
abschnitte = ""
for sid, titel, unter, speisen in KARTE:
    sig = ""
    if sid == "hauptgerichte":
        sig = f"""<div class="signatur" data-reveal>{img("schmorbraten", "Geschmorte Heidschnuckenkeule, aufgeschnitten", "(max-width: 760px) 100vw, 50vw")}
<div class="signatur-text"><p class="kicker">Unser Hausgericht</p><h3>Geschmorte Heidschnuckenkeule</h3><p>Die Lüneburger Heidschnucke pflegt seit Jahrhunderten die Heidelandschaft – und schmeckt dabei kräftig, fein und ein bisschen nach Wild. Wir schmoren die Keule sieben Stunden mit Wacholder, Rotwein und Wurzelgemüse.</p><p class="preis">28,50 €</p><a class="pfeil-link" style="color:var(--sand)" href="~/regionale-kueche/#heidschnucke">Mehr über die Heidschnucke</a></div></div>"""
    abschnitte += f"""
<section class="karten-abschnitt" id="{sid}" aria-labelledby="t-{sid}">
  <div class="karten-abschnitt-kopf" data-reveal><h2 id="t-{sid}">{titel}</h2><p>{unter}</p></div>
  {sig}
  <ul class="speisen">{"".join(speise_html(*s) for s in speisen)}</ul>
</section>"""

speisekarte = seiten_hero(
    "teilen-platte", "Brotzeitplatte und Bier auf einem Holztisch", "Speisekarte",
    "Speisekarte: Regionale Küche aus der Lüneburger Heide",
    "Norddeutsche Klassiker, saisonale Gerichte und echte Lieblingsgerichte für Kinder. Fast alles kochen wir selbst – von der Brühe bis zur Roten Grütze.",
    [("", "Start"), ("speisekarte/", "Speisekarte")],
) + f"""
<nav class="karten-nav" aria-label="Kategorien der Speisekarte"><div class="wrap"><ul>{karten_nav}</ul></div></nav>
<div class="wrap">
{abschnitte}
<p class="karten-hinweis">Alle Preise in Euro inkl. MwSt. Die Karte wechselt mit den Jahreszeiten. Informationen zu Allergenen und Zusatzstoffen geben wir dir gerne persönlich – sprich uns einfach an. Halbe Portionen für Kinder sind bei fast allen Hauptgerichten möglich.</p>
</div>
{cta("Appetit bekommen?", "Reserviere deinen Tisch – unter der Woche klappt es oft auch spontan. Am Wochenende lohnt sich die Reservierung.")}
"""
SEITEN.append({
    "pfad": "speisekarte/",
    "titel": "Speisekarte – Regionale Küche in Lüneburg | HEIDEHOF",
    "beschreibung": "Die Speisekarte des HEIDEHOF Lüneburg: Heidschnuckenkeule, Heidespargel, norddeutsche Klassiker, vegetarische & vegane Gerichte, Kinderkarte und Sonntagsfrühstück.",
    "preload": "teilen-platte",
    "inhalt": speisekarte,
    "schema": [menu_schema(), brotkrumen_schema([("", "Start"), ("speisekarte/", "Speisekarte")])],
})

# ---------------------------------------------------------------- Familien
faq_familien = [
    ("Gibt es Hochstühle und einen Wickeltisch?", "Ja. Wir haben zwölf Hochstühle, zwei Sitzerhöhungen und einen großen Wickelraum mit Windeln für den Notfall. Sag bei der Reservierung Bescheid, dann steht der Hochstuhl schon bereit."),
    ("Gibt es eine Kinderkarte?", "Ja, unsere Karte „Für kleine Heidjer“ mit Schnitzel, Nudeln, selbst gemachten Fischstäbchen und Pfannkuchen. Außerdem gibt es fast alle Hauptgerichte als halbe Portion. Gemüsesticks mit Dip sind für Kinder kostenlos."),
    ("Ist die Spielecke beaufsichtigt?", "Die Spielecke „Schnuckenstall“ ist nicht betreut, liegt aber in Sichtweite vieler Tische. Wenn du gern direkt daneben sitzen möchtest, schreib es in die Reservierung."),
    ("Kann ich Babybrei warm machen lassen?", "Natürlich. Gib das Gläschen oder Fläschchen einfach beim Service ab – wir wärmen es gern auf."),
    ("Wann ist die beste Zeit für einen Besuch mit kleinen Kindern?", "Mittags am Wochenende und abends ab 17 Uhr geht es besonders entspannt zu. Sonntags ist unser Heide-Frühstück bei Familien sehr beliebt – hier lohnt sich eine Reservierung."),
    ("Können wir mit dem Kinderwagen kommen?", "Ja. Der Eingang und der Gastraum sind stufenlos, Kinderwagen können am Tisch oder in unserer Kinderwagen-Ecke parken."),
]
familien = seiten_hero(
    "kinder-spielen", "Kinder spielen fröhlich auf einer Wiese", "Familienrestaurant in Lüneburg",
    "Kinderfreundliches Restaurant in Lüneburg – hier dürfen Kinder Kinder sein",
    "Gut essen gehen mit Kindern? Geht – und zwar entspannt. Im HEIDEHOF finden Kinder Raum zum Spielen und Entdecken, während die Großen in Ruhe genießen.",
    [("", "Start"), ("familien/", "Familien")],
    '<div class="btn-reihe"><a class="btn btn--creme" href="~/reservieren/">Familientisch reservieren</a></div>',
) + f"""
<section class="sektion papier">
  <div class="wrap">
    <div class="sektion-kopf" data-reveal><p class="kicker">Für die Kleinen</p><h2>Spielen, malen, satt werden</h2><p class="lead">Wir finden: Ein Restaurantbesuch muss für Kinder kein Stillsitz-Wettbewerb sein.</p></div>
    <div class="karten">
      {karte("haus", "Spielecke „Schnuckenstall“", "Mit Spielküche, Bauklötzen, Bilderbüchern und einer kuscheligen Leseecke – mitten im Gastraum und gut im Blick.", 0)}
      {karte("sonne", "Spielplatz im Heidegarten", "Sandkiste, Schaukel und Balancierbalken direkt neben der Terrasse. Bei Sonne der beliebteste Platz im Haus.", 1)}
      {karte("besteck", "Kinderkarte &amp; halbe Portionen", "Lieblingsgerichte für kleine Heidjer und fast alle Hauptgerichte als halbe Portion. Gemüsesticks gibt es gratis.", 2)}
      {karte("buch", "Malen &amp; Rätseln", "Jedes Kind bekommt unser Heide-Malheft. Die schönsten Bilder kommen an die Malwand – inzwischen über tausend.", 3)}
    </div>
  </div>
</section>

<section class="sektion sektion--hell">
  <div class="wrap split">
    <div class="split-bild" data-reveal>{img("familie", "Vater trägt lachend zwei Kinder", "(max-width: 860px) 100vw, 50vw")}</div>
    <div data-reveal style="--verz:.15s">
      <p class="kicker">Für die Großen</p>
      <h2>Und die Eltern essen in Ruhe auf.</h2>
      <p class="lead">Wir haben an das gedacht, was Familien wirklich brauchen.</p>
      <ul class="haken">
        <li>12 Hochstühle und Sitzerhöhungen – auf Wunsch schon am Tisch</li>
        <li>Großer Wickelraum mit Windeln und Feuchttüchern für den Notfall</li>
        <li>Stufenloser Zugang und Platz für Kinderwagen</li>
        <li>Ruhige Stillecke und Babygläschen-Service</li>
        <li>Allergien und Unverträglichkeiten? Wir kochen gern angepasst</li>
        <li>Familientische für bis zu 12 Personen</li>
      </ul>
    </div>
  </div>
</section>

<section class="sektion sektion--gruen">
  <div class="wrap split split--umgekehrt">
    <div class="split-bild split-bild--quer" data-reveal>{img("geburtstag", "Bunte Luftballons zur Geburtstagsfeier", "(max-width: 860px) 100vw, 50vw")}</div>
    <div data-reveal style="--verz:.15s">
      <p class="kicker">Kindergeburtstag in Lüneburg</p>
      <h2>Die Schnucken-Party</h2>
      <p class="lead">Kindergeburtstag ohne Chaos zu Hause: Wir decken einen bunten Tisch, backen den Kuchen und haben eine Heide-Schatzsuche im Garten vorbereitet.</p>
      <p>19 € pro Kind mit Kuchen, Kindergericht, Limonade und kleinem Geschenk. Ab 6 Kindern, Erwachsene bestellen à la carte.</p>
      <a class="btn btn--creme" href="~/feiern/#anfrage">Kindergeburtstag anfragen</a>
    </div>
  </div>
</section>

<section class="sektion">
  <div class="wrap wrap--schmal">
    <div class="sektion-kopf" data-reveal><p class="kicker">Häufige Fragen</p><h2>Gut zu wissen für Familien</h2></div>
    {faq_html(faq_familien)}
  </div>
</section>
{cta("Ein Tisch für die ganze Familie", "Reserviere online und sag uns gleich, ob ihr einen Hochstuhl oder einen Platz nahe der Spielecke braucht.", hell=True)}
"""
SEITEN.append({
    "pfad": "familien/",
    "titel": "Kinderfreundliches Restaurant Lüneburg | HEIDEHOF",
    "beschreibung": "Essen gehen mit Kindern in Lüneburg: Spielecke, Spielplatz, Kinderkarte, Hochstühle & Wickelraum. Der HEIDEHOF ist das Familienrestaurant für alle Generationen.",
    "preload": "kinder-spielen",
    "inhalt": familien,
    "schema": [faq_schema(faq_familien), brotkrumen_schema([("", "Start"), ("familien/", "Familien")])],
})

# ---------------------------------------------------------------- Feiern
faq_feiern = [
    ("Ab wie vielen Personen gibt es einen eigenen Raum?", "Die Kaminstube reservieren wir ab 15 Personen exklusiv für euch, die Große Diele ab 35 Personen. Kleinere Gruppen bekommen einen schönen, abgetrennten Bereich im Gastraum."),
    ("Wie früh sollten wir anfragen?", "Für Samstage im Mai, Juni und Dezember am besten drei bis sechs Monate vorher. Unter der Woche und für kleinere Runden klappt es oft auch kurzfristig."),
    ("Können wir eine eigene Torte mitbringen?", "Ja, sehr gern. Für das Anschneiden, Servieren und Geschirr berechnen wir 2,50 € pro Person. Oder du bestellst bei uns – unsere Buchweizentorte ist legendär."),
    ("Gibt es Angebote für Trauerfeiern?", "Ja. Wir richten einen ruhigen Kaffeetisch oder ein schlichtes Mittagessen aus – auch kurzfristig. Ruf uns am besten direkt an, wir kümmern uns um alles."),
    ("Ist Dekoration erlaubt?", "Natürlich. Tischdeko mit Heide, Leinen und Kerzen ist bei uns inklusive. Eigene Deko kannst du gern mitbringen, Konfetti bitte nur im Garten."),
    ("Können auch Gäste mit Allergien oder vegetarischer Ernährung mitessen?", "Selbstverständlich. Gib uns die Wünsche vorab durch, dann planen wir sie in jedes Buffet und jedes Menü ein."),
]
feiern = seiten_hero(
    "freunde-lachen", "Freunde lachen zusammen am Tisch", "Feiern &amp; Gruppen in Lüneburg",
    "Familienfeier, Geburtstag oder Firmenfeier in Lüneburg",
    "Ihr bringt die Gäste, wir kümmern uns um den Rest: drei Räume, regionale Buffets und Menüs, liebevolle Deko und ein Team, das gern feiert.",
    [("", "Start"), ("feiern/", "Feiern")],
    '<div class="btn-reihe"><a class="btn btn--creme" href="#anfrage">Feier anfragen</a></div>',
) + f"""
<section class="sektion papier">
  <div class="wrap">
    <div class="sektion-kopf" data-reveal><p class="kicker">Unsere Räume</p><h2>Für 8 bis 80 Gäste</h2></div>
    <div class="karten">
      {karte("haus", "Die Kaminstube · bis 30 Gäste", "Gemütlich mit Kachelofen und eigener Tür. Ideal für Taufe, Konfirmation, runde Geburtstage oder einen Trauerkaffee im kleinen Kreis.", 0)}
      {karte("glas", "Die Große Diele · bis 80 Gäste", "Hohe Balkendecke, lange Tafeln, eigene Theke und Tanzfläche. Für Hochzeiten, Jubiläen und Firmenfeiern.", 1)}
      {karte("sonne", "Der Heidegarten · bis 60 Gäste", "Von Mai bis September unter alten Eichen, direkt neben dem Spielplatz. Perfekt für Sommerfeste und Grillbuffets.", 2)}
    </div>
  </div>
</section>

<section class="sektion sektion--gruen">
  <div class="wrap split">
    <div data-reveal>
      <p class="kicker">Anlässe</p>
      <h2>Wir feiern alles, was zusammenbringt.</h2>
      <ul class="haken">
        <li>Taufe, Kommunion und Konfirmation</li>
        <li>Geburtstage – vom ersten bis zum neunzigsten</li>
        <li>Hochzeit im kleinen Kreis und Polterabend</li>
        <li>Goldene Hochzeit und Familientreffen</li>
        <li>Trauerkaffee und Gedenkessen</li>
        <li>Firmenfeier, Weihnachtsfeier und Teamessen</li>
        <li>Kindergeburtstag als „Schnucken-Party“</li>
      </ul>
    </div>
    <div class="split-bild split-bild--quer" data-reveal style="--verz:.15s">{img("gemeinsam-am-tisch", "Lange Tafel mit vielen Gästen beim Essen", "(max-width: 860px) 100vw, 50vw")}</div>
  </div>
</section>

<section class="sektion">
  <div class="wrap">
    <div class="sektion-kopf" data-reveal><p class="kicker">Pakete</p><h2>Gut geplant, ehrlich kalkuliert</h2><p class="lead">Alle Pakete passen wir an eure Wünsche an. Preise pro Person, inklusive Tischdeko.</p></div>
    <div class="karten">
      <article class="karte paket" data-reveal><h3>Kaffeetafel</h3><span class="preis">ab 18,50 €</span><ul class="haken"><li>Drei Torten und Kuchen nach Wahl</li><li>Kaffee und Tee satt</li><li>Ideal für Taufe und Trauerkaffee</li></ul></article>
      <article class="karte paket paket--hervor" data-reveal style="--verz:.08s"><h3>Heide-Buffet</h3><span class="preis">ab 39 €</span><ul class="haken"><li>Vorspeisen, drei Hauptgerichte, Desserts</li><li>Mit Heidschnucke und vegetarischer Auswahl</li><li>Kinder bis 12 Jahre zahlen die Hälfte</li></ul></article>
      <article class="karte paket" data-reveal style="--verz:.16s"><h3>Wirtshaus-Menü</h3><span class="preis">ab 45 €</span><ul class="haken"><li>Drei Gänge, am Tisch serviert</li><li>Saisonal und frei kombinierbar</li><li>Weinbegleitung ab 24 €</li></ul></article>
      <article class="karte paket" data-reveal style="--verz:.24s"><h3>Schnucken-Party</h3><span class="preis">19 € pro Kind</span><ul class="haken"><li>Kuchen, Kindergericht und Limonade</li><li>Heide-Schatzsuche im Garten</li><li>Kleines Geschenk für jedes Kind</li></ul></article>
    </div>
  </div>
</section>

<section class="sektion sektion--sand" id="anfrage">
  <div class="wrap split">
    <div data-reveal>
      <p class="kicker">Unverbindlich anfragen</p>
      <h2>Erzähl uns von deiner Feier.</h2>
      <p class="lead">Wir melden uns innerhalb von 24 Stunden mit einem Vorschlag – persönlich, nicht per Formbrief.</p>
      <p>Lieber telefonieren? Unser Veranstaltungsteam erreichst du Di – Fr von 10 bis 17 Uhr unter <a href="tel:{TEL}">{TEL_ANZEIGE}</a>.</p>
    </div>
    <div class="formular-box" data-reveal style="--verz:.15s">
      <form class="formular" data-demo-formular="feier-ok" novalidate>
        <div class="feld"><label for="f-anlass">Anlass</label><select id="f-anlass" name="anlass" required><option value="">Bitte wählen</option><option>Geburtstag</option><option>Taufe / Kommunion / Konfirmation</option><option>Hochzeit</option><option>Trauerkaffee</option><option>Firmen- oder Weihnachtsfeier</option><option>Kindergeburtstag</option><option>Etwas anderes</option></select></div>
        <div class="feld"><label for="f-datum">Wunschdatum</label><input id="f-datum" name="datum" type="date" required></div>
        <div class="feld"><label for="f-gaeste">Anzahl Gäste</label><input id="f-gaeste" name="gaeste" type="number" min="8" max="120" inputmode="numeric" required></div>
        <div class="feld"><label for="f-paket">Interesse an</label><select id="f-paket" name="paket"><option>Noch offen</option><option>Kaffeetafel</option><option>Heide-Buffet</option><option>Wirtshaus-Menü</option><option>Schnucken-Party</option></select></div>
        <div class="feld"><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required></div>
        <div class="feld"><label for="f-tel">Telefon</label><input id="f-tel" name="telefon" type="tel" autocomplete="tel"></div>
        <div class="feld voll"><label for="f-mail">E-Mail</label><input id="f-mail" name="email" type="email" autocomplete="email" required></div>
        <div class="feld voll"><label for="f-text">Was sollten wir wissen?</label><textarea id="f-text" name="nachricht" placeholder="z. B. Uhrzeit, Kinder, Allergien, Wunschraum …"></textarea></div>
        <div class="voll"><button class="btn btn--gruen" type="submit">Anfrage senden</button><p class="demo-hinweis">Demo-Formular: Es werden keine Daten übertragen.</p></div>
      </form>
      <div class="bestaetigung" id="feier-ok" role="status">
        <img src="~/assets/logo/heidehof-zeichen-gruen.svg" alt="" width="120" height="52" style="margin:0 auto 20px">
        <h3>Danke, <span data-name>du</span>!</h3>
        <p>Deine Anfrage ist bei uns angekommen. Wir melden uns innerhalb von 24 Stunden mit einem Vorschlag.</p>
        <p class="demo-hinweis">(Demo – es wurde nichts übertragen.)</p>
      </div>
    </div>
  </div>
</section>

<section class="sektion">
  <div class="wrap wrap--schmal">
    <div class="sektion-kopf" data-reveal><p class="kicker">Häufige Fragen</p><h2>Rund um eure Feier</h2></div>
    {faq_html(faq_feiern)}
  </div>
</section>
"""
SEITEN.append({
    "pfad": "feiern/",
    "titel": "Feiern in Lüneburg – Familienfeier & Geburtstag | HEIDEHOF",
    "beschreibung": "Räume für 8 bis 80 Gäste in Lüneburg: Taufe, Konfirmation, Geburtstag, Hochzeit, Trauerkaffee & Firmenfeier. Regionale Buffets und Menüs im HEIDEHOF.",
    "preload": "freunde-lachen",
    "inhalt": feiern,
    "schema": [faq_schema(faq_feiern), brotkrumen_schema([("", "Start"), ("feiern/", "Feiern")])],
})

# ---------------------------------------------------------------- Ausflug
faq_ausflug = [
    ("Sind Hunde im HEIDEHOF willkommen?", "Ja! Gut erzogene Hunde sind drinnen und im Heidegarten willkommen. Wassernapf und ein Hundekeks gehen aufs Haus."),
    ("Kann ich mein E-Bike laden?", "Ja, an unseren vier Ladepunkten am überdachten Fahrradstand. Das Laden ist für Gäste kostenlos. Ein Werkzeug-Set und eine Luftpumpe liegen ebenfalls bereit."),
    ("Kommen auch größere Wander- und Radgruppen unter?", "Sehr gern. Ab 12 Personen bitten wir um kurze Anmeldung, damit wir genug Platz und etwas Schnelles vorbereiten können – auch für Busgruppen."),
    ("Gibt es Kaffee und Kuchen am Nachmittag?", "Ja, täglich außer montags. Unsere Heide-Buchweizentorte mit Preiselbeeren ist der Klassiker – am Wochenende ist sie oft bis 16 Uhr ausverkauft."),
    ("Wann blüht die Heide?", "Die Heideblüte ist meist von Anfang August bis Mitte September. In dieser Zeit gibt es bei uns zusätzlich Heideblüten-Specials – und es wird voll, also lieber reservieren."),
]
ausflug = seiten_hero(
    "abendlicht-feld", "Weite Landschaft im goldenen Abendlicht", "Ausflugslokal am Tor zur Heide",
    "Ausflugslokal in der Lüneburger Heide: Einkehr für Radler &amp; Wanderer",
    "Ob Radtour, Heidewanderung oder Stadtbummel durch Lüneburg: Bei uns gibt es eine Pause mit regionaler Küche, Kaffee und Kuchen im Heidegarten – Hunde inklusive.",
    [("", "Start"), ("ausflug/", "Ausflug")],
) + f"""
<section class="sektion papier">
  <div class="wrap">
    <div class="sektion-kopf" data-reveal><p class="kicker">Für Ausflügler</p><h2>Ankommen, durchatmen, satt werden.</h2><p class="lead">Der HEIDEHOF liegt am südlichen Stadtrand von Lüneburg – dort, wo die Stadt aufhört und die Heide anfängt.</p></div>
    <div class="karten">
      {karte("rad", "Rad-Service", "Überdachte Fahrradständer, vier E-Bike-Ladepunkte, Flickzeug und Luftpumpe. Trinkflaschen füllen wir kostenlos auf.", 0)}
      {karte("pfote", "Hunde willkommen", "Drinnen und draußen. Mit Wassernapf, Hundekeks und Verständnis für schlammige Pfoten.", 1)}
      {karte("torte", "Kaffee &amp; Kuchen", "Heide-Buchweizentorte, Apfelkuchen vom Blech und Kaffee von einer Lüneburger Rösterei.", 2)}
      {karte("tasche", "Heide-Rucksack zum Mitnehmen", "Proviant für unterwegs: belegte Brote, Obst, Kuchen und Limonade – morgens bestellen, mittags abholen.", 3)}
    </div>
  </div>
</section>

<section class="sektion sektion--gruen">
  <div class="wrap split">
    <div class="split-bild" data-reveal>{img("heidschnucke", "Schaf auf einer sonnigen Weide", "(max-width: 860px) 100vw, 50vw")}</div>
    <div data-reveal style="--verz:.15s">
      <p class="kicker">August &amp; September</p>
      <h2>Zur Heideblüte in den HEIDEHOF</h2>
      <p class="lead">Wenn die Lüneburger Heide violett leuchtet, kochen wir eine eigene kleine Heideblüten-Karte: mit Heidehonig, frischen Heidelbeeren und Heidschnucke vom Schäfer.</p>
      <p>Unser Tipp: früh am Tag in die Heide, mittags oder nachmittags bei uns einkehren und den Tag im Heidegarten ausklingen lassen.</p>
    </div>
  </div>
</section>

<section class="sektion">
  <div class="wrap">
    <div class="sektion-kopf" data-reveal><p class="kicker">Ausflugstipps</p><h2>Rund um Lüneburg</h2><p class="lead">Ein paar Ideen, die sich gut mit einem Besuch bei uns verbinden lassen.</p></div>
    <div class="karten">
      {karte("haus", "Lüneburger Altstadt", "Giebelhäuser, das alte Wasserviertel an der Ilmenau und die Spuren der Salzgeschichte – perfekt für einen Stadtbummel.", 0)}
      {karte("blatt", "Naturpark Lüneburger Heide", "Weite Heideflächen, Wacholderhaine und Heidschnuckenherden. Zur Heideblüte ein echtes Erlebnis.", 1)}
      {karte("rad", "Radtouren an der Ilmenau", "Flache Wege durch Wiesen und Wälder – ideal für Familien mit Kindern und E-Bike-Touren.", 2)}
    </div>
  </div>
</section>

<section class="sektion sektion--hell">
  <div class="wrap wrap--schmal">
    <div class="sektion-kopf" data-reveal><p class="kicker">Häufige Fragen</p><h2>Gut zu wissen für deine Tour</h2></div>
    {faq_html(faq_ausflug)}
  </div>
</section>
{cta("Pause eingeplant?", "Für Gruppen ab 12 Personen bitte kurz anmelden – alle anderen sind auch spontan herzlich willkommen.")}
"""
SEITEN.append({
    "pfad": "ausflug/",
    "titel": "Ausflugslokal Lüneburger Heide – Einkehr für Radler | HEIDEHOF",
    "beschreibung": "Einkehren in Lüneburg am Tor zur Heide: E-Bike-Ladestation, Hunde willkommen, Kaffee & Buchweizentorte im Heidegarten. Ideal für Radtour & Heideblüte.",
    "preload": "abendlicht-feld",
    "inhalt": ausflug,
    "schema": [faq_schema(faq_ausflug), brotkrumen_schema([("", "Start"), ("ausflug/", "Ausflug")])],
})

# ---------------------------------------------------------------- Mittagstisch
wochenkarte = [
    ("Dienstag", "Hähnchenbrust mit Rahmchampignons und Bandnudeln", "Linsen-Bolognese mit Bandnudeln"),
    ("Mittwoch", "Frikadellen vom Strohschwein, Kartoffelpüree, Rahmkohlrabi", "Kartoffelpuffer mit Apfelmus"),
    ("Donnerstag", "Lachsforelle mit Senfsoße und Salzkartoffeln", "Ofengemüse mit Kräuterquark"),
    ("Freitag", "Heidschnucken-Bratwurst, Bratkartoffeln, Krautsalat", "Graupen-Eintopf mit Wurzelgemüse"),
]
wk_html = "".join(
    f'<li class="speise"><div class="speise-kopf"><h3>{t}</h3><span class="punkte" aria-hidden="true"></span><span class="preis">12,90 €</span></div>'
    f'<p>{a}<br><em>Vegetarisch:</em> {v}</p></li>' for t, a, v in wochenkarte
)
faq_mittag = [
    ("Wann gibt es Mittagstisch?", "Dienstag bis Freitag von 11:30 bis 14:30 Uhr. Am Wochenende kochen wir à la carte."),
    ("Was kostet der Mittagstisch?", "Jedes Wochengericht kostet 12,90 € inklusive Tagessuppe oder kleinem Salat. Mit der Mittagskarte ist jedes elfte Essen gratis."),
    ("Kann ich vorbestellen oder mitnehmen?", "Ja. Ruf bis 11 Uhr an, dann steht dein Essen pünktlich auf dem Tisch – oder in der Mehrwegschale zum Mitnehmen."),
    ("Gibt es Angebote für Firmen?", "Für Teams ab fünf Personen reservieren wir gern feste Tische. Auf Wunsch stellen wir eine Sammelrechnung."),
]
mittag = seiten_hero(
    "kueche-handwerk", "Koch schneidet frisches Gemüse auf einem Brett", "Mittagstisch in Lüneburg",
    "Mittagstisch in Lüneburg: frisch gekocht, schnell serviert",
    "Dienstag bis Freitag von 11:30 bis 14:30 Uhr – mit wechselnder Wochenkarte, immer auch vegetarisch. Gut essen, ohne die Mittagspause zu sprengen.",
    [("", "Start"), ("mittagstisch/", "Mittagstisch")],
) + f"""
<section class="sektion papier">
  <div class="wrap split">
    <div data-reveal>
      <p class="kicker">Beispiel-Wochenkarte</p>
      <h2>Was diese Woche auf den Tisch kommt</h2>
      <ul class="speisen" style="grid-template-columns:1fr">{wk_html}</ul>
      <p class="karten-hinweis">Inklusive Tagessuppe oder kleinem Salat. Die Wochenkarte wechselt jeden Dienstag.</p>
    </div>
    <div data-reveal style="--verz:.15s">
      <div class="karten" style="grid-template-columns:1fr">
        {karte("uhr", "In 45 Minuten zurück im Büro", "Wir wissen, dass deine Mittagspause nicht ewig ist. Sag uns Bescheid, dann geht es besonders flott.", 0)}
        {karte("stern", "Mittagskarte: das 11. Essen gratis", "Stempeln lassen, sammeln, genießen. Gilt auch fürs Mitnehmen.", 1)}
        {karte("tasche", "Vorbestellen &amp; mitnehmen", "Bis 11 Uhr anrufen, Essen abholen – in Mehrwegschalen, die du beim nächsten Mal wieder mitbringst.", 2)}
      </div>
    </div>
  </div>
</section>

<section class="sektion sektion--hell">
  <div class="wrap wrap--schmal">
    <div class="sektion-kopf" data-reveal><p class="kicker">Häufige Fragen</p><h2>Rund um den Mittagstisch</h2></div>
    {faq_html(faq_mittag)}
  </div>
</section>
{cta("Mittag gesichert?", "Für Gruppen ab fünf Personen reservieren wir gerne feste Tische. Ansonsten: einfach vorbeikommen.")}
"""
SEITEN.append({
    "pfad": "mittagstisch/",
    "titel": "Mittagstisch Lüneburg – Di bis Fr ab 12,90 € | HEIDEHOF",
    "beschreibung": "Mittagessen in Lüneburg: wechselnde Wochenkarte mit regionalen Gerichten, immer auch vegetarisch, ab 12,90 € inkl. Suppe. Di–Fr 11:30–14:30 Uhr, auch zum Mitnehmen.",
    "preload": "kueche-handwerk",
    "inhalt": mittag,
    "schema": [faq_schema(faq_mittag), brotkrumen_schema([("", "Start"), ("mittagstisch/", "Mittagstisch")])],
})

# ---------------------------------------------------------------- Regionale Küche
regional = seiten_hero(
    "gemuese-brett", "Frisches Gemüse auf einem Holzbrett", "Unsere Küche",
    "Regionale Küche aus der Lüneburger Heide",
    "Heidschnucke, Heidespargel, Buchweizen und Heidehonig: Wir kochen mit dem, was in der Region wächst – und mit Menschen, die wir persönlich kennen.",
    [("", "Start"), ("regionale-kueche/", "Unsere Küche")],
) + f"""
<section class="sektion papier" id="heidschnucke">
  <div class="wrap split">
    <div class="split-bild" data-reveal>{img("heidschnucke", "Schaf auf einer sonnigen Weide", "(max-width: 860px) 100vw, 50vw")}{zweig('zweig-deko')}</div>
    <div data-reveal style="--verz:.15s">
      <p class="kicker">Das Wappentier der Heide</p>
      <h2>Die Lüneburger Heidschnucke</h2>
      <p class="lead">Ohne Heidschnucken gäbe es die Lüneburger Heide nicht, wie wir sie kennen. Die genügsamen Schafe halten die Heideflächen frei und sorgen dafür, dass das Heidekraut jedes Jahr neu blühen kann.</p>
      <p>Ihr Fleisch ist fein, mager und hat ein leicht wildartiges Aroma – kein Wunder bei einem Leben unter freiem Himmel. Die „Lüneburger Heidschnucke“ ist in der EU als geschützte Ursprungsbezeichnung eingetragen.</p>
      <p>Unser Schäfer betreut seine Herde keine 30 Kilometer von unserer Küche entfernt. Daraus wird bei uns die geschmorte Keule, der Burger und die Bratwurst für den Mittagstisch.</p>
      <a class="pfeil-link" href="~/speisekarte/#hauptgerichte">Zu den Gerichten</a>
    </div>
  </div>
</section>

<section class="sektion sektion--gruen">
  <div class="wrap">
    <div class="sektion-kopf" data-reveal><p class="kicker">Unsere Erzeuger</p><h2>Wir wissen, wo es herkommt.</h2><p class="lead">Die meisten unserer Zutaten reisen weniger als 50 Kilometer. Ein paar der Menschen, mit denen wir zusammenarbeiten:</p></div>
    <div class="karten">
      {karte("blatt", "Die Schäferei", "Heidschnucken aus Landschaftspflege – das Fleisch kommt als ganzes Tier, wir verarbeiten alles.", 0)}
      {karte("sonne", "Der Gemüsehof", "Kartoffeln, Heidespargel, Kohl und Kürbis, im Sandboden der Heide gewachsen.", 1)}
      {karte("herz", "Die Imkerei", "Heidehonig, der nur in wenigen Wochen im Spätsommer entsteht – kräftig, würzig, unverwechselbar.", 2)}
      {karte("topf", "Die Teichwirtschaft", "Forellen und Lachsforellen aus klarem Quellwasser, frisch geräuchert oder für die Pfanne.", 3)}
    </div>
  </div>
</section>

<section class="sektion">
  <div class="wrap">
    <div class="sektion-kopf" data-reveal><p class="kicker">Saisonkalender</p><h2>Die Heide hat vier Speisekarten.</h2></div>
    <div class="saison" data-reveal>
      <div><h3>Frühling</h3><p>Heidespargel, Bärlauch, junger Spinat, Rhabarber, erste Erdbeeren.</p></div>
      <div><h3>Sommer</h3><p>Heidelbeeren, Matjes, Pfifferlinge, Gurken, Heidehonig zur Heideblüte.</p></div>
      <div><h3>Herbst</h3><p>Heidschnucke, Wild aus heimischer Jagd, Kürbis, Pilze, Äpfel.</p></div>
      <div><h3>Winter</h3><p>Grünkohl, Rotkohl, Ente, Schmorgerichte, Buchweizentorte am Kamin.</p></div>
    </div>
  </div>
</section>

<section class="sektion sektion--hell">
  <div class="wrap split split--umgekehrt">
    <div class="split-bild split-bild--quer" data-reveal>{img("kartoffeln", "Frische Kartoffeln aus der Region", "(max-width: 860px) 100vw, 50vw")}</div>
    <div data-reveal style="--verz:.15s">
      <p class="kicker">Handwerk statt Packung</p>
      <h2>Fast alles selbst gemacht</h2>
      <ul class="haken">
        <li>Brühen, Fonds und Soßen kochen wir jeden Tag frisch</li>
        <li>Rotkohl, Gurken und Preiselbeeren legen wir selbst ein</li>
        <li>Torten und Kuchen backen wir im eigenen Ofen</li>
        <li>Limonaden aus Holunder und Rhabarber setzen wir selbst an</li>
        <li>Nose to tail: Vom Tier verwenden wir alles</li>
      </ul>
    </div>
  </div>
</section>
{cta("Probier die Heide.", "Am besten bei der geschmorten Heidschnuckenkeule – oder einem Stück Buchweizentorte.", hell=True)}
"""
SEITEN.append({
    "pfad": "regionale-kueche/",
    "titel": "Regionale Küche Lüneburger Heide – Heidschnucke | HEIDEHOF",
    "beschreibung": "Heidschnucke, Heidespargel, Buchweizen & Heidehonig: Im HEIDEHOF Lüneburg kochen wir regional, saisonal und mit Erzeugern aus maximal 50 km Umkreis.",
    "preload": "gemuese-brett",
    "inhalt": regional,
    "schema": [brotkrumen_schema([("", "Start"), ("regionale-kueche/", "Unsere Küche")])],
})

# ---------------------------------------------------------------- Reservieren
faq_res = [
    ("Ab wie vielen Personen gilt eine Reservierung als Gruppe?", "Ab 10 Personen planen wir gemeinsam mit dir. Schau dafür am besten auf unserer Seite für Feiern und Gruppen vorbei."),
    ("Kann ich kurzfristig einen Tisch bekommen?", "Unter der Woche fast immer. Am Wochenende ruf am besten kurz an – wir finden oft noch eine Lösung."),
    ("Was ist, wenn wir doch nicht kommen können?", "Kein Problem, sag uns einfach so früh wie möglich Bescheid. Dann freut sich eine andere Familie über den Tisch."),
]
reservieren = f"""
<div class="seiten-kopf papier">
  <div class="wrap">
    {brotkrumen([("", "Start"), ("reservieren/", "Reservieren")])}
    <p class="kicker">Tisch reservieren</p>
    <h1>Tisch reservieren im HEIDEHOF Lüneburg</h1>
    <p class="lead" style="max-width:720px">In einer Minute erledigt. Wir bestätigen deine Reservierung so schnell wie möglich – und halten den Hochstuhl schon bereit, wenn du einen brauchst.</p>
  </div>
</div>
<section class="sektion papier" style="padding-top:24px">
  <div class="wrap split" style="align-items:start">
    <div class="formular-box" data-reveal>
      <form class="formular" data-demo-formular="res-ok" novalidate>
        <div class="feld"><label for="r-datum">Datum</label><input id="r-datum" name="datum" type="date" required><p class="hilfe">Montags ist Ruhetag.</p></div>
        <div class="feld"><label for="r-zeit">Uhrzeit</label><select id="r-zeit" name="zeit" required><option value="">Bitte wählen</option><option>09:30 (nur sonntags)</option><option>10:30 (nur sonntags)</option><option>11:30</option><option>12:00</option><option>12:30</option><option>13:00</option><option>13:30</option><option>17:00</option><option>17:30</option><option>18:00</option><option>18:30</option><option>19:00</option><option>19:30</option><option>20:00</option><option>20:30</option></select></div>
        <div class="feld"><label for="r-erw">Erwachsene</label><input id="r-erw" name="erwachsene" type="number" min="1" max="9" value="2" inputmode="numeric" required></div>
        <div class="feld"><label for="r-kinder">Kinder</label><input id="r-kinder" name="kinder" type="number" min="0" max="9" value="0" inputmode="numeric"></div>
        <div class="feld voll"><label for="r-wunsch">Wünsche</label><select id="r-wunsch" name="wunsch"><option>Keine besonderen Wünsche</option><option>Hochstuhl benötigt</option><option>Platz nahe der Spielecke</option><option>Ruhiger Tisch</option><option>Im Heidegarten (bei gutem Wetter)</option><option>Barrierefreier Platz</option><option>Wir haben einen Hund dabei</option></select></div>
        <div class="feld"><label for="r-name">Name</label><input id="r-name" name="name" autocomplete="name" required></div>
        <div class="feld"><label for="r-tel">Telefon</label><input id="r-tel" name="telefon" type="tel" autocomplete="tel" required></div>
        <div class="feld voll"><label for="r-mail">E-Mail</label><input id="r-mail" name="email" type="email" autocomplete="email" required></div>
        <div class="feld voll"><label for="r-text">Nachricht (optional)</label><textarea id="r-text" name="nachricht" placeholder="Allergien, Anlass, Geburtstagskind …"></textarea></div>
        <label class="check voll"><input type="checkbox" required> <span>Ich bin einverstanden, dass meine Angaben zur Bearbeitung der Reservierung verwendet werden. Mehr in der <a href="~/datenschutz/">Datenschutzerklärung</a>.</span></label>
        <div class="voll"><button class="btn btn--gruen" type="submit">Verbindlich reservieren</button><p class="demo-hinweis">Demo-Formular: Es werden keine Daten übertragen.</p></div>
      </form>
      <div class="bestaetigung" id="res-ok" role="status">
        <img src="~/assets/logo/heidehof-zeichen-gruen.svg" alt="" width="120" height="52" style="margin:0 auto 20px">
        <h2>Danke, <span data-name>du</span>!</h2>
        <p class="lead">Wir freuen uns auf euch. Eine Bestätigung kommt gleich per E-Mail.</p>
        <p class="demo-hinweis">(Demo – es wurde keine Reservierung übermittelt.)</p>
      </div>
    </div>
    <div data-reveal style="--verz:.15s">
      <h2 style="font-size:1.6rem">Lieber persönlich?</h2>
      <p>Ruf uns an unter <a href="tel:{TEL}"><strong>{TEL_ANZEIGE}</strong></a> – während der Öffnungszeiten sind wir für dich da.</p>
      <h3 style="margin-top:2em">Öffnungszeiten</h3>
      {zeiten_tabelle()}
      <h3 style="margin-top:2em">Adresse</h3>
      {adresse_html()}
      <p style="margin-top:1.4em"><a class="karte-link" href="{OSM}" target="_blank" rel="noopener">{KARTE_SVG}<span>Route planen ↗</span></a></p>
      <p><small>40 kostenlose Parkplätze direkt am Haus · Bushaltestelle in 3 Gehminuten · Stufenloser Eingang</small></p>
    </div>
  </div>
</section>
<section class="sektion sektion--hell">
  <div class="wrap wrap--schmal">
    <div class="sektion-kopf" data-reveal><p class="kicker">Häufige Fragen</p><h2>Rund um die Reservierung</h2></div>
    {faq_html(faq_res)}
  </div>
</section>
"""
SEITEN.append({
    "pfad": "reservieren/",
    "titel": "Tisch reservieren – HEIDEHOF Lüneburg",
    "beschreibung": "Reserviere deinen Tisch im HEIDEHOF Lüneburg online oder telefonisch. Öffnungszeiten, Anfahrt und Parken – Familienwirtshaus mit regionaler Küche.",
    "hero": False,
    "inhalt": reservieren,
    "schema": [faq_schema(faq_res), brotkrumen_schema([("", "Start"), ("reservieren/", "Reservieren")])],
})

# ---------------------------------------------------------------- Englisch
en = f"""
<header class="seiten-hero">
  <div class="hero-bild">{img("gemeinsam-am-tisch", "Friends and family sharing a meal at a long table", "100vw", eager=True)}</div>
  <div class="wrap">
    <p class="kicker">Lüneburg · Lüneburg Heath</p>
    <h1>HEIDEHOF – a family restaurant with regional food in Lüneburg</h1>
    <p class="lead">Good food. Together. Modern North German cooking with produce from the Lüneburg Heath, a warm welcome for all generations, and a play corner for the little ones.</p>
    <div class="btn-reihe"><a class="btn btn--creme" href="tel:{TEL}">Call to book: {TEL_ANZEIGE}</a><a class="btn btn--linie" href="~/speisekarte/" hreflang="de">Menu (German)</a></div>
  </div>
</header>
<section class="sektion papier">
  <div class="wrap">
    <div class="karten">
      {karte("blatt", "Regional &amp; seasonal", "Try our signature dish: slow-braised Heidschnucke lamb – the heath sheep that has shaped this landscape for centuries. Vegetarian and vegan dishes are always on the menu.", 0)}
      {karte("kind", "Family friendly", "Play corner, playground in the garden, kids’ menu, high chairs and baby-changing room. Children are welcome to be children here.", 1)}
      {karte("rad", "Perfect stop on your trip", "Free parking, e-bike charging, dogs welcome and a beer garden. Ideal after exploring Lüneburg’s old town or the heath in bloom (August–September).", 2)}
    </div>
  </div>
</section>
<section class="sektion sektion--gruen">
  <div class="wrap info-raster">
    <div><h3>Opening hours</h3><table class="zeiten"><tr data-tage="1"><th scope="row">Monday</th><td>Closed</td></tr><tr data-tage="2,3,4,5"><th scope="row">Tue – Fri</th><td>11:30 am – 2:30 pm<br>5 pm – 10 pm</td></tr><tr data-tage="6"><th scope="row">Saturday</th><td>11:30 am – 10:30 pm</td></tr><tr data-tage="0"><th scope="row">Sunday</th><td>9:30 am – 9 pm<br><small>Breakfast buffet until noon</small></td></tr></table></div>
    <div><h3>Address</h3>{adresse_html()}</div>
    <div><h3>Find us</h3><a class="karte-link" href="{OSM}" target="_blank" rel="noopener">{KARTE_SVG}<span>Plan your route ↗</span></a></div>
  </div>
</section>
"""
SEITEN.append({
    "pfad": "en/",
    "lang": "en",
    "titel": "HEIDEHOF Lüneburg – Family Restaurant & Regional Food",
    "beschreibung": "Family-friendly restaurant in Lüneburg, Germany: regional North German food from the Lüneburg Heath, kids’ play area, beer garden, dogs welcome. Call to book a table.",
    "preload": "gemeinsam-am-tisch",
    "inhalt": en,
    "schema": [restaurant_schema()],
})

# ---------------------------------------------------------------- Rechtliches
impressum = f"""
<div class="seiten-kopf papier"><div class="wrap wrap--schmal rechtstext">
{brotkrumen([("", "Start"), ("impressum/", "Impressum")])}
<h1>Impressum</h1>
<p class="lead"><strong>Hinweis:</strong> Dies ist eine Demo-Website. Der HEIDEHOF ist ein fiktives Restaurant, das im Rahmen eines Workshops entstanden ist. Alle Namen, Adressen, Preise und Angaben sind frei erfunden.</p>
<h2>Angaben gemäß § 5 DDG</h2>
<p>HEIDEHOF – Das Familienwirtshaus (fiktiv)<br>{STRASSE}<br>{PLZ} {ORT}</p>
<h2>Kontakt</h2>
<p>Telefon: {TEL_ANZEIGE} (Platzhalter)<br>E-Mail: {MAIL} (Platzhalter)</p>
<h2>Bildnachweise</h2>
<p>Fotos: Unsplash (unsplash.com, Unsplash-Lizenz). Logo und Markenmotive: HEIDEHOF-Konzept aus dem Workshop.</p>
</div></div>
"""
SEITEN.append({"pfad": "impressum/", "titel": "Impressum | HEIDEHOF Lüneburg", "beschreibung": "Impressum der Demo-Website HEIDEHOF – Das Familienwirtshaus.",
               "hero": False, "noindex": True, "inhalt": impressum})

datenschutz = f"""
<div class="seiten-kopf papier"><div class="wrap wrap--schmal rechtstext">
{brotkrumen([("", "Start"), ("datenschutz/", "Datenschutz")])}
<h1>Datenschutz</h1>
<p class="lead">Kurz und ehrlich: Diese Demo-Website setzt keine Cookies, nutzt kein Tracking und lädt keine Schriften oder Karten von fremden Servern.</p>
<h2>Hosting</h2>
<p>Die Website wird über GitHub Pages (GitHub Inc.) ausgeliefert. Beim Aufruf verarbeitet GitHub technisch notwendige Daten wie die IP-Adresse in Server-Logfiles. Details findest du in der Datenschutzerklärung von GitHub.</p>
<h2>Formulare</h2>
<p>Die Reservierungs- und Anfrageformulare sind Demo-Formulare. Eingaben verlassen deinen Browser nicht und werden nirgendwo gespeichert.</p>
<h2>Externe Links</h2>
<p>Der Link „Route planen“ führt zu OpenStreetMap. Erst beim Klick werden Daten an den Anbieter übertragen.</p>
</div></div>
"""
SEITEN.append({"pfad": "datenschutz/", "titel": "Datenschutz | HEIDEHOF Lüneburg", "beschreibung": "Datenschutzhinweise der Demo-Website HEIDEHOF – Das Familienwirtshaus.",
               "hero": False, "noindex": True, "inhalt": datenschutz})

fehler = f"""
<div class="seiten-kopf papier" style="min-height:70vh"><div class="wrap wrap--schmal zentriert">
<img src="~/assets/logo/heidehof-zeichen-gruen.svg" alt="" width="220" height="95" style="margin:0 auto 28px;width:220px">
<p class="kicker">Fehler 404</p>
<h1>Hier ist nur Heide.</h1>
<p class="lead">Diese Seite gibt es leider nicht – vielleicht ist sie mit der Herde weitergezogen.</p>
<div class="btn-reihe"><a class="btn btn--gruen" href="~/">Zur Startseite</a><a class="btn btn--linie" href="~/speisekarte/">Zur Speisekarte</a></div>
</div></div>
"""
SEITEN.append({"pfad": "404", "datei": "404.html", "R": "/website-demo/", "titel": "Seite nicht gefunden | HEIDEHOF", "beschreibung": "Diese Seite gibt es nicht.",
               "hero": False, "noindex": True, "inhalt": fehler})


# ---------------------------------------------------------------- Ausgabe
def main():
    for s in SEITEN:
        print("✓", os.path.relpath(seite_rendern(s), ROOT))
    urls = [s for s in SEITEN if not s.get("noindex")]
    prio = {"": "1.0", "speisekarte/": "0.9", "reservieren/": "0.8"}
    eintraege = "".join(
        f"<url><loc>{BASE}{s['pfad']}</loc><lastmod>{HEUTE}</lastmod><priority>{prio.get(s['pfad'], '0.7')}</priority></url>\n"
        for s in urls
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{eintraege}</urlset>\n')
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"# Gilt erst, wenn die Seite unter einer eigenen Domain im Wurzelverzeichnis liegt.\nUser-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n")
    print("✓ sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
