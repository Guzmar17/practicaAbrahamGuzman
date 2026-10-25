"""R8 · The server answers aggregates and anonymous points, and never an identifier."""

import pytest
from oxid_server.testing import Client

from microbiology import privacy

ROUTES = ["/api/hospitals", "/api/weekly?hospital=RBX", "/api/weekly?hospital=CSA", "/api/statistic", "/api/points"]


@pytest.fixture(scope="module")
def client():
    import server  # here, not at the top: until R1–R7 work it cannot import, and R8 fails alone

    with Client(server.app) as c:
        yield c


def test_every_route_answers(client):
    for route in ROUTES + ["/api/tat.svg"]:
        assert client.get(route).status == 200, route


def test_weekly(client):
    rows = client.get("/api/weekly?hospital=CSA").json()
    assert len(rows) == 26 and rows[0] == {"week": "2026-01-05", "positives": rows[0]["positives"]}
    assert {"week": "2026-02-16", "positives": 0} in rows
    assert client.get("/api/weekly?hospital=XYZ").status == 404


def test_points_send_what_the_chart_draws(client):
    points = client.get("/api/points").json()
    assert set(points[0]) == {"mic_log2", "diameter"}
    assert len(points) == 345


def test_the_svg_is_drawn_on_the_server(client):
    answer = client.get("/api/tat.svg")
    assert answer.header("content-type").startswith("image/svg+xml")
    assert answer.text().startswith("<svg")


def test_statistic(client):
    body = client.get("/api/statistic").json()
    assert body["tat"]["n"] == 2104 and body["correlation"]["n"] == 345 and body["k"] >= 5


def test_no_route_answers_an_identifier(client, cultures):
    codes = set(cultures["patient"]) | set(cultures["patient"].str.strip_chars_start("0"))
    surnames = set(cultures["surnames"])
    pseudonyms = set(privacy.generalise(cultures, privacy.key())["patient"])
    for route in ROUTES:
        text = client.get(route).text()
        leaked = [v for v in codes | surnames | pseudonyms if f'"{v}"' in text]
        assert not leaked, f"{route} answers {leaked[:3]}"
