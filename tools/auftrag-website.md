# Auftrag: auszeit.nxtchange.app modernisieren (Stand 28.10.2026)

Für den umsetzenden Agenten (Opus) im Repo `/Users/karlmaier/Claude/auszeit-legal`. Dieser Ordner `tools/` ist in
`_config.yml` von Jekyll ausgeschlossen, deshalb liegt der Auftrag hier und nicht im Wurzelordner (Jekyll rendert jede
`.md` im Wurzelordner als Seite).

## Ziel

Die Website ist die Landeseite jeder Presseerwähnung und der erste Blick eines Journalisten. Sie soll

1. beide Plattformen zeigen (iPhone und Android, Google Play ist seit Oktober 2026 live),
2. hell und modern aussehen, in der CI der aktuellen App-Store-Bilder („abend-hell“, siehe unten),
3. die Videos vom YouTube-Kanal „nxtChange Apps“ nutzen, ohne dass beim Seitenaufruf Daten an Google gehen,
4. technisch sauber sein (Canonical, hreflang, og:image, JSON-LD, robots, sitemap, llms.txt, 404-Seite, FAQ),
5. einen aktuellen Presse-Abschnitt mit allen Bildern haben,
6. ohne Tracking, ohne externe Schriften, ohne externe Skripte auskommen. Die Botschaft der App ist „kein Konto,
   keine Daten“, die Website muss das einlösen.

Fertig heißt: Generator läuft, `index.html` und `en/index.html` sind neu erzeugt, Vorschau liegt unter `preview/`,
alle Prüfungen aus dem Abschnitt „Abnahme“ sind grün, Bericht am Ende. **Nichts committen, nichts pushen.** Karl
sieht sich die Vorschau an und entscheidet. Keine Platzhalter wie „[Zitat folgt]“ im HTML: was fehlt, kommt in den
Bericht, nicht auf die Seite.

## Repo und Aufbau

- GitHub Pages mit Jekyll, Theme `jekyll-theme-primer`, `CNAME` auszeit.nxtchange.app, Branch `main`.
- Startseite `index.html` und `en/index.html` erzeugt `tools/build_site.py` aus dem `TEXT`-Dict, CSS liegt dort
  inline. Aufruf im Repo-Wurzelordner: `python3 -I tools/build_site.py .`; Vorschau mit eingebetteten Bildern:
  `python3 -I tools/build_site.py . --inline` schreibt nach `preview/` (nicht committen). **Änderungen nur im
  Generator, nie im erzeugten HTML.**
- Rechtstexte sind Markdown mit Front Matter (`title`, `permalink`): `datenschutz.md`, `privacy.md`,
  `nutzungsbedingungen.md`, `terms.md`, `support.md` (zweisprachig in einer Datei, englischer Teil unter dem
  Anker `#support-for-off-hours`). Layout `_layouts/default.html` (nutzt `{% seo %}` von jekyll-seo-tag und die
  Primer-CSS unter `/assets/css/style.css`).
- Jekyll ist lokal vermutlich nicht installiert (`bundle`, `jekyll` prüfen). Wenn nicht: nichts installieren. Die
  Startseite lässt sich ohne Jekyll prüfen (`python3 -m http.server` im Repo). Das Layout der Markdown-Seiten dann
  so ändern, dass es ohne lokalen Test sicher ist: Liquid-Syntax beibehalten, nur CSS-Datei und Kopf- und Fußzeile
  ergänzen.
- Python nur mit Standardbibliothek, wie `build_site.py`. Bilder dürfen mit Swift und AppKit erzeugt werden, so
  machen es die Store-Skripte (`swift datei.swift …`), oder mit `sips`.
- Quellen für Texte: `../auszeit/store/appstore-de.md` und `appstore-en.md` (iPhone), `../auszeit-android/store/play-de.md`
  und `play-en.md` (Android), `../auszeit-android/store/upload/formulare.md` (Erklärung der Bedienungshilfe). Nichts
  erfinden: Funktionen, Zahlen und Formulierungen aus diesen Dateien übernehmen.

