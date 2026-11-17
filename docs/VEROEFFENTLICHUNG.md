# Veröffentlichungsstand und GitHub-Einstellungen

Stand 17.11.2026: Das öffentliche Repository `1-connexion/schwimmoper-saunakalender` wurde vom Eigentümer angelegt. Projektcode und Kalender wurden hochgeladen; Pull Request #1 enthält die Implementierung. Lokal: 24 Tests bestanden, zwei bestätigte Gesamtbad-Schließungen, ICS erfolgreich eingelesen und validiert.

## Noch erforderliche Einstellung

Die verbundene GitHub-Integration kann Code pushen und Pull Requests erstellen. Die Pages-Erstellung über die API wurde jedoch mit HTTP 403 `Resource not accessible by integration` verweigert.

Der Eigentümer muss unter Repository → **Settings → Pages → Build and deployment → Source: GitHub Actions** auswählen.

Nach erfolgreicher CI und Merge auf `main` veröffentlicht der vorhandene Workflow den Inhalt von `public/`. Falls der erste Deploymentversuch vor der Pages-Einrichtung fehlschlägt, anschließend unter Actions → „Kalender prüfen und veröffentlichen“ → „Run workflow“ neu starten. Weitere mögliche Organisations-, Branchschutz- und Umgebungsrechte stehen in der README.

Vorgesehene Abo-Adresse:

https://1-connexion.github.io/schwimmoper-saunakalender/sauna.ics

Die Adresse ist erst nach einem erfolgreichen Pages-Deployment verfügbar. Die Tests allein bestätigen keine Veröffentlichung.

## Veröffentlichung prüfen

```sh
curl --fail --location https://1-connexion.github.io/schwimmoper-saunakalender/sauna.ics --output /tmp/sauna-veroeffentlicht.ics
schwimmoper-kalender --validate /tmp/sauna-veroeffentlicht.ics
```

Außerdem `status.json` auf derselben Website und die Workflowprotokolle prüfen. Der Kalender enthält Gesamtbad-Schließungen ohne gesonderte Sauna-Bestätigung. Feiertags-PDFs und unklare Formate werden nicht automatisch interpretiert.
