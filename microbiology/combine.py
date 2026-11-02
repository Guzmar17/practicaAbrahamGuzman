"""R4 · Joins: five systems become a table of cultures and a table of isolates, and nothing is
lost without a count.

A join is not a lookup. Every lookup here is declared `validate="m:1"`, so a duplicated key
raises instead of multiplying rows.
"""

import polars as pl


def unique_hospitals(hospitals: pl.DataFrame) -> pl.DataFrame:
    """One row per code. OLV appears twice (the hospital was renamed and the old row kept):
    keep the first, which is the name the network uses today."""
    # The first OLV row is today's name; the second is the old one, kept by mistake.
    return hospitals.unique(subset="code", keep="first", maintain_order=True)


def unmatched(samples: pl.DataFrame, patients: pl.DataFrame, tests: pl.DataFrame) -> dict[str, int]:
    """How many rows an inner join loses, with anti joins:
    {"samples_without_patient": …, "patients_without_sample": …, "tests_without_sample": …}
    (samples ⨝ patients on patient, both ways; tests ⨝ samples on sample_id, tests' side)."""
    samples_without_patient = samples.join(patients, on="patient", how="anti")
    patients_without_sample = patients.join(samples, on="patient", how="anti")
    tests_without_sample = tests.join(samples, on="sample_id", how="anti")
    return {
        "samples_without_patient": samples_without_patient.height,
        "patients_without_sample": patients_without_sample.height,
        "tests_without_sample": tests_without_sample.height,
    }


def cultures(samples: pl.DataFrame, patients: pl.DataFrame, hospitals: pl.DataFrame) -> pl.DataFrame:
    """One row per sample whose patient is known: the sample's columns, the patient's
    (name, surnames, born, sex, postcode) and hospital_name, hospital_beds.
    The hospital is joined on samples.hospital = hospitals.code."""
    # Both tables have a "name": the hospital's columns are renamed before the join.
    hospitals = hospitals.select(
        pl.col("code"),
        pl.col("name").alias("hospital_name"),
        pl.col("beds").alias("hospital_beds"),
    )
    # Inner: a sample whose patient is unknown is dropped (counted in unmatched).
    frame = samples.join(patients, on="patient", how="inner", validate="m:1")
    # The hospital is "hospital" in samples and "code" in hospitals.
    frame = frame.join(hospitals, left_on="hospital", right_on="code", how="left", validate="m:1")
    return frame


def isolates(tests: pl.DataFrame, cultures: pl.DataFrame) -> pl.DataFrame:
    """One row per antibiotic tested on a culture that is in `cultures`: the test's columns and
    the culture's hospital, patient, specimen, organism and collected_at."""
    culture_columns = cultures.select("sample_id", "hospital", "patient", "specimen", "organism", "collected_at")
    # Inner: a test whose sample is not a culture is dropped (counted in unmatched).
    return tests.join(culture_columns, on="sample_id", how="inner", validate="m:1")
