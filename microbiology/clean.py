"""R2 · Cleaning with expressions: what each source meant, written as Polars expressions.

Every fix is a decision. Write the decision in a comment beside it, and its count in INFORME.md.
"""

import polars as pl

from .load import SEX, SIR, SPECIMEN

#: The five organisms the network reports, by their code.
ORGANISM = pl.Enum(["ECO", "KPN", "PAE", "SAU", "EFA"])

#: Every spelling the three hospitals use, stripped and in lower case → its code; no growth → None.
ORGANISMS = {
    "escherichia coli": "ECO",
    "e. coli": "ECO",
    "e.coli": "ECO",
    "klebsiella pneumoniae": "KPN",
    "klebsiella pneumonie": "KPN",
    "k. pneumoniae": "KPN",
    "k.pneumoniae": "KPN",
    "pseudomonas aeruginosa": "PAE",
    "p. aeruginosa": "PAE",
    "p.aeruginosa": "PAE",
    "staphylococcus aureus": "SAU",
    "s. aureus": "SAU",
    "s.aureus": "SAU",
    "enterococcus faecalis": "EFA",
    "e. faecalis": "EFA",
    "e.faecalis": "EFA",
    "neg": None,
    "negatiu": None,
}


def patients(raw: pl.DataFrame) -> pl.DataFrame:
    """sex → Enum SEX (" h", "d" and "Dona" are H, D and D; empty is unknown), born → Date.
    patient, name, surnames and postcode stay String."""
    return raw.with_columns(
        # Trim and normalize the 38 non-canonical sex entries; an empty value stays null.
        pl.col("sex")
        .str.strip_chars()
        .str.to_lowercase()
        .replace_strict({"d": "D", "dona": "D", "h": "H", "home": "H"})
        .cast(SEX),
        # Patient birth dates are written day/month/year in the source CSV.
        pl.col("born").str.to_date("%d/%m/%Y", strict=False),
    )


def samples(raw: pl.DataFrame) -> pl.DataFrame:
    """patient → the 7-digit code (OLV's system wrote it as a number and lost the leading
    zeros), specimen → Enum SPECIMEN, organism → Enum ORGANISM through ORGANISMS (null: no
    growth). Adds tat_hours: reception to report in hours, one decimal, null while pending."""
    return raw.with_columns(
        # OLV lost leading zeros from 103 numeric patient codes; codes are identifiers, not numbers.
        pl.col("patient").str.pad_start(7, "0"),
        # Case and surrounding spaces do not change the four specimen categories.
        pl.col("specimen").str.strip_chars().str.to_lowercase().cast(SPECIMEN),
        # All 1,142 positive cultures map from 16 source spellings; neg/negatiu mean no growth.
        pl.col("organism")
        .str.strip_chars()
        .str.to_lowercase()
        .replace_strict(ORGANISMS, return_dtype=pl.String)
        .cast(ORGANISM),
        # Pending reports have no turnaround time; completed times are rounded to tenths of an hour.
        ((pl.col("reported_at") - pl.col("received_at")).dt.total_seconds() / 3600)
        .round(1)
        .alias("tat_hours"),
    )


def antibiogram(raw: pl.DataFrame) -> pl.DataFrame:
    """sir → Enum SIR ("s", " R", "Sensible", "resistent" are S, R, S, R; "pendent" is not a
    result yet: null). mic → Float64 in mg/L (decimal comma; "<=0.03" and ">64" keep their
    number) and mic_censored: Boolean, true when the MIC had a "<=" or ">". diameter in mm:
    CSA's reader writes centimetres."""
    return raw.with_columns(
        # Normalize whitespace/case and translate the 75 non-canonical results; pending is not S/I/R.
        pl.col("sir")
        .str.strip_chars()
        .str.to_lowercase()
        .replace_strict(
            {
                "s": "S",
                "sensible": "S",
                "i": "I",
                "intermedi": "I",
                "r": "R",
                "resistent": "R",
                "pendent": None,
            },
            return_dtype=pl.String,
        )
        .cast(SIR),
        # Keep whether the reported MIC was bounded before removing its qualifier and decimal comma.
        (
            pl.col("mic").str.starts_with("<=") | pl.col("mic").str.starts_with(">")
        )
        .fill_null(False)
        .alias("mic_censored"),
        pl.col("mic")
        .str.replace("<=", "", literal=True)
        .str.replace(">", "", literal=True)
        .str.replace(",", ".", literal=True)
        .cast(pl.Float64, strict=False),
        # CSA records halo diameter in centimetres; the network uses millimetres.
        pl.when(pl.col("lab") == "CSA")
        .then(pl.col("diameter") * 10)
        .otherwise(pl.col("diameter"))
        .alias("diameter"),
    )


def derive(cultures: pl.DataFrame) -> pl.DataFrame:
    """On the joined cultures (combine.cultures): age, the patient's age when the sample was
    collected, in whole years (UInt8)."""
    collected = pl.col("collected_at")
    born = pl.col("born")
    birthday_not_reached = (collected.dt.month() * 100 + collected.dt.day()) < (
        born.dt.month() * 100 + born.dt.day()
    )
    return cultures.with_columns(
        # Subtract one when the sample date falls before the patient's birthday that year.
        (collected.dt.year() - born.dt.year() - birthday_not_reached.cast(pl.Int32))
        .cast(pl.UInt8)
        .alias("age")
    )
