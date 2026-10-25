"""R12 · The published rates: a model that keeps the rules, a route, and the grouped bars."""

import patito as pt
import polars as pl
import pytest
from oxid_server.testing import Client

from microbiology import resistance


@pytest.fixture(scope="module")
def client():
    import server  # here, not at the top: until R1–R8 work it cannot import

    with Client(server.app) as c:
        yield c


def test_the_model_accepts_the_rates(isolates):
    for organism in ["ECO", "KPN", "PAE", "SAU", "EFA"]:
        resistance.Rate.validate(resistance.rates(isolates, organism))


def test_the_model_refuses_a_rate_over_too_few(isolates):
    rates = resistance.rates(isolates, "KPN")
    published = rates.with_columns(rate=(pl.col("resistant") / pl.col("tested")).round(3))
    with pytest.raises(pt.exceptions.DataFrameValidationError):
        resistance.Rate.validate(published)


def test_the_model_refuses_impossible_counts_and_extra_columns(isolates):
    rates = resistance.rates(isolates, "ECO")
    with pytest.raises(pt.exceptions.DataFrameValidationError):
        resistance.Rate.validate(rates.with_columns(resistant=pl.col("tested") + 1))
    with pytest.raises(pt.exceptions.DataFrameValidationError):
        resistance.Rate.validate(rates.with_columns(patient=pl.lit("0412345")))


def test_the_route(client):
    rows = client.get("/api/resistance?organism=KPN").json()
    assert set(rows[0]) == {"antibiotic", "hospital", "tested", "resistant", "rate"}
    assert len(rows) == 21 and sum(row["rate"] is None for row in rows) == 7
    assert client.get("/api/resistance?organism=XYZ").status == 404


@pytest.mark.filterwarnings("ignore:zoom, brush")
def test_the_grouped_bars(page):
    bars = [svg for svg in page.find_all("svg") if "Resistència d'E. coli" in svg.text]
    assert len(bars) == 1, "a fifth chart, titled"
