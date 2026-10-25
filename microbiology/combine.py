"""R4 · Joins: five systems become a table of cultures and a table of isolates, and nothing is
lost without a count.

A join is not a lookup. Every lookup here is declared `validate="m:1"`, so a duplicated key
raises instead of multiplying rows.
"""

import polars as pl


def unique_hospitals(hospitals: pl.DataFrame) -> pl.DataFrame:
    """One row per code. OLV appears twice (the hospital was renamed and the old row kept):
    keep the first, which is the name the network uses today."""
    raise NotImplementedError("R4")


def unmatched(samples: pl.DataFrame, patients: pl.DataFrame, tests: pl.DataFrame) -> dict[str, int]:
    """How many rows an inner join loses, with anti joins:
    {"samples_without_patient": …, "patients_without_sample": …, "tests_without_sample": …}
    (samples ⨝ patients on patient, both ways; tests ⨝ samples on sample_id, tests' side)."""
    raise NotImplementedError("R4")


def cultures(samples: pl.DataFrame, patients: pl.DataFrame, hospitals: pl.DataFrame) -> pl.DataFrame:
    """One row per sample whose patient is known: the sample's columns, the patient's
    (name, surnames, born, sex, postcode) and hospital_name, hospital_beds.
    The hospital is joined on samples.hospital = hospitals.code."""
    raise NotImplementedError("R4")


def isolates(tests: pl.DataFrame, cultures: pl.DataFrame) -> pl.DataFrame:
    """One row per antibiotic tested on a culture that is in `cultures`: the test's columns and
    the culture's hospital, patient, specimen, organism and collected_at."""
    raise NotImplementedError("R4")
