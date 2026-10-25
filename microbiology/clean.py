"""R2 · Cleaning with expressions: what each source meant, written as Polars expressions.

Every fix is a decision. Write the decision in a comment beside it, and its count in INFORME.md.
"""

import polars as pl

from .load import SEX, SIR, SPECIMEN

#: The five organisms the network reports, by their code.
ORGANISM = pl.Enum(["ECO", "KPN", "PAE", "SAU", "EFA"])

#: Every spelling the three hospitals use, stripped and in lower case → its code; a culture with
#: no growth → None. `replace_strict` fails on a spelling missing here: that is how you find them.
ORGANISMS = {"escherichia coli": "ECO", "e. coli": "ECO", "e.coli": "ECO"}  # TODO R2: every spelling in the data


def patients(raw: pl.DataFrame) -> pl.DataFrame:
    """sex → Enum SEX (" h", "d" and "Dona" are H, D and D; empty is unknown), born → Date.
    patient, name, surnames and postcode stay String."""
    raise NotImplementedError("R2")


def samples(raw: pl.DataFrame) -> pl.DataFrame:
    """patient → the 7-digit code (OLV's system wrote it as a number and lost the leading
    zeros), specimen → Enum SPECIMEN, organism → Enum ORGANISM through ORGANISMS (null: no
    growth). Adds tat_hours: reception to report in hours, one decimal, null while pending."""
    raise NotImplementedError("R2")


def antibiogram(raw: pl.DataFrame) -> pl.DataFrame:
    """sir → Enum SIR ("s", " R", "Sensible", "resistent" are S, R, S, R; "pendent" is not a
    result yet: null). mic → Float64 in mg/L (decimal comma; "<=0.03" and ">64" keep their
    number) and mic_censored: Boolean, true when the MIC had a "<=" or ">". diameter in mm:
    CSA's reader writes centimetres."""
    raise NotImplementedError("R2")


def derive(cultures: pl.DataFrame) -> pl.DataFrame:
    """On the joined cultures (combine.cultures): age, the patient's age when the sample was
    collected, in whole years (UInt8)."""
    raise NotImplementedError("R2")
