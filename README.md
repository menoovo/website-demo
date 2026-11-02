# HEIDEHOF – Das Familienwirtshaus (Demo-Website)

Live: https://menoovo.github.io/website-demo/

Statische Website für ein fiktives Familienwirtshaus in Lüneburg, erstellt für einen Workshop.
Keine Frameworks, keine Cookies, keine externen Ressourcen.

## Seiten & Zielgruppen (SEO)

| Seite | Zielgruppe / Suchintention |
|---|---|
| `/` | Restaurant Lüneburg, Familienwirtshaus, regionale Küche |
| `/speisekarte/` | Speisekarte, Heidschnucke, vegetarisch, Kinderkarte, Sonntagsfrühstück |
| `/familien/` | Kinderfreundliches Restaurant Lüneburg, Essen gehen mit Kindern |
| `/feiern/` | Familienfeier, Geburtstag, Taufe, Trauerkaffee, Firmenfeier Lüneburg |
| `/ausflug/` | Ausflugslokal Lüneburger Heide, Radler, Wanderer, Hunde, Heideblüte |
| `/mittagstisch/` | Mittagstisch / Mittagessen Lüneburg |
| `/regionale-kueche/` | Regionale Küche, Heidschnucke, Erzeuger, Saison |
| `/reservieren/` | Tisch reservieren, Öffnungszeiten, Anfahrt |
| `/en/` | Englischsprachige Gäste / Touristen |

Technik: eigene Title/Description je Seite, Canonical, hreflang (de/en), Open Graph,
JSON-LD (`Restaurant`, `Menu`, `FAQPage`, `BreadcrumbList`), `sitemap.xml`,
responsive WebP-Bilder mit `srcset`, selbst gehostete Schriften.

## Ändern & neu bauen

Inhalte, Speisekarte und Öffnungszeiten stehen in `build.py`. Danach:

```bash
python3 build.py
```

Design: `assets/css/style.css` · Interaktionen: `assets/js/main.js`