## Befund (28.10.2026, live geprüft)

- Nur ein App-Store-Link, kein Google-Play-Link; „iPhone“ neunmal, „Android“ nie. Kicker „iPhone-App“.
- `robots.txt`, `sitemap.xml`, `llms.txt`: 404. Keine 404-Seite im CI.
- Kein `<link rel="canonical">`, hreflang relativ (`./`, `./en/`), kein x-default.
- `og:image` ist das App-Icon mit relativem Pfad (`./assets/press/auszeit-icon-1024.png`), damit ohne Bild in
  Teasern. Kein `og:url`, kein `twitter:card`.
- Kein JSON-LD. Meta-Beschreibungen der Unterseiten sind kopiert.
- Startseite ist dunkel mit Goldakzent (die alte CI), die Store-Bilder sind seit 20.10.2026 hell.
- Bilder unter `assets/img/de|en` und `assets/press` sind die dunklen Store-Bilder vom 8.10.2026 (drei je Sprache).
- Presse-Abschnitt veraltet: „Plattform iPhone“, „Version 1.0, 8. Oktober 2026“, „38 europäische Länder“.
  Richtig: iPhone (iOS 17 oder neuer) und Android (8.0 oder neuer), 37 Länder im App Store und 36 bei Google Play,
  Versionsnummer weglassen (veraltet sofort). Play-Eintrag heißt „Auszeit: App Blocker & Fokus“.
- Die Fußzeile nennt Anbieter, Adresse, FN 648962g, Landesgericht für ZRS Graz, UID ATU81922038, E-Mail, Apple-Markenhinweis.
- nxtchange.app (das App-Register) zeigt für Auszeit bereits „Im App Store und bei Google Play“. Dort nichts ändern.

## Gestaltung: die helle CI der Store-Bilder

Vorbild ansehen: `~/Documents/Auszeit App-Store-Bilder 2026-10-20/abend-hell/6.9-Zoll/de/1-schirm.png` bis
`6-privat.png` (und `en/`). Quelle der Werte: `../auszeit/store/screenshots.swift`, Theme „abend-hell“.

| Rolle | Wert |
| --- | --- |
| Text | `#1A1614` |
| Akzent (Gold-Braun, zweite Überschriftzeile, Etikett) | `#804A12` |
| Gedämpft (Unterzeilen) | `#504036` |
| Grund, Verlauf von links oben nach rechts unten | `#FAF3E6` → `#F7DBA8` → `#EEAC7A` |
| Warmer Schein hinter Geräten | `#FFECC8` (35 %) |
| Abendlicht, weich, radial | `#FFF6DE` |
| Geräterahmen | `#181A20`, 14 px, Schatten schwarz 34 %, Blur 70 |
| Pille (Fußnote „Kein Konto · Keine Daten · Keine Werbung“) | Fläche `#1A1614`, Schrift `#FAF0DE` |
| Helles Gold (Pfeil, Akzente auf dunklem Grund) | `#E2C692` |

Dunkelmodus (`prefers-color-scheme: dark`, dazu `data-theme`-Attribut wie bisher) nach Theme „abend-dunkel“:
Text `#F8F5EE`, Akzent `#E2C692`, gedämpft `#BEC2D2`, Verlauf `#101424` → `#202848` → `#462C42`, Schein `#D6BA80` (22 %),
Rahmen `#E2C692` 60 %, 5 px. Hell ist die Hauptfassung, dunkel folgt nur der Systemeinstellung.

Typografie wie auf den Bildern: Etikett in Versalien mit Sperrung, Serifen-Überschrift (`"New York", "Iowan Old Style",
Georgia, serif`, Gewicht 600, enger Zeilenabstand), zweite Zeile im Akzent, Unterzeile in der Systemschrift, gedämpft.
Fließtext Systemschrift (`-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif`). Keine
Webfonts.

