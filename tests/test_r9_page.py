"""R9 · The page, mounted without a browser (conftest.page), its fetches answered by the real routes."""

import pytest


@pytest.mark.filterwarnings("ignore:zoom, brush")
def test_three_charts_and_the_summary(page):
    svgs = page.find_all("svg")
    titles = " ".join(svg.text for svg in svgs)
    for title in ["Mostres per hospital", "Cultius positius per setmana · RBX", "CMI i diàmetre"]:
        assert title in titles, title
    assert page.find("img").attrs["src"] == "/api/tat.svg"
    assert "k = " in page.text and "n = 2104" in page.text


@pytest.mark.filterwarnings("ignore:zoom, brush")
def test_a_hospital_button_redraws_the_week(page):
    page.click("button.hospital-CSA")
    assert "Cultius positius per setmana · CSA" in page.text
    assert page.find("button.hospital-CSA").attrs["aria-pressed"] == "true"
