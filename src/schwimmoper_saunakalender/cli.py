import argparse
from datetime import datetime, timedelta, timezone
import json
import logging
from pathlib import Path
from .calendar import render, uid, validate
from .fetch import Fetcher
from .parser import SOURCES, extract

LOG = logging.getLogger(__name__)

def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_bytes(data)
    temp.replace(path)

def write_json(path, data):
    atomic(path, (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())

def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default

def merge(previous, incoming, now):
    """Preserve absent events; conflicting intervals abort the entire update."""
    candidates = {}
    for event in incoming:
        key = uid(event)
        if key in candidates and candidates[key]['end'] != event['end']:
            raise ValueError('Widersprüchliche Endzeiten zwischen Quellen')
        candidates.setdefault(key, event)  # Detail source is preferred.
    merged = {uid(e): dict(e) for e in previous}
    for key, event in candidates.items():
        old = merged.get(key)
        updated = dict(event)
        updated['confirmed_at'] = now.isoformat()
        updated['sequence'] = (old or {}).get('sequence', 0) + int(bool(old and old['end'] != event['end']))
        merged[key] = updated
    values = sorted(merged.values(), key=lambda e: e['start'])
    for left, right in zip(values, values[1:]):
        if datetime.fromisoformat(left['end']) > datetime.fromisoformat(right['start']):
            raise ValueError('Überlappende Schließungen; Änderung muss manuell geprüft werden')
    return values

def run(root, fetcher=None, now=None):
    now = now or datetime.now(timezone.utc)
    state_path = root / 'data/confirmed.json'
    previous = load(state_path, [])  # Corrupt state must fail, never reset to empty.
    # Validate existing state before touching it or publishing a replacement.
    render(previous)
    crawl_path = root / 'data/crawl.json'
    crawl = load(crawl_path, {})
    if crawl.get('last_attempt') and now - datetime.fromisoformat(crawl['last_attempt']) < timedelta(hours=23):
        LOG.warning('Abruf übersprungen: Mindestintervall von 23 Stunden')
        return 0
    write_json(crawl_path, {'last_attempt': now.isoformat()})
    warnings, incoming = [], []
    fetcher = fetcher or Fetcher()
    failed = False
    for url in SOURCES:
        try:
            events, notes = extract(fetcher.read(url), url)
            incoming.extend(events)
            warnings.extend(notes)
        except Exception as exc:
            failed = True
            warnings.append(f'{url}: {type(exc).__name__}: {exc}')
    updated = previous
    if not failed:
        try:
            updated = merge(previous, incoming, now)
            absent = {uid(e) for e in previous} - {uid(e) for e in incoming}
            if absent:
                warnings.append(f'{len(absent)} ältere Termine nicht mehr im Text: weiterhin aufbewahrt; manuelle Prüfung nötig.')
        except ValueError as exc:
            failed = True
            warnings.append(str(exc))
    if failed:
        updated = previous
        warnings.append('Aktualisierung verworfen; zuletzt bestätigter Kalender bleibt erhalten.')
    data = render(updated)
    # On failure preserve calendar bytes as well as confirmed_at/UIDs.
    if not failed or not (root / 'public/sauna.ics').exists():
        atomic(root / 'public/sauna.ics', data)
    if not failed:
        write_json(state_path, updated)
    status = {'attempted_at': now.isoformat(), 'update_ok': not failed,
              'events': len(updated), 'warnings': warnings}
    write_json(root / 'public/status.json', status)
    for warning in warnings:
        LOG.warning(warning)
    LOG.info('%s bestätigte Termine; ICS erfolgreich geprüft', len(updated))
    return 1 if failed else 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--validate', type=Path, help='Nur vorhandene ICS prüfen; kein Netzabruf')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    if args.validate:
        print(f'{validate(args.validate.read_bytes())} Termine; ICS gültig')
        return
    raise SystemExit(run(args.root))

if __name__ == '__main__':
    main()
