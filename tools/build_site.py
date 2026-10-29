#!/usr/bin/env python3
"""Erzeugt die Startseite von Auszeit (Deutsch und Englisch) und die 404-Seite als statisches HTML in diesem Repo.

Aufruf im Repo-Wurzelordner:   python3 -I tools/build_site.py .
Vorschau, Bilder und CSS eingebettet, Videos und Downloads aus dem Repo (landet in preview/, nicht committen):
                               python3 -I tools/build_site.py . --inline

Schreibt index.html, en/index.html und 404.html. Gestaltung: assets/css/site.css (von Hand gepflegt, gilt auch für die
Rechtstexte über _layouts/default.html). Bilder, Videos und Pressemappen erzeugt tools/assets.sh (dazu
tools/og-bild.swift für das Teaserbild, tools/video.swift für die App-Vorschau und tools/gruenderfoto.swift für das
Gründerfoto im Querformat). robots.txt, sitemap.xml und llms.txt
im Wurzelordner sind von Hand gepflegt; neue Seiten dort nachtragen.

Texte folgen den Store-Texten, nichts erfinden: store/appstore-de.md und appstore-en.md im App-Repo auszeit (iPhone),
store/play-de.md und play-en.md im Repo auszeit-android (Android), dort store/upload/formulare.md (Bedienungshilfe);
Bildtexte aus store/screenshots.swift (iPhone) und store/play-bilder.swift (Android).
"""
import base64
import hashlib
import html
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(sys.argv[1]).resolve()
INLINE = "--inline" in sys.argv
OUT = ROOT / "preview" if INLINE else ROOT

SITE = "https://auszeit.nxtchange.app"
APP_ID = "6817406940"
PLAY_ID = "at.nxtchange.auszeit"
# pt: Anbieter-ID aus App Store Connect › App Analytics › Kampagnen (Content-Provider-ID des Kontos).
APPLE_PROVIDER = "129507889"
# Name im Store je Sprache. Ändert sich voraussichtlich mit 1.0.5, dann nur hier.
STORE_NAME = {"de": "Auszeit: App Blocker & Fokus", "en": "Off Hours: App Blocker & Focus"}
EMAIL = "apps@nxtchange-consulting.com"
# Gründerfoto fürs Pressematerial: Querformat aus dem Porträt, erzeugt tools/gruenderfoto.swift über tools/assets.sh
# (dort steht derselbe Bildnachweis für die Metadaten der JPEGs). Fotograf nicht dokumentiert, Nachweis bestätigt Karl.
FOUNDER_PHOTO = {"press": "press/karl-maier-1800x1200.jpg", "web": "img/karl-maier-1200x800.jpg"}
PHOTO_CREDIT = "nxtChange Consulting FlexCo"
LINKEDIN = "https://www.linkedin.com/in/karl-maier/"
PLAY_URL = (f"https://play.google.com/store/apps/details?id={PLAY_ID}"
            "&referrer=utm_source%3Dauszeit.nxtchange.app%26utm_medium%3Dwebsite%26utm_campaign%3Dbadge")
# Videos vom Kanal „nxtChange Apps“, nicht gelistet, Einbettung erlaubt. Standbilder lokal unter assets/img/video.
YOUTUBE = {
    "android-de": ("TQRQjztSKBM", "Auszeit: Weniger scrollen. Ohne Verbot. Die App für Android (30 s)"),
    "android-en": ("JQcw7RqWnOs", "Off Hours: Scroll less. No ban. The Android app in 30 seconds"),
    "access": ("oJJUE4cR4yY", "Off Hours: accessibility service demo"),
}


def apple_url(country: str) -> str:
    return f"https://apps.apple.com/{country}/app/apple-store/id{APP_ID}?pt={APPLE_PROVIDER}&ct=website&mt=8"


# Die sechs App-Store-Bilder (store/screenshots.swift, Theme „abend-hell“): Datei, Etikett, Zeilen, Unterzeile.
SLIDES = {
    "de": [
        ("1-schirm.png", "App-Blocker mit Bedenkzeit", ["Instagram?", "Erst 15 Sekunden."], "Eine kurze Pause, bevor die App aufgeht."),
        ("2-liste.png", "Automatisch zu festen Zeiten", ["Zu deinen Zeiten.", "Ganz von selbst."], "Abends, in der Arbeit oder ganztags."),
        ("3-entscheidung.png", "Entscheidung", ["Deine Entscheidung.", "Jedes Mal."], "Auszeit nehmen oder kurz eine Ausnahme machen."),
        ("4-editor.png", "Einstellung", ["So streng,", "wie du willst."], "Bedenkzeit, Ausnahme und Tage stellst du selbst ein."),
        ("5-apps.png", "Apps", ["Nur die Apps,", "die du wählst."], "Social Media, Spiele, Streaming: du entscheidest. Alles andere bleibt offen."),
        ("6-privat.png", "Privatsphäre", ["Kein Konto.", "Keine Daten.", "Keine Werbung."], "Alles bleibt auf deinem iPhone. In einer Minute eingerichtet."),
    ],
    "en": [
        ("1-shield.png", "App blocker with a pause", ["Instagram?", "First 15 seconds."], "A short pause before the app opens."),
        ("2-list.png", "Automatic schedules", ["On your schedule.", "Automatically."], "Evenings, work hours or all day."),
        ("3-decision.png", "Your call", ["Your decision.", "Every time."], "Take a break or make a short exception."),
        ("4-editor.png", "Settings", ["As strict", "as you like."], "You set the cooling-off, the exception and the days."),
        ("5-apps.png", "Apps", ["Only the apps", "you choose."], "Social media, games, streaming: your pick. Everything else stays open."),
        ("6-private.png", "Privacy", ["No account.", "No data.", "No ads."], "Everything stays on your iPhone. Set up in a minute."),
    ],
}
# Die fünf Google-Play-Bilder (store/play-bilder.swift im Repo auszeit-android) und die Funktionsgrafik.
ANDROID = {
    "de": [("01-schirm.png", "Weniger scrollen. Ohne Verbot."), ("02-entscheidung.png", "Deine Entscheidung. Jedes Mal."),
           ("03-liste.png", "Zu deinen Zeiten. Jeden Tag."), ("04-editor.png", "So streng, wie du willst."),
           ("05-apps.png", "Nur die Apps, die du wählst."), ("funktionsgrafik-1024x500.png", "Funktionsgrafik")],
    "en": [("01-shield.png", "Scroll less. No ban."), ("02-decision.png", "Your decision. Every time."),
           ("03-list.png", "On your schedule. Every day."), ("04-editor.png", "As strict as you like."),
           ("05-apps.png", "Only the apps you choose."), ("feature-graphic-1024x500.png", "Feature graphic")],
}

