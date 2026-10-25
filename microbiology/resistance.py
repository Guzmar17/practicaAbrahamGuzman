"""R11 · The cumulative antibiogram: how often an organism resists each antibiotic, per hospital.

Two rules make the figure honest. Only the **first isolate** of each patient and organism
counts: a patient cultured five times is one patient, not five resistances. And a rate over
fewer than MIN_N isolates is not published: with 12 isolates, one more resistant moves it 8 points.

R12 · Rate: the model that checks the published table keeps both rules.
"""

import patito as pt
import polars as pl

#: The fewest first isolates a published rate may rest on.
MIN_N = 30
HOSPITALS = ["RBX", "OLV", "CSA"]


def first_isolates(isolates: pl.DataFrame) -> pl.DataFrame:
    """The rows of each patient's first sample of each organism (earliest collected_at; on a tie,
    the smallest sample_id), with all of that sample's antibiotics. Same columns as isolates."""
    raise NotImplementedError("R11")


def rates(isolates: pl.DataFrame, organism: str) -> pl.DataFrame:
    """One row per antibiotic and hospital, over the organism's first isolates with a result
    (sir not null): antibiotic, hospital, tested, resistant (sir R; I is not R) and rate =
    resistant / tested, 3 decimals — null when tested < MIN_N. Sorted by antibiotic, hospital."""
    raise NotImplementedError("R11")


def cumulative(isolates: pl.DataFrame, organism: str) -> pl.DataFrame:
    """The table a microbiologist prints: one row per antibiotic, sorted; tested (all hospitals),
    network (% resistant over all of them, one decimal) and one column per hospital in HOSPITALS
    order with its % resistant, one decimal, null where rates() is null."""
    raise NotImplementedError("R11")


class Rate(pt.Model):
    """A row of rates() as it may be published: a rate only over MIN_N first isolates or more,
    never more resistant than tested, a share between 0 and 1. No column that names anyone."""

    pass  # TODO R12: one annotated field per column of rates(), and its rules
