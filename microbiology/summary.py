"""R5 · Aggregations: one row per group, the group's size beside every figure, and the groups
that had no rows still shown.
"""

from datetime import datetime

import polars as pl

#: The half year the data covers: Monday 5 January to Sunday 5 July 2026, 26 weeks.
FIRST_WEEK = datetime(2026, 1, 5)
LAST_WEEK = datetime(2026, 6, 29)


def by_hospital(cultures: pl.DataFrame) -> pl.DataFrame:
    """One row per hospital, sorted by hospital: hospital, hospital_name, samples, patients
    (distinct), positive (the share of samples that grew an organism, 3 decimals) and
    tat_median (hours, one decimal, reported samples only)."""
    raise NotImplementedError("R5")


def weekly(cultures: pl.DataFrame) -> pl.DataFrame:
    """Positive cultures (an organism grew) per hospital and week (week: the Monday, Datetime),
    every hospital × every one of the 26 weeks, a week with none as 0 — never a missing row.
    Columns hospital, week, positives; sorted by hospital, week."""
    raise NotImplementedError("R5")


def repeat_patients(isolates: pl.DataFrame) -> pl.DataFrame:
    """Patients with two or more E. coli (ECO) isolates with a ciprofloxacin (CIP) result:
    patient, results, first and last (the S/I/R of the earliest and latest collected sample,
    from those rows — never min/max) and acquired: first was S and last is R.
    Sorted by results, most first, then patient."""
    raise NotImplementedError("R5")


def above_hospital(cultures: pl.DataFrame) -> pl.DataFrame:
    """Every reported culture (tat_hours not null), plus hospital_median (that hospital's median
    tat_hours, `over`) and above = tat_hours − hospital_median, one decimal."""
    raise NotImplementedError("R5")
