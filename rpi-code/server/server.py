import socket
import subprocess

import re
import macchininoPrimitives
from multiprocessing import Process, Manager


def get_bluetooth_mac(interface='hci0'):
    try:
        output = subprocess.check_output(['hciconfig', interface], text=True)
        match = re.search(r'BD Address: (\S+)', output)
        if match:
            return match.group(1)
        else:
            print("MAC address non trovato.")
    except subprocess.CalledProcessError as e:
        print("Errore nell'esecuzione di hciconfig:", e)
    return None


def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.returncode, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stderr.strip()


def execute_move_command(invoked, shared):
    shared["move_command"] = invoked


def main():
    mac = get_bluetooth_mac()
    move_command_executing = "MOVE_STOP"
    gpio_process = None

    mgr = Manager()
    shared = mgr.dict({
        "move_command": "MOVE_STOP",
        "high_lights": False,
        "signal_turn_left": False,
        "signal_turn_right": False,
        "rgb_lights": (100, 100, 100),
    })

    gpio_process = Process(target=macchininoPrimitives.setup, args=(shared,))
    gpio_process.start()
    execute_move_command("SETUP", shared)

    server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    server_sock.bind((mac, 1))  # Port 1 for SPP
    server_sock.listen(1)

    print("Registering SPP Service...")
    try:
        subprocess.run(["sdptool", "add", "SP"], check=True)
        print("Registered SP Service.")
    except subprocess.CalledProcessError:
        print("Error: Cannot register SP service.")

    print("Waiting for Bluetooth connection...")
    client_sock, client_info = server_sock.accept()
    print("Connected to:", client_info)

    try:
        while True:
            data = client_sock.recv(1024)
            if not data:
                break
            decoded = data.decode('utf-8')
            print("Received:", decoded)
            decoded = decoded.strip()
            if decoded == "SYSTEM_SHUTDOWN":
                execute_command("shutdown 0")
            elif decoded == "SYSTEM_REBOOT":
                execute_command("reboot")
            elif decoded == "MOVE_STOP":
                execute_move_command(decoded, shared)
            elif decoded == "MOVE_AHEAD":
                execute_move_command(decoded, shared)
            elif decoded == "MOVE_BACK":
                execute_move_command(decoded, shared)
            elif decoded == "MOVE_LEFT":
                execute_move_command(decoded, shared)
            elif decoded == "MOVE_RIGHT":
                execute_move_command(decoded, shared)
            elif decoded == "TOGGLE_HIGH_LIGHTS":
                shared["high_lights"] = not shared["high_lights"]
            elif decoded == "TOGGLE_TR_LF":
                shared["signal_turn_left"] = not shared["signal_turn_left"]
            elif decoded == "TOGGLE_TR_RG":
                shared["signal_turn_right"] = not shared["signal_turn_right"]
            elif decoded.startswith("LIGHTS_"):
                match = re.match(r"LIGHTS_(\d+)_(\d+)_(\d+)", decoded)
                if match:
                    x, y, z = map(int, match.groups())
                    shared["rgb_lights"] = (x, y, z)

    except OSError:
        pass
    finally:
        print("Chiudo connessione Bluetooth e processi...")
        if gpio_process and gpio_process.is_alive():
            gpio_process.terminate()
            gpio_process.join()

        if mgr:
            mgr.shutdown()

    client_sock.close()
    server_sock.close()

while True:
    main()