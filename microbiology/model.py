"""R3 · Validation with Patito: a row that breaks a rule is kept aside with its reason, never
dropped in silence, and what is left is validated by a model that states the same rules.

The two lines of defence are on purpose: `split` decides, the models check that it did.
"""

from datetime import date, datetime
from typing import Literal

import patito as pt
import polars as pl

#: The half year the samples cover: Monday 5 January to Sunday 5 July 2026.
PERIOD = (datetime(2026, 1, 5), datetime(2026, 7, 6))
#: A zone of inhibition is at least the disc (6 mm) and never wider than the plate allows.
DIAMETER = (6, 50)

#: A rule is the reason (Catalan, as INFORME.md will quote it) and an expression true for a bad row.
PATIENT_RULES: dict[str, pl.Expr] = {
    "data de naixement sentinella": pl.col("born") == date(1900, 1, 1),
}
SAMPLE_RULES: dict[str, pl.Expr] = {
    "data de presa fora del període": (pl.col("collected_at") < PERIOD[0])
    | (pl.col("collected_at") >= PERIOD[1]),
    "recepció abans de la presa": pl.col("received_at") < pl.col("collected_at"),
}
TEST_RULES: dict[str, pl.Expr] = {
    "diàmetre impossible": (pl.col("diameter") < DIAMETER[0])
    | (pl.col("diameter") > DIAMETER[1]),
}


def split(df: pl.DataFrame, rules: dict[str, pl.Expr]) -> tuple[pl.DataFrame, pl.DataFrame]:
    """(kept, rejected). rejected has every column of df plus `reason`, the names of every rule
    the row broke joined by "; " in the order of `rules`. A rule that evaluates to null does
    not reject the row."""
    reason_parts = []
    for name, expression in rules.items():
        reason_parts.append(pl.when(expression).then(pl.lit(name)))

    if reason_parts:
        reason = pl.concat_str(
            reason_parts,
            separator="; ",
            ignore_nulls=True,
        )
    else:
        reason = pl.lit("")

    checked = df.with_columns(reason.alias("reason"))
    has_reason = pl.col("reason").is_not_null() & (pl.col("reason") != "")

    rejected = checked.filter(has_reason)
    kept = checked.filter(~has_reason).drop("reason")
    return kept, rejected


class Patient(pt.Model):
    """A patient as clean.patients leaves them, after split(PATIENT_RULES)."""

    patient: str
    name: str
    surnames: str
    born: date = pt.Field(constraints=pt.field != date(1900, 1, 1))
    sex: Literal["D", "H"] | None
    postcode: str


class Sample(pt.Model):
    """A sample as clean.samples leaves it, after split(SAMPLE_RULES)."""

    sample_id: str
    hospital: str
    patient: str = pt.Field(pattern=r"^\d{7}$")
    specimen: Literal["orina", "sang", "ferida", "esput"]
    collected_at: datetime = pt.Field(
        ge=PERIOD[0],
        lt=PERIOD[1],
        constraints=(pt.field >= PERIOD[0]) & (pt.field < PERIOD[1]),
    )
    received_at: datetime = pt.Field(
        constraints=pt.field >= pl.col("collected_at")
    )
    reported_at: datetime | None
    organism: Literal["ECO", "KPN", "PAE", "SAU", "EFA"] | None
    tat_hours: float | None


class Susceptibility(pt.Model):
    """One antibiotic tested on one sample, as clean.antibiogram leaves it, after split(TEST_RULES)."""

    sample_id: str
    lab: str
    antibiotic: str
    mic: float | None
    diameter: float | None = pt.Field(ge=DIAMETER[0], le=DIAMETER[1])
    sir: Literal["S", "I", "R"] | None
    mic_censored: bool
