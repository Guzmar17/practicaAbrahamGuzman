"""R7 · Pseudonymisation and anonymisation: what may leave the network.

A keyed hash links a patient's samples without naming them, and whoever has the key can undo
it: that is pseudonymised, still personal data. The release on top of it also generalises the
quasi-identifiers and suppresses whoever is still in a group of fewer than K people.
"""

import hashlib
import hmac
import os
from datetime import date
from typing import Literal

import patito as pt
import polars as pl

#: Where the key is: an environment variable, never the code or the repository.
KEY_VARIABLE = "ECB_MICROBIOLOGY_KEY"
K = 5
QUASI = ["age_band", "sex", "zone"]


def key() -> bytes:
    """The pseudonym key, from the environment as hex. A missing key is an error, never a default."""
    value = os.environ.get(KEY_VARIABLE)
    if not value:
        raise RuntimeError(f"{KEY_VARIABLE} is not set: no key, no pseudonyms")
    return bytes.fromhex(value)


def pseudonym(patient: str, secret: bytes) -> str:
    """HMAC-SHA256 of the 7-digit patient code under the key, the first 12 hex characters.
    "412345" and "0412345" are the same patient, so the same pseudonym."""
    # Padded first, so OLV's code without its leading zeros gives the same pseudonym.
    code = patient.zfill(7)
    digest = hmac.new(secret, code.encode(), hashlib.sha256).hexdigest()
    return digest[:12]


def generalise(cultures: pl.DataFrame, secret: bytes, band: int = 20) -> pl.DataFrame:
    """One row per culture with only: patient (the pseudonym), age_band (the person's youngest
    age in the data // band * band, UInt8: one band per person), sex, zone (the postcode's
    first four digits + "*": 08940 → "0894*"), hospital, month (the first day of the month collected, Date),
    specimen, organism, tat_hours. No patient code, name, surnames, born, postcode, exact time."""
    frame = cultures.with_columns(
        pl.col("patient").map_elements(lambda code: pseudonym(code, secret), return_dtype=pl.String),
        # The youngest age of each person, so a birthday between two samples does not split them.
        (pl.col("age").min().over("patient") // band * band).cast(pl.UInt8).alias("age_band"),
        (pl.col("postcode").str.slice(0, 4) + "*").alias("zone"),
        pl.col("collected_at").dt.month_start().cast(pl.Date).alias("month"),
    )
    return frame.select(
        "patient", "age_band", "sex", "zone", "hospital", "month", "specimen", "organism", "tat_hours"
    )


def k_anonymity(release: pl.DataFrame) -> int:
    """The smallest number of distinct *people* (patients, not rows) sharing one combination
    of QUASI. A patient with five samples is still one person."""
    # n_unique of patient, not len: a person with five samples counts once.
    groups = release.group_by(QUASI).agg(pl.col("patient").n_unique().alias("people"))
    return groups["people"].min()


def anonymise(cultures: pl.DataFrame, secret: bytes, band: int = 20) -> tuple[pl.DataFrame, int]:
    """(release, suppressed): generalise, then drop every row whose QUASI group has fewer than
    K people. suppressed counts the people dropped (distinct patients), not rows."""
    general = generalise(cultures, secret, band)
    people = pl.col("patient").n_unique().over(QUASI)
    release = general.filter(people >= K)
    dropped = general.filter(people < K)
    return release, dropped["patient"].n_unique()


class Release(pt.Model):
    """What may be published. A column not listed here is an error: superfluous columns are refused."""

    # Patito refuses any column not declared here (superfluous columns are an error).
    patient: str = pt.Field(
        pattern=r"^[0-9a-f]{12}$",
        # Every row's group of QUASI has at least K different people.
        constraints=pt.field.n_unique().over(QUASI) >= K,
    )
    age_band: int = pt.Field(dtype=pl.UInt8)
    sex: Literal["D", "H"] | None
    zone: str = pt.Field(pattern=r"^\d{4}\*$")
    hospital: str
    month: date
    specimen: Literal["orina", "sang", "ferida", "esput"]
    organism: Literal["ECO", "KPN", "PAE", "SAU", "EFA"] | None
    tat_hours: float | None
