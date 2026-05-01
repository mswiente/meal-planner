# Kindergarten Pusteblume – Website

WordPress-Website für den Kindergarten Pusteblume mit lokalem Docker-Entwicklungsumfeld und Custom-Theme.

## Schnellstart (Lokale Entwicklung)

### Voraussetzungen
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installiert

### 1. Umgebungsvariablen anlegen
```bash
cp .env.example .env
# .env nach Bedarf anpassen
```

### 2. Container starten
```bash
docker compose up -d
```

### 3. WordPress einrichten
- WordPress-Setup: http://localhost:8080
- phpMyAdmin: http://localhost:8081

### 4. Theme aktivieren
Im WordPress-Admin unter **Design > Themes** das Theme **Pusteblume** aktivieren.

### 5. Menüs einrichten
Unter **Design > Menüs** ein Menü für die **Hauptnavigation** erstellen.

---

## Projektstruktur

```
├── docker-compose.yml          # Lokale Entwicklungsumgebung
├── .env.example                # Beispiel-Umgebungsvariablen
├── wordpress/
│   ├── themes/
│   │   └── pusteblume/         # Custom WordPress-Theme
│   │       ├── style.css       # Theme-Deklaration
│   │       ├── functions.php   # Theme-Funktionen & Custom Post Types
│   │       ├── front-page.php  # Startseiten-Template
│   │       ├── page.php        # Seiten-Template
│   │       ├── single.php      # Beitrags-Template
│   │       ├── index.php       # Archiv/Blog-Template
│   │       ├── header.php      # Header
│   │       ├── footer.php      # Footer
│   │       ├── sidebar.php     # Sidebar
│   │       ├── template-parts/ # Wiederverwendbare Vorlagen
│   │       └── assets/
│   │           ├── css/main.css # Styles
│   │           └── js/main.js   # JavaScript
│   ├── plugins/                # Eigene/angepasste Plugins
│   ├── uploads/                # Medien (nicht in Git)
│   └── plugins.md              # Empfohlene Plugins
```

## Theme-Features

- **Responsive Design** – Mobile-First, funktioniert auf allen Geräten
- **Custom Post Types** – `Team` und `Gruppen` für strukturierte Inhaltspflege
- **Anpassbare Startseite** – Hero-Bild, Willkommenstext, Gruppen und Neuigkeiten
- **Footer-Widgets** – 3 anpassbare Spalten
- **DSGVO-freundlich** – Keine externen Ressourcen ohne Einwilligung geladen

## Seiten anlegen (empfohlen)

| Seitenname | Slug | Template |
|-----------|------|---------|
| Startseite | / | Startseite (unter Einstellungen > Lesen festlegen) |
| Über uns | ueber-uns | Standard |
| Unsere Gruppen | gruppen | Standard |
| Team | team | Standard |
| Aktuelles | aktuelles | Als Blog-Seite festlegen |
| Galerie | galerie | Standard |
| Kontakt | kontakt | Standard |
| Impressum | impressum | Standard |
| Datenschutz | datenschutz | Standard |

## Anpassung über den Customizer

Unter **Design > Customizer** können folgende Bereiche angepasst werden:
- Website-Name und Beschreibung
- Logo hochladen
- Hero-Titel, Untertitel und CTA-Button
- Willkommenstext der Startseite
- Kontakt-Telefon und E-Mail (erscheinen in der Kopfzeile)

## Plugins einrichten

Siehe [`wordpress/plugins.md`](wordpress/plugins.md) für empfohlene Plugins inkl. DSGVO-Hinweisen.

## Hosting / Deployment

Für das Hosting empfehlen wir:
- **All-Inkl.com** oder **Hetzner** (günstig, DSGVO-konform, deutsche Server)
- Export der lokalen Datenbank via phpMyAdmin (http://localhost:8081)
- Theme-Ordner per FTP/SFTP hochladen oder als ZIP unter **Design > Themes > Installieren** hochladen
