# Veröffentlichungsstand und GitHub-Einstellungen

Stand 17.11.2026: Das öffentliche Repository `1-connexion/schwimmoper-saunakalender` wurde vom Eigentümer angelegt. Projektcode und Kalender wurden hochgeladen; Pull Request #1 enthält die Implementierung. Lokal: 24 Tests bestanden, zwei bestätigte Gesamtbad-Schließungen, ICS erfolgreich eingelesen und validiert.

## Erfolgreich eingerichtet

Die verbundene GitHub-Integration kann Code pushen und Pull Requests erstellen. Die Pages-Erstellung über die API wurde jedoch mit HTTP 403 `Resource not accessible by integration` verweigert.

Der Eigentümer hat unter Repository → **Settings → Pages → Build and deployment → Source: GitHub Actions** ausgewählt. Anschließend war das Deployment erfolgreich. Am 17.11.2026 wurden Website, ICS und Statusdatei mit HTTP 200 abgerufen. Die ICS wurde erneut validiert: zwei Termine, Inhalt identisch mit dem geprüften Kalender. Es sind derzeit keine weiteren manuellen Einstellungen erforderlich.

Nach erfolgreicher CI und Merge auf `main` veröffentlicht der vorhandene Workflow den Inhalt von `public/`. Falls der erste Deploymentversuch vor der Pages-Einrichtung fehlschlägt, anschließend unter Actions → „Kalender prüfen und veröffentlichen“ → „Run workflow“ neu starten. Weitere mögliche Organisations-, Branchschutz- und Umgebungsrechte stehen in der README.

Öffentlich erreichbare Abo-Adresse:

https://1-connexion.github.io/schwimmoper-saunakalender/sauna.ics

Der tägliche Workflow ist auf `main` aktiv. Die erfolgreiche Veröffentlichung wurde zusätzlich zu den Tests durch direkten HTTP-Abruf überprüft.

## Veröffentlichung prüfen

```sh
curl --fail --location https://1-connexion.github.io/schwimmoper-saunakalender/sauna.ics --output /tmp/sauna-veroeffentlicht.ics
schwimmoper-kalender --validate /tmp/sauna-veroeffentlicht.ics
```

Außerdem `status.json` auf derselben Website und die Workflowprotokolle prüfen. Der Kalender enthält Gesamtbad-Schließungen ohne gesonderte Sauna-Bestätigung. Feiertags-PDFs und unklare Formate werden nicht automatisch interpretiert.
