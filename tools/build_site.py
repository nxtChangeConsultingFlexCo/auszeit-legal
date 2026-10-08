#!/usr/bin/env python3
"""Erzeugt die Auszeit-Seite (Deutsch und Englisch) als statisches HTML in diesem Repo.

Aufruf im Repo-Wurzelordner:   python3 -I tools/build_site.py .
Vorschau mit eingebetteten Bildern (landet in preview/, nicht committen):
                               python3 -I tools/build_site.py . --inline

Bilder unter assets/img (Store-Bilder 1, 2 und 6 je Sprache, Höhe 1200 px, per sips -Z 1200 aus dem Upload-Ordner
des Screenshot-Skripts im App-Repo), Icon 180/64 px aus App/Assets.xcassets/AppIcon.appiconset/AppIcon.png,
Abzeichen von https://tools.applemediaservices.com/api/badges/download-on-the-app-store/black/{de-de,en-gb}?size=250x83.
Pressebilder in Originalgröße unter assets/press. Texte folgen store/appstore-*.md im App-Repo.
"""
import base64
import html
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
INLINE = "--inline" in sys.argv
OUT = ROOT / "preview" if INLINE else ROOT
APP_ID = "6817406940"

TEXT = {
    "de": {
        "lang": "de",
        "root": "./",
        "other_lang": "en/",
        "other_label": "English",
        "title": "Auszeit: App Blocker & Fokus",
        "meta_desc": "Auszeit hält gewählte Apps zu festen Zeiten an und schiebt eine kurze Bedenkzeit dazwischen. Ohne Account, ohne Daten. iPhone-App aus Graz.",
        "name": "Auszeit",
        "kicker": "iPhone-App",
        "claim": "Abends das Handy weglegen, ohne Kampf mit der Willenskraft.",
        "lead": "Auszeit hält die Apps, die dich abends festhalten, zu festen Zeiten an. Öffnest du eine davon, zeigt dein iPhone zuerst eine kurze Bedenkzeit. Danach entscheidest du bewusst: Auszeit nehmen oder eine Ausnahme machen. Kein Verbot, keine Tricks, nur ein Moment zum Nachdenken.",
        "store_url": f"https://apps.apple.com/de/app/id{APP_ID}",
        "badge": "badge-de.svg",
        "badge_alt": "Laden im App Store",
        "store_note": "Gratis mit einer Auszeit für bis zu zwei Apps. Mehr mit Auszeit Plus, als Jahres- oder Monatsabo.",
        "images": [("de/1-schirm.png", "Schirm von Auszeit: Bedenkzeit von 15 Sekunden, bevor sich die App öffnet"),
                   ("de/2-entscheidung.png", "Entscheidung: Auszeit nehmen oder Ausnahme machen"),
                   ("de/6-privat.png", "Kein Konto, keine Daten, keine Werbung")],
        "how_h": "So funktioniert es",
        "how": [
            "Zeitfenster festlegen, zum Beispiel 21:00 bis 07:00, an den Tagen, die du willst.",
            "Apps auswählen. Auszeit nutzt dafür die Bildschirmzeit deines iPhones.",
            "Ab dann übernimmt iOS: Die Bedenkzeit greift pünktlich, auch wenn Auszeit geschlossen ist.",
            "Nach einer Ausnahme bleibt die App ein paar Minuten offen, dann gilt wieder die Bedenkzeit.",
            "Widget für den Home-Bildschirm mit dem Stand von jetzt.",
        ],
        "privacy_h": "Kein Konto. Keine Daten. Keine Werbung.",
        "privacy": "Kein Account, kein Server, keine Analyse. Alles bleibt auf deinem iPhone. Welche Apps du wählst, speichert Auszeit nur als verschlüsselte Kennungen von iOS. Auszeit sieht nicht, wie lange du Apps nutzt, und zeichnet nichts auf.",
        "honest_h": "Ehrlich gesagt",
        "honest": "Auszeit ist ein Hilfsmittel, kein Schutz vor dir selbst. Jede Auszeit lässt sich jederzeit ausschalten. Auszeit pausiert Apps, keine Webseiten.",
        "press_h": "Presse",
        "press": "Material für Berichte, ohne Rückfrage verwendbar. Fragen und Testzugänge: apps@nxtchange-consulting.com.",
        "press_short_h": "Kurztext",
        "press_short": "Auszeit ist eine iPhone-App aus Graz, die gewählte Apps zu festen Zeiten anhält und eine kurze Bedenkzeit dazwischenschiebt. Nutzer entscheiden danach bewusst: Auszeit nehmen oder eine Ausnahme machen. Die App braucht kein Konto, keinen Server und keine Analyse; alle Daten bleiben auf dem Gerät. Auszeit ist gratis mit einer Auszeit für bis zu zwei Apps, Auszeit Plus erweitert den Umfang. Anbieter ist nxtChange Consulting FlexCo.",
        "press_files_h": "Dateien",
        "press_files": [("press/auszeit-icon-1024.png", "App-Icon, 1024 × 1024 px"),
                        ("press/de-1-schirm.png", "Bild Bedenkzeit, 1284 × 2778 px"),
                        ("press/de-2-entscheidung.png", "Bild Entscheidung, 1284 × 2778 px"),
                        ("press/de-6-privat.png", "Bild Privatsphäre, 1284 × 2778 px")],
        "press_facts_h": "Eckdaten",
        "press_facts": [("Plattform", "iPhone, iOS 17 oder neuer"),
                        ("Veröffentlicht", "8. Oktober 2026, Version 1.0"),
                        ("Länder", "38 europäische Länder, Deutsch und Englisch"),
                        ("Preis", "Gratis; Auszeit Plus als Jahres- oder Monatsabo, Preise in der App"),
                        ("Anbieter", "nxtChange Consulting FlexCo, Graz")],
        "footer_links": [("support/", "Support"), ("datenschutz/", "Datenschutz"), ("nutzungsbedingungen/", "Nutzungsbedingungen")],
        "provider_h": "Anbieter",
        "footnote": "Apple, iPhone und App Store sind Marken der Apple Inc.",
    },
    "en": {
        "lang": "en",
        "root": "../",
        "other_lang": "../",
        "other_label": "Deutsch",
        "title": "Off Hours: App Blocker & Focus",
        "meta_desc": "Off Hours holds the apps you choose during the hours you set and adds a short cooling-off first. No account, no data. An iPhone app from Graz, Austria.",
        "name": "Off Hours",
        "kicker": "iPhone app",
        "claim": "Put the phone down in the evening, without a fight with your willpower.",
        "lead": "Off Hours holds the apps that keep you up at night during the hours you set. When you open one of them, your iPhone first shows a short cooling-off. Then you decide on purpose: take a break, or make an exception. No ban, no tricks, just a moment to think.",
        "store_url": f"https://apps.apple.com/gb/app/id{APP_ID}",
        "badge": "badge-en.svg",
        "badge_alt": "Download on the App Store",
        "store_note": "Free with one schedule for up to two apps. More with Off Hours Plus, as a yearly or monthly subscription.",
        "images": [("en/1-shield.png", "Off Hours shield: a 15-second cooling-off before the app opens"),
                   ("en/2-decision.png", "Decision: take a break or make an exception"),
                   ("en/6-private.png", "No account, no data, no ads")],
        "how_h": "How it works",
        "how": [
            "Set a time window, for example 9 PM to 7 AM, on the days you choose.",
            "Pick the apps. Off Hours uses your iPhone's Screen Time for this.",
            "From then on iOS takes over: the cooling-off starts on time, even when Off Hours is closed.",
            "After an exception the app stays open for a few minutes, then the cooling-off applies again.",
            "Home Screen widget with the current status.",
        ],
        "privacy_h": "No account. No data. No ads.",
        "privacy": "No account, no server, no analytics. Everything stays on your iPhone. Off Hours stores the apps you choose only as encrypted identifiers from iOS. Off Hours does not see how long you use apps, and it records nothing.",
        "honest_h": "Honestly",
        "honest": "Off Hours is an aid, not a safeguard against yourself. Any schedule can be switched off at any time. Off Hours pauses apps, not websites.",
        "press_h": "Press",
        "press": "Material for coverage, free to use without asking. Questions and review access: apps@nxtchange-consulting.com.",
        "press_short_h": "Short description",
        "press_short": "Off Hours is an iPhone app from Graz, Austria, that holds the apps you choose during the hours you set and adds a short cooling-off first. Users then decide on purpose: take a break or make an exception. The app needs no account, no server and no analytics; all data stays on the device. Off Hours is free with one schedule for up to two apps; Off Hours Plus extends it. The developer is nxtChange Consulting FlexCo.",
        "press_files_h": "Files",
        "press_files": [("press/auszeit-icon-1024.png", "App icon, 1024 × 1024 px"),
                        ("press/en-1-shield.png", "Image cooling-off, 1284 × 2778 px"),
                        ("press/en-2-decision.png", "Image decision, 1284 × 2778 px"),
                        ("press/en-6-private.png", "Image privacy, 1284 × 2778 px")],
        "press_facts_h": "Facts",
        "press_facts": [("Platform", "iPhone, iOS 17 or later"),
                        ("Released", "8 October 2026, version 1.0"),
                        ("Countries", "38 European countries, English and German"),
                        ("Price", "Free; Off Hours Plus as a yearly or monthly subscription, prices shown in the app"),
                        ("Developer", "nxtChange Consulting FlexCo, Graz, Austria")],
        "footer_links": [("support/#support-for-off-hours", "Support"), ("privacy/", "Privacy Policy"), ("terms/", "Terms of Use")],
        "provider_h": "Provider",
        "footnote": "Apple, iPhone and App Store are trademarks of Apple Inc.",
    },
}

