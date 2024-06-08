// Schneider Electric TM172 Code

PROGRAM Main
VAR
    house_left_switch AT %I0.0 : BOOL;
    house_right_switch AT %I0.1 : BOOL;
    swing_left_switch AT %I0.2 : BOOL;
    swing_right_switch AT %I0.3 : BOOL;
    swing_middle_switch AT %I0.4 : BOOL;
    pneumatic_cylinder AT %Q0.0 : BOOL;
    relay_turn_right AT %Q0.1 : BOOL;
    relay_turn_left AT %Q0.2 : BOOL;
    start_button AT %I0.5 : BOOL;
    stop_button AT %I0.6 : BOOL;
    emergency_stop AT %I0.7 : BOOL;
    brake_cylinder AT %Q0.3 : BOOL;
    brake_switch AT %I0.8 : BOOL;
    light_relay AT %Q0.4 : BOOL;
    turn_count : INT := 0;
    direction : BOOL := TRUE; (* TRUE = right, FALSE = left *)
    running : BOOL := FALSE;
    start_time : TIME;
    current_time : TIME;
    swing_position : STRING[10];
    house_position : STRING[10];
    brake_status : STRING[10];
    button_released : BOOL := FALSE;
END_VAR

// Lichtsteuerung
light_relay := start_button;

// Funktion zur Prüfung der Schaukelposition
IF swing_right_switch THEN
    swing_position := 'right';
ELSIF swing_left_switch THEN
    swing_position := 'left';
ELSIF swing_middle_switch THEN
    swing_position := 'middle';
ELSE
    swing_position := 'unknown';
END_IF;

// Funktion zur Prüfung der Hausposition
IF house_right_switch AND house_left_switch THEN
    house_position := 'upright';
ELSIF house_right_switch THEN
    house_position := 'tilted_right';
ELSIF house_left_switch THEN
    house_position := 'tilted_left';
ELSE
    house_position := 'unknown';
END_IF;

// Funktion zur Prüfung des Bremsstatus
IF brake_switch THEN
    brake_status := 'open';
ELSE
    brake_status := 'closed';
END_IF;

// Startprozess
IF start_button THEN
    start_time := TIME();
    button_released := FALSE;
    WHILE (TIME() - start_time) < T#3S DO
        IF NOT start_button THEN
            button_released := TRUE;
            EXIT;
        END_IF;
    END_WHILE;

    IF start_button AND NOT button_released THEN
        brake_cylinder := FALSE;
        IF brake_status <> 'open' THEN
            EXIT;
        END_IF;

        running := TRUE;
        turn_count := 0;
        direction := TRUE; (* Start Richtung ist rechts *)

        // Initiale Schaukel-Routine starten
        pneumatic_cylinder := TRUE;
        start_time := TIME();
        WHILE (TIME() - start_time) < T#3S DO
            IF swing_position = 'right' THEN
                EXIT;
            END_IF;
        END_WHILE;
        pneumatic_cylinder := FALSE;

        WHILE swing_position <> 'middle' DO END_WHILE;

        start_time := TIME();
        WHILE (TIME() - start_time) < T#3S DO
            IF swing_position = 'middle' THEN
                EXIT;
            END_IF;
        END_WHILE;

        // Drehe das Haus nach links und deaktiviere die Schaukel
        relay_turn_right := FALSE;
        relay_turn_left := TRUE;
        TIME := TIME();
        WHILE (TIME() - start_time) < T#1S DO END_WHILE;
        pneumatic_cylinder := FALSE;

        WHILE running DO
            // Not-Aus prüfen
            IF emergency_stop THEN
                running := FALSE;
                braking_routine(direction);
                EXIT;
            END_IF;

            // Stop-Taste prüfen
            IF stop_button THEN
                running := FALSE;
                braking_routine(direction);
                EXIT;
            END_IF;

            // Normale Schaukel-Routine starten
            pneumatic_cylinder := TRUE;
            start_time := TIME();
            WHILE (TIME() - start_time) < T#3S DO
                IF swing_position = 'right' THEN
                    EXIT;
                END_IF;
            END_WHILE;
            pneumatic_cylinder := FALSE;

            WHILE swing_position <> 'middle' DO END_WHILE;

            start_time := TIME();
            WHILE (TIME() - start_time) < T#3S DO
                IF swing_position = 'left' THEN
                    EXIT;
                END_IF;
            END_WHILE;

            WHILE swing_position <> 'middle' DO END_WHILE;

            pneumatic_cylinder := TRUE;
            start_time := TIME();
            WHILE (TIME() - start_time) < T#3S DO
                IF swing_position = 'right' THEN
                    EXIT;
                END_IF;
            END_WHILE;
            pneumatic_cylinder := FALSE;

            // Hausposition prüfen
            WHILE house_position NOT IN ['tilted_right', 'tilted_left'] DO END_WHILE;

            // Überkopfposition erreicht
            IF house_position IN ['tilted_right', 'tilted_left'] THEN
                // Call swing_routine_15_degrees here
                turn_count := turn_count + 1;
                IF turn_count >= 2 THEN
                    relay_turn_left := FALSE;
                    WHILE house_position <> 'upright' DO END_WHILE;
                    direction := NOT direction;
                    turn_count := 0;
                END_IF;
            END_IF;

            // Warte, bis das Haus wieder aufrecht steht
            WHILE house_position <> 'upright' DO END_WHILE;
            relay_turn_left := FALSE;
            relay_turn_right := FALSE;

            IF turn_count >= 4 THEN
                // Call braking_routine here
                EXIT;
            END_IF;
        END_WHILE;
    END_IF;
END_IF;

// Set brake when house is in upright position
IF house_position = 'upright' AND swing_position = 'middle' THEN
    brake_cylinder := TRUE;
END_IF;
