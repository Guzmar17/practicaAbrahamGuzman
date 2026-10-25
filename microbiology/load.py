"""R1 · Loading: each file read with its own conventions, typed, renamed to English. Nothing is fixed here.

Five files come from five systems (data/README.md); the three hospitals' samples become one
table. Loading answers "what does the file say?"; cleaning (clean.py) answers "what did they
mean?". Keep the two apart: a test can then check that the load lost nothing.
"""

from pathlib import Path

import polars as pl

DATA = Path(__file__).resolve().parent.parent / "data"

SEX = pl.Enum(["D", "H"])
#: The four kinds of sample the network cultures.
SPECIMEN = pl.Enum(["orina", "sang", "ferida", "esput"])
#: Susceptible < intermediate (susceptible at a higher dose) < resistant: an Enum compares in this order.
SIR = pl.Enum(["S", "I", "R"])
#: The columns of one table of samples, in this order, whatever hospital wrote them.
SAMPLE_COLUMNS = [
    "sample_id",
    "hospital",
    "patient",
    "specimen",
    "collected_at",
    "received_at",
    "reported_at",
    "organism",
]


def patients(path: Path = DATA / "patients.csv") -> pl.DataFrame:
    """The network's patient index: `;`, dd/mm/yyyy, Catalan headers.

    Columns: patient, name, surnames, born, sex, postcode — all String: a patient code and a
    postcode are codes, never numbers ("0412345" is not 412345).
    """
    raise NotImplementedError("R1")


def samples(folder: Path = DATA) -> pl.DataFrame:
    """The three hospitals' samples in one table, SAMPLE_COLUMNS in that order, `hospital` saying
    whose file the row came from (RBX, OLV, CSA). Every column String except the three times,
    Datetime: each file has its own separator, headers, date format and spelling of "missing"."""
    raise NotImplementedError("R1")


def antibiogram(path: Path = DATA / "antibiogram.csv") -> pl.DataFrame:
    """The network laboratory's results, one row per sample and antibiotic. sample_id, lab,
    antibiotic, mic and sir String (a MIC can read "<=0.03" or "0,5"), diameter Float64; missing
    ("", "NA", "-") is null."""
    raise NotImplementedError("R1")


def hospitals(path: Path = DATA / "hospitals.csv") -> pl.DataFrame:
    """The network's hospital list: code, name, town, beds (UInt16). As the file has it."""
    raise NotImplementedError("R1")
