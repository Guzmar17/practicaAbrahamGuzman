"""The whole analysis in order, once: load → clean → split and validate → join → derive.

Given complete. Read it to see which of your functions feeds which; run it with
`uv run python -m microbiology.pipeline` to print the counts INFORME.md asks for.
"""

from dataclasses import dataclass, field

import polars as pl

from . import clean, combine, load, model, privacy, resistance, statistic, summary


@dataclass
class Analysis:
    cultures: pl.DataFrame  # one row per sample with a known patient
    isolates: pl.DataFrame  # one row per antibiotic tested on one of those samples
    rejected: dict[str, pl.DataFrame]
    lost: dict[str, int]
    counts: dict[str, int] = field(default_factory=dict)


def run() -> Analysis:
    raw = {"patients": load.patients(), "samples": load.samples(), "antibiogram": load.antibiogram()}
    patients, bad_patients = model.split(clean.patients(raw["patients"]), model.PATIENT_RULES)
    samples, bad_samples = model.split(clean.samples(raw["samples"]), model.SAMPLE_RULES)
    tests, bad_tests = model.split(clean.antibiogram(raw["antibiogram"]), model.TEST_RULES)
    model.Patient.validate(patients)
    model.Sample.validate(samples)
    model.Susceptibility.validate(tests)

    hospitals = combine.unique_hospitals(load.hospitals())
    lost = combine.unmatched(samples, patients, tests)
    cultures = clean.derive(combine.cultures(samples, patients, hospitals))
    isolates = combine.isolates(tests, cultures)
    counts = {name: frame.height for name, frame in raw.items()}
    counts |= {"cultures": cultures.height, "isolates": isolates.height}
    rejected = {"patients": bad_patients, "samples": bad_samples, "antibiogram": bad_tests}
    return Analysis(cultures, isolates, rejected, lost, counts)


def main() -> None:
    analysis = run()
    print("rows read:", analysis.counts)
    print("rejected:", {name: frame.height for name, frame in analysis.rejected.items()})
    for name, frame in analysis.rejected.items():
        if frame.height:
            print(f"  {name}:", frame.group_by("reason").len().sort("reason").rows())
    print("lost in the joins:", analysis.lost)
    with pl.Config(tbl_rows=12, tbl_cols=-1, tbl_width_chars=140):
        print(summary.by_hospital(analysis.cultures))
        print(resistance.cumulative(analysis.isolates, "ECO"))
    print("turnaround (h):", statistic.describe(analysis.cultures["tat_hours"]))
    print("diameter ~ log2 MIC:", statistic.correlation(analysis.isolates))
    try:
        release, suppressed = privacy.anonymise(analysis.cultures, privacy.key())
    except RuntimeError as error:
        print("release: skipped,", error)
    else:
        print(f"release: {release.height} rows, k = {privacy.k_anonymity(release)}, {suppressed} people suppressed")


if __name__ == "__main__":
    main()
