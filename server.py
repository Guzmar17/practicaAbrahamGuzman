"""R8 · The server: the analysis runs once when a worker starts, and only aggregates and
anonymous points ever leave it. Not one route answers a name, a patient code or a pseudonym.

    uv run oxid serve app --server server.py        # while you work (OXID_SERVER_RUNTIME=cpython)
    uv run oxid build app --out www && uv run oxid-server server.py --runtime cpython
"""

import polars as pl
from oxid import render_to_string
from oxid.chart import X, Y, chart
from oxid_server import App, HTTPError, Response

from microbiology import pipeline, privacy, resistance, statistic, summary

app = App(title="ecb-microbiology", static="www")

#: The analysis, once per worker. A missing ECB_MICROBIOLOGY_KEY stops the server here, on purpose.
ANALYSIS = pipeline.run()
RELEASE, SUPPRESSED = privacy.anonymise(ANALYSIS.cultures, privacy.key())
HOSPITALS = summary.by_hospital(ANALYSIS.cultures).drop("patients")
WEEKLY = summary.weekly(ANALYSIS.cultures).with_columns(pl.col("week").dt.strftime("%Y-%m-%d"))
TAT = None  # TODO R8: turnaround in buckets of 12 hours: bucket (its first hour), samples
RATES = {}  # TODO R12: organism code → its rates() checked by resistance.Rate


@app.get("/api/hospitals")
async def hospitals():
    """One row per hospital: samples, share positive, median turnaround in hours."""
    raise NotImplementedError("R8")


@app.get("/api/weekly")
async def weekly(hospital: str = "RBX"):
    """Positive cultures per week in one hospital, every week of the half year; 404 for a hospital that does not exist."""
    raise NotImplementedError("R8")


@app.get("/api/statistic")
async def statistic_():
    """The turnaround described (statistic.describe), the diameter–MIC correlation, and the release's k and suppressed people."""
    raise NotImplementedError("R8")


@app.get("/api/points")
async def points():
    """E. coli and ciprofloxacin: log2 of the MIC (mic_log2) and the diameter of every test that has
    both — the two columns the scatter draws, nothing else."""
    raise NotImplementedError("R8")


@app.get("/api/tat.svg")
async def tat_svg():
    """The turnaround histogram, drawn here: an <img> needs no Python in the page."""
    raise NotImplementedError("R8")


@app.get("/api/resistance")
async def resistance_(organism: str = "ECO"):
    """R12 · The organism's rates per antibiotic and hospital (resistance.rates, checked by
    resistance.Rate); 404 for an organism the network does not report."""
    raise NotImplementedError("R12")
