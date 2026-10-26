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
    """Read the patient CSV and rename its columns.

    Keep every value as text so codes like "0412345" keep their leading zero.
    """
    frame = pl.read_csv(
        path,
        separator=";",
        infer_schema_length=0,
        null_values=["", "n/a", "NA", "-"],
    )
    english_names = ["patient", "name", "surnames", "born", "sex", "postcode"]
    if len(frame.columns) != len(english_names):
        raise ValueError(
            f"Expected {len(english_names)} patient columns, got {len(frame.columns)}"
        )

    # Match each original header with its English name.
    rename_columns = dict(zip(frame.columns, english_names))
    frame = frame.rename(rename_columns)
    return frame.with_columns(pl.all().cast(pl.String))


def samples(folder: Path = DATA) -> pl.DataFrame:
    """The three hospitals' samples in one table, SAMPLE_COLUMNS in that order, `hospital` saying
    whose file the row came from (RBX, OLV, CSA). Every column String except the three times,
    Datetime: each file has its own separator, headers, date format and spelling of "missing"."""
    null_values = ["", "n/a", "NA", "-"]

    rbx = pl.read_csv(
        folder / "samples_rbx.csv",
        separator=",",
        infer_schema_length=0,
        null_values=null_values,
    ).with_columns(pl.lit("RBX").alias("hospital"))

    olv = pl.read_csv(
        folder / "samples_olv.csv",
        separator=";",
        infer_schema_length=0,
        null_values=null_values,
    ).rename(
        {
            "mostra": "sample_id",
            "pacient": "patient",
            "tipus_mostra": "specimen",
            "data_presa": "collected_at",
            "data_recepcio": "received_at",
            "data_informe": "reported_at",
            "microorganisme": "organism",
        }
    ).with_columns(pl.lit("OLV").alias("hospital"))

    csa = pl.read_csv(
        folder / "samples_csa.csv",
        separator=",",
        infer_schema_length=0,
        null_values=null_values,
    ).with_columns(pl.lit("CSA").alias("hospital"))

    date_formats = {
        "RBX": "%Y-%m-%d %H:%M",
        "OLV": "%d/%m/%Y %H:%M",
        "CSA": "%Y-%m-%dT%H:%M:%S",
    }

    def parse_dates(frame: pl.DataFrame, hospital: str) -> pl.DataFrame:
        return frame.with_columns(
            pl.col(column).str.to_datetime(format=date_formats[hospital], strict=False)
            for column in ["collected_at", "received_at", "reported_at"]
        ).select(SAMPLE_COLUMNS)

    return pl.concat(
        [parse_dates(rbx, "RBX"), parse_dates(olv, "OLV"), parse_dates(csa, "CSA")]
    )


def antibiogram(path: Path = DATA / "antibiogram.csv") -> pl.DataFrame:
    """The network laboratory's results, one row per sample and antibiotic. sample_id, lab,
    antibiotic, mic and sir String (a MIC can read "<=0.03" or "0,5"), diameter Float64; missing
    ("", "NA", "-") is null."""
    frame = pl.read_csv(
        path,
        infer_schema_length=0,
        null_values=["", "NA", "-"],
    )
    return frame.with_columns(pl.col("diameter").cast(pl.Float64, strict=False))


def hospitals(path: Path = DATA / "hospitals.csv") -> pl.DataFrame:
    """The network's hospital list: code, name, town, beds (UInt16). As the file has it."""
    frame = pl.read_csv(path, infer_schema_length=0)
    return frame.with_columns(pl.col("beds").cast(pl.UInt16))
