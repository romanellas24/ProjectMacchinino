import RPi.GPIO as GPIO
import time
from multiprocessing import Process

# Mappatura pin
AIN1 = 16
AIN2 = 20
AIN3 = 21
AIN4 = 26
AENA = 12  # PWM per motore 1
AENB = 19  # PWM per motore 2
BIN1 = 2
BIN2 = 3
BIN3 = 4
BIN4 = 14
BENA = 15
BENB = 18

# Luci di STOP
LSTOP = 13
LRETR = 6
FR_DX = 5
FR_SX = 11

#Luci RGB anteriori
RBG_RED = 9
RBG_GREEN = 25
RBG_BLUE = 10

all_pins = [AIN1, AIN2, AIN3, AIN4, AENA, AENB, BIN1, BIN2, BIN3, BIN4, BENA, BENB, LSTOP, LRETR, FR_DX, FR_SX, RBG_RED, RBG_GREEN, RBG_BLUE]

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


def conv(v):
    return int(v * 100 / 255)

def set_color(r, g, b):
    pinsRgb["R"].ChangeDutyCycle(conv(r))
    pinsRgb["G"].ChangeDutyCycle(conv(g))
    pinsRgb["B"].ChangeDutyCycle(conv(b))


def motore1_avanti(velocita_percento):
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    pwmA.ChangeDutyCycle(velocita_percento)


def motore2_avanti(velocita_percento):
    GPIO.output(AIN3, GPIO.HIGH)
    GPIO.output(AIN4, GPIO.LOW)
    pwmB.ChangeDutyCycle(velocita_percento)


def motore1_indietro(velocita_percento):
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    pwmA.ChangeDutyCycle(velocita_percento)


def motore2_indietro(velocita_percento):
    GPIO.output(AIN3, GPIO.LOW)
    GPIO.output(AIN4, GPIO.HIGH)
    pwmB.ChangeDutyCycle(velocita_percento)


def motore3_avanti(velocita_percento):
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)
    pwmC.ChangeDutyCycle(velocita_percento)


def motore4_avanti(velocita_percento):
    GPIO.output(BIN3, GPIO.HIGH)
    GPIO.output(BIN4, GPIO.LOW)
    pwmD.ChangeDutyCycle(velocita_percento)


def motore3_indietro(velocita_percento):
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)
    pwmC.ChangeDutyCycle(velocita_percento)


def motore4_indietro(velocita_percento):
    GPIO.output(BIN3, GPIO.LOW)
    GPIO.output(BIN4, GPIO.HIGH)
    pwmD.ChangeDutyCycle(velocita_percento)


def accendi_luci_stop():
    GPIO.output(LSTOP, GPIO.HIGH)


def accendi_luci_retr():
    GPIO.output(LRETR, GPIO.HIGH)


def spegni_luci_stop():
    GPIO.output(LSTOP, GPIO.LOW)


def spegni_luci_retr():
    GPIO.output(LRETR, GPIO.LOW)


def ferma_tutto():
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(AIN3, GPIO.LOW)
    GPIO.output(AIN4, GPIO.LOW)
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.LOW)
    GPIO.output(BIN3, GPIO.LOW)
    GPIO.output(BIN4, GPIO.LOW)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)
    pwmC.ChangeDutyCycle(0)
    pwmD.ChangeDutyCycle(0)
    spegni_luci_retr()


def gira_90_deg():
    motore1_avanti(100)
    motore2_avanti(100)
    motore3_avanti(100)
    motore4_avanti(100)
    time.sleep(1)

    motore1_indietro(100)
    motore2_avanti(100)
    motore3_indietro(100)
    motore4_avanti(100)
    time.sleep(1)


def accendi_fr_destra():
    global freccia_dx_is_working
    if freccia_dx_is_working is None or not freccia_dx_is_working.is_alive():
        freccia_dx_is_working = Process(target=accendi_fr_destra_work)
        freccia_dx_is_working.start()


