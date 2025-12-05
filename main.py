import serial
import json
import time
import threading
import matplotlib.pyplot as plt

with open("config.json", "r") as f:
    CONFIG = json.load(f)
    COMMANDS = CONFIG["commands"]


DEFAULT_PORT = CONFIG["default_port"]
DEFAULT_BAUNDRATE = CONFIG["default_baundrate"]

PACKAGE_PREFIX = CONFIG["package_settings"]["prefix"]
PACKAGE_SUBFIX = CONFIG["package_settings"]["subfix"]
PACKAGE_LENGTH = CONFIG["package_settings"]["length"]

read_packages = []
is_serial_running = False
ser = None


def find_command_name(trigger):
    for cmd in COMMANDS:
        if (COMMANDS[cmd]["trigger"] == trigger):
            return cmd
def send_serial_package(msg):
    package = b'\xff' + msg.encode('utf-8') + b'\r\n'
    ser.write(package)

def read_serial_package():
    global is_serial_running
    packet_buffer = bytearray()
    is_collecting = False

    while is_serial_running:
        byte = ser.read(1)
        if byte:
            if byte == b'\xff':
                packet_buffer = bytearray(byte)
                is_collecting = True 
            elif is_collecting:
                packet_buffer += byte
                if packet_buffer.endswith(b'\r\n'):                    
                    if len(packet_buffer) <= 16:
                        raw_payload = packet_buffer[1:-2]
                        decoded_data = raw_payload.decode('utf-8')

                        read_packages.append((decoded_data, time.time()))
                    is_collecting = False
                    packet_buffer = bytearray()                
                elif len(packet_buffer) > 16:
                    is_collecting = False
                    packet_buffer = bytearray()

def run_interface():
    global ser
    global is_serial_running
    global read_serial_package_thread
    while(True):
        code = input("> ")
        if (len(code) == 0):
            continue
        splited_code = code.split()
        command = splited_code[0]
        command_name = find_command_name(command)

        args = splited_code[1:]
        
        if (COMMANDS[command_name]["min_args"] > len(args)):
            print("Syntax Error. Usage: " + COMMANDS[command_name]["usage"])
            continue

        if (command == COMMANDS["start_serial"]["trigger"]):
            if (len(args) == 0): 
                ser = serial.Serial(DEFAULT_PORT, DEFAULT_BAUNDRATE)
                print(f"Serial begin at {DEFAULT_PORT} in {DEFAULT_BAUNDRATE}!")
            elif (len(args) == 1):
                ser = serial.Serial(args[0], DEFAULT_BAUNDRATE)
                print(f"Serial begin at {args[0]} in {DEFAULT_BAUNDRATE}!")
            elif (len(args) >= 2):
                ser = serial.Serial(args[0], int(args[1]))
                print(f"Serial begin at {args[0]} in {args[1]}!")
            
            is_serial_running = True
            read_serial_package_thread = threading.Thread(target=read_serial_package)
            read_serial_package_thread.start()
        elif (command == COMMANDS["read"]["trigger"]):
            if (len(read_packages) > 0):
                print(f"Data: {read_packages[-1][0]} Acquire Time: {read_packages[-1][1]}")
            else:
                print("There isn't any packages read recently.")
        elif (command == COMMANDS["write"]["trigger"]):
            send_serial_package(args[0])
            print("The message's writen successfully!")
        elif (command == COMMANDS["read_save"]["trigger"]):
            with open("data.json", "r") as f:
                data_json = json.load(f)

            length_old = len(read_packages)
            
            time.sleep(int(args[0]))

            length_new = len(read_packages)
            
            if(length_new - length_old == 0):
                print(f"There aren't any data acquired within {args[0]} seconds.")
                continue

            data = read_packages[length_old:(length_new - 1)]
            id = data_json["saved_datas"][-1]["id"] + 1 if len(data_json["saved_datas"]) > 0 else 0
            
            data_object = {
                "id": id,
                "name": args[1],
                "duration": int(args[0]),
                "data": data
            }
            
            data_json["saved_datas"].append(data_object)

            with open("data.json", "w") as f:
                json.dump(data_json, f, indent=4)

            print(f"Read data has saved successfully! Save ID: {id}")
        elif (command == COMMANDS["plot"]["trigger"]):
            with open("data.json", "r") as f:
                data_json = json.load(f)

            x_axis = []
            y_axis = []

            if (len(data_json["saved_datas"]) > int(args[0])):
                datas = data_json["saved_datas"][int(args[0])]["data"]
                name = data_json["saved_datas"][int(args[0])]["name"]
                for data in datas:
                    x_axis.append(data[1]) 
                    y_axis.append(data[0])

                plt.figure(figsize=(10, 6))

                plt.plot(x_axis, y_axis, marker='o', linestyle='-', color='b', label=name)

                plt.title("Time - Data")
                plt.xlabel("scnds")
                plt.ylabel("data")

                plt.grid(True) 
                plt.legend()
                plt.show()
        elif (command == COMMANDS["help"]["trigger"]):
            print("Help:")
            for cmd in COMMANDS:
                print(f"{COMMANDS[cmd]["trigger"]}: {COMMANDS[cmd]["description"]} Usage: {COMMANDS[cmd]["usage"]}")
        elif (command == COMMANDS["close"]["trigger"]):
            is_serial_running = False
            ser.close()

            break

run_interface()

print("Ending the program...")
