from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import pytest
from icalendar import Calendar
from schwimmoper_saunakalender.parser import DETAIL, OVERVIEW, extract, parse_sentence
from schwimmoper_saunakalender.calendar import render, uid, validate
from schwimmoper_saunakalender.cli import merge, run
from schwimmoper_saunakalender.fetch import Fetcher

FIX = Path(__file__).parent / 'fixtures'
SENTENCE = 'Die Schwimmoper wird hierfür vom 16.11.28 (Do) ab 18.00 Uhr bis einschließlich 19.11.28 (So) geschlossen.'
NOW = datetime(2028, 11, 1, tzinfo=timezone.utc)

def test_html_scope_and_ambiguity():
    events, warnings = extract((FIX/'detail.html').read_text(), DETAIL)
    assert len(events) == 2
    assert events[0]['end'] == '2028-11-20T00:00:00+01:00'
    assert events[1]['start'] == '2028-12-01T08:00:00+01:00'
    assert len(warnings) == 2
    overview, warnings = extract((FIX/'overview.html').read_text(), OVERVIEW)
    assert len(overview) == 1 and not warnings
    assert overview[0]['start'] == events[0]['start']

@pytest.mark.parametrize('text', [
    SENTENCE.replace('16.11.28', '16.11.'),
    SENTENCE.replace('16.11.28', '16. November 2028'),
    SENTENCE.replace('16.11.28', '31.11.28'),
    SENTENCE.replace('(Do)', '(Fr)'),
    SENTENCE.replace('19.11.28', '12.11.28'),
    SENTENCE.replace('18.00', '25.00'),
    SENTENCE + ' Die Sauna bleibt aber geöffnet.',
    SENTENCE.replace('Die Schwimmoper', 'Das Stadtbad Uellendahl'),
    'Die Sauna ist am 16.11.2028 geschlossen.',
    'Die Sauna bleibt voraussichtlich bis 19.11.2028 geschlossen.',
    'Vom 24.12.2028 bis 26.12.2028 gelten geänderte Öffnungszeiten.',
])
def test_reject_unverified_formats(text):
    with pytest.raises(ValueError): parse_sentence(text)

@pytest.mark.parametrize('start,end', [('26.03.28','26.03.28'), ('29.10.28','29.10.28')])
def test_dst_ambiguous_nonexistent_rejected(start, end):
    text = f'Die Schwimmoper wird hierfür vom {start} (So) ab 02.30 Uhr bis einschließlich {end} (So) geschlossen.'
    with pytest.raises(ValueError): parse_sentence(text)

def test_ics_roundtrip_stable_and_update():
    events, _ = extract((FIX/'detail.html').read_text(), DETAIL)
    confirmed = merge([], events, NOW)
    data = render(confirmed)
    assert validate(data) == 2
    cal = Calendar.from_ical(data)
    assert cal.walk('VTIMEZONE')
    assert b'\r\n' in data
    assert all(len(line) <= 75 for line in data.split(b'\r\n'))
    first = cal.walk('VEVENT')[0]
    assert str(first['URL']) == DETAIL
    assert first.decoded('DTEND').day == 20
    assert render(confirmed) == data
    changed = dict(events[0], end='2028-11-21T00:00:00+01:00')
    updated = merge(confirmed, [changed], NOW+timedelta(days=1))
    assert uid(updated[0]) == uid(confirmed[0])
    assert updated[0]['sequence'] == 1
    assert len(updated) == 2

def test_conflicting_sources_and_overlaps():
    event = dict(parse_sentence(SENTENCE), source=DETAIL)
    with pytest.raises(ValueError):
        merge([], [event, dict(event, end='2028-11-21T00:00:00+01:00')], NOW)
    old = merge([], [event], NOW)
    with pytest.raises(ValueError):
        merge(old, [dict(event, start='2028-11-17T18:00:00+01:00')], NOW)

class Fake:
    def __init__(self, error=False): self.calls = 0; self.error = error
    def read(self, url):
        self.calls += 1
        if self.error: raise TimeoutError('Test timeout')
        return (FIX/('detail.html' if url == DETAIL else 'overview.html')).read_text()

def test_last_good_on_network_error_and_interval(tmp_path):
    client = Fake()
    assert run(tmp_path, client, NOW) == 0
    paths = [tmp_path/'data/confirmed.json', tmp_path/'public/sauna.ics']
    before = [p.read_bytes() for p in paths]
    assert run(tmp_path, client, NOW+timedelta(hours=1)) == 0
    assert client.calls == 2
    assert run(tmp_path, Fake(True), NOW+timedelta(days=1)) == 1
    assert [p.read_bytes() for p in paths] == before
    assert not json.loads((tmp_path/'public/status.json').read_text())['update_ok']

def test_structure_changed_and_corrupt_state(tmp_path):
    with pytest.raises(ValueError): extract('<p>geschlossen</p>', DETAIL)
    assert run(tmp_path, Fake(), NOW) == 0
    (tmp_path/'data/confirmed.json').write_text('broken')
    with pytest.raises(json.JSONDecodeError): run(tmp_path, Fake(), NOW+timedelta(days=1))

class Response:
    def __init__(self, text, status=200, kind='text/plain'):
        self.text=text; self.status_code=status; self.headers={'Content-Type':kind}
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def iter_content(self, size): yield self.text.encode()
class Session:
    def __init__(self, responses): self.responses=iter(responses); self.headers={}; self.calls=[]
    def get(self, url, **kwargs): self.calls.append((url,kwargs)); return next(self.responses)

@pytest.mark.parametrize('response', [Response('',403), Response('',404), Response('',429), Response('',302), Response('bad',kind='application/pdf')])
def test_robots_failure_closed(response):
    session = Session([response])
    with pytest.raises(ValueError): Fetcher(session, lambda _:None).read(DETAIL)
    assert len(session.calls) == 1

def test_robots_disallow_and_delay():
    session=Session([Response('User-agent: *\nDisallow: /tourismus-freizeit/')])
    with pytest.raises(ValueError): Fetcher(session, lambda _:None).read(DETAIL)
    assert len(session.calls)==1
    sleeps=[]
    session=Session([Response('User-agent: *\nCrawl-delay: 5\nAllow: /'), Response('<html/>',kind='text/html')])
    assert Fetcher(session, sleeps.append).read(DETAIL)=='<html/>'
    assert 4.8 < sleeps[0] <= 5
    assert session.calls[1][1]['allow_redirects'] is False
