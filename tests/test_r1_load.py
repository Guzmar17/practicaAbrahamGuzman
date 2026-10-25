"""R1 · Loading: the files read typed, nothing lost, codes kept as text, three hospitals in one table."""

import polars as pl

from microbiology import load


def test_patients_keep_their_codes_as_text():
    patients = load.patients()
    assert patients.shape == (900, 6)
    assert patients.columns == ["patient", "name", "surnames", "born", "sex", "postcode"]
    assert patients.schema["patient"] == pl.String and patients.schema["postcode"] == pl.String
    assert patients["patient"].str.starts_with("0").sum() == 133, "a code read as a number loses its leading zeros"
    assert patients["postcode"].str.starts_with("08").all()


def test_three_hospitals_one_table():
    samples = load.samples()
    assert samples.columns == load.SAMPLE_COLUMNS
    assert samples.group_by("hospital").len().sort("hospital").rows() == [("CSA", 454), ("OLV", 757), ("RBX", 933)]
    assert samples.schema["patient"] == pl.String and samples.schema["sample_id"] == pl.String


def test_three_date_formats_are_datetimes():
    samples = load.samples()
    for column in ["collected_at", "received_at", "reported_at"]:
        assert samples.schema[column] == pl.Datetime("us"), column
    assert samples["collected_at"].null_count() == 0, "every hospital's dates parsed, none lost"
    assert samples["reported_at"].null_count() == 18, '"n/a" and "" are a sample still in the lab'
    olv = samples.filter(pl.col("sample_id") == "OLV26-00026").row(0, named=True)
    assert (olv["patient"], olv["collected_at"].isoformat()) == ("825523", "2026-01-09T17:38:00"), "the file as it is"


def test_antibiogram_as_the_lab_wrote_it():
    tests = load.antibiogram()
    assert tests.height == 6854
    assert tests.schema["mic"] == pl.String, '"<=0.03" and "0,5" are not numbers yet'
    assert tests.schema["diameter"] == pl.Float64
    assert tests["mic"].null_count() == 30, '"", "NA" and "-" are all missing'
    assert tests["sir"].null_count() == 0, '"pendent" is text: cleaning decides what it means'


def test_hospitals_as_the_file_has_them():
    hospitals = load.hospitals()
    assert hospitals.height == 4, "loading fixes nothing: the duplicated hospital is still there"
    assert hospitals.schema["beds"] == pl.UInt16
