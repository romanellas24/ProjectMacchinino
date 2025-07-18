import time

import RPi.GPIO as GPIO
import sys
from TimedSwitch import TimedSwitch
import signal

# Mappatura pin per motori anteriori
AIN1 = 16
AIN2 = 20
AIN3 = 21
AIN4 = 26
AENA = 12  # PWM per motore 1
AENB = 19  # PWM per motore 2

# Pin per motori posteriori
BIN1 = 2
BIN2 = 3
BIN3 = 4
BIN4 = 14
BENA = 15  # PWM per motore 3
BENB = 18  # PWM per motore 3

# Luci di STOP
LSTOP = 13
# Retromarcia
LRETR = 6
# Freccie di DX
FR_DX = 5
# Freccie di SX
FR_SX = 22
# Luci abbaglianti
LABB = 27

# Luci RGB anteriori
RBG_RED = 9
RBG_GREEN = 11
RBG_BLUE = 10

all_pins = [AIN1, AIN2, AIN3, AIN4, AENA, AENB, BIN1, BIN2, BIN3, BIN4, BENA, BENB, LSTOP, LRETR, FR_DX, FR_SX, RBG_RED,
            RBG_GREEN, RBG_BLUE, LABB]

freccia_dx_is_working = None
freccia_sx_is_working = None


def setup_pins(pins):
    # Setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Imposta i pin
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)


def conv(v):
    return int(v * 100 / 255)


def motore1_avanti(velocita_percento, pwm):
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    pwm.ChangeDutyCycle(velocita_percento)


def motore2_avanti(velocita_percento, pwm):
    GPIO.output(AIN3, GPIO.HIGH)
    GPIO.output(AIN4, GPIO.LOW)
    pwm.ChangeDutyCycle(velocita_percento)


def motore1_indietro(velocita_percento, pwm):
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    pwm.ChangeDutyCycle(velocita_percento)


def motore2_indietro(velocita_percento, pwm):
    GPIO.output(AIN3, GPIO.LOW)
    GPIO.output(AIN4, GPIO.HIGH)
    pwm.ChangeDutyCycle(velocita_percento)


def motore3_avanti(velocita_percento, pwm):
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)
    pwm.ChangeDutyCycle(velocita_percento)


def motore4_avanti(velocita_percento, pwm):
    GPIO.output(BIN3, GPIO.HIGH)
    GPIO.output(BIN4, GPIO.LOW)
    pwm.ChangeDutyCycle(velocita_percento)


def motore3_indietro(velocita_percento, pwm):
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)
    pwm.ChangeDutyCycle(velocita_percento)


def motore4_indietro(velocita_percento, pwm):
    GPIO.output(BIN3, GPIO.LOW)
    GPIO.output(BIN4, GPIO.HIGH)
    pwm.ChangeDutyCycle(velocita_percento)


def accendi_fr_destra():
    GPIO.output(FR_DX, GPIO.HIGH)


def spegni_fr_destra():
    GPIO.output(FR_DX, GPIO.LOW)


def accendi_fr_sinistra():
    GPIO.output(FR_SX, GPIO.HIGH)


def spegni_fr_sinistra():
    GPIO.output(FR_SX, GPIO.LOW)


def accendi_luci_stop():
    GPIO.output(LSTOP, GPIO.HIGH)


def accendi_abbaglianti():
    GPIO.output(LABB, GPIO.HIGH)


def spegni_abbaglianti():
    GPIO.output(LABB, GPIO.LOW)


def accendi_luci_retr():
    GPIO.output(LRETR, GPIO.HIGH)


def spegni_luci_stop():
    GPIO.output(LSTOP, GPIO.LOW)


def spegni_luci_retr():
    GPIO.output(LRETR, GPIO.LOW)


def handle_move_command(move_command, pwmA, pwmB, pwmC, pwmD):
    if move_command == "MOVE_STOP":
        spegni_luci_retr()
        accendi_luci_stop()
        motore1_avanti(0, pwmA)
        motore2_avanti(0, pwmB)
        motore3_avanti(0, pwmC)
        motore4_avanti(0, pwmD)
    elif move_command == "MOVE_AHEAD":
        spegni_luci_retr()
        spegni_luci_stop()
        motore1_avanti(100, pwmA)
        motore2_avanti(100, pwmB)
        motore3_avanti(100, pwmC)
        motore4_avanti(100, pwmD)
    elif move_command == "MOVE_BACK":
        accendi_luci_retr()
        accendi_luci_stop()
        motore1_indietro(100, pwmA)
        motore2_indietro(100, pwmB)
        motore3_indietro(100, pwmC)
        motore4_indietro(100, pwmD)
    elif move_command == "MOVE_LEFT":
        spegni_luci_retr()
        spegni_luci_stop()
        motore1_indietro(100, pwmA)
        motore2_avanti(100, pwmB)
        motore3_indietro(100, pwmC)
        motore4_avanti(100, pwmD)
    elif move_command == "MOVE_RIGHT":
        spegni_luci_retr()
        spegni_luci_stop()
        motore1_avanti(100, pwmA)
        motore2_indietro(100, pwmB)
        motore3_avanti(100, pwmC)
        motore4_indietro(100, pwmD)