Kontrast: `#804A12` auf `#FAF3E6` ist etwa 6,5:1, auf dem Orange-Ende `#EEAC7A` nur etwa 3,7:1. Auf dem dunkleren Teil
des Verlaufs deshalb nur große Überschriften oder Text in `#1A1614`. Mindestens 4,5:1 für Fließtext prüfen.

Modern heißt hier: viel Luft, ein Verlaufsband hinter dem Hero wie der „Abendverlauf“ der Bilder, große Serifen-
Überschrift, Geräte mit dunklem Rahmen und Schatten, Karten oder Listen für „So funktioniert es“, FAQ als
`<details>`, horizontale Galerie der sechs Store-Bilder mit `scroll-snap`, ruhige Übergänge, `prefers-reduced-motion`
beachten. Keine Frameworks, kein JavaScript außer dem Nachladen der Videos. Phone-Breite mit 16 px Rand, kein
horizontales Scrollen der Seite.

Gemeinsames CSS: in `assets/css/site.css` auslagern und vom Generator und vom Jekyll-Layout einbinden, damit die
Rechtstexte dieselbe Kopf- und Fußzeile und dieselben Farben bekommen. Primer-CSS im Layout kann bleiben, wenn die
eigene Datei danach lädt und die Typografie übernimmt; sonst Primer weglassen.

## Inhalte

Bestehende Texte sind wortgleich mit den Store-Texten, das bleibt so. Änderungen:

- Namen: App-Store-Name „Auszeit: App Blocker & Fokus“ und „Off Hours: App Blocker & Focus“ (eine Konstante im
  Generator, der Name wird in 1.0.5 wahrscheinlich geändert).
- H1 bleibt: „Abends das Handy weglegen, ohne Kampf mit der Willenskraft.“ / „Put the phone down in the evening,
  without a fight with your willpower.“ Kicker neu: „App-Blocker für iPhone und Android“ / „App blocker for iPhone
  and Android“.
- Lead: „dein iPhone“ wird „dein Handy“, wo es um beide Plattformen geht. Plattformunterschied einmal sauber
  erklären: auf dem iPhone nutzt Auszeit die Bildschirmzeit, auf Android die Bedienungshilfe (einmal einschalten).
  Wortlaut aus `play-de.md` „So funktioniert es“ und `formulare.md`.
- Abschnittsüberschriften aus den sechs Store-Bildern übernehmen (Etikett + zwei Zeilen, Gold auf der zweiten):
  „App-Blocker mit Bedenkzeit · Instagram? Erst 15 Sekunden.“, „Automatisch zu festen Zeiten · Zu deinen Zeiten. Ganz
  von selbst.“, „Entscheidung · Deine Entscheidung. Jedes Mal.“, „Einstellung · So streng, wie du willst.“, „Apps · Nur
  die Apps, die du wählst.“, „Privatsphäre · Kein Konto. Keine Daten. Keine Werbung.“ Englisch in `screenshots.swift`.
- Store-Knöpfe nebeneinander: App-Store-Abzeichen (vorhanden, `assets/img/badge-de.svg`, `badge-en.svg`) und
  Google-Play-Abzeichen, offiziell und unverändert, von
  `https://play.google.com/intl/de_de/badges/static/images/badges/de_badge_web_generic.png` und
  `https://play.google.com/intl/en_gb/badges/static/images/badges/en_badge_web_generic.png` (einmal herunterladen
  nach `assets/img/`, Höhe an das Apple-Abzeichen angleichen, nur per CSS skalieren). Fußzeile ergänzen: „Google Play
  und das Google Play-Logo sind Marken von Google LLC.“ / „Google Play and the Google Play logo are trademarks of
  Google LLC.“ Klappt der Download nicht: Textlink und Hinweis im Bericht.
