# Quellenprüfung vom 17. November 2026

Direkter HTTPS-Abruf der offiziellen Schwimmoper-Seite, der Bäderübersicht, der städtischen Bäderseite, von robots.txt und Impressum. Suchmaschinen-Snippets waren teils älter als der direkte Abruf und werden nicht als Kalenderquelle verwendet.

HTML-Detailseite: `article#SP-Content`, normale `p`-Absätze; Öffnungszeiten Sauna als Strukturmarker. Medien mit Öffnungszeitangaben stehen zusätzlich als Bilder bereit. Geschlossene Cafeteria und allgemeine Beschreibungen werden nicht als Schließungsereignis übernommen. Veröffentlichte Beschreibungen werden selbst formuliert.

Eindeutig genannte Gesamtbad-Zeiträume:

| Beginn (Europe/Berlin) | Ende laut Quelle | Exklusives ICS-Ende |
| --- | --- | --- |
| 19.11.2026 18:00 | einschließlich 22.11.2026 | 23.11.2026 00:00 |
| 04.12.2026 08:00 | einschließlich 07.12.2026 | 08.12.2026 00:00 |

Die städtische Bäderseite bestätigt den ersten Zeitraum im Schwimmoper-Teaser (`a.SP-Teaser` mit exakt zugehörigem href, darin `.SP-Teaser__abstract`). Andere Teaser betreffen andere Bäder, teilweise mit beiläufigem Verweis auf die Schwimmoper. Sie dürfen keinesfalls zusammen mit deren Daten ausgewertet werden.

Die Bäderübersicht ist ein Verzeichnis ohne separaten Terminfeed. Feiertagsregelungen liegen als PDF vor; ihre Tabellen werden nicht automatisch zu Saunaschließungen umgedeutet. Neue Satzmuster, reine Bildmeldungen, unklare Endzeiten oder reine Sauna-Hinweise benötigen zusätzliche manuelle Quellenprüfung und passende Negativtests.

Keine gesonderte Sauna-Schließungsbestätigung gefunden. Die Ausgabe benennt deshalb den offiziellen Geltungsbereich „Gesamtbad“ und die Einschränkung ausdrücklich. Es werden keine normalen wöchentlichen Schließzeiten aus Öffnungszeitentabellen ergänzt.

robots.txt: Beim Prüftermin explizite Googlebot-Sperren auf Personen-/Bekanntmachungspfaden; keine einschlägige Sperre für den verwendeten Client auf Bäderpfaden. Impressum: Urheberrechtshinweise mit Zustimmungserfordernis für Text-/Bildvervielfältigung. Keine entsprechende pauschale Nachnutzungslizenz vorgefunden. Kein Volltextarchiv im öffentlichen Projekt.
