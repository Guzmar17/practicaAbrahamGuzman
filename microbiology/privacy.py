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
    raise NotImplementedError("R7")


def pseudonym(patient: str, secret: bytes) -> str:
    """HMAC-SHA256 of the 7-digit patient code under the key, the first 12 hex characters.
    "412345" and "0412345" are the same patient, so the same pseudonym."""
    raise NotImplementedError("R7")


def generalise(cultures: pl.DataFrame, secret: bytes, band: int = 20) -> pl.DataFrame:
    """One row per culture with only: patient (the pseudonym), age_band (the person's youngest
    age in the data // band * band, UInt8: one band per person), sex, zone (the postcode's
    first four digits + "*": 08940 → "0894*"), hospital, month (the first day of the month collected, Date),
    specimen, organism, tat_hours. No patient code, name, surnames, born, postcode, exact time."""
    raise NotImplementedError("R7")


def k_anonymity(release: pl.DataFrame) -> int:
    """The smallest number of distinct *people* (patients, not rows) sharing one combination
    of QUASI. A patient with five samples is still one person."""
    raise NotImplementedError("R7")


def anonymise(cultures: pl.DataFrame, secret: bytes, band: int = 20) -> tuple[pl.DataFrame, int]:
    """(release, suppressed): generalise, then drop every row whose QUASI group has fewer than
    K people. suppressed counts the people dropped (distinct patients), not rows."""
    raise NotImplementedError("R7")


class Release(pt.Model):
    """What may be published. A column not listed here is an error: superfluous columns are refused."""

    pass  # TODO R7: the columns generalise() leaves, and k >= K as a constraint
