#!/bin/sh
# Holt und erzeugt die Bilder und Videos der Startseite (die Pressemappen packt tools/build_site.py). Aufruf im Repo-Wurzelordner:
#
#   sh tools/assets.sh
#
# Quellen (außerhalb dieses Repos, nichts davon wird dort geändert):
#   Store-Bilder iPhone, hell:  ~/Documents/Auszeit App-Store-Bilder 2026-10-20/abend-hell/6.9-Zoll/{de,en}/
#                               (gebaut mit store/screenshots.swift im App-Repo auszeit)
#   Store-Video iPhone:         ~/Documents/Auszeit Store-Video 2026-10-20/store-video-{de,en}.mp4
#   Android-Bilder:             ../auszeit-android/store/upload/{de,en-GB}/
#   Google-Play-Abzeichen:      play.google.com/intl/{de_de,en_gb}/badges/… (offiziell, unverändert)
#   YouTube-Standbilder:        i.ytimg.com/vi/<id>/maxresdefault.jpg, sonst hqdefault.jpg
#   Gründerfoto (Porträt):      ../mappe-antrag-anhaenge/2-quellen/fotos/Foto_Karl_Maier.jpg (quadratisch, 1200 px)
# Heruntergeladen wird nur, was noch fehlt. Die ZIPs sind deterministisch (feste Zeitstempel, feste Reihenfolge,
# ohne Zusatzattribute), damit ein erneuter Lauf ohne neue Quellen keine Änderung im Repo erzeugt.
set -eu

STORE="$HOME/Documents/Auszeit App-Store-Bilder 2026-10-20/abend-hell/6.9-Zoll"
VIDEO="$HOME/Documents/Auszeit Store-Video 2026-10-20"
ANDROID="../auszeit-android/store/upload"
VIDEOS="TQRQjztSKBM JQcw7RqWnOs oJJUE4cR4yY"
FOTO="../mappe-antrag-anhaenge/2-quellen/fotos/Foto_Karl_Maier.jpg"
# Bildnachweis wie PHOTO_CREDIT in tools/build_site.py; landet in den Metadaten der JPEGs.
FOTO_NACHWEIS="nxtChange Consulting FlexCo"

mkdir -p assets/img/de assets/img/en assets/img/video assets/press assets/video

# Startseite: die sechs Store-Bilder je Sprache, 1200 px hoch.
for lang in de en; do
  rm -f assets/img/$lang/*.png
  for f in "$STORE/$lang"/*.png; do
    sips -Z 1200 "$f" --out "assets/img/$lang/$(basename "$f")" >/dev/null
  done
done

# Pressebilder in Originalgröße: iPhone (6,9 Zoll), Android (Telefon und Funktionsgrafik).
rm -f assets/press/de-*.png assets/press/en-*.png
for lang in de en; do
  for f in "$STORE/$lang"/*.png; do cp "$f" "assets/press/$lang-$(basename "$f")"; done
done
for f in "$ANDROID"/de/0[1-5]-*.png; do cp "$f" "assets/press/de-android-$(basename "$f")"; done
for f in "$ANDROID"/en-GB/0[1-5]-*.png; do cp "$f" "assets/press/en-android-$(basename "$f")"; done
cp "$ANDROID/de/funktionsgrafik-1024x500.png" assets/press/de-android-funktionsgrafik-1024x500.png
cp "$ANDROID/en-GB/feature-graphic-1024x500.png" assets/press/en-android-feature-graphic-1024x500.png

# Google-Play-Abzeichen, einmal geladen.
[ -s assets/img/google-play-de.png ] || curl -fsS -o assets/img/google-play-de.png \
  https://play.google.com/intl/de_de/badges/static/images/badges/de_badge_web_generic.png
[ -s assets/img/google-play-en.png ] || curl -fsS -o assets/img/google-play-en.png \
  https://play.google.com/intl/en_gb/badges/static/images/badges/en_badge_web_generic.png

# Standbilder der YouTube-Videos für die Klick-Fassade, einmal geladen.
for id in $VIDEOS; do
  [ -s "assets/img/video/$id.jpg" ] || curl -fsS -o "assets/img/video/$id.jpg" "https://i.ytimg.com/vi/$id/maxresdefault.jpg" \
    || curl -fsS -o "assets/img/video/$id.jpg" "https://i.ytimg.com/vi/$id/hqdefault.jpg"
done

# Vorschaubild für Teaser und die App-Vorschau als kleines MP4. Das Video trägt einen Zeitstempel im Container und
# entsteht deshalb nur, wenn es fehlt (zum Neubauen vorher löschen).
swift tools/og-bild.swift assets/press/auszeit-icon-1024.png assets/img
for lang in de en; do
  [ -s "assets/video/store-video-$lang.mp4" ] || swift tools/video.swift "$VIDEO/store-video-$lang.mp4" "assets/video/store-video-$lang.mp4"
done

# Gründerfoto im Querformat (3:2) für Presse und Website, aus dem quadratischen Porträt. Fehlt die Quelle auf diesem
# Rechner, bleiben die vorhandenen Dateien.
if [ -s "$FOTO" ]; then
  swift tools/gruenderfoto.swift "$FOTO" assets/press/karl-maier-1800x1200.jpg assets/img/karl-maier-1200x800.jpg \
    "$FOTO_NACHWEIS" "Karl Maier, MA, Gründer und Entwickler von Auszeit (Off Hours), Graz"
elif [ ! -s assets/press/karl-maier-1800x1200.jpg ] || [ ! -s assets/img/karl-maier-1200x800.jpg ]; then
  echo "Fehlt: $FOTO (Quelle für das Gründerfoto)" >&2; exit 1
fi

# Die Pressemappen (ZIP mit Icon, Gründerfoto, Pressetext und Bildern) packt tools/build_site.py, weil der Pressetext aus
# denselben Texten entsteht wie die Seite.
