# STATUS – Site (auszeit-legal)

## AUS-24 – Block „Presse über Auszeit“
- Umsetzung: index.html/en/index.html werden aus `tools/build_site.py` erzeugt, daher dort geändert (Texte `coverage_h`/`coverage`, Liste `.coverage`) und neu gebaut. Eintrag: Trending Topics, target="_blank" rel="noopener", EN mit hreflang="de". 404.html nur wegen neuer CSS-Version (?v=) geändert.
- CSS: 3 kleine Regeln `.coverage` in assets/css/site.css (Listenstil wie `.files li`, `overflow-wrap:anywhere` für sauberen Umbruch). Kein neues Skript, keine externen Ressourcen.
- preview/: wird vom Generator erzeugt und ist nicht im Repo (nicht versioniert) – unverändert gelassen.
- Mobilprüfung 375 px/Desktop: NICHT visuell geprüft. Im Container gibt es weder Jekyll/bundle noch Chromium/Playwright/ui-probe. Geprüft nur: Generator-Lauf fehlerfrei, HTML-Diff enthält ausschließlich den Block. Bitte Sicht auf dem Branch-Deploy/Vorschau nachholen.
- Uncommittete Änderungen im Arbeitsbaum (press-Zips, Datenschutz/Texte, build_site.py u. a.) wurden nicht angefasst; Arbeit im separaten Worktree von origin/main.
