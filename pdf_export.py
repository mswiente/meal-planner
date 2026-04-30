from datetime import date
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
MONATE_DE = [
    "", "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]


def erstelle_pdf(
    plan: list[dict[str, Any]],
    config: dict[str, Any],
    einsaetze: dict[str, int],
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    titel_stil = ParagraphStyle(
        "Titel", parent=styles["Heading1"], fontSize=16, spaceAfter=12
    )
    abschnitt_stil = ParagraphStyle(
        "Abschnitt", parent=styles["Heading2"], fontSize=12, spaceAfter=6, spaceBefore=12
    )
    normal_stil = styles["Normal"]
    normal_stil.fontSize = 9

    eltern_map = {e["name"]: e for e in config["eltern"]}
    inhalt = []

    inhalt.append(Paragraph("Kochplan Kindergarten", titel_stil))

    # Plan nach Monaten gruppieren
    monate: dict[str, list[dict[str, Any]]] = {}
    for eintrag in plan:
        d = date.fromisoformat(eintrag["datum"])
        schluessel = f"{d.year}-{d.month:02d}"
        monate.setdefault(schluessel, []).append(eintrag)

    for schluessel, eintraege in sorted(monate.items()):
        jahr, monat = schluessel.split("-")
        inhalt.append(Paragraph(f"{MONATE_DE[int(monat)]} {jahr}", abschnitt_stil))

        tabellen_daten = [["Datum", "Wochentag", "Gericht", "Elternteil", "Telefon"]]
        for e in eintraege:
            d = date.fromisoformat(e["datum"])
            elternteil = eltern_map.get(e["elternteil"], {})
            telefon = elternteil.get("telefon", "") if elternteil else ""
            markierung = " *" if e.get("manuell_geaendert") else ""
            tabellen_daten.append([
                d.strftime("%d.%m.%Y"),
                e["wochentag_name"],
                e["gericht"],
                f"{e['elternteil']}{markierung}",
                telefon,
            ])

        tabelle = Table(
            tabellen_daten,
            colWidths=[2.8 * cm, 2.8 * cm, 4.0 * cm, 4.5 * cm, 3.0 * cm],
        )
        tabelle.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A7C59")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F4F0")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        inhalt.append(tabelle)

    inhalt.append(Spacer(1, 0.5 * cm))
    inhalt.append(Paragraph("Einsätze im Planungszeitraum", abschnitt_stil))

    statistik_daten = [["Elternteil", "Einsätze", "Vorstand"]]
    for elternteil in config["eltern"]:
        name = elternteil["name"]
        statistik_daten.append([
            name,
            str(einsaetze.get(name, 0)),
            "Ja" if elternteil.get("ist_vorstand") else "Nein",
        ])

    statistik_tabelle = Table(statistik_daten, colWidths=[6 * cm, 3 * cm, 3 * cm])
    statistik_tabelle.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A7C59")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F4F0")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    inhalt.append(statistik_tabelle)
    inhalt.append(Spacer(1, 0.3 * cm))
    inhalt.append(Paragraph("* = manuell angepasst", normal_stil))
    inhalt.append(Paragraph("Vorstandsmitglieder werden halb so oft eingeplant.", normal_stil))

    doc.build(inhalt)
    return buffer.getvalue()