TEXT = {
    "de": {
        "lang": "de", "locale": "de_AT", "other_locale": "en_GB", "path": "/", "root": "./",
        "other_href": "en/", "other_lang": "en", "other_label": "English",
        "name": "Auszeit",
        "title": f"{STORE_NAME['de']} · für iPhone und Android",
        "meta_desc": "Auszeit hält gewählte Apps zu festen Zeiten an und schiebt eine kurze Bedenkzeit dazwischen. "
                     "Für iPhone und Android, ohne Konto, ohne Daten. App aus Graz.",
        "og_alt": "Auszeit, App-Blocker für iPhone und Android: Abends das Handy weglegen, ohne Kampf mit der Willenskraft.",
        "skip": "Zum Inhalt",
        "nav_label": "Hauptnavigation",
        "nav": [("#so-funktioniert-es", "So funktioniert es", True), ("#preise", "Preise", True),
                ("#fragen", "Fragen", True), ("#presse", "Presse", False), ("support/", "Support", False)],
        "kicker": "App-Blocker für iPhone und Android",
        "claim": ["Abends das Handy weglegen,", "ohne Kampf mit der Willenskraft."],
        "lead": "Auszeit hält die Apps, die dich abends festhalten, zu festen Zeiten an. Öffnest du eine davon, zeigt dein "
                "Handy zuerst eine kurze Bedenkzeit. Danach entscheidest du bewusst: Auszeit nehmen oder eine Ausnahme "
                "machen. Kein Verbot, keine Tricks, nur ein Moment zum Nachdenken.",
        "apple_country": "de",
        "badge_apple": "badge-de.svg", "badge_apple_alt": "Laden im App Store",
        "badge_play": "google-play-de.png", "badge_play_alt": "Jetzt bei Google Play",
        "price": "Gratis. Auszeit Plus 9,99 € im Jahr oder 3,99 € im Monat (Preis in Österreich, Apple und Google "
                 "rechnen je Land um, der genaue Preis steht in der App).",
        "video_button": "Video ansehen",
        "video_label": "App-Vorschau von Auszeit auf dem iPhone",
        "video_caption": "App-Vorschau iPhone · 22 s, mit Ton",
        "video_fallback": "Dein Browser spielt das Video hier nicht ab:",
        "video_download": "Video laden (MP4)",
        "gallery_label": "Bilder aus dem App Store",
        "glance": "Auf einen Blick",
        "how_id": "so-funktioniert-es",
        "how_intro": "So funktioniert es: Auf dem iPhone nutzt Auszeit die Bildschirmzeit von iOS. Auf Android nutzt "
                     "Auszeit die Bedienungshilfe, die du einmal einschaltest. Ab dann greift die Bedenkzeit pünktlich, "
                     "auch wenn Auszeit geschlossen ist.",
        "ios_h": "iPhone", "ios_req": "iOS 17 oder neuer · nutzt die Bildschirmzeit",
        "ios_os": "iOS 17 oder neuer",
        "ios_steps": [
            "Zeitfenster festlegen, zum Beispiel 21:00 bis 07:00, an den Tagen, die du willst.",
            "Apps auswählen. Auszeit nutzt dafür die Bildschirmzeit deines iPhones.",
            "Ab dann übernimmt iOS: Die Bedenkzeit greift pünktlich, auch wenn Auszeit geschlossen ist.",
            "Nach einer Ausnahme bleibt die App ein paar Minuten offen, dann gilt wieder die Bedenkzeit.",
            "Widget für den Home-Bildschirm mit dem Stand von jetzt.",
        ],
        "android_h": "Android", "android_req": "Android 8.0 oder neuer · nutzt die Bedienungshilfe",
        "android_os": "Android 8.0 oder neuer",
        "android_steps": [
            "Zeitfenster festlegen, zum Beispiel 21:00 bis 07:00, an den Tagen, die du willst.",
            "Apps auswählen, einzeln oder als ganze Kategorie, aus der Liste deiner installierten Apps.",
            "Bedienungshilfe einmal einschalten. Ab dann greift die Bedenkzeit pünktlich, auch wenn Auszeit geschlossen ist.",
            "Nach einer Ausnahme bleibt die App ein paar Minuten offen, dann gilt wieder die Bedenkzeit.",
            "Widget für den Startbildschirm mit dem Stand von jetzt.",
        ],
        "android_video": "android-de",
        "android_video_caption": "Auszeit auf Android in 30 Sekunden.",
        "yt_note": "Beim Abspielen lädt YouTube",
        "yt_play": "Video auf YouTube abspielen",
        "price_id": "preise",
        "free_h": "Gratis", "free_amount": "0 €",
        "free": "Eine Auszeit mit bis zu zwei Apps, 15 Sekunden Bedenkzeit und 5 Minuten Ausnahme.",
        "plus_h": "Auszeit Plus", "plus_amount": "9,99 € im Jahr", "plus_amount_alt": "oder 3,99 € im Monat",
        "plus": [
            "Weitere Auszeiten, etwa fürs Wochenende",
            "Mehr als zwei Apps je Auszeit, auch ganze Kategorien (auf dem iPhone bis zu 50 Apps je Auszeit, auf "
            "Android ohne Obergrenze)",
            "Bedenkzeit 30 oder 90 Sekunden, oder ganz sperren bis zum Ende der Auszeit",
            "Ausnahme 1, 5 oder 15 Minuten",
            "„Jetzt bis Ende“: eine Auszeit sofort starten, auch vom Widget aus",
        ],
        "fine": "Preise in Österreich; Apple und Google rechnen je Land um, der genaue Preis steht in der App. Plus gibt es "
                "als Jahres- oder Monatsabo. Das Abo verlängert sich automatisch, bis du es kündigst: auf dem iPhone in "
                "den Einstellungen unter Apple-Account › Abos, auf Android in Google Play unter Zahlungen und Abos. Ein "
                "Abo gilt nur für die Plattform, auf der du es gekauft hast.",
        "honest_h": "Ehrlich gesagt",
        "honest": "Auszeit ist ein Hilfsmittel, kein Schutz vor dir selbst. Jede Auszeit lässt sich jederzeit "
                  "ausschalten. Auszeit pausiert Apps, keine Webseiten. Manche Android-Geräte beenden Dienste im "
                  "Hintergrund, um Akku zu sparen; die App sagt dir, wo du das für Auszeit ausschaltest.",
        "privacy_id": "privatsphaere",
        "privacy_sub": "Kein Account, kein Server, keine Analyse. Alles bleibt auf deinem Handy.",
        "privacy_cols": [
            ("Auf dem iPhone", "Welche Apps du wählst, speichert Auszeit nur als verschlüsselte Kennungen von iOS. Den "
             "Namen einer App bekommt allein der Schirm, um ihn anzuzeigen. Auszeit sieht nicht, wie lange du Apps "
             "nutzt, und zeichnet nichts auf."),
            ("Auf Android", "Auszeit nutzt die Bedienungshilfe von Android nur, um zu erkennen, welche App gerade vorn "
             "ist, und legt dann die Bedenkzeit darüber. Sie liest keine Bildschirminhalte, sieht nicht, was du tippst, "
             "und zeichnet nichts auf. Auszeit sieht nicht, wie lange du Apps nutzt."),
        ],
        "privacy_more": ("datenschutz/", "Alles Weitere in der Datenschutzerklärung"),
        "faq_id": "fragen", "faq_h": "Häufige Fragen",
        "faq": [
            ("Ist Auszeit dasselbe wie die „Auszeit“ in Apples Bildschirmzeit?",
             ["Nein. Die Auszeit in Apples Bildschirmzeit sperrt Apps zu festen Zeiten. Die App Auszeit nutzt die "
              "Bildschirmzeit als Grundlage und setzt eine Bedenkzeit mit Entscheidung davor, statt eines Verbots: "
              "Auszeit nehmen oder eine Ausnahme machen. Auszeit ist eine eigene App von nxtChange Consulting FlexCo, "
              "nicht von Apple."], None),
            ("Funktioniert Auszeit nur abends?",
             ["Nein. Du legst das Zeitfenster selbst fest, zum Beispiel 21:00 bis 07:00, an den Tagen, die du willst: "
              "abends, in der Arbeit oder ganztags. Gratis gilt eine Auszeit; mit Auszeit Plus kommen weitere dazu, "
              "etwa fürs Wochenende."], None),
            ("Was braucht Auszeit auf Android, und warum die Bedienungshilfe?",
             ["Ein Android-Handy ab Android 8.0 und die Bedienungshilfe von Android, die du einmal in den "
              "Einstellungen einschaltest. Auf Android gibt es keine Bildschirmzeit-Schnittstelle für andere Apps, und "
              "ohne Geräteadministrator oder Unternehmensprofil keinen anderen Weg, zu festen Zeiten eine Bedenkzeit "
              "über eine andere App zu legen.",
              "Auszeit nutzt die Bedienungshilfe nur, um zu erkennen, welche App gerade vorn ist, und legt dann die "
              "Bedenkzeit darüber. Sie liest keine Bildschirminhalte, sieht nicht, was du tippst, und zeichnet nichts "
              "auf. Bevor die App dich zum Einschalten in die Einstellungen führt, erklärt sie dir das in einem Dialog."],
             ("access", "Vorführung der Bedienungshilfe, vom Dialog bis zur Bedenkzeit über einer App. Das Video ist "
                        "auf Englisch, mit Untertiteln.")),
            ("Sieht Auszeit, welche Apps ich nutze?",
             ["Nein. Kein Account, kein Server, keine Analyse: Alles bleibt auf deinem Handy. Auf dem iPhone speichert "
              "Auszeit die gewählten Apps nur als verschlüsselte Kennungen von iOS; den Namen einer App bekommt allein "
              "der Schirm, um ihn anzuzeigen. Auf Android verarbeitet die Bedienungshilfe nur den Paketnamen der App, "
              "die gerade vorn ist, und speichert ihn nicht. Auszeit sieht nicht, wie lange du Apps nutzt, und zeichnet "
              "nichts auf."], None),
            ("Kann ich die Sperre umgehen?",
             ["Ja. Auszeit ist ein Hilfsmittel, kein Schutz vor dir selbst. Jede Auszeit lässt sich jederzeit "
              "ausschalten. Wer es strenger will, stellt mit Auszeit Plus eine Bedenkzeit von 30 oder 90 Sekunden ein "
              "oder sperrt die Apps ganz bis zum Ende der Auszeit."], None),
            ("Was kostet Auszeit?",
             ["Auszeit ist gratis, mit einer Auszeit für bis zu zwei Apps, 15 Sekunden Bedenkzeit und 5 Minuten "
              "Ausnahme. Auszeit Plus kostet 9,99 € im Jahr oder 3,99 € im Monat (Preis in Österreich, Apple und "
              "Google rechnen je Land um, der genaue Preis steht in der App). Das Abo verlängert sich automatisch, bis "
              "du es kündigst."], None),
            ("Pausiert Auszeit auch Webseiten?",
             ["Nein. Auszeit pausiert Apps, keine Webseiten. Ob Mitteilungen einer pausierten App erscheinen, "
              "entscheidet das System."], None),
            ("Auf welchen Geräten läuft Auszeit?",
             ["Auf dem iPhone mit iOS 17 oder neuer und auf Android-Handys ab Android 8.0. Auszeit gibt es im App Store "
              "und bei Google Play, auf Deutsch und Englisch."], None),
        ],
        "press_id": "presse", "press_h": "Presse",
        "press_intro": "Material für Berichte, ohne Rückfrage verwendbar. Fragen und Testzugänge:",
        "press_short_h": "Kurztext",
        "press_short": "Auszeit ist eine App für iPhone und Android aus Graz, die gewählte Apps zu festen Zeiten anhält "
                       "und eine kurze Bedenkzeit dazwischenschiebt. Nutzer entscheiden danach bewusst: Auszeit nehmen "
                       "oder eine Ausnahme machen. Auf dem iPhone nutzt Auszeit die Bildschirmzeit, auf Android die "
                       "Bedienungshilfe. Die App braucht kein Konto, keinen Server und keine Analyse; alle Daten bleiben "
                       "auf dem Gerät. Auszeit ist gratis mit einer Auszeit für bis zu zwei Apps, Auszeit Plus erweitert "
                       "den Umfang. Anbieter ist nxtChange Consulting FlexCo.",
        "press_facts_h": "Eckdaten",
        "press_facts": [
            ("Name", f"Auszeit (englisch: Off Hours), im Store „{STORE_NAME['de']}“"),
            ("Plattformen", "iPhone (iOS 17 oder neuer) und Android (8.0 oder neuer)"),
            ("Veröffentlicht", "Oktober 2026"),
            ("Länder", "37 im App Store, 36 bei Google Play, alle in Europa"),
            ("Sprachen", "Deutsch und Englisch"),
            ("Preis", "Gratis; Auszeit Plus 9,99 € im Jahr oder 3,99 € im Monat (Preis in Österreich)"),
            ("Gründer", "Karl Maier, Ein-Personen-Projekt ohne Investoren"),
            ("Anbieter", "nxtChange Consulting FlexCo, Graz"),
        ],
        # Gründergeschichte wie in den Presse-Pitches (Outlook-Entwurf vom 25.10.2026): Ein-Personen-Projekt, persönlicher
        # Anlass, Instagram als Zitat. Nichts erfinden, Wortlaut aus dem Pitch.
        "founder_id": "gruender", "founder_h": "Gründer", "founder_name": "Karl Maier",
        "founder_role": "Gründer und Entwickler von Auszeit · nxtChange Consulting FlexCo, Graz",
        "founder_job": "Gründer und Entwickler von Auszeit",
        "founder_intro": "Karl Maier, Unternehmensberater aus Graz, hat Auszeit Anfang Oktober 2026 für iPhone und Android "
                         "veröffentlicht: als Ein-Personen-Projekt ohne Investoren, über seine nxtChange Consulting FlexCo. "
                         "Der Anlass war persönlich.",
        "founder_quote": "Oft wollte ich nur kurz in Instagram schauen, und dann waren zwei Stunden weg.",
        "founder_quote_by": "Karl Maier, Gründer von Auszeit",
        "founder_after": "Auszeit unterbricht diesen Reflex. In einem frei wählbaren Zeitfenster, meist abends, auf Wunsch "
                         "rund um die Uhr, kommt vor ausgewählten Apps zuerst eine kurze Pause mit Countdown. Danach "
                         "entscheidet man bewusst: Auszeit nehmen oder eine Ausnahme machen. Kein Konto, kein Server, kein "
                         "Tracking.",
        "founder_note": "Zitat und Text sind für Berichte frei verwendbar.",
        "q_open": "„", "q_close": "“",
        "photo_alt": "Karl Maier, Gründer und Entwickler von Auszeit, Porträt im Querformat",
        "photo_credit_label": "Foto", "photo_download": "Foto in Druckgröße laden",
        "files_founder_h": "Gründerfoto", "files_founder": "Karl Maier, Querformat 3:2",
        "press_files_h": "Dateien",
        "kit": "auszeit-pressemappe-de", "kit_label": "Pressemappe laden",
        "kit_meta": "ZIP mit allen {n} Dateien, {size}",
        "files_icon_h": "App-Icon", "files_icon": "App-Icon",
        "files_ios_h": "iPhone, App Store", "files_android_h": "Android, Google Play",
        "footer_links": [("support/", "Support"), ("datenschutz/", "Datenschutz"),
                         ("nutzungsbedingungen/", "Nutzungsbedingungen"), ("impressum/", "Impressum"),
                         ("https://nxtchange.app/", "Alle Apps")],
        "provider_h": "Anbieter", "country": "Österreich",
        "register": "FN 648962g, Landesgericht für ZRS Graz · UID ATU81922038",
        "footnotes": ["Apple, iPhone und App Store sind Marken der Apple Inc.",
                      "Google Play und das Google Play-Logo sind Marken von Google LLC."],
        "category": "Produktivität",
        "decimal": ",",
    },
    "en": {
        "lang": "en", "locale": "en_GB", "other_locale": "de_AT", "path": "/en/", "root": "../",
        "other_href": "../", "other_lang": "de", "other_label": "Deutsch",
        "name": "Off Hours",
        "title": f"{STORE_NAME['en']} · for iPhone and Android",
        "meta_desc": "Off Hours holds the apps you choose during the hours you set and adds a short cooling-off first. "
                     "For iPhone and Android, no account, no data. An app from Graz, Austria.",
        "og_alt": "Off Hours, app blocker for iPhone and Android: Put the phone down in the evening, without a fight "
                  "with your willpower.",
        "skip": "Skip to content",
        "nav_label": "Main navigation",
        "nav": [("#how-it-works", "How it works", True), ("#pricing", "Pricing", True), ("#faq", "FAQ", True),
                ("#press", "Press", False), ("support/#support-for-off-hours", "Support", False)],
        "kicker": "App blocker for iPhone and Android",
        "claim": ["Put the phone down in the evening,", "without a fight with your willpower."],
        "lead": "Off Hours holds the apps that keep you up at night during the hours you set. When you open one of them, "
                "your phone first shows a short cooling-off. Then you decide on purpose: take a break, or make an "
                "exception. No ban, no tricks, just a moment to think.",
        "apple_country": "gb",
        "badge_apple": "badge-en.svg", "badge_apple_alt": "Download on the App Store",
        "badge_play": "google-play-en.png", "badge_play_alt": "Get it on Google Play",
        "price": "Free. Off Hours Plus €9.99 a year or €3.99 a month (Austrian price; Apple and Google convert it for "
                 "each country, the exact price is shown in the app).",
        "video_button": "Watch the video",
        "video_label": "App preview of Off Hours on iPhone",
        "video_caption": "iPhone app preview · 22 s, with sound",
        "video_fallback": "Your browser cannot play the video here:",
        "video_download": "Download the video (MP4)",
        "gallery_label": "Images from the App Store",
        "glance": "At a glance",
        "how_id": "how-it-works",
        "how_intro": "How it works: on iPhone, Off Hours uses Screen Time in iOS. On Android, Off Hours uses the "
                     "accessibility service, which you turn on once. From then on the cooling-off starts on time, even "
                     "when Off Hours is closed.",
        "ios_h": "iPhone", "ios_req": "iOS 17 or later · uses Screen Time",
        "ios_os": "iOS 17 or later",
        "ios_steps": [
            "Set a time window, for example 21:00 to 07:00, on the days you choose.",
            "Pick the apps. Off Hours uses your iPhone's Screen Time for this.",
            "From then on iOS takes over: the cooling-off starts on time, even when Off Hours is closed.",
            "After an exception the app stays open for a few minutes, then the cooling-off applies again.",
            "Home Screen widget with the current status.",
        ],
        "android_h": "Android", "android_req": "Android 8.0 or later · uses the accessibility service",
        "android_os": "Android 8.0 or later",
        "android_steps": [
            "Set a time window, for example 21:00 to 07:00, on the days you choose.",
            "Pick the apps, one by one or as a whole category, from the list of apps on your phone.",
            "Turn on the accessibility service once. From then on the cooling-off starts on time, even when Off Hours "
            "is closed.",
            "After an exception the app stays open for a few minutes, then the cooling-off applies again.",
            "Home screen widget with the current status.",
        ],
        "android_video": "android-en",
        "android_video_caption": "Off Hours on Android in 30 seconds.",
        "yt_note": "Playing loads YouTube",
        "yt_play": "Play the video on YouTube",
        "price_id": "pricing",
        "free_h": "Free", "free_amount": "€0",
        "free": "One schedule with up to two apps, a 15-second cooling-off and a 5-minute exception.",
        "plus_h": "Off Hours Plus", "plus_amount": "€9.99 a year", "plus_amount_alt": "or €3.99 a month",
        "plus": [
            "More schedules, for example for weekends",
            "More than two apps per schedule, including whole categories (up to 50 apps per schedule on iPhone, no "
            "upper limit on Android)",
            "Cooling-off of 30 or 90 seconds, or lock the apps until the schedule ends",
            "Exception of 1, 5 or 15 minutes",
            "“Start now”: begin a schedule immediately, also from the widget",
        ],
        "fine": "Austrian prices; Apple and Google convert them for each country, the exact price is shown in the app. "
                "Plus is available as a yearly or monthly subscription. The subscription renews automatically until you "
                "cancel it: on iPhone in Settings under Apple Account › Subscriptions, on Android in Google Play under "
                "Payments and subscriptions. A subscription applies only to the platform you bought it on.",
        "honest_h": "Honestly",
        "honest": "Off Hours is an aid, not a safeguard against yourself. Any schedule can be switched off at any time. "
                  "Off Hours pauses apps, not websites. Some Android phones stop background services to save battery; "
                  "the app tells you where to switch that off for Off Hours.",
        "privacy_id": "privacy",
        "privacy_sub": "No account, no server, no analytics. Everything stays on your phone.",
        "privacy_cols": [
            ("On iPhone", "Off Hours stores the apps you choose only as encrypted identifiers from iOS. Only the shield "
             "receives an app's name, to display it. Off Hours does not see how long you use apps, and it records "
             "nothing."),
            ("On Android", "Off Hours uses Android's accessibility service only to notice which app is in front, and "
             "then shows the cooling-off over it. It does not read screen content, does not see what you type and "
             "records nothing. Off Hours does not see how long you use apps."),
        ],
        "privacy_more": ("privacy/", "Everything else is in the privacy policy"),
        "faq_id": "faq", "faq_h": "Frequently asked questions",
        "faq": [
            ("Is Off Hours the same as Downtime in Apple's Screen Time?",
             ["No. Apple's Downtime blocks apps during set hours. Off Hours builds on Screen Time and puts a cooling-off "
              "with a decision in front of the app instead of a ban: take a break, or make an exception. Off Hours is a "
              "separate app by nxtChange Consulting FlexCo, not by Apple."], None),
            ("Does Off Hours only work in the evening?",
             ["No. You set the time window yourself, for example 21:00 to 07:00, on the days you choose: evenings, work "
              "hours or all day. The free tier has one schedule; Off Hours Plus adds more, for example for weekends."],
             None),
            ("What does Off Hours need on Android, and why the accessibility service?",
             ["An Android phone with Android 8.0 or later and Android's accessibility service, which you turn on once in "
              "Settings. Android has no Screen Time interface for other apps, and without a device-admin or enterprise "
              "profile there is no other way to show a cooling-off over another app at a scheduled time.",
              "Off Hours uses the accessibility service only to notice which app is in front, and then shows the "
              "cooling-off over it. It does not read screen content, does not see what you type and records nothing. "
              "Before the app sends you to the accessibility settings, it explains this in a dialog."],
             ("access", "Demo of the accessibility service, from the dialog to the cooling-off over an app. With "
                        "subtitles.")),
            ("Does Off Hours see which apps I use?",
             ["No. No account, no server, no analytics: everything stays on your phone. On iPhone, Off Hours stores the "
              "apps you choose only as encrypted identifiers from iOS; only the shield receives an app's name, to "
              "display it. On Android, the accessibility service handles only the package name of the app in front "
              "and does not store it. Off Hours does not see how long you use apps, and it records nothing."], None),
            ("Can I get around the block?",
             ["Yes. Off Hours is an aid, not a safeguard against yourself. Any schedule can be switched off at any "
              "time. If you want it stricter, Off Hours Plus offers a cooling-off of 30 or 90 seconds or locks the "
              "apps until the schedule ends."], None),
            ("What does Off Hours cost?",
             ["Off Hours is free with one schedule for up to two apps, a 15-second cooling-off and a 5-minute "
              "exception. Off Hours Plus costs €9.99 a year or €3.99 a month (Austrian price; Apple and Google convert "
              "it for each country, the exact price is shown in the app). The subscription renews automatically until "
              "you cancel it."], None),
            ("Does Off Hours pause websites too?",
             ["No. Off Hours pauses apps, not websites. Whether notifications from a paused app appear is up to the "
              "system."], None),
            ("Which devices does Off Hours run on?",
             ["On iPhone with iOS 17 or later and on Android phones with Android 8.0 or later. Off Hours is available "
              "on the App Store and Google Play, in English and German."], None),
        ],
        "press_id": "press", "press_h": "Press",
        "press_intro": "Material for coverage, free to use without asking. Questions and review access:",
        "press_short_h": "Short description",
        "press_short": "Off Hours is an app for iPhone and Android from Graz, Austria, that holds the apps you choose "
                       "during the hours you set and adds a short cooling-off first. Users then decide on purpose: take "
                       "a break or make an exception. On iPhone, Off Hours uses Screen Time; on Android, the "
                       "accessibility service. The app needs no account, no server and no analytics; all data stays on "
                       "the device. Off Hours is free with one schedule for up to two apps; Off Hours Plus extends it. "
                       "The developer is nxtChange Consulting FlexCo.",
        "press_facts_h": "Facts",
        "press_facts": [
            ("Name", f"Off Hours (German: Auszeit), in the stores “{STORE_NAME['en']}”"),
            ("Platforms", "iPhone (iOS 17 or later) and Android (8.0 or later)"),
            ("Released", "October 2026"),
            ("Countries", "37 on the App Store, 36 on Google Play, all in Europe"),
            ("Languages", "English and German"),
            ("Price", "Free; Off Hours Plus €9.99 a year or €3.99 a month (Austrian price)"),
            ("Founder", "Karl Maier, one-person project without investors"),
            ("Developer", "nxtChange Consulting FlexCo, Graz, Austria"),
        ],
        "founder_id": "founder", "founder_h": "Founder", "founder_name": "Karl Maier",
        "founder_role": "Founder and developer of Off Hours · nxtChange Consulting FlexCo, Graz, Austria",
        "founder_job": "Founder and developer of Off Hours",
        "founder_intro": "Karl Maier, a management consultant from Graz, Austria, released Off Hours for iPhone and Android "
                         "in early October 2026: a one-person project without investors, through his company nxtChange "
                         "Consulting FlexCo. The reason was personal.",
        "founder_quote": "Often I just wanted to take a quick look at Instagram, and then two hours were gone.",
        "founder_quote_by": "Karl Maier, founder of Off Hours",
        "founder_after": "Off Hours interrupts that reflex. During a time window of your choice, usually in the evening, "
                         "around the clock if you like, the apps you pick first show a short pause with a countdown. Then "
                         "you decide on purpose: take a break or make an exception. No account, no server, no tracking.",
        "founder_note": "Quote and text are free to use for coverage. The quote is translated from German.",
        "q_open": "“", "q_close": "”",
        "photo_alt": "Karl Maier, founder and developer of Off Hours, landscape portrait",
        "photo_credit_label": "Photo", "photo_download": "Download the print-size photo",
        "files_founder_h": "Founder photo", "files_founder": "Karl Maier, landscape 3:2",
        "press_files_h": "Files",
        "kit": "off-hours-press-kit-en", "kit_label": "Download the press kit",
        "kit_meta": "ZIP with all {n} files, {size}",
        "files_icon_h": "App icon", "files_icon": "App icon",
        "files_ios_h": "iPhone, App Store", "files_android_h": "Android, Google Play",
        "footer_links": [("support/#support-for-off-hours", "Support"), ("privacy/", "Privacy Policy"),
                         ("terms/", "Terms of Use"), ("imprint/", "Legal Notice"),
                         ("https://nxtchange.app/", "All apps")],
        "provider_h": "Provider", "country": "Austria",
        "register": "FN 648962g, Landesgericht für ZRS Graz · UID ATU81922038",
        "footnotes": ["Apple, iPhone and App Store are trademarks of Apple Inc.",
                      "Google Play and the Google Play logo are trademarks of Google LLC."],
        "category": "Productivity",
        "decimal": ".",
    },
}

