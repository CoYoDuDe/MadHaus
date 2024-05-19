# MadHaus Steuerung

Dieses Projekt steuert ein MadHaus, das sich dreht und gleichzeitig eine interne Schaukel bewegt. Die Steuerung erfolgt über einen Raspberry Pi, der verschiedene Sensoren und Aktoren überwacht und ansteuert. Es gibt Start-, Stopp- und Not-Aus-Taster.

## Komponenten und GPIO-Belegung

- **Magnetschalter für Hausposition:**
  - `house_left_switch`: Erkennung, wenn das Haus nach links gekippt ist.
  - `house_right_switch`: Erkennung, wenn das Haus nach rechts gekippt ist.
- **Magnetschalter für Schaukelposition:**
  - `swing_left_switch`: Erkennung, wenn die Schaukel nach links gekippt ist.
  - `swing_right_switch`: Erkennung, wenn die Schaukel nach rechts gekippt ist.
  - `swing_middle_switch`: Erkennung, wenn die Schaukel in der Mitte ist.
- **Pneumatikzylinder:**
  - `pneumatic_cylinder`: Steuerung der Schaukelbewegung.
  - `brake_cylinder`: Steuerung der Bremse.
- **Relais für Drehrichtung:**
  - `relay_turn_right`: Steuerung der Drehung nach rechts.
  - `relay_turn_left`: Steuerung der Drehung nach links.
- **Taster:**
  - `start_button`: Start des Vorgangs.
  - `stop_button`: Stopp des Vorgangs.
  - `emergency_stop`: Not-Aus.

## Funktionsweise des Codes

### Initialisierung

Der Code initialisiert die GPIO-Pins und setzt die Warnungen des Raspberry Pi zurück.

### Warte auf den Start-Taster

Der Code befindet sich in einer Schleife und wartet darauf, dass die Start-Taste gedrückt wird. Wenn die Start-Taste gedrückt wird, beginnt der Vorgang.

### Überprüfung der Bremse

Die Bremse wird deaktiviert, und es wird eine kurze Wartezeit eingelegt, damit die Bremse vollständig geöffnet wird. Der Zustand der Bremse wird überprüft (Magnetschalter). Wenn die Bremse nicht geöffnet ist, wird der Vorgang abgebrochen.

### Initialisierung der Steuerung

- `turn_count` wird auf 0 gesetzt, um die Anzahl der Drehungen zu verfolgen.
- `direction` wird auf `'right'` gesetzt, um die anfängliche Drehrichtung festzulegen.
- `running` wird auf `True` gesetzt, um den laufenden Zustand des Vorgangs anzuzeigen.

### Hauptsteuerungsschleife

Die Schleife läuft, solange `running` `True` ist und `turn_count` kleiner als 4 ist (für vier vollständige Drehungen).

#### Not-Aus und Stopp-Taster

Der Zustand des Not-Aus- und des Stopp-Tasters wird regelmäßig überprüft. Wenn einer dieser Taster gedrückt wird, wird der Vorgang gestoppt.

#### Drehen des Hauses

Das Haus dreht sich in die aktuelle Richtung (`right` oder `left`), indem das entsprechende Relais aktiviert wird. Der Code wartet, bis das Haus die 15-Grad-Überkopfposition erreicht hat (erkannt durch die Magnetschalter).

#### Überkopfposition und Schaukeln

Wenn das Haus die Überkopfposition erreicht, wird die Schaukel aktiviert und für bis zu 3 Sekunden gehalten (oder bis die Schaukel die mittlere Position erreicht). Die Richtung des Hauses wird gewechselt (`right` zu `left` und umgekehrt).

#### Warten auf aufrechte Position

Der Code wartet, bis das Haus wieder in der aufrechten Position ist und stoppt dann die Drehung.

#### Schaukeln der Schaukel

Die Schaukel wird nach rechts geschwungen und gehalten, bis sie entweder die rechte Position erreicht oder 3 Sekunden vergangen sind. Dann schwingt die Schaukel zurück zur mittleren Position. Die Schaukel wird nach links geschwungen und gehalten, bis sie entweder die linke Position erreicht oder 3 Sekunden vergangen sind. Schließlich schwingt die Schaukel zurück zur mittleren Position.

#### Erhöhen der Drehzahl

`turn_count` wird erhöht, um die Anzahl der abgeschlossenen Drehungen zu verfolgen.

### Abschluss

Nach vier vollständigen Drehungen wird die Bremse aktiviert, um das Haus in der neutralen Position zu halten. Der Vorgang wird beendet, und der Code gibt eine Abschlussmeldung aus.

### Fehlerbehandlung

Wenn das Programm durch eine Tastenkombination (z.B. Strg+C) unterbrochen wird, wird eine entsprechende Nachricht ausgegeben, und die GPIOs werden bereinigt.
