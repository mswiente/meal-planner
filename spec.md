# Spezifikation: Kindergarten-Mittagsplanung

## Überblick

Ein Tool zur Erstellung und Verwaltung von Kochplänen für den Kindergarten, bei dem Eltern reihum das Mittagessen für die Gruppe zubereiten.

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

#### 1.3 Eltern
- Eltern werden einem oder mehreren Kindern zugeordnet.
- Pro Elternteil können folgende Regeln konfiguriert werden:
  - **Erlaubte Wochentage**: Das Elternteil kann nur an bestimmten Tagen eingeplant werden (z.B. nur Mo, Mi, Fr).
  - **Vorstandsmitglied**: Vorstandsmitglieder werden nur halb so häufig eingeplant wie andere Eltern.
  - **Ausschlusszeiten**: Zeiträume (Urlaub, Krankheit etc.), in denen das Elternteil nicht eingeplant werden soll.
  - **Geschwisterkinder**: Haben mehrere Kinder eines Elternteils denselben Elternteil, zählt dieser nur einmal.

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
  - Der Algorithmus berücksichtigt bereits absolvierte Kocheinsätze aus früheren Planungsperioden (optional: Carry-over-Zähler).

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
  - Optionale Kontaktdaten der Eltern (E-Mail/Telefon).
  - Legende mit Regeln und Farbcodes.

#### 3.2 Weitere Exportformate (optional)
- CSV/Excel für Weiterverarbeitung.
- Druckfreundliche HTML-Ansicht.

---

### 4. Benutzeroberfläche und Implementierungsalternativen

#### Option A: Excel/LibreOffice Calc (einfachste Lösung)
- **Konfiguration**: Stammdaten in Tabellenblättern (`Kinder`, `Eltern`, `Gerichte`, `Einstellungen`).
- **Planung**: Ein Makro (VBA/Basic) generiert den Plan automatisch in einem weiteren Tabellenblatt.
- **Manuelle Anpassung**: Direkt in der Tabelle.
- **PDF-Export**: Über eingebaute Excel/Calc-Funktion.
- **Vorteile**: Keine Installation, bekannte Oberfläche, offline nutzbar.
- **Nachteile**: Makros müssen aktiviert werden, eingeschränkte Darstellung, Wartung komplex.

#### Option B: Python-CLI mit YAML-Konfiguration (flexibelste Lösung)
- **Konfiguration**: YAML-Dateien für Gerichte, Kinder, Eltern und Regeln.
- **Planung**: Python-Skript generiert Plan und schreibt Ergebnis in YAML/CSV.
- **Manuelle Anpassung**: Direkte Bearbeitung der generierten YAML/CSV-Datei.
- **PDF-Export**: Via `reportlab` oder `weasyprint`.
- **Vorteile**: Sehr flexibel, gut erweiterbar, versionierbar (Git), keine GUI nötig.
- **Nachteile**: Erfordert Python-Installation, weniger zugänglich für nicht-technische Nutzer.

#### Option C: Web-App (benutzerfreundlichste Lösung)
- **Stack**: Python (FastAPI/Flask) Backend + einfaches HTML/JS Frontend oder ein Framework wie Streamlit.
- **Konfiguration**: Formulare im Browser.
- **Planung**: Server-seitig, Ergebnis wird im Browser angezeigt.
- **Manuelle Anpassung**: Direkt im Browser via Drag-and-Drop oder Dropdown.
- **PDF-Export**: Server-seitig generiert, Download-Link.
- **Vorteile**: Sehr zugänglich, kein lokales Setup für Endnutzer.
- **Nachteile**: Erfordert Hosting oder lokalen Server, mehr Entwicklungsaufwand.

#### Option D: Streamlit-App (guter Kompromiss)
- **Stack**: Python + Streamlit (läuft lokal, öffnet sich im Browser).
- **Konfiguration**: Seitenleiste mit Formularen.
- **Planung**: Automatisch bei Konfigurationsänderung.
- **Manuelle Anpassung**: Interaktive Tabelle im Browser.
- **PDF-Export**: Download-Button.
- **Vorteile**: Einfache Installation (`pip install streamlit`), gute UX, kein Hosting nötig.
- **Nachteile**: Erfordert Python, Streamlit muss installiert sein.

---

### 5. Datenmodell

```
Kindergarten
├── settings
│   ├── planning_months: int          # Planungszeitraum in Monaten
│   ├── start_date: date
│   └── holidays: list[date]
│
├── dishes
│   └── weekday_dishes: dict          # {0: "Kartoffeln", 1: "Polenta", ...}
│
├── children
│   └── Child
│       ├── name: str
│       └── parents: list[Parent]
│
└── parents
    └── Parent
        ├── name: str
        ├── contact: str              # E-Mail oder Telefon
        ├── allowed_weekdays: list[int]  # 0=Mo..4=Fr, leer = alle
        ├── is_board_member: bool     # Vorstandsmitglied → halbe Häufigkeit
        ├── weight: float             # abgeleitet: 0.5 wenn Vorstand, sonst 1.0
        └── unavailable_dates: list[date]

Plan
└── PlanEntry
    ├── date: date
    ├── weekday: int
    ├── dish: str
    ├── parent: Parent
    └── is_manual_override: bool
```

---

### 6. Verteilungsalgorithmus (Pseudocode)

```
Für jeden Planungstag t im Zeitraum:
  1. Wenn t ein Feiertag oder Schließtag → überspringen
  2. Wochentag w = weekday(t)
  3. Gericht = dishes[w]
  4. Kandidaten = [p für p in Eltern wenn:
       - w in p.allowed_weekdays (oder p.allowed_weekdays leer)
       - t nicht in p.unavailable_dates]
  5. Wähle Kandidat mit niedrigstem Wert:
       score(p) = bisherige_einsätze(p) / p.weight
  6. Weise t → gewählter Kandidat zu
  7. bisherige_einsätze(p) += 1
```

---

### 7. Empfehlung

Für einen Kindergarten mit nicht-technischen Nutzern empfehle ich **Option D (Streamlit)**:
- Einfache Installation mit einem Befehl.
- Intuitive Browser-Oberfläche.
- Konfiguration per Formulare, kein Texteditor nötig.
- PDF-Export mit einem Klick.
- Kann lokal auf dem Laptop des Koordinators laufen.

Als Zwischenlösung oder Fallback eignet sich **Option A (Excel)**, wenn keine Python-Installation möglich ist.

---

### 8. Offene Punkte / Entscheidungsbedarf

- [ ] Sollen Eltern per E-Mail über ihren Kocheinsatz benachrichtigt werden?
- [ ] Soll der Plan öffentlich (z.B. als Aushang) oder nur intern genutzt werden?
- [ ] Wie soll mit krankheitsbedingten Ausfällen umgegangen werden (Ersatzplanung)?
- [ ] Sollen historische Pläne archiviert und bei der nächsten Planung berücksichtigt werden?
- [ ] Welche Sprache soll die Benutzeroberfläche haben (Deutsch)?
- [ ] Sollen Geschwisterkinder besonders behandelt werden (ein Elternteil für mehrere Kinder)?
