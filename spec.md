# Spezifikation: Kindergarten-Mittagsplanung

## Überblick

Ein Tool zur Erstellung und Verwaltung von Kochplänen für den Kindergarten, bei dem Eltern reihum das Mittagessen für die Gruppe zubereiten. Implementierung als **Streamlit-App** (Option D).

---

## Anforderungen

### 1. Stammdaten

#### 1.1 Gerichte pro Wochentag
- Jedem Wochentag (Montag bis Freitag) wird ein Gericht zugeordnet.
- Die Zuordnung ist frei konfigurierbar, z.B.:
  - Montag → Kartoffelgericht
  - Dienstag → Polenta
  - Mittwoch → Nudelgericht
  - Donnerstag → Reistopf
  - Freitag → Suppe

#### 1.2 Kinder
- Jedes Kind wird mit Name und zugehörigen Eltern/Erziehungsberechtigten erfasst.
- Die Kinderliste ist konfigurierbar (hinzufügen, entfernen, bearbeiten).
- Geschwisterkinder werden nicht gesondert behandelt.

#### 1.3 Eltern
- Eltern werden einem oder mehreren Kindern zugeordnet.
- Pro Elternteil können folgende Regeln konfiguriert werden:
  - **Erlaubte Wochentage**: Das Elternteil kann nur an bestimmten Tagen eingeplant werden (z.B. nur Mo, Mi, Fr).
  - **Vorstandsmitglied**: Vorstandsmitglieder werden nur halb so häufig eingeplant wie andere Eltern.
  - **Ausschlusszeiten**: Zeiträume (Urlaub etc.), in denen das Elternteil nicht eingeplant werden soll.

---

### 2. Planungsfunktion

#### 2.1 Planungszeitraum
- Die Planung erfolgt für einen konfigurierbaren Zeitraum (Standard: 3 Monate).
- Startdatum und Endedatum sind frei wählbar.
- Feiertage und Schließzeiten des Kindergartens sind als nicht belegbare Tage markierbar.

#### 2.2 Verteilungsalgorithmus
- Eltern werden so verteilt, dass innerhalb des Planungszeitraums eine möglichst gleichmäßige Häufigkeit erreicht wird.
- Gewichtungsregeln:
  - Vorstandsmitglieder erhalten Gewicht 0,5 (halb so oft).
  - Eltern mit eingeschränkten Wochentagen werden nur an erlaubten Tagen eingeplant.
- **Historische Pläne werden berücksichtigt**: Einsatzzähler aus vergangenen Planungsperioden fließen in die Verteilung ein, sodass langfristig eine faire Gleichverteilung entsteht (Carry-over-Zähler).

#### 2.3 Manuelle Anpassung
- Jeder automatisch generierte Eintrag kann manuell geändert werden.
- Änderungen werden visuell hervorgehoben.
- Konflikte (z.B. Elternteil an einem unerlaubten Tag) werden als Warnung angezeigt.

---

### 3. Ausgabe

#### 3.1 PDF-Export
- Der fertige Plan wird als PDF exportiert.
- Inhalt des PDFs:
  - Monatsübersicht mit Datum, Wochentag, Gericht und eingeplantem Elternteil.
  - Kontaktdaten der Eltern (Telefon).
  - Legende mit Hinweisen zu Sonderregeln.

#### 3.2 Weitere Exportformate (optional)
- CSV/Excel für Weiterverarbeitung.

---

### 4. Implementierung: Streamlit-App

- **Stack**: Python + Streamlit (läuft lokal, öffnet sich im Browser).
- **Sprache**: Deutsch (gesamte Benutzeroberfläche).
- **Konfiguration**: Seitenleiste mit Formularen für Gerichte, Kinder, Eltern und Einstellungen.
- **Planung**: Plan wird auf Knopfdruck generiert und als interaktive Tabelle angezeigt.
- **Manuelle Anpassung**: Dropdown je Zeile zum Ändern des zugewiesenen Elternteils.
- **PDF-Export**: Download-Button.
- **Datenpersistenz**: Konfiguration und historische Pläne werden lokal als JSON-Dateien gespeichert.

---

### 5. Datenmodell

```
Einstellungen
├── planungsmonate: int               # Planungszeitraum in Monaten (Standard: 3)
├── startdatum: date
└── feiertage: list[date]

Gerichte
└── wochentag_gerichte: dict          # {0: "Kartoffeln", 1: "Polenta", ...}

Kind
├── name: str
└── eltern: list[str]                 # Verweise auf Eltern-Namen

Elternteil
├── name: str
├── telefon: str
├── erlaubte_wochentage: list[int]    # 0=Mo..4=Fr, leer = alle erlaubt
├── ist_vorstand: bool                # → Gewicht 0.5, sonst 1.0
└── sperrzeiten: list[date]

Planeintrag
├── datum: date
├── wochentag: int
├── gericht: str
├── elternteil: str
└── manuell_geaendert: bool

HistorischerEinsatz
├── elternteil: str
└── anzahl_einsaetze: int             # Carry-over aus abgeschlossenen Plänen
```

---

### 6. Verteilungsalgorithmus (Pseudocode)

```
Lade historische Einsatzzähler aus gespeicherten abgeschlossenen Plänen.

Für jeden Planungstag t im Zeitraum:
  1. Wenn t ein Feiertag oder Schließtag → überspringen
  2. Wochentag w = weekday(t)
  3. Gericht = wochentag_gerichte[w]
  4. Kandidaten = [p für p in Eltern wenn:
       - w in p.erlaubte_wochentage (oder Liste leer)
       - t nicht in p.sperrzeiten]
  5. Wähle Kandidat mit niedrigstem Score:
       score(p) = gesamteinsaetze(p) / p.gewicht
       (gesamteinsaetze = historische Einsätze + Einsätze im aktuellen Plan)
  6. Weise t → gewählter Kandidat zu
  7. gesamteinsaetze(p) += 1
```

---

### 7. Projektstruktur

```
meal-planner/
├── app.py                  # Streamlit-Hauptanwendung
├── planer.py               # Planungslogik und Algorithmus
├── daten.py                # Laden/Speichern von JSON-Daten
├── pdf_export.py           # PDF-Generierung
├── daten/
│   ├── config.json         # Gerichte, Kinder, Eltern, Einstellungen
│   └── historie.json       # Historische Einsatzzähler
├── requirements.txt
└── spec.md
```

---

### 8. Entschiedene Punkte

- [x] Sprache: Deutsch
- [x] Implementierung: Streamlit (Option D)
- [x] Historische Pläne werden für die Verteilung berücksichtigt (Carry-over)
- [x] Geschwisterkinder: keine Sonderbehandlung
- [x] Ausfallmanagement: manuell per WhatsApp, keine App-Unterstützung nötig
- [x] E-Mail-Benachrichtigung: nicht im ersten Schritt
