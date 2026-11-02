"""R6 · Statistics: a handful of numbers that describe the turnaround time, and n beside every one."""

import polars as pl


def describe(values: pl.Series) -> dict[str, float | int]:
    """n (non-null), missing, mean, median, std (sample), q1, q3 (linear), iqr, low and high
    (the 1.5·IQR fences) and outliers (how many values fall outside them). Floats to 2 decimals."""
    present = values.drop_nulls()
    q1 = present.quantile(0.25, interpolation="linear")
    q3 = present.quantile(0.75, interpolation="linear")
    iqr = q3 - q1
    # Tukey's fences: 1.5 IQR below the first quartile and above the third.
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    outside = present.filter((present < low) | (present > high))
    return {
        "n": present.len(),
        "missing": values.null_count(),
        "mean": round(present.mean(), 2),
        "median": round(present.median(), 2),
        "std": round(present.std(), 2),
        "q1": round(q1, 2),
        "q3": round(q3, 2),
        "iqr": round(iqr, 2),
        "low": round(low, 2),
        "high": round(high, 2),
        "outliers": outside.len(),
    }


def outliers(cultures: pl.DataFrame) -> pl.DataFrame:
    """The cultures whose tat_hours is above the high fence, slowest first: sample_id, hospital,
    specimen, organism, received_at, tat_hours. Slow is not wrong: look at what they are."""
    high = describe(cultures["tat_hours"])["high"]
    frame = cultures.filter(pl.col("tat_hours") > high)
    frame = frame.select("sample_id", "hospital", "specimen", "organism", "received_at", "tat_hours")
    return frame.sort("tat_hours", descending=True)


def correlation(isolates: pl.DataFrame) -> dict[str, float | int]:
    """Pearson's r between the disc's diameter and log2 of the MIC (`pl.col("mic").log(2)`),
    for E. coli and ciprofloxacin, over the tests that have both, and that n. 3 decimals."""
    # The MIC doubles from one dilution to the next: log2 puts those steps at equal distance.
    frame = isolates.filter((pl.col("organism") == "ECO") & (pl.col("antibiotic") == "CIP"))
    frame = frame.drop_nulls(["diameter", "mic"])
    r = frame.select(pl.corr("diameter", pl.col("mic").log(2))).item()
    return {"n": frame.height, "r": round(r, 3)}
