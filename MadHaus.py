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
