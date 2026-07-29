cat << 'EOF' > README.md
# KNX Scene Cycler for Home Assistant

Eine universelle, geräteunabhängige Home Assistant Integration, um komplexe Szenen-Steuerungen über KNX-Taster (wie den MDT Glastaster II Smart) flüssig zu verwalten.

## Features
- **Szenen-Wechsel (Kurzer Druck):** Wechselt zyklisch zwischen 4 konfigurierten Home Assistant Szenen basierend auf dem empfangenen KNX-Wert.
- **Intelligentes Toggle (Langer Druck):** Schaltet bei langem Druck (Wert `0`) in die konfigurierte Neutralszene (AUS). Ein erneuter langer Druck holt exakt die letzte aktive Szene aus dem Gedächtnis zurück.
- **Status-LED Rückmeldung:** Sendet den Systemstatus (`1` für aktiv, `0` für neutral) live zurück an den KNX-Bus, um Taster-LEDs synchron zu halten.
- **Dashboard-Sync:** Die erzeugten Entitäten verhalten sich im Lovelace-Dashboard identisch zum physischen Taster.

## Installation
1. Kopiere den Ordner `custom_components/knx_scene_cycler` in dein Home Assistant `/config/custom_components/` Verzeichnis.
2. Starte Home Assistant neu.
3. Navigiere zu **Einstellungen -> Geräte & Dienste -> Integration hinzufügen** und suche nach **KNX Scene Cycler**.

## ETS Anforderungen
Die Taste des KNX-Tasters muss als **Zwei-Objekt-Bedienung** konfiguriert sein:
- **Objekt 1 (Kurz):** Sendet Werte (1-64) für die Szenenauswahl.
- **Objekt 2 (Lang):** Sendet fest den Wert `0` (Aktion bei langem Tastendruck = "AUS").

## Lizenz
Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE.md](LICENSE.md) Datei für Details.
EOF
