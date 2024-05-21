(* Deklaration der Variablen *)
VAR
    house_left_switch : BOOL; (* DI1 *)
    house_right_switch : BOOL; (* DI2 *)
    swing_left_switch : BOOL; (* DI3 *)
    swing_right_switch : BOOL; (* DI4 *)
    swing_middle_switch : BOOL; (* DI5 *)
    pneumatic_cylinder : BOOL; (* DO1 *)
    relay_turn_right : BOOL; (* DO2 *)
    relay_turn_left : BOOL; (* DO3 *)
    start_button : BOOL; (* DI6 *)
    stop_button : BOOL; (* DI7 *)
    emergency_stop : BOOL; (* DI8 *)
    brake_cylinder : BOOL; (* DO4 *)
    brake_switch : BOOL; (* DI9 *)
    light_relay : BOOL; (* DO5 *)
    turn_count : INT;
    direction : BOOL; (* TRUE = right, FALSE = left *)
    running : BOOL;
    start_time : TIME;
    current_time : TIME;
    swing_position : STRING;
    house_position : STRING;
    brake_status : STRING;
END_VAR

(* Initialisierung *)
direction := TRUE; (* Start Richtung ist rechts *)
running := FALSE;
turn_count := 0;

(* Lichtsteuerung *)
light_relay := TRUE;

(* Funktion zur Prüfung der Schaukelposition *)
CASE TRUE OF
    swing_right_switch: swing_position := 'right';
    swing_left_switch: swing_position := 'left';
    swing_middle_switch: swing_position := 'middle';
    ELSE swing_position := 'unknown';
END_CASE

(* Funktion zur Prüfung der Hausposition *)
CASE TRUE OF
    (house_right_switch AND house_left_switch): house_position := 'upright';
    house_right_switch: house_position := 'tilted_right';
    house_left_switch: house_position := 'tilted_left';
    ELSE house_position := 'unknown';
END_CASE

(* Funktion zur Prüfung des Bremsstatus *)
IF brake_switch THEN
    brake_status := 'open';
ELSE
    brake_status := 'closed';
END_IF

(* Startprozess *)
IF start_button THEN
    start_time := TIME();
    WHILE TIME() - start_time < T#3S DO
        IF NOT start_button THEN
            EXIT;
        END_IF
    END_WHILE;

    IF start_button THEN
        brake_cylinder := FALSE;
        IF brake_status <> 'open' THEN
            EXIT;
        END_IF

        running := TRUE;
        turn_count := 0;
        direction := TRUE; (* Start Richtung ist rechts *)
        
        WHILE running DO
            (* Not-Aus prüfen *)
            IF emergency_stop THEN
                running := FALSE;
                EXIT;
            END_IF

            (* Stop-Taste prüfen *)
            IF stop_button THEN
                running := FALSE;
                EXIT;
            END_IF

            (* Haus drehen *)
            IF direction THEN
                relay_turn_right := TRUE;
                relay_turn_left := FALSE;
            ELSE
                relay_turn_right := FALSE;
                relay_turn_left := TRUE;
            END_IF

            (* Normale Schaukel-Routine *)
            pneumatic_cylinder := TRUE;
            start_time := TIME();
            WHILE TIME() - start_time < T#3S DO
                IF swing_position = 'right' THEN
                    EXIT;
                END_IF
            END_WHILE;
            pneumatic_cylinder := FALSE;

            WHILE swing_position <> 'middle' DO END_WHILE;

            start_time := TIME();
            WHILE TIME() - start_time < T#3S DO
                IF swing_position = 'left' THEN
                    EXIT;
                END_IF
            END_WHILE;

            WHILE swing_position <> 'middle' DO END_WHILE;

            pneumatic_cylinder := TRUE;
            start_time := TIME();
            WHILE TIME() - start_time < T#3S DO
                IF swing_position = 'right' THEN
                    EXIT;
                END_IF
            END_WHILE;
            pneumatic_cylinder := FALSE;

            (* Hausposition prüfen *)
            WHILE house_position NOT IN ['tilted_right', 'tilted_left'] DO END_WHILE;

            (* Überkopfposition erreicht *)
            IF house_position IN ['tilted_right', 'tilted_left'] THEN
                pneumatic_cylinder := TRUE;
                start_time := TIME();
                WHILE TIME() - start_time < T#3S DO
                    IF swing_position = 'right' THEN
                        EXIT;
                    END_IF
                END_WHILE;

                WHILE swing_position <> 'middle' DO END_WHILE;
                pneumatic_cylinder := FALSE;

                WHILE swing_position <> 'left' DO END_WHILE;
                start_time := TIME();
                WHILE TIME() - start_time < T#3S DO
                    IF swing_position = 'left' THEN
                        EXIT;
                    END_IF
                END_WHILE;

                pneumatic_cylinder := TRUE;
                start_time := TIME();
                WHILE TIME() - start_time < T#3S DO
                    IF swing_position = 'right' THEN
                        EXIT;
                    END_IF
                END_WHILE;
                pneumatic_cylinder := FALSE;
            END_IF

            (* Richtung wechseln nach zwei Umdrehungen *)
            IF turn_count >= 2 THEN
                relay_turn_right := FALSE;
                relay_turn_left := FALSE;
                WHILE house_position <> 'upright' DO END_WHILE;
                direction := NOT direction;
                turn_count := 0;
            END_IF

            (* Warte, bis das Haus wieder aufrecht steht *)
            WHILE house_position <> 'upright' DO END_WHILE;
            relay_turn_right := FALSE;
            relay_turn_left := FALSE;

            turn_count := turn_count + 1;
        END_WHILE

        (* Vorgang abgeschlossen *)
        WHILE house_position <> 'upright' OR swing_position <> 'middle' DO END_WHILE;
        brake_cylinder := TRUE;
    END_IF
END_IF