CSS = """
:root{--bg:#121214;--bg2:#1b1b1e;--fg:#f1efe9;--muted:#a9a7a0;--gold:#c8b48a;--line:#2b2b2f;--maxw:1040px;color-scheme:dark}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
a{color:var(--gold)}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 16px}
header.top{display:flex;align-items:center;justify-content:space-between;padding:20px 0}
header.top .brand{display:flex;align-items:center;gap:12px;color:var(--fg);text-decoration:none;font-weight:600}
header.top .brand img{width:40px;height:40px;border-radius:10px}
header.top nav a{color:var(--muted);text-decoration:none;margin-left:18px;font-size:15px}
header.top nav a:hover{color:var(--fg)}
.hero{padding:40px 0 24px}
.kicker{color:var(--gold);letter-spacing:.14em;text-transform:uppercase;font-size:12px;font-weight:600}
h1{font-family:"New York","Iowan Old Style",Georgia,"Times New Roman",serif;font-weight:600;font-size:clamp(34px,6vw,56px);line-height:1.08;margin:10px 0 18px;letter-spacing:-.01em}
h1 em{font-style:normal;color:var(--gold)}
.lead{font-size:19px;color:var(--muted);max-width:640px;margin:0 0 26px}
.store{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.store img{height:54px;width:auto;display:block}
.store p{margin:0;color:var(--muted);font-size:15px;max-width:420px}
.shots{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;padding:30px 0}
.shots img{width:100%;height:auto;display:block;border-radius:22px;border:1px solid var(--line)}
section{padding:30px 0;border-top:1px solid var(--line)}
h2{font-family:"New York","Iowan Old Style",Georgia,"Times New Roman",serif;font-weight:600;font-size:30px;margin:0 0 14px;letter-spacing:-.01em}
h3{font-size:17px;margin:22px 0 8px}
section p{max-width:680px;margin:0 0 12px}
ul.how{list-style:none;padding:0;margin:0;max-width:680px}
ul.how li{padding:10px 0 10px 28px;position:relative;border-bottom:1px solid var(--line)}
ul.how li::before{content:"";position:absolute;left:0;top:19px;width:10px;height:10px;border-radius:50%;background:var(--gold)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:32px}
dl.facts{display:grid;grid-template-columns:max-content 1fr;gap:6px 18px;margin:0;max-width:680px}
dl.facts dt{color:var(--muted)}
dl.facts dd{margin:0}
ul.files{padding-left:20px;margin:0}
ul.files li{margin:4px 0}
footer{border-top:1px solid var(--line);padding:28px 0 40px;color:var(--muted);font-size:14px}
footer .links a{margin-right:18px;color:var(--fg);text-decoration:none}
footer .links a:hover{text-decoration:underline}
footer address{font-style:normal;margin:16px 0 0;line-height:1.5}
footer .note{margin-top:16px}
@media (max-width:720px){.shots{grid-template-columns:1fr 1fr}.two{grid-template-columns:1fr}header.top nav a{margin-left:12px}}
@media (max-width:480px){.shots{grid-template-columns:1fr;max-width:360px;margin:0 auto}}
@media (prefers-color-scheme:light){:root:not([data-theme="dark"]){--bg:#f6f4ee;--bg2:#fff;--fg:#1a1a1c;--muted:#5d5b55;--gold:#8a7445;--line:#e2dfd6;color-scheme:light}}
:root[data-theme="light"]{--bg:#f6f4ee;--bg2:#fff;--fg:#1a1a1c;--muted:#5d5b55;--gold:#8a7445;--line:#e2dfd6;color-scheme:light}
"""