def accendi_fr_destra_work():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    while True:
        GPIO.output(FR_DX, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(FR_DX, GPIO.LOW)
        time.sleep(1)


def spegni_fr_destra():
    global freccia_dx_is_working

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(FR_DX, GPIO.OUT)

    if freccia_dx_is_working is not None and freccia_dx_is_working.is_alive():
        freccia_dx_is_working.terminate()
        freccia_dx_is_working.join()

    GPIO.output(FR_DX, GPIO.LOW)
    freccia_dx_is_working = None


def accendi_fr_sinistra():
    global freccia_sx_is_working
    if freccia_sx_is_working is None or not freccia_sx_is_working.is_alive():
        freccia_sx_is_working = Process(target=accendi_fr_sinistra_work)
        freccia_sx_is_working.start()


def accendi_fr_sinistra_work():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    while True:
        GPIO.output(FR_SX, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(FR_SX, GPIO.LOW)
        time.sleep(1)


def spegni_fr_sinistra():
    global freccia_sx_is_working

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(FR_SX, GPIO.OUT)

    if freccia_sx_is_working is not None and freccia_sx_is_working.is_alive():
        freccia_sx_is_working.terminate()
        freccia_sx_is_working.join()

    GPIO.output(FR_SX, GPIO.LOW)
    freccia_sx_is_working = None


try:
    print("Test motore 1")
    motore1_avanti(100)
    time.sleep(5)
    motore1_avanti(0)
    print("Test motore 2")
    motore2_avanti(100)
    time.sleep(5)
    motore2_avanti(0)
    print("Test motore 3")
    motore3_avanti(100)
    time.sleep(5)
    motore3_avanti(0)
    print("Test motore 4")
    motore4_avanti(100)
    time.sleep(5)
    motore4_avanti(0)

    """
    print("Test motore 1")
    motore1_avanti(100)
    time.sleep(5)
    motore1_avanti(0)
    print("Test motore 2")
    motore2_avanti(100)
    time.sleep(5)
    motore2_avanti(0)
    print("Test motore 3")
    motore3_avanti(100)
    time.sleep(5)
    motore3_avanti(0)
    print("Test motore 4")
    motore4_avanti(100)
    time.sleep(5)
    motore4_avanti(0)
    print("Velocita diverse")
    motore1_avanti(100)
    motore2_avanti(100)
    motore3_avanti(100)
    motore4_avanti(100)
    time.sleep(300)
    
    spegni_luci_retr()
    spegni_luci_stop()

    motore1_avanti(100)
    motore2_avanti(100)
    motore3_avanti(100)
    motore4_avanti(100)
    time.sleep(0.25)
    ferma_tutto()
    accendi_luci_stop()
    time.sleep(2)

    accendi_luci_retr()
    motore1_indietro(100)
    motore2_indietro(100)
    motore3_indietro(100)
    motore4_indietro(100)
    time.sleep(0.25)
    ferma_tutto()
    
    accendi_fr_destra()
    time.sleep(5)
    motore1_avanti(100)
    motore2_avanti(100)
    motore3_avanti(100)
    motore4_avanti(100)
    time.sleep(0.25)
    ferma_tutto()
    accendi_luci_stop()
    time.sleep(5)

    accendi_luci_retr()
    motore1_indietro(100)
    motore2_indietro(100)
    motore3_indietro(100)
    motore4_indietro(100)
    time.sleep(0.25)
    spegni_fr_destra()
    ferma_tutto()

    

    set_color(255, 0, 0)
    time.sleep(5)
    set_color(0, 255, 0)
    time.sleep(5)
    set_color(0, 0, 255)
    time.sleep(5)
    set_color(255, 255, 255)
    time.sleep(5)


    accendi_fr_destra()
    accendi_fr_sinistra()
    time.sleep(5)
    spegni_fr_destra()
    spegni_fr_sinistra()
    time.sleep(5)
    accendi_fr_destra()
    accendi_fr_sinistra()
    time.sleep(5)
    spegni_fr_destra()
    spegni_fr_sinistra()

    """
    """
    print("Motori avanti a velocità 50% per 5 secondi")
    motore1_avanti(50)
    motore2_avanti(50)
    time.sleep(5)

    print("Motori avanti a velocità 100% per 3 secondi")
    motore1_avanti(100)
    motore2_avanti(100)
    time.sleep(3)

    print("Motori indietro a velocità 70% per 4 secondi")
    motore1_indietro(70)
    motore2_indietro(70)
    time.sleep(4)
"""
    print("Stop!")
    ferma_tutto()


finally:
    pwmA.stop()
    pwmB.stop()
    pwmC.stop()
    pwmD.stop()
    GPIO.cleanup()
