import socket
import subprocess
import threading

import macchininoPrimitives
from multiprocessing import Process
from threading import Thread

freccia_sx_is_working = None
freccia_dx_is_working = None

move_command_executing = "MOVE_STOP"
move_command_process = None

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return (result.returncode, result.stdout.strip())
    except subprocess.CalledProcessError as e:
        return (e.returncode, e.stderr.strip())


def accendi_fr_destra():
    global freccia_dx_is_working
    if freccia_dx_is_working is None or not freccia_dx_is_working.is_alive():
        freccia_dx_is_working = Process(target=macchininoPrimitives.accendi_fr_destra_work)
        freccia_dx_is_working.start()


def accendi_fr_sinistra():
    global freccia_sx_is_working
    if freccia_sx_is_working is None or not freccia_sx_is_working.is_alive():
        freccia_sx_is_working = Process(target=macchininoPrimitives.accendi_fr_sinistra_work)
        freccia_sx_is_working.start()

def execute_move_command(invoked, callback):
    global move_command_executing, move_command_process
    if move_command_executing != invoked:
        move_command_executing = invoked
    else:
        return

    if move_command_process is not None:
        print(move_command_process)
        move_command_process.terminate()
        move_command_process.join()

    print("Called execute_move_command.")
    move_command_process = Process(target=callback)
    move_command_process.start()


server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
server_sock.bind((macchininoPrimitives.SERVER_MAC_ADDRESS, 1))  # Port 1 for SPP
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
            execute_move_command(decoded, macchininoPrimitives.ferma_tutto)
        elif decoded == "MOVE_AHEAD":
            execute_move_command(decoded, macchininoPrimitives.cammina)
        elif decoded == "MOVE_BACK":
            execute_move_command(decoded, macchininoPrimitives.retromarcia)
        """
        elif decoded == "TOGGLE_FRECCIA_DX":
            
        elif decoded == "TOGGLE_FRECCIA_SX":
           """


except OSError:
    pass

client_sock.close()
server_sock.close()
