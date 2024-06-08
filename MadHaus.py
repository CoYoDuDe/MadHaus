import RPi.GPIO as GPIO
import time

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
light_relay = 26  # Pin für die Innenbeleuchtung

# Setup der Pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
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
GPIO.setup(light_relay, GPIO.OUT)

# Funktion zur Steuerung der Innenbeleuchtung
def turn_on_light():
    GPIO.output(light_relay, GPIO.HIGH)

def turn_off_light():
    GPIO.output(light_relay, GPIO.LOW)

def flicker_light(duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        GPIO.output(light_relay, GPIO.LOW)
        time.sleep(random.uniform(0.05, 0.2))
        GPIO.output(light_relay, GPIO.HIGH)
        time.sleep(random.uniform(0.05, 0.2))

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

def swing_routine_initial():
    print("Initiale Schaukel-Routine gestartet...")

    # Erste Schwingung nach rechts
    activate_pneumatic_cylinder()
    start_time = time.time()
    while (time.time() - start_time) < 3:
        if check_swing_position() == 'right':
            break
        time.sleep(0.1)
    deactivate_pneumatic_cylinder()

    # Schaukel schwingt zur Mitte
    while check_swing_position() != 'middle':
        time.sleep(0.1)

    # 3 Sekunden warten oder bis Position Mitte erreicht wird
    start_time = time.time()
    while (time.time() - start_time) < 3:
        if check_swing_position() == 'middle':
            break
        time.sleep(0.1)

def normal_swing_routine():
    print("Normale Schaukel-Routine gestartet...")

    # Erste Schwingung nach rechts
    activate_pneumatic_cylinder()
    start_time = time.time()
    while (time.time() - start_time) < 3:
        if check_swing_position() == 'right':
            break
        time.sleep(0.1)
    deactivate_pneumatic_cylinder()

    # Schaukel schwingt zur Mitte
    while check_swing_position() != 'middle':
        time.sleep(0.1)

    # 3 Sekunden warten oder bis Position links erreicht wird
    start_time = time.time()
    while (time.time() - start_time) < 3:
        if check_swing_position() == 'left':
            break
        time.sleep(0.1)

    # Zweite Schwingung nach rechts (nach passieren der Mitte)
    while check_swing_position() != 'middle':
        time.sleep(0.1)

    activate_pneumatic_cylinder()
    start_time = time.time()
    while (time.time() - start_time) < 3:
        if check_swing_position() == 'right':
            break
        time.sleep(0.1)
    deactivate_pneumatic_cylinder()

def swing_routine_15_degrees(direction):
    print("Schaukel-Routine bei 15 Grad gestartet...")

    # Erste Schwingung nach rechts und halten bis Position Mitte erreicht ist
    activate_pneumatic_cylinder()
    start_time = time.time()
    while (time.time() - start_time) < 3:
        if check_swing_position() == 'right':
            break
        time.sleep(0.1)

    while check_swing_position() != 'middle':
        time.sleep(0.1)

    deactivate_pneumatic_cylinder()

    # Schaukel schwingt nach links
    while check_swing_position() != 'left':
        time.sleep(0.1)

    # Nach Erreichen der Mitte, wird 3 Sekunden gewartet oder bis die Position links erreicht wird
    start_time = time.time()
    while (time.time() - start_time) < 3:
        if check_swing_position() == 'left':
            break
        time.sleep(0.1)

    # Einmalige Schwingung nach rechts
    activate_pneumatic_cylinder()
    start_time = time.time()
    while (time.time() - start_time) < 3:
        if check_swing_position() == 'right':
            break
        time.sleep(0.1)

    while check_swing_position() != 'middle':
        time.sleep(0.1)

    deactivate_pneumatic_cylinder()

def braking_routine(direction):
    print("Bremsroutine gestartet...")

    def position_house():
        for _ in range(5):
            if direction == 'right':
                # Bremsroutine links
                for i in range(5):
                    turn_house_left()
                    time.sleep(0.1 * (i + 1))
                    stop_turning()
                    time.sleep(0.2 * (5 - i))

                # Drehrichtung ändern
                for i in range(3):
                    turn_house_right()
                    time.sleep(0.1 * (i + 1))
                    stop_turning()
                    time.sleep(0.2 * (3 - i))
            else:
                # Bremsroutine rechts
                for i in range(5):
                    turn_house_right()
                    time.sleep(0.1 * (i + 1))
                    stop_turning()
                    time.sleep(0.2 * (5 - i))

                # Drehrichtung ändern
                for i in range(3):
                    turn_house_left()
                    time.sleep(0.1 * (i + 1))
                    stop_turning()
                    time.sleep(0.2 * (3 - i))

            # Haus in die Position bringen, in der beide Magnetschalter aktiviert sind
            if GPIO.input(house_left_switch) == GPIO.LOW and GPIO.input(house_right_switch) == GPIO.LOW:
                return True
            else:
                if GPIO.input(house_right_switch) == GPIO.LOW:
                    turn_house_left()
                elif GPIO.input(house_left_switch) == GPIO.LOW:
                    turn_house_right()
                else:
                    stop_turning()
                time.sleep(0.1)
        return False

    def swing_to_middle():
        pulse_time = 0.1
        for _ in range(5):
            activate_pneumatic_cylinder()
            time.sleep(pulse_time)
            deactivate_pneumatic_cylinder()
            time.sleep(1)
            if check_swing_position() == 'middle':
                return True
            pulse_time += 0.1
        return False

    while not position_house():
        pass

    while not swing_to_middle():
        pass

    activate_brake()
    time.sleep(1)  # Wartezeit zum Schließen der Bremse

def main():
    try:
        # Schalte die Innenbeleuchtung ein
        turn_on_light()

        while True:
            # Warte auf Start-Taste
            if GPIO.input(start_button) == GPIO.LOW:
                print("Start-Taste gedrückt. Überprüfung beginnt...")

                # Warte 3 Sekunden und prüfe, ob der Start-Button noch gedrückt ist
                start_time = time.time()
                button_released = False
                while (time.time() - start_time) < 3:
                    if GPIO.input(start_button) != GPIO.LOW:
                        button_released = True
                        break
                    time.sleep(0.1)

                # Falls die Start-Taste 3 Sekunden lang gedrückt blieb, starte den Vorgang
                if GPIO.input(start_button) == GPIO.LOW and not button_released:
                    print("Start-Taste bestätigt. Vorgang beginnt...")

                    # Deaktiviere Bremse und überprüfe den Zustand
                    deactivate_brake()
                    time.sleep(1)  # Wartezeit zum Öffnen der Bremse
                    if check_brake_status() != 'open':
                        print("Bremse nicht geöffnet. Vorgang abgebrochen.")
                        continue

                    turn_count = 0
                    direction = 'right'
                    running = True

                    # Initiale Schaukel-Routine starten
                    swing_routine_initial()

                    # Warte, bis die Schaukel zur Mitte zurückkehrt oder 3 Sekunden vergangen sind
                    start_time = time.time()
                    while (time.time() - start_time) < 3:
                        if check_swing_position() == 'middle':
                            break
                        time.sleep(0.1)

                    # Drehe das Haus nach links und deaktiviere die Schaukel
                    print("Drehe das Haus nach links...")
                    turn_house_left()
                    time.sleep(1)  # Wartezeit, bevor die Schaukel deaktiviert wird
                    deactivate_pneumatic_cylinder()

                    while running:
                        # Überprüfen des Not-Aus-Tasters
                        if GPIO.input(emergency_stop) == GPIO.LOW:
                            print("Not-Aus-Taste gedrückt. Vorgang wird gestoppt.")
                            braking_routine(direction)
                            running = False
                            break

                        # Überprüfen des Stop-Tasters
                        if GPIO.input(stop_button) == GPIO.LOW:
                            print("Stop-Taste gedrückt. Vorgang wird gestoppt.")
                            braking_routine(direction)
                            running = False
                            break

                        # Normale Schaukel-Routine starten
                        normal_swing_routine()

                        # Warte, bis das Haus die gekippte Position erreicht
                        while check_house_position() not in ['tilted_right', 'tilted_left']:
                            time.sleep(0.1)

                        # Überkopfposition erreicht (15 Grad)
                        if check_house_position() in ['tilted_right', 'tilted_left']:
                            print("Haus ist über Kopf. Starte Schaukel-Routine bei 15 Grad...")
                            swing_routine_15_degrees(direction)

                            # Wechsel der Richtung nach zwei Umdrehungen
                            if turn_count >= 2:
                                print("Richtung wechseln...")
                                stop_turning()
                                while check_house_position() != 'upright':
                                    time.sleep(0.1)
                                direction = 'left' if direction == 'right' else 'right'
                                turn_count = 0

                        # Warte, bis das Haus wieder aufrecht steht
                        while check_house_position() != 'upright':
                            time.sleep(0.1)
                        stop_turning()

                        # Erhöhe die Drehzahl nach jeder zweiten Drehung
                        turn_count += 1

                        # Stop-Routine nach zwei vollen Umdrehungen in beide Richtungen
                        if turn_count >= 4:
                            braking_routine(direction)
                            break

                print("Vorgang abgeschlossen. Haus ist zurück in der Ausgangsposition.")

                # Überprüfen, ob das Haus in der normalen Position ist und die Schaukel in der Mitte ist
                while check_house_position() != 'upright' or check_swing_position() != 'middle':
                    time.sleep(0.1)

                # Bremse aktivieren
                activate_brake()
                time.sleep(1)  # Wartezeit zum Schließen der Bremse

    except KeyboardInterrupt:
        print("Programm gestoppt.")
    finally:
        # Schalte die Innenbeleuchtung aus
        turn_off_light()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
