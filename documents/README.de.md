# ASH

Grundstruktur.
# A Science Hub (ASH)

## Überblick

A Science Hub ist eine Desktop-Anwendung mit Werkzeugen für Physik, Chemie, Biologie, Geologie und Mathematik. Enthalten sind Rechner, Umrechner, Simulatoren und Referenzwerkzeuge. Die Oberfläche basiert auf PyQt6.

## Funktionen

* **Biologie**: Codon-Nachschlagewerk, GC-Gehalt, Leserahmen-Übersetzung, Transkription/Translation, Sequenzwerkzeuge, Populationswachstum, pH-Rechner, Osmose-Tonizität
* **Chemie**: Element-Explorer, Eigenschaftsdiagramme, Isotopen-Notation, Molmasse, Molekülbibliothek mit 3D-Ansicht, Phasenvorhersage, Reaktionsausgleich, Schalenvisualisierung
* **Elektrizität**: Coulomb-Kraft, elektrische und magnetische Feldrechner/Visualisierungen, RC-Schaltkreis-Helfer, Ohmsches Gesetz, Induktionswerkzeuge
* **Mechanik**: Geschwindigkeit, Beschleunigung, kinetische Energie, Luftwiderstand, Wurfparabel, Endgeschwindigkeit, Linsen-/Spiegelgleichung
* **Geologie**: Mineralien-Explorer, Mineralien-Identifizierung, Radioaktive Datierung, Halbwertszeit-Rechner, Plattengrenzen-Designer, Plattengeschwindigkeit
* **Mathematik**: Algebra-Rechner, Funktionsplotter, Quadratlöser, Dreiecksrechner, Vektorrechner
* **Panel-Tools**: Einheitenumrechner, SI-Präfix-Kombinator/Teiler, signifikante Stellen, Notationsumrechner, Konstanten-Nachschlagewerk, Größenprüfer, Rechner, Log-Viewer, Schnell-Suche, Fenster-Manager

## Struktur

```
core/        # Kernlogik, Datenbanken, Funktionen
UI/          # Panels, Fenster, Assets
tools/       # Werkzeuge nach Kategorie
storage/     # Nutzerdaten: Logs, Ergebnisse, Bilder, Formeln, Favoriten
documents/   # Dokumentation und Release Notes
misc/        # Tests, Helfer, Vorlagen
```

## Installation

```bash
pip install -r requirements.txt
```

## Start

```bash
python main.py
```
