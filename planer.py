from datetime import date, timedelta
from typing import Any

from daten import schliesszeit_daten

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]


def _gewicht(kind: dict[str, Any]) -> float:
    return 0.5 if kind.get("ist_vorstand", False) else 1.0


def generiere_plan(
    config: dict[str, Any],
    historie: dict[str, int],
    startdatum: date,
    enddatum: date,
) -> list[dict[str, Any]]:
    schliesszeiten = schliesszeit_daten(config)
    gerichte: dict[str, str] = config["gerichte"]
    kinder: list[dict[str, Any]] = config["kinder"]

    zaehler: dict[str, float] = {
        k["name"]: historie.get(k["name"], 0) / _gewicht(k) for k in kinder
    }

    plan: list[dict[str, Any]] = []
    aktuelles_datum = startdatum

    while aktuelles_datum <= enddatum:
        wochentag = aktuelles_datum.weekday()
        if wochentag >= 5:
            aktuelles_datum += timedelta(days=1)
            continue

        sz_name = schliesszeiten.get(aktuelles_datum.isoformat())
        if sz_name is not None:
            plan.append({
                "datum": aktuelles_datum.isoformat(),
                "wochentag": wochentag,
                "wochentag_name": WOCHENTAGE[wochentag],
                "gericht": "",
                "kind": "",
                "schliesszeit_name": sz_name,
                "manuell_geaendert": False,
            })
            aktuelles_datum += timedelta(days=1)
            continue

        gericht = gerichte.get(str(wochentag), "")
        sperrzeiten_kinder = {
            k["name"]
            for k in kinder
            if aktuelles_datum.isoformat() in k.get("sperrzeiten", [])
        }
        kandidaten = [
            k for k in kinder
            if _ist_verfuegbar(k, wochentag, sperrzeiten_kinder)
        ]

        if kandidaten:
            bestes = min(kandidaten, key=lambda k: zaehler.get(k["name"], 0.0))
            zaehler[bestes["name"]] = zaehler.get(bestes["name"], 0.0) + 1.0 / _gewicht(bestes)
            kind_name = bestes["name"]
        else:
            kind_name = ""

        plan.append({
            "datum": aktuelles_datum.isoformat(),
            "wochentag": wochentag,
            "wochentag_name": WOCHENTAGE[wochentag],
            "gericht": gericht,
            "kind": kind_name,
            "schliesszeit_name": "",
            "manuell_geaendert": False,
        })
        aktuelles_datum += timedelta(days=1)

    return plan


def _ist_verfuegbar(
    kind: dict[str, Any],
    wochentag: int,
    sperrzeiten_kinder: set[str],
) -> bool:
    if kind["name"] in sperrzeiten_kinder:
        return False
    erlaubte = kind.get("erlaubte_wochentage", [])
    if erlaubte and wochentag not in erlaubte:
        return False
    return True


def berechne_einsaetze(plan: list[dict[str, Any]]) -> dict[str, int]:
    zaehler: dict[str, int] = {}
    for eintrag in plan:
        if eintrag.get("schliesszeit_name"):
            continue
        name = eintrag.get("kind", "")
        if name:
            zaehler[name] = zaehler.get(name, 0) + 1
    return zaehler


def validiere_plan(
    plan: list[dict[str, Any]], config: dict[str, Any]
) -> list[dict[str, Any]]:
    kinder_map = {k["name"]: k for k in config["kinder"]}
    warnungen = []
    for eintrag in plan:
        if eintrag.get("schliesszeit_name"):
            continue
        name = eintrag.get("kind", "")
        if not name:
            warnungen.append({
                "datum": eintrag["datum"],
                "meldung": f"Kein Kind für {eintrag['wochentag_name']}, {eintrag['datum']} zugewiesen.",
            })
            continue
        kind = kinder_map.get(name)
        if not kind:
            continue
        erlaubte = kind.get("erlaubte_wochentage", [])
        if erlaubte and eintrag["wochentag"] not in erlaubte:
            warnungen.append({
                "datum": eintrag["datum"],
                "meldung": f"{name} ist am {eintrag['wochentag_name']} ({eintrag['datum']}) nicht verfügbar (erlaubte Tage: {[WOCHENTAGE[t] for t in erlaubte]}).",
            })
    return warnungen
