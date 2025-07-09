from threading import Event

import RPi.GPIO as GPIO

SERVER_MAC_ADDRESS = "2C:CF:67:4F:11:F0"
SERVER_SUBPROCESS_SLEEP = 0.1

move_command_stop_event = Event()

# Mappatura pin per motori anteriori
AIN1 = 16
AIN2 = 20
AIN3 = 21
AIN4 = 26
AENA = 12  # PWM per motore 1
AENB = 19  # PWM per motore 2

#Pin per motori posteriori
BIN1 = 2
BIN2 = 3
BIN3 = 4
BIN4 = 14
BENA = 15 # PWM per motore 3
BENB = 18 # PWM per motore 3

# Luci di STOP
LSTOP = 13
#Retromarcia
LRETR = 6
#Freccie di DX
FR_DX = 5
#Freccie di SX
FR_SX = 22
#Luci abbaglianti
LABB = 27

#Luci RGB anteriori
RBG_RED = 9
RBG_GREEN = 11
RBG_BLUE = 10

all_pins = [AIN1, AIN2, AIN3, AIN4, AENA, AENB, BIN1, BIN2, BIN3, BIN4, BENA, BENB, LSTOP, LRETR, FR_DX, FR_SX, RBG_RED, RBG_GREEN, RBG_BLUE, LABB]

freccia_dx_is_working = None
freccia_sx_is_working = None

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Imposta i pin
for pin in all_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Imposta PWM su ENA e ENB a 1kHz
pwmA = GPIO.PWM(AENA, 1000)  # Frequenza di 1 kHz
pwmB = GPIO.PWM(AENB, 1000)
pwmC = GPIO.PWM(BENA, 1000)
pwmD = GPIO.PWM(BENB, 1000)

pwmRed = GPIO.PWM(RBG_RED, 1000)
pwmGreen = GPIO.PWM(RBG_GREEN, 1000)
pwmBlue = GPIO.PWM(RBG_BLUE, 1000)
pinsRgb = {'R': pwmRed, 'G': pwmGreen, 'B': pwmBlue}

pwmA.start(0)  # All'inizio motori fermi
pwmB.start(0)
pwmC.start(0)
pwmD.start(0)
pinsRgb["R"].start(0)
pinsRgb["G"].start(0)
pinsRgb["B"].start(0)