cat << 'EOF' > LICENSE.md
MIT License

Copyright (c) 2026 fpwilhelm

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

cat << 'EOF' > TODO.md
# TODOs - Future Enhancements

Hier sind die geplanten Funktionen für zukünftige Versionen der Integration:

- [ ] **ETS-Projekt-Import (.knxproj):** Automatisches Auslesen der Gruppenadressen aus der KNX-Datenbank für Autocomplete im Config-Flow.
- [ ] **Erweiterter Options-Flow:** Visuelles Bearbeiten und Löschen bereits bestehender Tasten über die Benutzeroberfläche.
- [ ] **Unterstützung für Tunable White (TW):** Dynamische Farbtemperatur-Rückmeldung im Dashboard (Kelvin statt RGB), falls Lampen kein Farb-LED unterstützen.
- [ ] **HACS-Kompatibilität:** Hinzufügen der notwendigen Metadaten, um die Integration über den Home Assistant Community Store installierbar zu machen.
EOF