NOT_FOUND = {
    "lang": "de", "root": "/", "name": "Auszeit",
    "title": "Seite nicht gefunden · Auszeit",
    "meta_desc": "Diese Seite gibt es auf auszeit.nxtchange.app nicht.",
    "label": "Fehler 404",
    "h": ["Diese Seite", "gibt es nicht."],
    "text": "Vielleicht hat sich die Adresse geändert. Von hier geht es weiter:",
    "links": [("/", "Startseite"), ("/support/", "Support"), ("/datenschutz/", "Datenschutz")],
    "en_text": "This page does not exist.",
    "en_links": [("/en/", "Off Hours in English"), ("/support/#support-for-off-hours", "Support")],
}

e = html.escape


# ---------------------------------------------------------------------------------------------------------------- Dateien

def png_size(path: pathlib.Path) -> tuple:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"{path}: kein PNG")
    return struct.unpack(">II", data[16:24])


def jpeg_size(path: pathlib.Path) -> tuple:
    data = path.read_bytes()
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    raise SystemExit(f"{path}: Größe nicht gefunden")


def image_size(path: pathlib.Path) -> tuple:
    return jpeg_size(path) if path.suffix == ".jpg" else png_size(path)


def need(rel: str) -> pathlib.Path:
    path = ROOT / "assets" / rel
    if not path.is_file():
        raise SystemExit(f"Fehlt: assets/{rel} (erst sh tools/assets.sh laufen lassen)")
    return path


