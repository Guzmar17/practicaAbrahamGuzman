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
# Only reported samples have a turnaround; each one goes to the 12-hour bucket it starts in.
TAT = (
    ANALYSIS.cultures.filter(pl.col("tat_hours").is_not_null())
    .with_columns((pl.col("tat_hours") // 12 * 12).cast(pl.Int64).alias("bucket"))
    .group_by("bucket")
    .agg(pl.len().alias("samples"))
    .sort("bucket")
)
RATES = {}  # TODO R12: organism code → its rates() checked by resistance.Rate


@app.get("/api/hospitals")
async def hospitals():
    """One row per hospital: samples, share positive, median turnaround in hours."""
    return HOSPITALS.to_dicts()


@app.get("/api/weekly")
async def weekly(hospital: str = "RBX"):
    """Positive cultures per week in one hospital, every week of the half year; 404 for a hospital that does not exist."""
    rows = WEEKLY.filter(pl.col("hospital") == hospital)
    if rows.height == 0:
        raise HTTPError(404, "unknown hospital: " + hospital)
    return rows.select("week", "positives").to_dicts()


@app.get("/api/statistic")
async def statistic_():
    """The turnaround described (statistic.describe), the diameter–MIC correlation, and the release's k and suppressed people."""
    # Only figures: no row of any table leaves here.
    return {
        "tat": statistic.describe(ANALYSIS.cultures["tat_hours"]),
        "correlation": statistic.correlation(ANALYSIS.isolates),
        "k": privacy.k_anonymity(RELEASE),
        "suppressed": SUPPRESSED,
    }


@app.get("/api/points")
async def points():
    """E. coli and ciprofloxacin: log2 of the MIC (mic_log2) and the diameter of every test that has
    both — the two columns the scatter draws, nothing else."""
    # The same filter as statistic.correlation, and only the two columns the scatter draws.
    tests = ANALYSIS.isolates.filter((pl.col("organism") == "ECO") & (pl.col("antibiotic") == "CIP"))
    tests = tests.drop_nulls(["diameter", "mic"])
    return tests.select(pl.col("mic").log(2).alias("mic_log2"), pl.col("diameter")).to_dicts()


@app.get("/api/tat.svg")
async def tat_svg():
    """The turnaround histogram, drawn here: an <img> needs no Python in the page."""
    picture = chart(
        TAT.to_dicts(),
        "bar",
        x=X("bucket:O").title("Temps de resposta (h, trams de 12 h)"),
        y=Y("samples:Q").title("Mostres"),
        title="Temps de resposta del laboratori",
        render="svg",
    )
    return Response(render_to_string(picture), media_type="image/svg+xml")


@app.get("/api/resistance")
async def resistance_(organism: str = "ECO"):
    """R12 · The organism's rates per antibiotic and hospital (resistance.rates, checked by
    resistance.Rate); 404 for an organism the network does not report."""
    raise NotImplementedError("R12")
