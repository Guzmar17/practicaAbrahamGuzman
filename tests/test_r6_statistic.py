"""R6 · Statistics: n beside every number, fences that find real values."""

import polars as pl

from microbiology import statistic


def test_describe_turnaround(cultures):
    assert statistic.describe(cultures["tat_hours"]) == {
        "n": 2104,
        "missing": 18,
        "mean": 45.56,
        "median": 38.6,
        "std": 29.28,
        "q1": 26.6,
        "q3": 53.8,
        "iqr": 27.2,
        "low": -14.2,
        "high": 94.6,
        "outliers": 145,
    }


def test_outliers_are_the_described_ones(cultures):
    slow = statistic.outliers(cultures)
    assert slow.height == 145
    assert slow["tat_hours"].min() > 94.6 and slow["tat_hours"].is_sorted(descending=True)
    assert slow.columns == ["sample_id", "hospital", "specimen", "organism", "received_at", "tat_hours"]
    assert slow.filter(pl.col("specimen") == "sang").height == 141, "slow is a protocol, not an error"


def test_correlation_says_its_n(isolates):
    assert statistic.correlation(isolates) == {"n": 345, "r": -0.924}
