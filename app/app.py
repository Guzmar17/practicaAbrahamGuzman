"""R9 · The page: four charts of the half year, from the server's routes (and R12's fifth).

Only this folder goes to the browser. It never imports microbiology/ or server.py: what the page
knows arrives through /api, already aggregated and anonymised.
"""

import json

from oxid import Loading, Resource, Signal, h, mount
from oxid.chart import Color, X, Y, chart
from oxid.runtime import window

HOSPITALS = ["RBX", "OLV", "CSA"]


async def load(path):
    response = await window.fetch("/api" + path)
    return json.loads(await response.text())


hospital = Signal("RBX")
picked = Signal(None)


def samples_by_hospital(hospitals):
    """Bars: samples per hospital, from /api/hospitals. Marks expected: 3, one per hospital."""
    return h.p("TODO R9: mostres per hospital")


def choose(name):
    def handler(ev):
        hospital.set(name)

    return handler


def pressed(name):
    def value():
        return "true" if hospital() == name else "false"

    return value


def week_title():
    return f"Cultius positius per setmana · {hospital()}"


def positives_by_week(weekly):
    """A line: the chosen hospital's positive cultures per week, from /api/weekly. Marks expected: one line, 26 weeks."""
    return h.p("TODO R9: cultius positius per setmana de l'hospital triat")


def scatter(points):
    """Points: the disc's diameter against log2 of the MIC from /api/points, with a brush. Marks expected: one per row."""
    return h.p("TODO R9: dispersió diàmetre–CMI amb brush")


def selected():
    return "TODO R9: quantes proves hi ha dins el requadre"


def resistance_bars(rates):
    """R12 · Grouped bars: % resistant per antibiotic, one bar per hospital side by side (color and
    offset), from /api/resistance?organism=ECO. Marks expected: one per row with a rate."""
    return h.p("TODO R12: resistència d'E. coli per antibiòtic i hospital")


def summary_line(stats):
    s = stats()
    t = s["tat"]
    return (
        f"Temps de resposta: n = {t['n']}, mitjana {t['mean']} h, mediana {t['median']} h, "
        f"{t['outliers']} mostres per sobre de {t['high']} h. "
        f"r(diàmetre, log2 CMI) = {s['correlation']['r']} (n = {s['correlation']['n']}). "
        f"Publicació amb k = {s['k']}; {s['suppressed']} persones suprimides."
    )


def hole(view, resource):
    """A hole that redraws when the resource arrives or changes: `view(resource)` is read inside it."""

    def draw():
        return view(resource)

    return draw


def page():
    # Made here, in the component, not at import: a Resource starts loading when it is created.
    hospitals = Resource(lambda: load("/hospitals"))
    weekly = Resource(lambda name: load("/weekly?hospital=" + name), source=hospital)
    points = Resource(lambda: load("/points"))
    stats = Resource(lambda: load("/statistic"))
    rates = Resource(lambda: load("/resistance?organism=ECO"))
    return h.main(
        h.h1("Xarxa de microbiologia del Riubaix · gener–juliol 2026"),
        h.p("Dades inventades. Cap persona d'aquestes dades existeix.", class_="note"),
        Loading(h.p("Carregant…"), h.p(hole(summary_line, stats), class_="note")),
        h.h2("Hospitals"),
        Loading(h.p("Carregant…"), h.div(hole(samples_by_hospital, hospitals))),
        h.h2("Setmana a setmana"),
        h.nav(
            *[
                h.button(name, class_="hospital-" + name, on_click=choose(name), aria_pressed=pressed(name))
                for name in HOSPITALS
            ]
        ),
        Loading(h.p("Carregant…"), h.div(hole(positives_by_week, weekly))),
        h.h2("Temps de resposta"),
        h.img(src="/api/tat.svg", alt="Histograma del temps de resposta del laboratori, en trams de 12 hores"),
        h.h2("CMI i diàmetre"),
        Loading(h.p("Carregant…"), h.div(hole(scatter, points))),
        h.p(selected),
        h.h2("Resistències"),
        Loading(h.p("Carregant…"), h.div(hole(resistance_bars, rates))),
    )


mount(page, "#app")
