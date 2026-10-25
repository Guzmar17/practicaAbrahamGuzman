"""Shared by every test: the repository on the path, a key of the tests' own, the analysis once,
and the page mounted without a browser (R9, R12)."""

import os
import sys
from pathlib import Path

import oxid.runtime
import pytest
from oxid.testing import App
from oxid_server.testing import Client

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# A key for the tests only, set before server.py is imported and reads it. Never a real one.
os.environ.setdefault("ECB_MICROBIOLOGY_KEY", "00" * 32)


@pytest.fixture(scope="session")
def analysis():
    from microbiology import pipeline

    return pipeline.run()


@pytest.fixture(scope="session")
def cultures(analysis):
    return analysis.cultures


@pytest.fixture(scope="session")
def isolates(analysis):
    return analysis.isolates


URLS = ["/api/hospitals", "/api/points", "/api/statistic", "/api/resistance?organism=ECO"] + [
    f"/api/weekly?hospital={h}" for h in ["RBX", "OLV", "CSA"]
]


class Answer:
    def __init__(self, text):
        self._text = text

    async def text(self):
        return self._text


class Window:
    """window.fetch, answered from what server.py really answers."""

    def __init__(self, answers):
        self.answers = answers

    async def fetch(self, url):
        return Answer(self.answers[url])


@pytest.fixture
def page(monkeypatch):
    import server  # here, not at the top: until R1–R8 work it cannot import, and R9 and R12 fail alone

    with Client(server.app) as client:
        answers = {url: client.get(url).text() for url in URLS}
    monkeypatch.setattr(oxid.runtime, "window", Window(answers))
    monkeypatch.syspath_prepend(str(ROOT / "app"))
    sys.modules.pop("app", None)
    app = App.from_module("app")
    yield app
    app.dispose()
