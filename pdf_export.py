import os
from datetime import date, timedelta
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    HRFlowable,
    Image,
)


WOCHENTAGE_KURZ = ["Mo", "Di", "Mi", "Do", "Fr"]
WOCHENTAGE_LANG = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]


def _kw(d: date) -> int:
    return d.isocalendar()[1]


def _kw_jahr(d: date) -> int:
    return d.isocalendar()[0]


def erstelle_pdf(
    plan: list[dict[str, Any]],
    config: dict[str, Any],
    einsaetze: dict[str, int],
) -> bytes:
    buffer = BytesIO()
    seitengroesse = landscape(A4)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=seitengroesse,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    titel_stil = ParagraphStyle(
        "Titel", parent=styles["Heading1"], fontSize=14, spaceAfter=6, alignment=1
    )
    untertitel_stil = ParagraphStyle(
        "Untertitel", parent=styles["Normal"], fontSize=8, spaceAfter=2, alignment=1,
        textColor=colors.HexColor("#555555"),
    )
    zellen_datum_stil = ParagraphStyle(
        "ZelleDatum", parent=styles["Normal"], fontSize=7,
        textColor=colors.HexColor("#666666"), spaceAfter=1,
    )
    zellen_name_stil = ParagraphStyle(
        "ZelleName", parent=styles["Normal"], fontSize=9, fontName="Helvetica-Bold",
    )
    zellen_sonder_stil = ParagraphStyle(
        "ZelleSonder", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Oblique",
        textColor=colors.HexColor("#888888"),
    )
    kopf_stil = ParagraphStyle(
        "Kopf", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold",
        alignment=1, textColor=colors.white,
    )
    kopf_gericht_stil = ParagraphStyle(
        "KopfGericht", parent=styles["Normal"], fontSize=7,
        alignment=1, textColor=colors.HexColor("#DDEEEE"),
    )

    gerichte = config.get("gerichte", {})

    # Plan nach Datum indizieren
    plan_index: dict[str, dict[str, Any]] = {e["datum"]: e for e in plan}

    # Datumsbereich ermitteln
    if not plan:
        doc.build([Paragraph("Kein Plan vorhanden.", styles["Normal"])])
        return buffer.getvalue()

    erster_tag = date.fromisoformat(plan[0]["datum"])
    letzter_tag = date.fromisoformat(plan[-1]["datum"])

    # Auf Montag zurückgehen
    montag_start = erster_tag - timedelta(days=erster_tag.weekday())
    # Auf Freitag vorspulen
    freitag_ende = letzter_tag + timedelta(days=(4 - letzter_tag.weekday()))

    # Wochen sammeln
    wochen: list[list[date]] = []
    aktuell = montag_start
    while aktuell <= freitag_ende:
        woche = [aktuell + timedelta(days=i) for i in range(5)]
        wochen.append(woche)
        aktuell += timedelta(days=7)

    # Zeitraum-Bezeichnung für Titel
    monate_de = [
        "", "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember",
    ]
    if erster_tag.month == letzter_tag.month:
        zeitraum = f"{monate_de[erster_tag.month]} {erster_tag.year}"
    elif erster_tag.year == letzter_tag.year:
        zeitraum = f"{monate_de[erster_tag.month]} – {monate_de[letzter_tag.month]} {erster_tag.year}"
    else:
        zeitraum = f"{monate_de[erster_tag.month]} {erster_tag.year} – {monate_de[letzter_tag.month]} {letzter_tag.year}"

    inhalt = []

    # Kopfbereich: Logo links, Titel rechts
    logo_pfad = config["einstellungen"].get("logo_pfad", "")
    titel_absatz = [
        Paragraph("Kochdienste Kindergarten", titel_stil),
        Paragraph(zeitraum, untertitel_stil),
    ]
    if logo_pfad and os.path.exists(logo_pfad):
        logo_hoehe = 2.0 * cm
        iw, ih = ImageReader(logo_pfad).getSize()
        logo_breite = logo_hoehe * (iw / ih)
        logo_img = Image(logo_pfad, height=logo_hoehe, width=logo_breite)
        # 3-Spalten-Layout: Logo | Titel (zentriert) | Leerraum gleicher Breite
        kopf_tabelle = Table(
            [[logo_img, titel_absatz, ""]],
            colWidths=[logo_breite + 0.3 * cm, None, logo_breite + 0.3 * cm],
        )
        kopf_tabelle.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        inhalt.append(kopf_tabelle)
    else:
        inhalt.append(Paragraph("Kochdienste Kindergarten", titel_stil))
        inhalt.append(Paragraph(zeitraum, untertitel_stil))

    inhalt.append(Spacer(1, 0.3 * cm))

    # Tabelle aufbauen
    # Kopfzeile
    kopf_zeile = [Paragraph("Woche", kopf_stil)]
    for i, tag in enumerate(WOCHENTAGE_LANG):
        gericht = gerichte.get(str(i), "")
        zelle = [Paragraph(tag, kopf_stil)]
        if gericht:
            zelle.append(Paragraph(gericht, kopf_gericht_stil))
        kopf_zeile.append(zelle)

    tabellen_daten = [kopf_zeile]

    for woche in wochen:
        zeile = [Paragraph(f"KW {_kw(woche[0])}", ParagraphStyle(
            "KW", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold", alignment=1
        ))]
        for tag in woche:
            datum_str = tag.isoformat()
            eintrag = plan_index.get(datum_str)

            if eintrag is None:
                zeile.append(Paragraph("", styles["Normal"]))
            elif eintrag.get("schliesszeit_name"):
                inhalt_zelle = [
                    Paragraph(tag.strftime("%d.%m.%Y"), zellen_datum_stil),
                    Paragraph(eintrag["schliesszeit_name"], zellen_sonder_stil),
                ]
                zeile.append(inhalt_zelle)
            else:
                kind_name = eintrag.get("kind", "")
                inhalt_zelle = [
                    Paragraph(tag.strftime("%d.%m.%Y"), zellen_datum_stil),
                    Paragraph(kind_name if kind_name else "–", zellen_name_stil),
                ]
                zeile.append(inhalt_zelle)

        tabellen_daten.append(zeile)

    # Spaltenbreiten: KW-Spalte schmal, Rest gleich verteilt
    verfuegbare_breite = seitengroesse[0] - 3 * cm  # Margins
    kw_breite = 1.4 * cm
    tag_breite = (verfuegbare_breite - kw_breite) / 5

    col_widths = [kw_breite] + [tag_breite] * 5

    tabelle = Table(tabellen_daten, colWidths=col_widths, repeatRows=1)

    header_farbe = colors.HexColor("#4A7C59")
    zeilen_farben = [colors.white, colors.HexColor("#F0F4F0")]

    zeilenstile = []
    for i in range(1, len(tabellen_daten)):
        farbe = zeilen_farben[i % 2]
        zeilenstile.append(("BACKGROUND", (0, i), (-1, i), farbe))

    tabelle.setStyle(TableStyle([
        # Kopfzeile
        ("BACKGROUND", (0, 0), (-1, 0), header_farbe),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        # KW-Spalte
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#E8F0EA")),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("VALIGN", (0, 0), (0, -1), "MIDDLE"),
        # Allgemein
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        # Zeilenfarben
        *zeilenstile,
    ]))

    inhalt.append(tabelle)

    # Legende
    inhalt.append(Spacer(1, 0.4 * cm))
    inhalt.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC")))
    inhalt.append(Spacer(1, 0.2 * cm))

    legende_stil = ParagraphStyle(
        "Legende", parent=styles["Normal"], fontSize=7,
        textColor=colors.HexColor("#666666"),
    )
    inhalt.append(Paragraph(
        "Vorstandsmitglieder werden halb so oft eingeplant. Manuelle Anpassungen sind im System markiert.",
        legende_stil,
    ))

    doc.build(inhalt)
    return buffer.getvalue()
