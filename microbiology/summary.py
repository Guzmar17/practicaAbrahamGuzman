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
    # Only reported samples have a tat_hours; median() skips the nulls of the pending ones.
    frame = cultures.group_by("hospital", "hospital_name").agg(
        pl.len().alias("samples"),
        pl.col("patient").n_unique().alias("patients"),
        pl.col("organism").is_not_null().mean().round(3).alias("positive"),
        pl.col("tat_hours").median().round(1).alias("tat_median"),
    )
    return frame.sort("hospital")


def weekly(cultures: pl.DataFrame) -> pl.DataFrame:
    """Positive cultures (an organism grew) per hospital and week (week: the Monday, Datetime),
    every hospital × every one of the 26 weeks, a week with none as 0 — never a missing row.
    Columns hospital, week, positives; sorted by hospital, week."""
    # Every hospital × every Monday, so a week with no positives still has its row.
    hospitals = cultures.select("hospital").unique()
    weeks = pl.DataFrame({"week": pl.datetime_range(FIRST_WEEK, LAST_WEEK, "1w", eager=True)})
    grid = hospitals.join(weeks, how="cross")

    # truncate("1w") takes each date back to its Monday.
    positives = (
        cultures.filter(pl.col("organism").is_not_null())
        .with_columns(pl.col("collected_at").dt.truncate("1w").alias("week"))
        .group_by("hospital", "week")
        .agg(pl.len().alias("positives"))
    )

    frame = grid.join(positives, on=["hospital", "week"], how="left")
    frame = frame.with_columns(pl.col("positives").fill_null(0))
    return frame.sort("hospital", "week")


def repeat_patients(isolates: pl.DataFrame) -> pl.DataFrame:
    """Patients with two or more E. coli (ECO) isolates with a ciprofloxacin (CIP) result:
    patient, results, first and last (the S/I/R of the earliest and latest collected sample,
    from those rows — never min/max) and acquired: first was S and last is R.
    Sorted by results, most first, then patient."""
    # Sorted by date, first() and last() are the real first and last results.
    # min/max would compare S < I < R instead, and lose the order in time.
    frame = (
        isolates.filter(
            (pl.col("organism") == "ECO") & (pl.col("antibiotic") == "CIP") & pl.col("sir").is_not_null()
        )
        .sort("collected_at", "sample_id")
        .group_by("patient")
        .agg(
            pl.len().alias("results"),
            pl.col("sir").first().alias("first"),
            pl.col("sir").last().alias("last"),
        )
    )
    frame = frame.filter(pl.col("results") >= 2)
    frame = frame.with_columns(((pl.col("first") == "S") & (pl.col("last") == "R")).alias("acquired"))
    return frame.sort(["results", "patient"], descending=[True, False])


def above_hospital(cultures: pl.DataFrame) -> pl.DataFrame:
    """Every reported culture (tat_hours not null), plus hospital_median (that hospital's median
    tat_hours, `over`) and above = tat_hours − hospital_median, one decimal."""
    # over("hospital") puts each hospital's median on every one of its rows.
    frame = cultures.filter(pl.col("tat_hours").is_not_null())
    frame = frame.with_columns(pl.col("tat_hours").median().over("hospital").alias("hospital_median"))
    frame = frame.with_columns((pl.col("tat_hours") - pl.col("hospital_median")).round(1).alias("above"))
    return frame
