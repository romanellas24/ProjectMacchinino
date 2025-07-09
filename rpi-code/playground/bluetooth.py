import subprocess
import bluetooth
import RPi.GPIO as GPIO

LED_PIN = 17  # Puoi cambiare questo pin

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)

def setup_bluetooth():
    print("⚙️  Configuro Bluetoothctl (no PIN, discoverable)...")

    script_btctl = """
power on
agent NoInputNoOutput
default-agent
discoverable on
pairable on
"""
    subprocess.run(["bluetoothctl"], input=script_btctl.encode(), timeout=5)

def avvia_ricezione_comandi():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", 1))
    server_sock.listen(1)

    print("📡 In ascolto su RFCOMM porta 1...")
    client_sock, client_info = server_sock.accept()
    print("🔗 Connesso con:", client_info)

    try:
        while True:
            data = client_sock.recv(1024)
            comando = data.decode("utf-8").strip().upper()
            print("📥 Comando ricevuto:", comando)

            if comando == "ACCENDI_LED":
                GPIO.output(LED_PIN, GPIO.HIGH)
                print("💡 LED acceso")
            elif comando == "SPEGNI_LED":
                GPIO.output(LED_PIN, GPIO.LOW)
                print("🕯️ LED spento")
            elif comando == "EXIT":
                print("🛑 Uscita richiesta")
                break
            else:
                print("❓ Comando non riconosciuto")
    except OSError:
        print("⚠️ Connessione interrotta.")
    finally:
        client_sock.close()
        server_sock.close()
        GPIO.cleanup()
        print("🔌 Server Bluetooth terminato.")

if __name__ == "__main__":
    setup_gpio()
    setup_bluetooth()
    avvia_ricezione_comandi()
