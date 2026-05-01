import json
import os
from datetime import date, datetime, timedelta
from typing import Any

DATEN_VERZEICHNIS = os.path.join(os.path.dirname(__file__), "daten")
CONFIG_DATEI = os.path.join(DATEN_VERZEICHNIS, "config.json")
HISTORIE_DATEI = os.path.join(DATEN_VERZEICHNIS, "historie.json")

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


def lade_historie() -> dict[str, int]:
    _sicherstellen_verzeichnis()
    if not os.path.exists(HISTORIE_DATEI):
        return {}
    with open(HISTORIE_DATEI, encoding="utf-8") as f:
        return json.load(f)


def speichere_historie(historie: dict[str, int]) -> None:
    _sicherstellen_verzeichnis()
    with open(HISTORIE_DATEI, "w", encoding="utf-8") as f:
        json.dump(historie, f, ensure_ascii=False, indent=2)


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
