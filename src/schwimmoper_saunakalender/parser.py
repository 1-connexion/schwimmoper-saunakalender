"""Only the sentence grammar verified on the official page is accepted.
No fuzzy dates, inferred years, opening hours, OCR, or whole-page matching.
"""
from datetime import datetime, timedelta, timezone
import re
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
BASE = 'https://www.wuppertal.de'
DETAIL_PATH = '/tourismus-freizeit/baeder/schwimmoper.php'
DETAIL = BASE + DETAIL_PATH
OVERVIEW = BASE + '/tourismus-freizeit/baeder/staedtische_baeder.php'
SOURCES = (DETAIL, OVERVIEW)
TZ = ZoneInfo('Europe/Berlin')
DATE = r'\d{1,2}\.\d{1,2}\.\d{4}|\d{1,2}\.\d{1,2}\.\d{2}'
PATTERN = re.compile(
    rf'Die Schwimmoper wird hierfür vom (?P<start>{DATE})'
    r' \((?:Mo|Di|Mi|Do|Fr|Sa|So)\) ab (?P<hour>\d{2})[.:](?P<minute>\d{2}) Uhr'
    rf' bis einschließlich (?P<end>{DATE}) \((?:Mo|Di|Mi|Do|Fr|Sa|So)\) geschlossen\.'
)

def german_date(value):
    day, month, year = map(int, value.split('.'))
    if len(value.split('.')[-1]) == 2:
        year += 2000  # Explicit 2000–2099 convention; never infer current year.
    return datetime(year, month, day, tzinfo=TZ)

def parse_sentence(text):
    match = PATTERN.fullmatch(text)
    if not match:
        raise ValueError('Unbekanntes oder unvollständiges Schließungsformat')
    start = german_date(match['start']).replace(hour=int(match['hour']), minute=int(match['minute']))
    end = german_date(match['end']) + timedelta(days=1)
    if not start < end or end - start > timedelta(days=366):
        raise ValueError('Ungültiger oder ungewöhnlich langer Zeitraum')
    weekdays = ('Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So')
    expected = (weekdays[start.weekday()], weekdays[(end-timedelta(days=1)).weekday()])
    if tuple(re.findall(r'\((Mo|Di|Mi|Do|Fr|Sa|So)\)', text)) != expected:
        raise ValueError('Wochentag widerspricht Datum')
    if start.astimezone(timezone.utc).astimezone(TZ) != start or start.replace(fold=1).utcoffset() != start.utcoffset():
        raise ValueError('Mehrdeutige oder nicht existierende Ortszeit')
    return {'start': start.isoformat(), 'end': end.isoformat(), 'scope': 'Schwimmoper gesamt'}

def extract(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    root = soup.select_one('article#SP-Content')
    if root is None:
        raise ValueError('Erwarteter Inhaltsbereich fehlt')
    warnings = []
    if url == DETAIL:
        blocks = root.select('p')
        if 'Öffnungszeiten Sauna' not in root.get_text(' ', strip=True):
            raise ValueError('Schwimmoper-Seitenstruktur nicht wiedererkannt')
        if root.select('a[href$=".pdf"], img'):
            warnings.append('PDF-/Bildinhalte werden nicht ausgewertet; Feiertagsschließungen können fehlen.')
    elif url == OVERVIEW:
        blocks = root.select(f'a.SP-Teaser[href="{DETAIL_PATH}"] .SP-Teaser__abstract')
        if not blocks:
            raise ValueError('Schwimmoper-Teaser fehlt')
    else:
        raise ValueError('Quelle nicht freigegeben')
    events = []
    for block in blocks:
        text = ' '.join(block.get_text(' ', strip=True).split())
        if not re.search(r'geschloss|schließ|schliess|gesperrt|entfällt', text, re.I):
            continue
        if url == OVERVIEW and 'Die Schwimmoper wird hierfür vom ' in text:
            text = text[text.index('Die Schwimmoper wird hierfür vom '):]
        if not ('Schwimmoper' in text or 'Sauna' in text or 'Saunabereich' in text):
            continue
        try:
            event = parse_sentence(text)
            event['source'] = url
            events.append(event)
        except ValueError as exc:
            warnings.append(f'{url}: {exc}; Absatz nicht übernommen.')
    return events, warnings
