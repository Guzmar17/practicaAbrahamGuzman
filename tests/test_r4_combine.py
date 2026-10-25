"""R4 · Joins: declared, counted, and refusing a duplicated key."""

import polars as pl
import pytest

from microbiology import clean, combine, load, model


def kept(frame, rules):
    return model.split(frame, rules)[0]


@pytest.fixture(scope="module")
def sides():
    patients = kept(clean.patients(load.patients()), model.PATIENT_RULES)
    samples = kept(clean.samples(load.samples()), model.SAMPLE_RULES)
    tests = kept(clean.antibiogram(load.antibiogram()), model.TEST_RULES)
    return samples, patients, tests


def test_a_duplicated_hospital_is_refused_not_multiplied(sides):
    samples, patients, _ = sides
    with pytest.raises(pl.exceptions.ComputeError):
        combine.cultures(samples, patients, load.hospitals())


def test_unique_hospitals():
    hospitals = combine.unique_hospitals(load.hospitals())
    assert hospitals["code"].to_list() == ["RBX", "OLV", "CSA"]
    assert hospitals.filter(pl.col("code") == "OLV")["name"].item() == "Hospital de l'Olivar"


def test_what_the_inner_joins_lose(sides):
    assert combine.unmatched(*sides) == {
        "samples_without_patient": 17,
        "patients_without_sample": 0,
        "tests_without_sample": 25,
    }


def test_cultures(cultures, sides):
    samples, _, _ = sides
    assert cultures.height == samples.height - 17 == 2122
    assert {"name", "postcode", "hospital_name", "hospital_beds", "organism", "tat_hours"} <= set(cultures.columns)
    assert cultures["hospital_name"].null_count() == 0
    assert cultures["sample_id"].is_unique().all()


def test_isolates(isolates, cultures):
    assert isolates.height == 6783
    assert {"antibiotic", "sir", "mic", "hospital", "patient", "organism", "collected_at"} <= set(isolates.columns)
    assert isolates["organism"].null_count() == 0, "only a culture that grew has an antibiogram"
    assert set(isolates["sample_id"]) <= set(cultures["sample_id"])
