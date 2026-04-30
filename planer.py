from datetime import date, timedelta
from typing import Any


WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]


def _gewicht(elternteil: dict[str, Any]) -> float:
    return 0.5 if elternteil.get("ist_vorstand", False) else 1.0


def elternteil_zu_kinder(config: dict[str, Any]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for kind in config.get("kinder", []):
        for elternteil in kind.get("eltern", []):
            mapping.setdefault(elternteil, []).append(kind["name"])
    return mapping


def generiere_plan(
    config: dict[str, Any],
    historie: dict[str, int],
    startdatum: date,
    enddatum: date,
) -> list[dict[str, Any]]:
    feiertage = {
        date.fromisoformat(d) for d in config["einstellungen"].get("feiertage", [])
    }
    schliesztage = {
        date.fromisoformat(d) for d in config["einstellungen"].get("schliesztage", [])
    }
    gerichte: dict[str, str] = config["gerichte"]
    eltern: list[dict[str, Any]] = config["eltern"]

    zaehler: dict[str, float] = {
        e["name"]: historie.get(e["name"], 0) / _gewicht(e) for e in eltern
    }

    plan: list[dict[str, Any]] = []
    aktuelles_datum = startdatum

    while aktuelles_datum <= enddatum:
        wochentag = aktuelles_datum.weekday()
        if wochentag >= 5:
            aktuelles_datum += timedelta(days=1)
            continue

        if aktuelles_datum in feiertage:
            aktuelles_datum += timedelta(days=1)
            continue

        if aktuelles_datum in schliesztage:
            plan.append({
                "datum": aktuelles_datum.isoformat(),
                "wochentag": wochentag,
                "wochentag_name": WOCHENTAGE[wochentag],
                "gericht": "",
                "elternteil": "",
                "ist_schliesztag": True,
                "manuell_geaendert": False,
            })
            aktuelles_datum += timedelta(days=1)
            continue

        gericht = gerichte.get(str(wochentag), "")
        sperrzeiten_eltern = {
            e["name"]
            for e in eltern
            if aktuelles_datum.isoformat() in e.get("sperrzeiten", [])
        }
        kandidaten = [
            e
            for e in eltern
            if _ist_verfuegbar(e, wochentag, aktuelles_datum, sperrzeiten_eltern)
        ]

        if kandidaten:
            bester = min(kandidaten, key=lambda e: zaehler.get(e["name"], 0.0))
            zaehler[bester["name"]] = zaehler.get(bester["name"], 0.0) + 1.0 / _gewicht(bester)
            elternteil_name = bester["name"]
        else:
            elternteil_name = ""

        plan.append({
            "datum": aktuelles_datum.isoformat(),
            "wochentag": wochentag,
            "wochentag_name": WOCHENTAGE[wochentag],
            "gericht": gericht,
            "elternteil": elternteil_name,
            "ist_schliesztag": False,
            "manuell_geaendert": False,
        })
        aktuelles_datum += timedelta(days=1)

    return plan


def _ist_verfuegbar(
    elternteil: dict[str, Any],
    wochentag: int,
    datum: date,
    sperrzeiten_eltern: set[str],
) -> bool:
    if elternteil["name"] in sperrzeiten_eltern:
        return False
    erlaubte = elternteil.get("erlaubte_wochentage", [])
    if erlaubte and wochentag not in erlaubte:
        return False
    return True


def berechne_einsaetze(plan: list[dict[str, Any]]) -> dict[str, int]:
    zaehler: dict[str, int] = {}
    for eintrag in plan:
        if eintrag.get("ist_schliesztag"):
            continue
        name = eintrag.get("elternteil", "")
        if name:
            zaehler[name] = zaehler.get(name, 0) + 1
    return zaehler


def validiere_plan(
    plan: list[dict[str, Any]], config: dict[str, Any]
) -> list[dict[str, Any]]:
    eltern_map = {e["name"]: e for e in config["eltern"]}
    warnungen = []
    for eintrag in plan:
        if eintrag.get("ist_schliesztag"):
            continue
        name = eintrag.get("elternteil", "")
        if not name:
            warnungen.append({
                "datum": eintrag["datum"],
                "meldung": f"Kein Elternteil für {eintrag['wochentag_name']}, {eintrag['datum']} zugewiesen.",
            })
            continue
        elternteil = eltern_map.get(name)
        if not elternteil:
            continue
        erlaubte = elternteil.get("erlaubte_wochentage", [])
        if erlaubte and eintrag["wochentag"] not in erlaubte:
            warnungen.append({
                "datum": eintrag["datum"],
                "meldung": f"{name} ist am {eintrag['wochentag_name']} ({eintrag['datum']}) nicht verfügbar (erlaubte Tage: {[WOCHENTAGE[t] for t in erlaubte]}).",
            })
    return warnungen
