"""R6 · Statistics: a handful of numbers that describe the turnaround time, and n beside every one."""

import polars as pl


def describe(values: pl.Series) -> dict[str, float | int]:
    """n (non-null), missing, mean, median, std (sample), q1, q3 (linear), iqr, low and high
    (the 1.5·IQR fences) and outliers (how many values fall outside them). Floats to 2 decimals."""
    raise NotImplementedError("R6")


def outliers(cultures: pl.DataFrame) -> pl.DataFrame:
    """The cultures whose tat_hours is above the high fence, slowest first: sample_id, hospital,
    specimen, organism, received_at, tat_hours. Slow is not wrong: look at what they are."""
    raise NotImplementedError("R6")


def correlation(isolates: pl.DataFrame) -> dict[str, float | int]:
    """Pearson's r between the disc's diameter and log2 of the MIC (`pl.col("mic").log(2)`),
    for E. coli and ciprofloxacin, over the tests that have both, and that n. 3 decimals."""
    raise NotImplementedError("R6")