- Store-Links mit Kampagnenkennung, ohne Tracking auf der Seite:
  - Apple: `https://apps.apple.com/de/app/apple-store/id6817406940?pt=129507889&ct=website&mt=8` (englische Seite wie
    bisher mit dem Land aus dem Generator). `pt` ist die Anbieter-ID aus App Store Connect › App Analytics ›
    Kampagnen; 129507889 ist die Content-Provider-ID des Kontos und sehr wahrscheinlich richtig, Karl prüft das.
  - Google Play: `https://play.google.com/store/apps/details?id=at.nxtchange.auszeit&referrer=utm_source%3Dauszeit.nxtchange.app%26utm_medium%3Dwebsite%26utm_campaign%3Dbadge`
- Preise sichtbar: „Gratis. Auszeit Plus 9,99 € im Jahr oder 3,99 € im Monat (Preis in Österreich, Apple und Google
  rechnen je Land um, der genaue Preis steht in der App).“ Englisch entsprechend („Austrian price“).
- FAQ, sichtbar und als FAQPage-JSON-LD, Deutsch und Englisch, Antworten aus den Store-Texten:
  1. Ist Auszeit dasselbe wie die „Auszeit“ in Apples Bildschirmzeit? (Nein. Apples Funktion sperrt Apps zu festen
     Zeiten. Die App Auszeit nutzt Bildschirmzeit als Grundlage und setzt eine Bedenkzeit mit Entscheidung davor,
     statt eines Verbots.)
  2. Funktioniert Auszeit nur abends? (Nein, jedes Zeitfenster, jede Tagesauswahl, mit Plus mehrere Auszeiten.)
  3. Was braucht Auszeit auf Android, und warum die Bedienungshilfe? (Wortlaut aus `formulare.md`, dazu das
     Demo-Video, siehe Videos.)
  4. Sieht Auszeit, welche Apps ich nutze? (Privatsphäre-Text.)
  5. Kann ich die Sperre umgehen? (Ehrlich: ja, jede Auszeit lässt sich ausschalten. Hilfsmittel, kein Schutz vor
     dir selbst.)
  6. Was kostet Auszeit? (Gratis-Umfang und Plus-Preise.)
  7. Pausiert Auszeit auch Webseiten? (Nein, nur Apps.)
  8. Welche Geräte? (iPhone mit iOS 17 oder neuer, Android-Handys ab 8.0. Nichts über iPad oder Tablets behaupten.)
- Presse-Abschnitt (eigene Seite `/presse/` und `/en/press/` mit Anker von der Startseite, oder weiter als
  Abschnitt, Entscheidung nach Umfang): Kurztext mit „App für iPhone und Android aus Graz“; Eckdaten Plattformen,
  „Veröffentlicht Oktober 2026“, Länder 37 (App Store) und 36 (Google Play), Sprachen Deutsch und Englisch, Preis,
  Anbieter; Kontakt und Testzugänge wie bisher. Dateien: Icon 1024, alle sechs hellen Store-Bilder je Sprache in
  Originalgröße (6.9-Zoll aus `~/Documents/Auszeit App-Store-Bilder 2026-10-20/abend-hell/`), die Android-Bilder
  `01` bis `05` und die Funktionsgrafik je Sprache aus `../auszeit-android/store/upload/de` und `en-GB`. Dazu ein ZIP
  je Sprache als „Pressemappe“ (per `zip` erzeugen, deterministisch, ohne `.DS_Store`). Die drei alten dunklen Bilder
  unter `assets/press` und `assets/img` ersetzen.
- Startseiten-Bilder: alle sechs hellen Store-Bilder je Sprache, Höhe 1200 px (`sips -Z 1200`), unter
  `assets/img/de|en`, in der Galerie mit `loading="lazy"`, `width`/`height` und Alt-Texten aus den Slide-Texten.