def size_label(n: int, t: dict) -> str:
    if n >= 1024 * 1024:
        return f"{n / 1024 / 1024:.1f}".replace(".", t["decimal"]) + " MB"
    return f"{round(n / 1024)} KB"


def img(rel: str, root: str) -> str:
    """Bild unter assets/, bei --inline als data:-URI."""
    path = need(rel)
    if INLINE:
        mime = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg"}[path.suffix]
        return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"
    return f"{root}assets/{rel}"


def file(rel: str, root: str) -> str:
    """Datei unter assets/ (Video, Downloads); die Vorschau verweist ins Repo."""
    need(rel)
    if INLINE and root != "/":
        return f"../{root}assets/{rel}".replace("/./", "/")
    return f"{root}assets/{rel}"


def page_link(href: str, root: str) -> str:
    """Link auf eine andere Seite der Website; in der Vorschau auf die Live-Seite, die es lokal nicht gibt."""
    if href.startswith(("https://", "mailto:", "#")):
        return href
    if INLINE and not href.startswith("/"):
        return f"{SITE}/{href}"
    return root + href if not href.startswith("/") else href


def css(root: str) -> str:
    path = ROOT / "assets" / "css" / "site.css"
    text = path.read_text(encoding="utf-8")
    if INLINE:
        return f"<style>\n{text}</style>"
    version = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f'<link rel="stylesheet" href="{root}assets/css/site.css?v={version}">'


