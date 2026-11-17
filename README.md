# schwimmoper-saunakalender

Kostenloser, öffentlich abonnierbarer **inoffizieller** ICS-Kalender für ausdrücklich angekündigte Schließungen der Wuppertaler Schwimmoper. Keine Verbindung zur Stadt Wuppertal. Keine Garantie für Vollständigkeit oder Aktualität.

**Kalender:** https://1-connexion.github.io/schwimmoper-saunakalender/sauna.ics  
**Status und Hinweise:** https://1-connexion.github.io/schwimmoper-saunakalender/

Die URL ist nach erfolgreicher Einrichtung von GitHub Pages verfügbar und bleibt bei unverändertem Konto-/Repositorynamen stabil. Ein leerer Kalender bedeutet nicht, dass die Sauna geöffnet ist.

## Abonnieren

- **Apple Kalender (Mac):** Ablage → Neues Kalenderabonnement → die HTTPS-Kalenderadresse einfügen → Abonnieren. Automatische Aktualisierung z. B. täglich einstellen. Auf iPhone/iPad unter Einstellungen → Apps → Kalender → Kalenderaccounts → Account hinzufügen → Andere → Kalenderabo hinzufügen (Bezeichnungen je nach iOS-Version). Alternativ die Adresse mit `webcal://` anstelle von `https://` öffnen.
- **Google Kalender (Web):** Neben „Weitere Kalender“ auf + → „Per URL“ → die öffentliche HTTPS-Kalenderadresse einfügen → Kalender hinzufügen. Das Abo erscheint anschließend auch in den verbundenen Apps. Google bestimmt den Aktualisierungsrhythmus; neue Meldungen können verspätet erscheinen.

**Abonnieren statt eine Datei zu importieren:** Ein Dateiimport aktualisiert sich nicht automatisch.

## Quellen und Grenzen

Geprüft am 17.11.2026:

