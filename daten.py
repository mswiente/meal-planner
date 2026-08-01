import json
import os
from datetime import date, datetime, timedelta
from typing import Any

DATEN_VERZEICHNIS = os.path.join(os.path.dirname(__file__), "daten")
CONFIG_DATEI = os.path.join(DATEN_VERZEICHNIS, "config.json")
PLAENE_DATEI = os.path.join(DATEN_VERZEICHNIS, "plaene.json")
ENTWURF_DATEI = os.path.join(DATEN_VERZEICHNIS, "entwurf.json")

STANDARD_CONFIG: dict[str, Any] = {
    "einstellungen": {
        "startdatum": date.today().isoformat(),
        "enddatum": date(date.today().year, 12, 31).isoformat(),
        "bundesland": "HE",
        "schliesszeiten": [],
    },
    "gerichte": {
        "0": "Kartoffelgericht",
        "1": "Polenta",
        "2": "Nudelgericht",
        "3": "Reistopf",
        "4": "Suppe",
    },
    "kinder": [],
}


def _sicherstellen_verzeichnis() -> None:
    os.makedirs(DATEN_VERZEICHNIS, exist_ok=True)


def lade_config() -> dict[str, Any]:
    _sicherstellen_verzeichnis()
    if not os.path.exists(CONFIG_DATEI):
        return STANDARD_CONFIG.copy()
    with open(CONFIG_DATEI, encoding="utf-8") as f:
        return json.load(f)


def speichere_config(config: dict[str, Any]) -> None:
    _sicherstellen_verzeichnis()
    with open(CONFIG_DATEI, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def lade_plaene() -> list[dict[str, Any]]:
    _sicherstellen_verzeichnis()
    if not os.path.exists(PLAENE_DATEI):
        return []
    with open(PLAENE_DATEI, encoding="utf-8") as f:
        return json.load(f)


def speichere_plaene(plaene: list[dict[str, Any]]) -> None:
    _sicherstellen_verzeichnis()
    with open(PLAENE_DATEI, "w", encoding="utf-8") as f:
        json.dump(plaene, f, ensure_ascii=False, indent=2)


def lade_entwurf() -> dict[str, Any] | None:
    _sicherstellen_verzeichnis()
    if not os.path.exists(ENTWURF_DATEI):
        return None
    with open(ENTWURF_DATEI, encoding="utf-8") as f:
        return json.load(f)


def speichere_entwurf(entwurf: dict[str, Any] | None) -> None:
    _sicherstellen_verzeichnis()
    if entwurf is None:
        if os.path.exists(ENTWURF_DATEI):
            os.remove(ENTWURF_DATEI)
        return
    with open(ENTWURF_DATEI, "w", encoding="utf-8") as f:
        json.dump(entwurf, f, ensure_ascii=False, indent=2)


def gesamteinsaetze(plaene: list[dict[str, Any]]) -> dict[str, int]:
    from planer import berechne_einsaetze
    gesamt: dict[str, int] = {}
    for plan in plaene:
        for name, anzahl in berechne_einsaetze(plan["eintraege"]).items():
            gesamt[name] = gesamt.get(name, 0) + anzahl
    return gesamt


def schliesszeit_daten(config: dict[str, Any]) -> dict[str, str]:
    """Expandiert alle Schließzeiten-Zeiträume zu einem Dict {datum_iso: name}."""
    lookup: dict[str, str] = {}
    for sz in config["einstellungen"].get("schliesszeiten", []):
        von = datetime.fromisoformat(sz["von"]).date()
        bis = datetime.fromisoformat(sz["bis"]).date()
        aktuell = von
        while aktuell <= bis:
            lookup[aktuell.isoformat()] = sz["name"]
            aktuell += timedelta(days=1)
    return lookup


def datum_zu_str(d: date) -> str:
    return d.isoformat()


def str_zu_datum(s: str) -> date:
    return datetime.fromisoformat(s).date()