# ------------------------------------------------------------------------------------------------------------- Bausteine

def lines_html(lines: list, tag: str, cls: str = "") -> str:
    spans = " ".join(f'<span class="accent">{e(x)}</span>' if i == len(lines) - 1 else f"<span>{e(x)}</span>"
                     for i, x in enumerate(lines))
    return f'<{tag} class="lines{" " + cls if cls else ""}">{spans}</{tag}>'


def section_head(slide: tuple, sub: str = None, tag: str = "h2") -> str:
    _, label, lines, slide_sub = slide
    return (f'<div class="section-head">\n      <p class="label">{e(label)}</p>\n      {lines_html(lines, tag)}\n'
            f'      <p class="sub">{e(sub if sub is not None else slide_sub)}</p>\n    </div>')


def stores(t: dict, root: str) -> str:
    apple = img(f"img/{t['badge_apple']}", root)
    play = img(f"img/{t['badge_play']}", root)
    pw, ph = png_size(need(f"img/{t['badge_play']}"))
    return (f'<div class="stores">\n'
            f'        <a href="{e(apple_url(t["apple_country"]))}"><img class="badge-apple" src="{apple}" '
            f'alt="{e(t["badge_apple_alt"])}" width="162" height="54"></a>\n'
            f'        <a href="{e(PLAY_URL)}"><img class="badge-play-{t["lang"]}" src="{play}" '
            f'alt="{e(t["badge_play_alt"])}" width="{pw}" height="{ph}"></a>\n      </div>')


