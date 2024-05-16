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

## Code

```python
import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Pins für Magnetschalter, Pneumatikzylinder, Relais und Taster
house_left_switch = 17
house_right_switch = 27
swing_left_switch = 22
swing_right_switch = 23
swing_middle_switch = 24
pneumatic_cylinder = 18
relay_turn_right = 5
relay_turn_left = 6
start_button = 12
stop_button = 16
emergency_stop = 20
brake_cylinder = 21
brake_switch = 25

# Setup der Pins
GPIO.setup(house_left_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(house_right_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(swing_left_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(swing_right_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(swing_middle_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pneumatic_cylinder, GPIO.OUT)
GPIO.setup(relay_turn_right, GPIO.OUT)
GPIO.setup(relay_turn_left, GPIO.OUT)
GPIO.setup(start_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(stop_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(emergency_stop, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(brake_cylinder, GPIO.OUT)
GPIO.setup(brake_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def activate_pneumatic_cylinder():
    GPIO.output(pneumatic_cylinder, GPIO.HIGH)

def deactivate_pneumatic_cylinder():
    GPIO.output(pneumatic_cylinder, GPIO.LOW)

def activate_brake():
    GPIO.output(brake_cylinder, GPIO.HIGH)

def deactivate_brake():
    GPIO.output(brake_cylinder, GPIO.LOW)

def turn_house_right():
    GPIO.output(relay_turn_right, GPIO.HIGH)
    GPIO.output(relay_turn_left, GPIO.LOW)

def turn_house_left():
    GPIO.output(relay_turn_right, GPIO.LOW)
    GPIO.output(relay_turn_left, GPIO.HIGH)

def stop_turning():
    GPIO.output(relay_turn_right, GPIO.LOW)
    GPIO.output(relay_turn_left, GPIO.LOW)

def check_swing_position():
    if GPIO.input(swing_right_switch) == GPIO.LOW:
        return 'right'
    elif GPIO.input(swing_left_switch) == GPIO.LOW:
        return 'left'
    elif GPIO.input(swing_middle_switch) == GPIO.LOW:
        return 'middle'
    else:
        return 'unknown'

def check_house_position():
    if GPIO.input(house_right_switch) == GPIO.LOW and GPIO.input(house_left_switch) == GPIO.LOW:
        return 'upright'
    elif GPIO.input(house_right_switch) == GPIO.LOW:
        return 'tilted_right'
    elif GPIO.input(house_left_switch) == GPIO.LOW:
        return 'tilted_left'
    else:
        return 'unknown'

def check_brake_status():
    if GPIO.input(brake_switch) == GPIO.LOW:
        return 'open'
    else:
        return 'closed'

def main():
    try:
        while True:
            # Warte auf Start-Taste
            if GPIO.input(start_button) == GPIO.LOW:
                print("Start-Taste gedrückt. Vorgang beginnt...")

                # Deaktiviere Bremse und überprüfe den Zustand
                deactivate_brake()
                time.sleep(1)  # Wartezeit zum Öffnen der Bremse
                if check_brake_status() != 'open':
                    print("Bremse nicht geöffnet. Vorgang abgebrochen.")
                    continue
                
                turn_count = 0
                direction = 'right'
                running = True

                while running and turn_count < 4:
                    # Überprüfen des Not-Aus-Tasters
                    if GPIO.input(emergency_stop) == GPIO.LOW:
                        print("Not-Aus-Taste gedrückt. Vorgang wird gestoppt.")
                        break

                    # Überprüfen des Stop-Tasters
                    if GPIO.input(stop_button) == GPIO.LOW:
                        print("Stop-Taste gedrückt. Vorgang wird gestoppt.")
                        running = False
                        break

                    # Drehe das Haus in die aktuelle Richtung
                    if direction == 'right':
                        print("Drehe das Haus nach rechts...")
                        turn_house_right()
                    else:
                        print("Drehe das Haus nach links...")
                        turn_house_left()

                    # Warte, bis das Haus die gekippte Position erreicht
                    while check_house_position() not in ['tilted_right', 'tilted_left']:
                        time.sleep(0.1)

                    # Überkopfposition erreicht (15 Grad)
                    if check_house_position() in ['tilted_right', 'tilted_left']:
                        print("Haus ist über Kopf. Schwinge die Schaukel.")
                        activate_pneumatic_cylinder()
                        start_time = time.time()
                        while (time.time() - start_time) < 3:
                            if check_swing_position() == 'middle':
                                break
                            time.sleep(0.1)
                        deactivate_pneumatic_cylinder()

                        # Wechsel der Richtung
                        direction = 'left' if direction == 'right' else 'right'
                        
                    # Warte, bis das Haus wieder aufrecht steht
                    while check_house_position() != 'upright':
                        time.sleep(0.1)
                    stop_turning()

                    # Schaukel nach rechts schwingen
                    activate_pneumatic_cylinder()
                    start_time = time.time()
                    while check_swing_position() != 'right' and (time.time() - start_time) < 3:
                        time.sleep(0.1)
                    deactivate_pneumatic_cylinder()

                    # Schaukel zurück zur Mitte schwingen lassen
                    while check_swing_position() != 'middle':
                        time.sleep(0.1)

                    # Schaukel nach links schwingen
                    activate_pneumatic_cylinder()
                    start_time = time.time()
                    while check_swing_position() != 'left' and (time.time() - start_time) < 3:
                        time.sleep(0.1)
                    deactivate_pneumatic_cylinder()

                    # Schaukel zurück zur Mitte schwingen lassen
                    while check_swing_position() != 'middle':
                        time.sleep(0.1)

                    # Erhöhe die Drehzahl nach jeder zweiten Drehung
                    turn_count += 1
                
                print("Vorgang abgeschlossen. Haus ist zurück in der Ausgangsposition.")
                stop_turning()

                # Bremse aktivieren
                activate_brake()
                time.sleep(1)  # Wartezeit zum Schließen der Bremse

    except KeyboardInterrupt:
        print("Programm gestoppt.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
