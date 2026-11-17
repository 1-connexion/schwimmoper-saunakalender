"""Low-volume, fail-closed HTTP client; no redirect or robots failure bypass."""
import time
from urllib.robotparser import RobotFileParser
import requests
from .parser import BASE, SOURCES

AGENT = 'SchwimmoperSaunakalender/0.1 (+https://github.com/1-connexion/schwimmoper-saunakalender)'

class Fetcher:
    def __init__(self, session=None, sleep=time.sleep):
        self.session = session or requests.Session()
        self.session.headers.update({'User-Agent': AGENT, 'Accept': 'text/html,text/plain;q=0.9'})
        self.sleep = sleep
        self.delay = 3
        self.last = None
        self.robots = None

    def _request(self, url):
        if self.last is not None:
            self.sleep(max(0, self.delay - (time.monotonic() - self.last)))
        self.last = time.monotonic()
        # requests honors inherited proxy/CA settings. Never disable TLS verification.
        with self.session.get(url, timeout=(10, 30), allow_redirects=False, stream=True) as response:
            if response.status_code != 200:
                raise ValueError(f'HTTP {response.status_code} für {url}; keine Wiederholung (auch bei 429).')
            kind = response.headers.get('Content-Type', '').lower()
            expected = ('text/plain',) if url.endswith('/robots.txt') else ('text/html', 'application/xhtml+xml')
            if not kind.startswith(expected):
                raise ValueError(f'Unerwarteter Inhaltstyp für {url}')
            chunks, size = [], 0
            for chunk in response.iter_content(65536):
                size += len(chunk)
                if size > 2_000_000:
                    raise ValueError('Antwort überschreitet 2 MB')
                chunks.append(chunk)
            return b''.join(chunks).decode('utf-8', errors='strict')

    def read(self, url):
        if url not in SOURCES:
            raise ValueError('URL nicht freigegeben')
        if self.robots is None:
            text = self._request(BASE + '/robots.txt')
            self.robots = RobotFileParser()
            self.robots.parse(text.splitlines())
            delay = self.robots.crawl_delay(AGENT)
            rate = self.robots.request_rate(AGENT)
            self.delay = max(3, delay or 0, (rate.seconds / rate.requests) if rate else 0)
            if self.delay > 60:
                raise ValueError('robots.txt verlangt größeres Abrufintervall; manuelle Prüfung nötig')
        if not self.robots.can_fetch(AGENT, url):
            raise ValueError('robots.txt untersagt Abruf')
        return self._request(url)