PLAY_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="10.5" fill="none" '
             'stroke="currentColor" stroke-width="1.5"/><path d="M10 7.8 16.2 12 10 16.2z" fill="currentColor"/></svg>')
YT_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 4.5v15l12.5-7.5z" '
           'fill="#FAF0DE"/></svg>')
DOWNLOAD_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 3v12m0 0-5-5m5 5 5-5M4 '
                 '17v3h16v-3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
                 'stroke-linejoin="round"/></svg>')
HOURGLASS = ('<svg class="hourglass" viewBox="0 0 44 60" aria-hidden="true" focusable="false"><path d="M5 3h34M5 57h34" '
             'stroke="currentColor" stroke-width="4.5" stroke-linecap="round"/><path d="M10 5c0 13 8 18 12 25-4 7-12 '
             '12-12 25h24c0-13-8-18-12-25 4-7 12-12 12-25" fill="none" stroke="currentColor" stroke-width="3.5" '
             'stroke-linejoin="round"/><path d="M13.5 53c1.5-7 5.5-10 8.5-13 3 3 7 6 8.5 13z" fill="currentColor"/>'
             '<path d="M16 15h12c-1.2 4-3.6 6.4-6 9-2.4-2.6-4.8-5-6-9z" fill="currentColor" opacity=".55"/></svg>')


def youtube(key: str, t: dict, root: str, caption: str, row: bool = False) -> str:
    """Klick-Fassade: lokales Standbild mit Play-Symbol und Hinweis; erst der Klick lädt youtube-nocookie.com.
    Ohne JavaScript ist das Standbild ein Link zum Video auf YouTube."""
    vid, title = YOUTUBE[key]
    thumb = f"img/video/{vid}.jpg"
    w, h = jpeg_size(need(thumb))
    if row:
        cap = f'<strong>{e(caption)}</strong><span lang="{"de" if "Auszeit" in title else "en"}">{e(title)}</span>'
    elif t["lang"] == "de" and key == "access":
        cap = f'{e(caption)} <span lang="en">„{e(title)}“</span>'
    else:
        cap = e(caption)
    return (f'<figure class="film{" film-row" if row else ""}">\n'
            f'        <div class="yt-box">\n'
            f'          <a class="yt" href="https://www.youtube.com/watch?v={vid}" data-yt="{vid}" data-title="{e(title)}">\n'
            f'            <img src="{img(thumb, root)}" alt="" width="{w}" height="{h}" loading="lazy" decoding="async">\n'
            f'            <span class="yt-play">{YT_ICON}<span class="visually-hidden">{e(t["yt_play"])}: {e(title)}</span></span>\n'
            f'            <span class="yt-note"><span>{e(t["yt_note"])}</span></span>\n'
            f'          </a>\n'
            f'        </div>\n'
            f'        <figcaption>{cap}</figcaption>\n'
            f'      </figure>')


def top(t: dict, root: str, home: str, nav: list, other: tuple) -> str:
    icon = img("img/icon-180.png", root)
    wide_class = ' class="wide"'
    links = "\n".join(f'        <a href="{e(page_link(href, root))}"{wide_class if wide else ""}>{e(label)}</a>'
                      for href, label, wide in nav)
    href, lang, label = other
    return (f'<div class="wrap top">\n'
            f'      <a class="brand" href="{home}"><img src="{icon}" alt="" width="36" height="36"><span>{e(t["name"])}</span></a>\n'
            f'      <nav aria-label="{e(t["nav_label"])}">\n{links}\n'
            f'        <a href="{href}" lang="{lang}" hreflang="{lang}">{e(label)}</a>\n'
            f'      </nav>\n    </div>')


def footer(t: dict, root: str, home: str) -> str:
    icon = img("img/icon-180.png", root)
    links = "\n".join(f'        <a href="{e(page_link(href, root))}">{e(label)}</a>' for href, label in t["footer_links"])
    notes = " ".join(e(x) for x in t["footnotes"])
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="foot-top">
      <a class="brand" href="{home}"><img src="{icon}" alt="" width="36" height="36"><span>{e(t['name'])}</span></a>
      <nav class="foot-links" aria-label="{e(t['footer_links'][0][1])}, {e(t['footer_links'][1][1])}">
{links}
      </nav>
    </div>
    <address>
      <strong>{e(t['provider_h'])}:</strong> nxtChange Consulting FlexCo · Neugasse 9/1 · 8045 Graz, {e(t['country'])}<br>
      {e(t['register'])} · <a href="mailto:{EMAIL}">{EMAIL}</a>
    </address>
    <p class="note">{notes}</p>
  </div>