def handle_turn_indicators(isLeft = False, isOn = False):
    if isLeft and isOn:
        accendi_fr_sinistra()
    if isLeft and not isOn:
        spegni_fr_sinistra()
    if not isLeft and isOn:
        accendi_fr_destra()
    if not isLeft and not isOn:
        spegni_fr_destra()

def set_color(r, g, b, pinsRgb):
    pinsRgb[0].ChangeDutyCycle(conv(r))
    pinsRgb[1].ChangeDutyCycle(conv(g))
    pinsRgb[2].ChangeDutyCycle(conv(b))

def setup(shared):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    move_command = shared.get("move_command")
    high_lights = shared.get("high_lights")
    signal_turn_left = shared.get("signal_turn_left")
    signal_turn_right = shared.get("signal_turn_right")
    rgb_lights = shared.get("rgb_lights")

    all_pins = [AIN1, AIN2, AIN3, AIN4, AENA, AENB, BIN1, BIN2, BIN3, BIN4, BENA, BENB, LSTOP, LRETR, FR_DX, FR_SX,
                RBG_RED, RBG_GREEN, RBG_BLUE, LABB]

    for pin in all_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

    accendi_luci_stop()
    spegni_luci_retr()

    def safe_exit(signum, frame):
        print("[setup] Interrotto da SIGTERM. Cleanup...")
        GPIO.cleanup(all_pins)
        sys.exit(0)
    signal.signal(signal.SIGTERM, safe_exit)

    pwmA = GPIO.PWM(AENA, 1000)
    pwmB = GPIO.PWM(AENB, 1000)
    pwmC = GPIO.PWM(BENA, 1000)
    pwmD = GPIO.PWM(BENB, 1000)

    pwmA.start(0)
    pwmB.start(0)
    pwmC.start(0)
    pwmD.start(0)
    timed_switch_directions = TimedSwitch(1000)
    directions_indicators = False

    pwmRed = GPIO.PWM(RBG_RED, 1000)
    pwmGreen = GPIO.PWM(RBG_GREEN, 1000)
    pwmBlue = GPIO.PWM(RBG_BLUE, 1000)
    pinsRgb = {0: pwmRed, 1: pwmGreen, 2: pwmBlue}
    pinsRgb[0].start(0)
    pinsRgb[1].start(0)
    pinsRgb[2].start(0)


    set_color(rgb_lights[0], rgb_lights[1], rgb_lights[2], pinsRgb)

    try:
        while True:
            if move_command != shared.get("move_command"):
                move_command = shared.get("move_command")
                handle_move_command(move_command, pwmA, pwmB, pwmC, pwmD)

            #Aggiornamento valori abbaglianti
            if high_lights != shared.get("high_lights"):
                high_lights = shared.get("high_lights")
                if high_lights:
                    accendi_abbaglianti()
                else:
                    spegni_abbaglianti()

            #Aggiornamento valori indicatori di posizione
            if signal_turn_left != shared.get("signal_turn_left"):
                signal_turn_left = shared.get("signal_turn_left")

            if signal_turn_right != shared.get("signal_turn_right"):
                signal_turn_right = shared.get("signal_turn_right")

            #Gestione indicatori di direzione
            if signal_turn_right or signal_turn_left:
                if timed_switch_directions.is_elapse():
                    directions_indicators = not directions_indicators
                    if signal_turn_left:
                        handle_turn_indicators(True, directions_indicators)
                    if signal_turn_right:
                        handle_turn_indicators(False, directions_indicators)
            else:
                timed_switch_directions.reset()

            #Gestione luci anteriori
            if rgb_lights[0] != shared.get("rgb_lights")[0] or rgb_lights[1] != shared.get("rgb_lights")[1] or rgb_lights[2] != shared.get("rgb_lights")[2]:
                rgb_lights = shared.get("rgb_lights")
                set_color(rgb_lights[0], rgb_lights[1], rgb_lights[2], pinsRgb)

            time.sleep(0.1)
    except KeyboardInterrupt:
        safe_exit(None, None)
