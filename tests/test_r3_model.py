"""R3 · Validation: bad rows put aside with every reason, the rest checked by a Patito model."""

import patito as pt
import pytest

from microbiology import clean, load, model


def test_rejected_with_their_reasons(analysis):
    reasons = {name: sorted(frame.group_by("reason").len().rows()) for name, frame in analysis.rejected.items()}
    assert reasons == {
        "patients": [("data de naixement sentinella", 4)],
        "samples": [
            ("data de presa fora del període; recepció abans de la presa", 2),
            ("recepció abans de la presa", 3),
        ],
        "antibiogram": [("diàmetre impossible", 2)],
    }


def test_split_keeps_every_row():
    samples = clean.samples(load.samples())
    kept, rejected = model.split(samples, model.SAMPLE_RULES)
    assert kept.height + rejected.height == samples.height
    assert kept.columns == samples.columns and "reason" in rejected.columns


def test_the_models_refuse_what_split_would_reject():
    with pytest.raises(pt.exceptions.DataFrameValidationError):
        model.Patient.validate(clean.patients(load.patients()))
    with pytest.raises(pt.exceptions.DataFrameValidationError):
        model.Sample.validate(clean.samples(load.samples()))
    with pytest.raises(pt.exceptions.DataFrameValidationError):
        model.Susceptibility.validate(clean.antibiogram(load.antibiogram()))


def test_the_sample_model_refuses_a_code_without_its_zeros():
    kept = model.split(clean.samples(load.samples()), model.SAMPLE_RULES)[0]
    with pytest.raises(pt.exceptions.DataFrameValidationError):
        model.Sample.validate(kept.with_columns(kept["patient"].str.strip_chars_start("0")))


def test_the_models_accept_what_split_kept():
    model.Patient.validate(model.split(clean.patients(load.patients()), model.PATIENT_RULES)[0])
    model.Sample.validate(model.split(clean.samples(load.samples()), model.SAMPLE_RULES)[0])
    model.Susceptibility.validate(model.split(clean.antibiogram(load.antibiogram()), model.TEST_RULES)[0])