</footer>"""


SCRIPT = """<script>
/* Videos erst auf Klick: App-Vorschau (selbst gehostet) und YouTube (youtube-nocookie.com). Sonst kein JavaScript. */
(function () {
  var d = document;
  Array.prototype.forEach.call(d.querySelectorAll("button[data-play]"), function (button) {
    var video = d.getElementById(button.getAttribute("data-play"));
    if (!video) return;
    video.removeAttribute("controls");
    button.hidden = false;
    button.addEventListener("click", function () {
      video.setAttribute("controls", "");
      button.hidden = true;
      video.play();
      video.focus();
    });
  });
  d.addEventListener("click", function (event) {
    var link = event.target.closest && event.target.closest("a[data-yt]");
    if (!link) return;
    event.preventDefault();
    var frame = d.createElement("iframe");
    frame.src = "https://www.youtube-nocookie.com/embed/" + link.getAttribute("data-yt") + "?autoplay=1&rel=0";
    frame.title = link.getAttribute("data-title");
    frame.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
    frame.allowFullscreen = true;
    link.parentNode.replaceChild(frame, link);
    frame.focus();
  });
})();
</script>"""


# ---------------------------------------------------------------------------------------------------------------- JSON-LD

def jsonld(t: dict) -> str:
    lang = t["lang"]
    home = SITE + t["path"]
    org_id = SITE + "/#organisation"
    common = {
        "applicationCategory": "UtilitiesApplication",
        "applicationSubCategory": t["category"],
        "description": t["meta_desc"],
        "inLanguage": ["de", "en"],
        "image": f"{SITE}/assets/press/auszeit-icon-1024.png",
        "url": home,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
        "publisher": {"@id": org_id},
    }
    founder = {
        "@type": "Person", "@id": SITE + "/#karl-maier", "name": "Karl Maier", "jobTitle": t["founder_job"],
        "worksFor": {"@id": org_id}, "sameAs": [LINKEDIN],
        "image": {"@type": "ImageObject", "contentUrl": f"{SITE}/assets/{FOUNDER_PHOTO['press']}",
                  "creditText": PHOTO_CREDIT, "copyrightNotice": PHOTO_CREDIT, "caption": t["photo_alt"]},
    }
    graph = [
        {"@type": "Organization", "@id": org_id, "name": "nxtChange Consulting FlexCo", "url": "https://nxtchange.app/",
         "email": EMAIL, "vatID": "ATU81922038", "founder": founder,
         "address": {"@type": "PostalAddress", "streetAddress": "Neugasse 9/1", "postalCode": "8045",
                     "addressLocality": "Graz", "addressCountry": "AT"}},
        {"@type": "MobileApplication", "@id": home + "#app-ios", "name": STORE_NAME[lang],
         "operatingSystem": t["ios_os"], "installUrl": f"https://apps.apple.com/{t['apple_country']}/app/id{APP_ID}",
         "screenshot": [f"{SITE}/assets/img/{lang}/{s[0]}" for s in SLIDES[lang]], **common},
        {"@type": "MobileApplication", "@id": home + "#app-android", "name": STORE_NAME[lang],
         "operatingSystem": t["android_os"], "installUrl": f"https://play.google.com/store/apps/details?id={PLAY_ID}",
         "screenshot": [f"{SITE}/assets/press/{lang}-android-{f}" for f, _ in ANDROID[lang][:5]], **common},
        {"@type": "FAQPage", "@id": home + "#" + t["faq_id"], "inLanguage": lang,
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": " ".join(answer)}}
                        for q, answer, _ in t["faq"]]},
    ]
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    return data.replace("</", "<\\/")


# ------------------------------------------------------------------------------------------------------------------ Seiten

def head(t: dict, root: str, title: str, desc: str, extra: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="{t['lang']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
{extra}
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#FAF3E6" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#101424" media="(prefers-color-scheme: dark)">
  <link rel="icon" href="{img('img/icon-64.png', root)}" type="image/png">
  <link rel="apple-touch-icon" href="{img('img/icon-180.png', root)}">
  {css(root)}"""