- [Schwimmoper](https://www.wuppertal.de/tourismus-freizeit/baeder/schwimmoper.php): HTML `article#SP-Content`, Textabsätze unter den geänderten Öffnungszeiten. Zwei explizite Gesamtbad-Schließungen, Beginn mit Uhrzeit, Ende als einschließlich angegebenes Datum.
- [Städtische Bäder](https://www.wuppertal.de/tourismus-freizeit/baeder/staedtische_baeder.php): nur der mit der Schwimmoper-Detailseite verknüpfte Teaser wird ausgewertet. Er bestätigt aktuell eine der Schließungen.
- [Bäderübersicht](https://www.wuppertal.de/tourismus-freizeit/baeder/index.php): Verzeichnis und Links; kein eigenständiger Terminfeed.
- [Feiertagsregelung](https://www.wuppertal.de/Feiertagsregelung_2026.pdf): PDF wird **nicht** automatisch ausgewertet. Keine OCR und keine Ableitung von Schließungen aus Öffnungszeitentabellen.

Die aktuellen Meldungen nennen die gesamte Schwimmoper, nicht ausdrücklich die Sauna. Sie werden als **Gesamtbad-Schließungen** veröffentlicht; Beschreibungen machen die fehlende gesonderte Sauna-Bestätigung deutlich. Schwimmwettkämpfe, eingeschränkter Badebetrieb, geschlossene Cafeteria oder fremde Bäder allein begründen keinen Termin.

Der Parser akzeptiert ausschließlich das tatsächlich beobachtete Satzmuster mit vollständig genannten Daten, Wochentagen, Startuhrzeit und „bis einschließlich … geschlossen“. Numerische Jahre mit zwei Ziffern bedeuten ausdrücklich 2000–2099. Vierstellige Jahre und Punkt-/Doppelpunkt-Uhrzeiten sind getestet. Andere Formate, z. B. „18. Juli“, fehlende Jahre, offene Enden oder sauna-spezifische neue Formulierungen, werden bis zur manuellen Prüfung abgewiesen. Es gibt keine spekulative Datumserkennung. Der Kalender ist deshalb bewusst unvollständig.

## Verhalten bei Änderungen und Fehlern

- `requests` mit Zeitlimits, TLS-Prüfung, identifizierbarem User-Agent, 2-MB-Limit und ohne automatische Redirects oder Wiederholungen.
- `robots.txt` vor jedem Abrufzyklus prüfen; bei Fehler, Sperre, Redirect oder unerwartetem Inhalt abbrechen. Mindestens 3 Sekunden Abstand, längere Crawl-delay/Request-rate beachten. Bei 429 keine Wiederholung; nächster regulärer Tageslauf. Serverregeln mit mehr als 60 Sekunden Abstand benötigen manuelle Anpassung.
- Mindestens 23 Stunden zwischen Abrufversuchen, auch bei Fehlern, über `data/crawl.json` gespeichert. GitHub Actions läuft täglich um 05:17 UTC; Startzeiten können durch GitHub verzögert werden.
- Fehlgeschlagene Quellen oder widersprüchliche/überlappende Intervalle verwerfen die gesamte Aktualisierung. Letzte bestätigte Termine und ICS bleiben erhalten. Unbekannte einzelne Absätze erzeugen Warnungen und keine Termine.
- Entfernte Meldungen löschen bestätigte Termine **nicht** automatisch. `confirmed_at` zeigt die letzte Bestätigung je Termin. Veraltete oder abgesagte Termine müssen nach Quellenprüfung manuell in `data/confirmed.json` entfernt/korrigiert und der Kalender neu erzeugt werden. Geänderte Startdaten mit Überlappung erfordern ebenfalls manuelle Prüfung; nicht überlappende Verschiebungen können als zusätzlicher Termin erscheinen. Diese Grenze der automatischen Zuordnung ist bewusst sichtbar.
- Stabile UID aus Geltungsbereich und Startzeit, unabhängig von Abrufzeit und Quelle. Endzeitänderungen behalten die UID und erhöhen SEQUENCE. Bei unveränderten Terminen bleibt SEQUENCE gleich.
- `Europe/Berlin`, VTIMEZONE, UTF-8, CRLF, gefaltete Zeilen und exklusives DTEND. Ein einschließlich Sonntag genanntes Ende wird als Montag 00:00 Ortszeit dargestellt; keine erfundene Wiederöffnungsuhrzeit.
- Warnungen im Workflowprotokoll und in `public/status.json`. Bei Fehlern darf ein alter Kalender weiter veröffentlicht werden; der Status zeigt die fehlgeschlagene Aktualisierung an.

## Lokal ausführen

Python 3.12 oder neuer:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
pytest -q
schwimmoper-kalender
schwimmoper-kalender --validate public/sauna.ics
```

Keine Zugangsdaten erforderlich. Der normale Lauf beachtet das gespeicherte Mindestintervall. Zum bloßen Neuerzeugen aus bereits bestätigtem Bestand, ohne Netzabruf:

```sh
python -c "import json; from pathlib import Path; from schwimmoper_saunakalender.calendar import render; Path('public/sauna.ics').write_bytes(render(json.loads(Path('data/confirmed.json').read_text())))"
```

Die HTML-Testdaten sind synthetisch, bilden die geprüfte Seitenstruktur nach und enthalten keine kopierten vollständigen Stadtseiten. Tests prüfen auch negative Fälle, Quellenzuordnung, Zeitumstellungen, stabile UIDs, Konflikte, HTTP-/robots-Fehler und den Erhalt letzter bestätigter Daten.

## GitHub Actions und Pages

Der Workflow prüft Pull Requests ohne Netzabrufe oder Deployment. Auf `main`, täglich und manuell laufen Tests, Abruf, Validierung, Datensicherung als Commit und Pages-Deployment. Keine externen Bezahldienste und keine zusätzlichen Secrets nötig.

Falls noch erforderlich, unter Repository → Settings:

1. **Pages → Build and deployment → Source: GitHub Actions** auswählen.
2. **Actions → General:** GitHub Actions und die verwendeten offiziellen Actions zulassen. Der Workflow fordert `contents: write` nur im Aktualisierungsjob sowie `pages: write` und `id-token: write` nur im Deploymentjob an. Organisationsrichtlinien müssen diese Rechte zulassen.
3. Branchschutz/Rulesets müssen den Daten-Commit des Workflows auf `main` erlauben. Andernfalls muss die Persistenz auf einen separaten Datenbranch umgestellt werden; keine Schutzregeln pauschal deaktivieren.
4. Falls eine Freigabe für die Umgebung `github-pages` verlangt wird, das Deployment freigeben.
5. Unter Actions den Workflow einmal manuell starten und den erfolgreichen Pages-Job prüfen. Die Kalender-URL muss HTTP 200 und eine lesbare ICS-Datei liefern.

GitHub kann geplante Workflows bei Inaktivität öffentlicher Repositories deaktivieren; dann unter Actions wieder aktivieren. Status gelegentlich prüfen. Konto-/Repositoryumbenennung verändert die URL und erfordert ein neues Abo.

## Rechtliche Hinweise

[robots.txt](https://www.wuppertal.de/robots.txt) enthält beim Prüftermin keine Sperre für diesen Client auf den verwendeten Bäderseiten. Das ist keine rechtliche Nutzungserlaubnis. Das [Impressum](https://www.wuppertal.de/service/impressum.php) weist auf Urheberrechte und Zustimmungserfordernisse für die Vervielfältigung von Texten/Bildern hin. Veröffentlicht werden daher nur strukturierte Terminangaben mit selbst formulierten Beschreibungen und Quellenlinks; keine Stadtbilder, Logos oder vollständigen Meldungstexte. Bei geänderten Nutzungsbedingungen oder einem Widerspruch der Stadt Abrufe einstellen und die Nutzung prüfen. Es besteht kein Anspruch auf Vollständigkeit; vor einem Besuch immer die offizielle Quelle prüfen.
