# Veröffentlichungsstand und Fortsetzung

Stand 17.11.2026: Projekt lokal vollständig implementiert und getestet. Der echte Quellenabruf hat zwei bestätigte Gesamtbad-Schließungen ergeben. Die generierte ICS wurde eingelesen und validiert.

**Noch nicht veröffentlicht:** Die verbundene GitHub-Integration identifiziert das Konto `1-connexion`, verweigert aber das Erstellen eines Repositorys mit `Resource not accessible by integration (createRepository)`. Die sichere Browser-Anmeldung wurde abgebrochen. Es existiert daher aus diesem Auftrag noch kein Remote-Repository, kein Pull Request und kein aktives Pages-Deployment. Die README nennt die vorgesehene, noch nicht aktive Abo-URL.

## Fortsetzen mit GitHub CLI

Ein GitHub-Login mit Berechtigung zur Repository-Erstellung ist erforderlich. Keine Tokens im Projekt ablegen.

```sh
cd schwimmoper-saunakalender
gh auth login
gh repo create 1-connexion/schwimmoper-saunakalender --public --source . --remote origin
git push origin main feat/calendar
gh pr create --base main --head feat/calendar --title 'Schließungskalender mit konservativem Scraper und Pages' --body-file docs/PR.md
```

Alternativ ein **leeres öffentliches** Repository dieses Namens im GitHub-Konto erstellen, dann:

```sh
git remote add origin https://github.com/1-connexion/schwimmoper-saunakalender.git
git push origin main feat/calendar
gh pr create --base main --head feat/calendar --title 'Schließungskalender mit konservativem Scraper und Pages' --body-file docs/PR.md
```

Falls bereits ein origin-Remote eingerichtet ist, dessen Ziel prüfen und den `remote add`-Schritt auslassen. Der lokale Branch `main` enthält nur einen Ausgangscommit mit `.gitignore`; `feat/calendar` enthält das vollständige Projekt für den Pull Request.

Anschließend PR und CI prüfen, mergen und Settings → Pages → Source: **GitHub Actions** einstellen. Die weiteren möglichen Rechte-/Branch-/Umgebungseinstellungen stehen in der README. Danach unter Actions einmal manuell starten. Erst nach erfolgreichem Deployment ist die URL abonnierbar.

Die veröffentlichte Datei mit HTTP-Status 200 abrufen und erneut prüfen:

```sh
curl --fail --location https://1-connexion.github.io/schwimmoper-saunakalender/sauna.ics --output /tmp/sauna-veroeffentlicht.ics
schwimmoper-kalender --validate /tmp/sauna-veroeffentlicht.ics
```

## Bei Verwendung des ZIP-Archivs

Das ZIP enthält Quellcode ohne Git-Historie. Vor den obigen CLI-Schritten die lokalen Branches anlegen:

```sh
cd schwimmoper-saunakalender
git init -b main
git add .gitignore
git commit -m 'chore: Projektbasis anlegen'
git switch -c feat/calendar
git add .
git commit -m 'feat: Schwimmoper-Schließungskalender'
```

Git benötigt dafür den lokal konfigurierten Namen und die Commit-E-Mail-Adresse.