def home_page(t: dict) -> str:
    lang, root = t["lang"], t["root"]
    url = SITE + t["path"]
    slides = SLIDES[lang]
    og = f"{SITE}/assets/img/og-{lang}.png"
    ow, oh = png_size(need(f"img/og-{lang}.png"))
    meta = f"""  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="de" href="{SITE}/">
  <link rel="alternate" hreflang="en" href="{SITE}/en/">
  <link rel="alternate" hreflang="x-default" href="{SITE}/">
  <meta name="apple-itunes-app" content="app-id={APP_ID}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{e(t['name'])}">
  <meta property="og:title" content="{e(t['title'])}">
  <meta property="og:description" content="{e(t['meta_desc'])}">
  <meta property="og:url" content="{url}">
  <meta property="og:locale" content="{t['locale']}">
  <meta property="og:locale:alternate" content="{t['other_locale']}">
  <meta property="og:image" content="{og}">
  <meta property="og:image:width" content="{ow}">
  <meta property="og:image:height" content="{oh}">
  <meta property="og:image:alt" content="{e(t['og_alt'])}">
  <meta name="twitter:card" content="summary_large_image">"""

    # Galerie: sechs Store-Bilder, 1200 px hoch, Alt-Text aus dem Bildtext.
    gallery = []
    for f, label, lines, sub in slides:
        w, h = png_size(need(f"img/{lang}/{f}"))
        alt = f"{label}: {' '.join(lines)} {sub}"
        gallery.append(f'        <li><img src="{img(f"img/{lang}/{f}", root)}" alt="{e(alt)}" width="{w}" height="{h}" '
                       f'loading="lazy" decoding="async"></li>')
    pw, ph = png_size(need(f"img/{lang}/{slides[0][0]}"))

    tiles = "\n".join(
        f'      <article class="tile">\n        <p class="label">{e(slides[i][1])}</p>\n'
        f'        {lines_html(slides[i][2], "h3")}\n        <p class="sub">{e(slides[i][3])}</p>\n      </article>'
        for i in (0, 2, 4))

    def steps(items):
        return "\n".join(f"            <li>{e(x)}</li>" for x in items)

    plus = "\n".join(f"            <li>{e(x)}</li>" for x in t["plus"])
    cols = "\n".join(f'        <div>\n          <h3>{e(h)}</h3>\n          <p>{e(p)}</p>\n        </div>'
                     for h, p in t["privacy_cols"])

    faq = []
    for q, answer, film in t["faq"]:
        body = "\n".join(f"          <p>{e(p)}</p>" for p in answer)
        if film:
            body += "\n          " + youtube(film[0], t, root, film[1])
        faq.append(f'      <details>\n        <summary>{e(q)}</summary>\n        <div class="answer">\n{body}\n'
                   f'        </div>\n      </details>')

    facts = "\n".join(f"          <dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in t["press_facts"])

    def entry(rel: str, label: str, extra: str = "") -> str:
        path = need(rel)
        w, h = image_size(path)
        kind = "JPEG" if path.suffix == ".jpg" else "PNG"
        meta_text = f"{kind}, {w} × {h} px, {size_label(path.stat().st_size, t)}" + (f", {extra}" if extra else "")
        return f'            <li><a href="{file(rel, root)}" download>{e(label)}</a><small>{e(meta_text)}</small></li>'

    ios_files = "\n".join(entry(f"press/{lang}-{f}", f"{i}. {' '.join(lines)}")
                          for i, (f, _, lines, _) in enumerate(slides, 1))
    android_files = "\n".join(entry(f"press/{lang}-android-{f}", (f"{i}. {label}" if i <= 5 else label))
                              for i, (f, label) in enumerate(ANDROID[lang], 1))
    photo_w, photo_h = image_size(need(FOUNDER_PHOTO["web"]))
    credit = f"{t['photo_credit_label']}: {PHOTO_CREDIT}"
    kit_path = need(f"press/{t['kit']}.zip")
    kit_meta = t["kit_meta"].format(n=2 + len(slides) + len(ANDROID[lang]), size=size_label(kit_path.stat().st_size, t))
    video_rel = f"video/store-video-{lang}.mp4"

    nav_other = (t["other_href"], t["other_lang"], t["other_label"])
    return f"""{head(t, root, t['title'], t['meta_desc'], meta)}
  <script type="application/ld+json">
{jsonld(t)}
  </script>
</head>
<body>
<a class="skip" href="#inhalt">{e(t['skip'])}</a>
<header class="band">
    {top(t, root, "./", t['nav'], nav_other)}
  <div class="wrap hero-grid" id="inhalt">
    <div class="hero-text">
      <p class="label">{e(t['kicker'])}</p>
      {lines_html(t['claim'], 'h1')}
      <p class="lead">{e(t['lead'])}</p>
      {stores(t, root)}
      <p class="price">{e(t['price'])}</p>
    </div>
    <figure class="hero-video">
      <div class="screen">
        <video id="vorschau" controls preload="none" playsinline poster="{img(f'img/{lang}/{slides[0][0]}', root)}" width="{pw}" height="{ph}" aria-label="{e(t['video_label'])}">
          <source src="{file(video_rel, root)}" type="video/mp4">
          <p>{e(t['video_fallback'])} <a href="{file(video_rel, root)}">{e(t['video_download'])}</a></p>
        </video>
        <button class="play" type="button" data-play="vorschau" hidden>{PLAY_ICON}{e(t['video_button'])}</button>
      </div>
      <figcaption>{e(t['video_caption'])}</figcaption>
    </figure>
  </div>
</header>

<main>
  <section class="gallery-band" aria-label="{e(t['gallery_label'])}">
    <ul class="gallery" tabindex="0" aria-label="{e(t['gallery_label'])}">
{chr(10).join(gallery)}
    </ul>
  </section>

  <section class="wrap" aria-labelledby="glance">
    <h2 class="visually-hidden" id="glance">{e(t['glance'])}</h2>
    <div class="trio">
{tiles}
    </div>
  </section>

  <section class="wrap section" id="{t['how_id']}">
    {section_head(slides[1])}
    <p class="intro">{e(t['how_intro'])}</p>
    <div class="cards">
      <article class="card" id="iphone">
        <h3>{e(t['ios_h'])}</h3>
        <p class="req">{e(t['ios_req'])}</p>
        <ol class="steps">
{steps(t['ios_steps'])}
        </ol>
        <div class="stores"><a href="{e(apple_url(t['apple_country']))}"><img class="badge-apple" src="{img(f"img/{t['badge_apple']}", root)}" alt="{e(t['badge_apple_alt'])}" width="162" height="54" loading="lazy"></a></div>
      </article>
      <article class="card" id="android">
        <h3>{e(t['android_h'])}</h3>
        <p class="req">{e(t['android_req'])}</p>
        <ol class="steps">
{steps(t['android_steps'])}
        </ol>
        <div class="stores"><a href="{e(PLAY_URL)}"><img class="badge-play-{lang}" src="{img(f"img/{t['badge_play']}", root)}" alt="{e(t['badge_play_alt'])}" width="646" height="250" loading="lazy"></a></div>
      </article>
    </div>
    {youtube(t['android_video'], t, root, t['android_video_caption'], row=True)}
  </section>

  <section class="wrap section" id="{t['price_id']}">
    {section_head(slides[3])}
    <div class="plans">
      <div>
        <article class="plan">
          <h3>{e(t['free_h'])}</h3>
          <p class="amount">{e(t['free_amount'])}</p>
          <p>{e(t['free'])}</p>
        </article>
        <aside class="honest">
          <h3>{e(t['honest_h'])}</h3>
          <p>{e(t['honest'])}</p>
        </aside>
      </div>
      <article class="plan plus">
        <h3>{e(t['plus_h'])}</h3>
        <p class="amount">{e(t['plus_amount'])}<small>{e(t['plus_amount_alt'])}</small></p>
        <ul>
{plus}
        </ul>
      </article>
    </div>
    <p class="fine">{e(t['fine'])}</p>
  </section>

  <section class="quiet" id="{t['privacy_id']}">
    <div class="wrap">
      {HOURGLASS}
      <p class="label">{e(slides[5][1])}</p>
      {lines_html(slides[5][2], 'h2')}
      <hr class="rule">
      <p class="sub">{e(t['privacy_sub'])}</p>
      <div class="columns">
{cols}
      </div>
      <p class="more"><a href="{e(page_link(t['privacy_more'][0], root))}">{e(t['privacy_more'][1])}</a></p>
    </div>
  </section>

  <section class="wrap section" id="{t['faq_id']}">
    <h2>{e(t['faq_h'])}</h2>
    <div class="faq">
{chr(10).join(faq)}
    </div>
  </section>

  <section class="wrap section press" id="{t['press_id']}">
    <h2>{e(t['press_h'])}</h2>
    <p class="sub">{e(t['press_intro'])} <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    <div class="press-grid" style="margin-top:28px">
      <div>
        <h3>{e(t['press_short_h'])}</h3>
        <p>{e(t['press_short'])}</p>
        <a class="kit" href="{file(f"press/{t['kit']}.zip", root)}" download>{DOWNLOAD_ICON}<span>{e(t['kit_label'])}</span></a>
        <p class="price">{e(kit_meta)}</p>
      </div>
      <div>
        <h3>{e(t['press_facts_h'])}</h3>
        <dl class="facts">
{facts}
        </dl>
      </div>
    </div>
    <div class="founder" id="{t['founder_id']}">
      <figure class="founder-photo">
        <img src="{img(FOUNDER_PHOTO['web'], root)}" alt="{e(t['photo_alt'])}" width="{photo_w}" height="{photo_h}" loading="lazy" decoding="async">
        <figcaption>{e(credit)} · <a href="{file(FOUNDER_PHOTO['press'], root)}" download>{e(t['photo_download'])}</a></figcaption>
      </figure>
      <div class="founder-text">
        <p class="label">{e(t['founder_h'])}</p>
        <h3>{e(t['founder_name'])}</h3>
        <p class="req">{e(t['founder_role'])}</p>
        <p>{e(t['founder_intro'])}</p>
        <blockquote>
          <p>{e(t['q_open'])}{e(t['founder_quote'])}{e(t['q_close'])}</p>
          <footer>{e(t['founder_quote_by'])}</footer>
        </blockquote>
        <p>{e(t['founder_after'])}</p>
        <p class="fine">{e(t['founder_note'])}</p>
      </div>
    </div>
    <h3 class="visually-hidden">{e(t['press_files_h'])}</h3>
    <div class="files">
      <div>
        <h4>{e(t['files_icon_h'])}</h4>
        <ul>
{entry("press/auszeit-icon-1024.png", t['files_icon'])}
        </ul>
      </div>
      <div>
        <h4>{e(t['files_ios_h'])}</h4>
        <ul>
{ios_files}
        </ul>
      </div>
      <div>
        <h4>{e(t['files_android_h'])}</h4>
        <ul>
{android_files}
        </ul>
      </div>
      <div>
        <h4>{e(t['files_founder_h'])}</h4>
        <ul>
{entry(FOUNDER_PHOTO['press'], t['files_founder'], credit)}
        </ul>
      </div>
    </div>
  </section>
</main>

{footer(t, root, "./")}
{SCRIPT}
</body>
</html>
"""


def not_found_page() -> str:
    t = dict(TEXT["de"])
    n = NOT_FOUND
    root = n["root"]
    meta = '  <meta name="robots" content="noindex">'
    links = "\n".join(f'      <a href="{href}">{e(label)}</a>' for href, label in n["links"])
    en_links = " · ".join(f'<a href="{href}">{e(label)}</a>' for href, label in n["en_links"])
    nav = [("/support/", "Support", False)]
    return f"""{head(t, root, n['title'], n['meta_desc'], meta)}
</head>
<body>
<header class="band page-band">
    {top(t, root, "/", nav, ("/en/", "en", "English"))}
</header>
<main class="wrap notfound">
  <p class="label">{e(n['label'])}</p>
  {lines_html(n['h'], 'h1')}
  <p class="lead">{e(n['text'])}</p>
  <nav class="links" aria-label="{e(n['label'])}">
{links}
  </nav>
  <p lang="en">{e(n['en_text'])} {en_links}</p>
</main>

{footer(t, root, "/")}
</body>
</html>
"""


for lang, t in TEXT.items():
    target = OUT / ("index.html" if lang == "de" else "en/index.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(home_page(t), encoding="utf-8")
    print(f"{target} ({target.stat().st_size // 1024} KB)")
target = OUT / "404.html"
target.write_text(not_found_page(), encoding="utf-8")
print(f"{target} ({target.stat().st_size // 1024} KB)")