- og:image 1200 × 630 je Sprache erzeugen (Swift/AppKit wie `screenshots.swift`): heller Verlauf, Icon, Name, Claim.
  Absolute URL `https://auszeit.nxtchange.app/assets/img/og-de.png` bzw. `og-en.png`. Dazu `og:url`,
  `og:locale` (`de_AT`, `en_GB`), `twitter:card` `summary_large_image`.

## Videos

Vom Kanal „nxtChange Apps“ (`https://www.youtube.com/channel/UCn9MXH8Q_HCMdrZeiSdNqJw`), alle „nicht gelistet“,
Einbettung ist erlaubt:

| ID | Titel | Einsatz |
| --- | --- | --- |
| `TQRQjztSKBM` | Auszeit: Weniger scrollen. Ohne Verbot. Die App für Android (30 s) | deutsche Startseite, Abschnitt Android |
| `JQcw7RqWnOs` | Off Hours: Scroll less. No ban. The Android app in 30 seconds | englische Startseite, Abschnitt Android |
| `oJJUE4cR4yY` | Off Hours: accessibility service demo (englisch, mit Untertiteln) | FAQ „Was braucht Auszeit auf Android“, auf beiden Seiten, auf der deutschen mit Hinweis „englisch“ |

Regeln:

- Kein Google-Request beim Seitenaufruf. Klick-Fassade: lokales Vorschaubild (Standbild einmalig nach
  `assets/img/video/<id>.jpg` holen von `https://i.ytimg.com/vi/<id>/maxresdefault.jpg`, Fallback `hqdefault.jpg`)
  mit Play-Symbol und dem Hinweis „Beim Abspielen lädt YouTube“; erst nach Klick wird der `<iframe>` von
  `https://www.youtube-nocookie.com/embed/<id>?autoplay=1&rel=0` eingesetzt. Kleines Inline-Skript ohne externe
  Abhängigkeit; ohne JavaScript ist das Vorschaubild ein Link zum Video.
- iPhone-Vorschau gibt es nicht auf YouTube. Sie liegt als MP4 unter `~/Documents/Auszeit Store-Video 2026-10-20/`
  (`store-video-de.mp4`, `store-video-en.mp4`, 886 × 1920, 22 s, je etwa 8,5 MB, mit Ton). Für den Hero: Bild 1 als
  Poster, Knopf „Video ansehen“ spielt das selbst gehostete Video inline ab (`<video>` mit `preload="none"`,
  `playsinline`, Steuerung, kein Autoplay). Falls `ffmpeg` vorhanden ist, auf etwa 2 bis 3 MB herunterrechnen
  (H.264, 720 px hoch reicht); sonst unverändert nach `assets/video/` kopieren und die Größe im Bericht nennen.
- Datenschutz ergänzen (`datenschutz.md` Abschnitt „Diese Website“ und `privacy.md`): selbst gehostete Videos ohne
  Dritte; YouTube-Videos laden erst nach Klick, dann verarbeitet YouTube (Google Ireland Limited) Daten wie die
  IP-Adresse, erweiterter Datenschutzmodus (youtube-nocookie.com), Link auf Googles Datenschutzerklärung. „Stand“-Datum
  der beiden Seiten auf das heutige Datum setzen.

## Technik

- `<link rel="canonical">` absolut je Seite; hreflang `de`, `en`, `x-default` (deutsch) absolut; auf den Markdown-Seiten
  über Front Matter (`description`, ggf. `lang`) und das Layout.
- JSON-LD auf der Startseite: zwei `SoftwareApplication`/`MobileApplication` (iOS, Android) mit `operatingSystem`,
  `applicationCategory`, `offers` (0 EUR) und `publisher`; `Organization` mit Adresse; `FAQPage`. **Kein
  `aggregateRating`**, solange keine Bewertungen auf der Seite stehen.