def asset(rel: str, root: str) -> str:
    """Pfad zu einer Datei unter assets/img, bei --inline als data:-URI."""
    path = ROOT / "assets" / "img" / rel
    if INLINE:
        mime = "image/svg+xml" if rel.endswith(".svg") else "image/png"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{data}"
    return f"{root}assets/img/{rel}"


def page(t: dict) -> str:
    e = html.escape
    root = t["root"]
    icon = asset("icon-180.png", root)
    icon64 = asset("icon-64.png", root)
    shots = "\n".join(
        f'      <img src="{asset(src, root)}" alt="{e(alt)}" width="554" height="1200" loading="lazy">'
        for src, alt in t["images"])
    how = "\n".join(f"        <li>{e(x)}</li>" for x in t["how"])
    facts = "\n".join(f"        <dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in t["press_facts"])
    files = "\n".join(f'        <li><a href="{root}assets/{e(href)}" download>{e(label)}</a></li>'
                      for href, label in t["press_files"])
    links = "\n".join(f'        <a href="{root}{e(href)}">{e(label)}</a>' for href, label in t["footer_links"])
    claim = e(t["claim"])
    return f"""<!DOCTYPE html>
<html lang="{t['lang']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(t['title'])}</title>
  <meta name="description" content="{e(t['meta_desc'])}">
  <meta name="apple-itunes-app" content="app-id={APP_ID}">
  <meta property="og:title" content="{e(t['title'])}">
  <meta property="og:description" content="{e(t['meta_desc'])}">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{root}assets/press/auszeit-icon-1024.png">
  <meta name="color-scheme" content="dark light">
  <link rel="icon" href="{icon64}" type="image/png">
  <link rel="apple-touch-icon" href="{icon}">
  <link rel="alternate" hreflang="de" href="{root}">
  <link rel="alternate" hreflang="en" href="{root}en/">
  <style>{CSS}</style>
</head>
<body>
  <div class="wrap">
    <header class="top">
      <a class="brand" href="{root}"><img src="{icon}" alt="" width="40" height="40">{e(t['name'])}</a>
      <nav>
        <a href="#presse">{e(t['press_h'])}</a>
        <a href="{root}{e(t['footer_links'][0][0])}">{e(t['footer_links'][0][1])}</a>
        <a href="{t['other_lang']}" lang="{'en' if t['lang'] == 'de' else 'de'}">{e(t['other_label'])}</a>
      </nav>
    </header>

    <div class="hero">
      <div class="kicker">{e(t['kicker'])}</div>
      <h1>{claim}</h1>
      <p class="lead">{e(t['lead'])}</p>
      <div class="store">
        <a href="{t['store_url']}"><img src="{asset(t['badge'], root)}" alt="{e(t['badge_alt'])}" width="162" height="54"></a>
        <p>{e(t['store_note'])}</p>
      </div>
    </div>

    <div class="shots">
{shots}
    </div>

    <section>
      <h2>{e(t['how_h'])}</h2>
      <ul class="how">
{how}
      </ul>
    </section>

    <section>
      <div class="two">
        <div>
          <h2>{e(t['privacy_h'])}</h2>
          <p>{e(t['privacy'])}</p>
        </div>
        <div>
          <h2>{e(t['honest_h'])}</h2>
          <p>{e(t['honest'])}</p>
        </div>
      </div>
    </section>

    <section id="presse">
      <h2>{e(t['press_h'])}</h2>
      <p>{e(t['press'])}</p>
      <h3>{e(t['press_short_h'])}</h3>
      <p>{e(t['press_short'])}</p>
      <h3>{e(t['press_facts_h'])}</h3>
      <dl class="facts">
{facts}
      </dl>
      <h3>{e(t['press_files_h'])}</h3>
      <ul class="files">
{files}
      </ul>
    </section>

    <footer>
      <div class="links">
{links}
      </div>
      <address>
        <strong>{e(t['provider_h'])}:</strong> nxtChange Consulting FlexCo · Neugasse 9/1 · 8045 Graz, Österreich<br>
        FN 648962g, Landesgericht für ZRS Graz · UID ATU81922038 · <a href="mailto:apps@nxtchange-consulting.com">apps@nxtchange-consulting.com</a>
      </address>
      <p class="note">{e(t['footnote'])}</p>
    </footer>
  </div>
</body>
</html>
"""


for lang, t in TEXT.items():
    target = OUT / ("index.html" if lang == "de" else "en/index.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page(t), encoding="utf-8")
    print(f"{target} ({target.stat().st_size // 1024} KB)")
