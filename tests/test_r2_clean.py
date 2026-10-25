"""R2 · Cleaning: each source's habits undone with expressions."""

import polars as pl

from microbiology import clean, load


def test_patients_typed():
    patients = clean.patients(load.patients())
    assert patients.schema["sex"] == load.SEX and patients.schema["born"] == pl.Date
    assert patients["sex"].null_count() == 7, "an empty sex is unknown, not a third value"
    assert patients.filter(pl.col("patient") == "8331112")["sex"].item() == "H", '"Home" is H'
    assert patients.filter(pl.col("patient") == "2944396")["sex"].item() == "D", '"Dona" is D'


def test_samples_codes_specimens_organisms():
    samples = clean.samples(load.samples())
    assert samples["patient"].str.len_chars().unique().to_list() == [7], "OLV's 825523 is 0825523"
    assert samples.filter(pl.col("sample_id") == "OLV26-00026")["patient"].item() == "0825523"
    assert samples.schema["specimen"] == load.SPECIMEN
    assert samples.schema["organism"] == clean.ORGANISM
    assert samples.group_by("organism").len().sort("organism").rows() == [
        (None, 1002),
        ("ECO", 519),
        ("KPN", 191),
        ("PAE", 126),
        ("SAU", 192),
        ("EFA", 114),
    ], '"E. coli", "E.COLI" and "Escherichia coli" are one organism; "negatiu", "NEG" and "" are none'


def test_turnaround_in_hours():
    samples = clean.samples(load.samples())
    assert samples["tat_hours"].null_count() == 18, "a pending sample has no turnaround yet"
    one = samples.filter(pl.col("sample_id") == "OLV26-00026")["tat_hours"].item()
    assert one == 51.8, "09/01 18:43 → 11/01 22:32"


def test_antibiogram_one_vocabulary():
    tests = clean.antibiogram(load.antibiogram())
    assert tests.schema["sir"] == load.SIR
    assert tests.group_by("sir").len().sort("sir").rows() == [(None, 14), ("S", 4910), ("I", 229), ("R", 1701)]
    assert tests.schema["mic"] == pl.Float64 and tests["mic"].null_count() == 30
    assert (tests["mic"].min(), tests["mic"].max()) == (0.03, 64.0), "<=0.03 and >64 keep their number"
    assert tests["mic_censored"].sum() == 631
    csa = tests.filter((pl.col("sample_id") == "CSA26-00001") & (pl.col("antibiotic") == "CIP"))
    assert csa["diameter"].item() == 17, "CSA's 1.7 cm is 17 mm"


def test_age(cultures):
    assert cultures.schema["age"] == pl.UInt8
    assert cultures["age"].max() < 100 and cultures["age"].min() == 0