- `robots.txt` (alles erlaubt, `Sitemap:`-Zeile), `sitemap.xml` von Hand mit allen Seiten beider Sprachen und
  hreflang-Alternates, `llms.txt` (Kurzbeschreibung, Plattformen, Links zu Startseite, Presse, Support, Datenschutz,
  beide Sprachen). Statische Dateien im Wurzelordner liefert GitHub Pages so aus.
- `404.html` im CI mit Links zu Startseite, Support, englischer Seite.
- Jede Seite: eigene Meta-Beschreibung, `<html lang>`, sichtbarer Sprachwechsel, Kopfzeile mit Icon, Fußzeile mit
  Impressumsdaten wie bisher plus Google-Markenhinweis. Impressum inhaltlich nicht erweitern (siehe Fragen an Karl).
- Keine Anfragen an fremde Hosts beim Laden: nach dem Bau mit `grep -o 'https\?://[^"'"'"' )]*' index.html en/index.html`
  prüfen; erlaubt sind nur Links (`<a href>`), Store-Links und die JSON-LD-URLs, keine `src`, `href` von Stylesheets
  oder `@import` auf fremde Hosts.
- Barrierefreiheit: Fokus sichtbar, Alt-Texte, `<details>`-FAQ, Kontraste geprüft, Videos mit Steuerung.

## Nicht in diesem Auftrag

- Ratgeberseiten (`/ratgeber/…`, „one sec alternative“, Abgrenzung zu Apples „Auszeit“): eigener Auftrag, erst nach
  der Presse. Die Seitenstruktur soll solche Seiten aber zulassen (Markdown-Seite mit dem neuen Layout reicht).
- Google Search Console und Bing Webmaster Tools: Konten legt Karl an. Eine Bestätigungsdatei im Wurzelordner ist
  später möglich.
- Store-Texte, Name der App (1.0.5), Bewertungen, Presseversand.
- Änderungen an nxtchange.app (eigenes Repo `apps-site`).

## Abnahme

1. `python3 -I tools/build_site.py .` läuft ohne Fehler; `index.html`, `en/index.html` neu; `--inline` schreibt `preview/`.
2. Beide Startseiten: Play-Abzeichen und App-Store-Abzeichen, Kampagnenlinks, Preise, FAQ, Galerie mit sechs Bildern,
   Video-Fassaden, Presse-Abschnitt mit neuen Eckdaten und Dateien.
3. `grep -c iPhone index.html` ist nicht mehr die einzige Plattform: „Android“ kommt auf beiden Seiten vor.
4. Head: canonical, drei hreflang, og:image absolut 1200 × 630, og:url, twitter:card, eigene description.
5. `robots.txt`, `sitemap.xml`, `llms.txt`, `404.html` vorhanden und gültig (XML mit `python3 -c "import xml.dom.minidom…"` prüfen).
6. JSON-LD mit `python3 -c "import json…"` aus dem HTML geparst, ohne `aggregateRating`.
7. Keine fremden `src`/Stylesheet-Hosts im HTML (grep wie oben).
8. Markdown-Seiten: Front Matter unverändert gültig, Layout rendert Liquid-Syntax weiter (Sichtprüfung des Layouts).
9. Datenschutz (DE und EN) mit Video-Absatz und neuem Stand.
10. Repo-Größe: neue Binärdateien im Bericht aufführen (Bilder, Videos, ZIPs mit Größe).

## Bericht am Ende

Kurz, auf Deutsch: was geändert wurde (Dateien), was neu an Binärdateien dazukam, was nicht ging, offene Fragen.
Pfad zur Vorschau nennen. Dazu die Liste „Karl macht“: Push, `pt`-Wert prüfen, Search Console und Bing, iPhone-Vorschau
auf YouTube hochladen (optional), Impressum um Kammer und Gewerbe ergänzen (ECG § 5: Mitgliedschaft WKO, anwendbare
Gewerbevorschriften, Aufsichtsbehörde; Fachgruppe UBIT laut Unterlagen, bitte von Karl bestätigen, nicht selbst auf die
Seite schreiben).
