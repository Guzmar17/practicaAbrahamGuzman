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
    # TODO R3: "reason": expression true for a bad row
}
SAMPLE_RULES: dict[str, pl.Expr] = {
    # TODO R3
}
TEST_RULES: dict[str, pl.Expr] = {
    # TODO R3
}


def split(df: pl.DataFrame, rules: dict[str, pl.Expr]) -> tuple[pl.DataFrame, pl.DataFrame]:
    """(kept, rejected). rejected has every column of df plus `reason`, the names of every rule
    the row broke joined by "; " in the order of `rules`. A rule that evaluates to null does
    not reject the row."""
    raise NotImplementedError("R3")


class Patient(pt.Model):
    """A patient as clean.patients leaves them, after split(PATIENT_RULES)."""

    pass  # TODO R3: one annotated field per column, with its Field(...) rules


class Sample(pt.Model):
    """A sample as clean.samples leaves it, after split(SAMPLE_RULES)."""

    pass  # TODO R3: one annotated field per column, with its Field(...) rules


class Susceptibility(pt.Model):
    """One antibiotic tested on one sample, as clean.antibiogram leaves it, after split(TEST_RULES)."""

    pass  # TODO R3: one annotated field per column, with its Field(...) rules
