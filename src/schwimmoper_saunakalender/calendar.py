from datetime import datetime, timezone, date
import hashlib
from icalendar import Calendar, Event, Timezone
from .parser import TZ

def uid(event):
    key = event['scope'] + '|' + event['start']
    return hashlib.sha256(key.encode()).hexdigest()[:32] + '@schwimmoper-saunakalender'

def render(events):
    cal = Calendar()
    for key, value in [('prodid','-//schwimmoper-saunakalender//Inoffiziell//DE'), ('version','2.0'), ('calscale','GREGORIAN'), ('method','PUBLISH'), ('x-wr-calname','Schwimmoper – angekündigte Schließungen (inoffiziell)'), ('x-wr-timezone','Europe/Berlin')]:
        cal.add(key, value)
    dates = [datetime.fromisoformat(e[k]).astimezone(TZ) for e in events for k in ('start', 'end')]
    if dates:
        cal.add_component(Timezone.from_tzinfo(TZ, first_date=date(min(dates).year-1,1,1), last_date=date(max(dates).year+1,12,31)))
    for item in sorted(events, key=lambda e: e['start']):
        event = Event()
        event.add('uid', uid(item))
        event.add('dtstamp', datetime.fromisoformat(item['confirmed_at']).astimezone(timezone.utc))
        event.add('sequence', item.get('sequence', 0))
        for field, key in [('dtstart', 'start'), ('dtend', 'end')]:
            event.add(field, datetime.fromisoformat(item[key]).astimezone(TZ))
        event.add('summary', 'Schwimmoper geschlossen – Gesamtbad')
        event.add('description', 'Inoffizieller Kalender. Angekündigte Schließung der gesamten Schwimmoper. '
                  'Keine gesonderte Sauna-Bestätigung. Enddatum einschließlich; Kalenderende am Folgetag um 00:00 Uhr. '
                  'Zuletzt bestätigt: ' + item['confirmed_at'] + '. Quelle: ' + item['source'] +
                  '. Angaben können sich ändern; bitte vor dem Besuch die Quelle prüfen.')
        event.add('url', item['source'])
        event.add('location', 'Schwimmoper, Südstraße 29, Wuppertal')
        event.add('status', 'CONFIRMED')
        event.add('transp', 'TRANSPARENT')
        cal.add_component(event)
    result = cal.to_ical()
    validate(result)
    return result

def validate(data):
    cal = Calendar.from_ical(data)
    assert str(cal['VERSION']) == '2.0'
    seen = set()
    for event in cal.walk('VEVENT'):
        assert not event.errors
        assert str(event['UID']) not in seen
        seen.add(str(event['UID']))
        assert event.decoded('DTSTART') < event.decoded('DTEND')
        assert event['DTSTART'].params['TZID'] == 'Europe/Berlin'
        assert event['DTEND'].params['TZID'] == 'Europe/Berlin'
        assert str(event['URL']).startswith('https://www.wuppertal.de/')
    return len(seen)
