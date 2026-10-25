"""R5 · Aggregations: group sizes beside the figures, and the week that had none."""

from datetime import datetime

import polars as pl

from microbiology import summary


def test_by_hospital(cultures):
    hospitals = summary.by_hospital(cultures)
    assert hospitals.columns == ["hospital", "hospital_name", "samples", "patients", "positive", "tat_median"]
    assert hospitals.rows() == [
        ("CSA", "Hospital de Castellsalat", 450, 236, 0.531, 38.3),
        ("OLV", "Hospital de l'Olivar", 748, 351, 0.516, 37.9),
        ("RBX", "Hospital de Riubaix", 924, 423, 0.548, 39.5),
    ]


def test_weekly_has_every_week(cultures):
    weekly = summary.weekly(cultures)
    assert weekly.height == 3 * 26
    assert weekly["positives"].sum() == cultures["organism"].is_not_null().sum() == 1131
    closed = weekly.filter((pl.col("hospital") == "CSA") & (pl.col("week") == datetime(2026, 2, 16)))
    assert closed["positives"].to_list() == [0], "a week with none is a 0, not a missing row"


def test_first_and_last_come_from_real_rows(isolates):
    repeat = summary.repeat_patients(isolates)
    assert repeat.height == 88
    assert repeat["acquired"].sum() == 12
    for row in repeat.filter(pl.col("acquired") | (pl.col("first") != pl.col("last"))).iter_rows(named=True):
        rows = (
            isolates.filter(
                (pl.col("patient") == row["patient"]) & (pl.col("organism") == "ECO") & (pl.col("antibiotic") == "CIP")
            )
            .drop_nulls("sir")
            .sort("collected_at", "sample_id")
        )
        assert (row["first"], row["last"]) == (rows["sir"][0], rows["sir"][-1]), row["patient"]


def test_above_hospital_is_relative_to_its_own_hospital(cultures):
    above = summary.above_hospital(cultures)
    assert above.height == 2104
    medians = above.group_by("hospital").agg(pl.col("above").median())
    assert medians["above"].abs().max() < 0.1
