"""R11 · The cumulative antibiogram: first isolates only, and no rate over fewer than MIN_N."""

import polars as pl

from microbiology import resistance


def test_first_isolates_count_people(isolates):
    first = resistance.first_isolates(isolates)
    assert first.columns == isolates.columns
    per_person = first.group_by("patient", "organism").agg(pl.col("sample_id").n_unique())
    assert per_person["sample_id"].max() == 1, "one sample per patient and organism"
    assert first.filter(pl.col("organism") == "ECO")["sample_id"].n_unique() == 405
    assert isolates.filter(pl.col("organism") == "ECO")["sample_id"].n_unique() == 511


def test_first_is_the_earliest(isolates):
    first = resistance.first_isolates(isolates)
    earliest = isolates.group_by("patient", "organism").agg(pl.col("collected_at").min())
    joined = first.join(earliest, on=["patient", "organism"], suffix="_min")
    assert (joined["collected_at"] == joined["collected_at_min"]).all()


def test_rates_with_their_n(isolates):
    rates = resistance.rates(isolates, "ECO")
    assert rates.columns == ["antibiotic", "hospital", "tested", "resistant", "rate"]
    assert rates.height == 7 * 3
    cip = rates.filter(pl.col("antibiotic") == "CIP").sort("hospital").rows()
    assert cip == [("CIP", "CSA", 93, 11, 0.118), ("CIP", "OLV", 133, 51, 0.383), ("CIP", "RBX", 177, 51, 0.288)]


def test_no_rate_under_min_n(isolates):
    rates = resistance.rates(isolates, "KPN")
    small = rates.filter(pl.col("tested") < resistance.MIN_N)
    assert small.height == 7 and small["hospital"].unique().to_list() == ["CSA"]
    assert small["rate"].null_count() == 7, "28 isolates: no published rate"
    assert rates.filter(pl.col("tested") >= resistance.MIN_N)["rate"].null_count() == 0


def test_the_cumulative_table(isolates):
    table = resistance.cumulative(isolates, "ECO")
    assert table.columns == ["antibiotic", "tested", "network", "RBX", "OLV", "CSA"]
    assert table["antibiotic"].to_list() == ["AMC", "AMP", "CIP", "CTX", "GEN", "MEM", "SXT"]
    assert table.filter(pl.col("antibiotic") == "CIP").row(0) == ("CIP", 403, 28.0, 28.8, 38.3, 11.8)
    kpn = resistance.cumulative(isolates, "KPN")
    assert kpn["CSA"].null_count() == 7 and kpn["network"].null_count() == 0
