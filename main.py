import serial
import json
import time
import matplotlib.pyplot as plt

DEFAULT_PORT = 'COM3'
DEFAULT_BAUNDRATE = 115200

with open("config.json", "r") as f:
    CONFIG = json.load(f)
    COMMANDS = CONFIG["commands"]

def find_command_name(trigger):
    for cmd in COMMANDS:
        if (COMMANDS[cmd]["trigger"] == trigger):
            return cmd    

while(True):
    code = input("> ")
    splited_code = code.split()
    command = splited_code[0]
    command_name = find_command_name(command)

    args = splited_code[1:]
    
    if (COMMANDS[command_name]["min_args"] > len(args)):
        print("Syntax Error. Usage: " + COMMANDS[command_name]["usage"])
        continue

    if (command == COMMANDS["start_serial"]["trigger"]): # USAGE: -ss <PORT> <BOUNDRATE>
        if (len(args) == 0): 
            ser = serial.Serial(DEFAULT_PORT, DEFAULT_BAUNDRATE)
            print(f"Serial begin at {DEFAULT_PORT} in {DEFAULT_BAUNDRATE}!") # More than 1 serial connection will be added
        elif (len(args) == 1):
            ser = serial.Serial(args[0], DEFAULT_BAUNDRATE)
            print(f"Serial begin at {args[0]} in {DEFAULT_BAUNDRATE}!")
        elif (len(args) >= 2):
            ser = serial.Serial(args[0], int(args[1]))
            print(f"Serial begin at {args[0]} in {args[1]}!")

    elif (command == COMMANDS["read"]["trigger"]): #read USAGE: -r
        receive = False
        while (not receive): 
            receivedData = ser.readline()

            if (receivedData):
                message = receivedData.decode('utf-8').strip()
                print(f"stm32> {message}")
                receive = True
    elif (command == COMMANDS["write"]["trigger"]):
        ser.write(args[0].encode('utf-8'))
        print("The message's writen successfully!")
    elif (command == COMMANDS["read_save"]["trigger"]):
        with open("data.json", "r") as f:
            data_json = json.load(f)

        data = []
        starting_time = time.time()
        while ((time.time() - starting_time) < int(args[0])):
            receivedData = ser.readline()
            data.append((time.time(), receivedData.decode('utf-8').strip()))
        
        id = data_json["saved_datas"][-1]["id"] + 1 if len(data_json["saved_datas"]) > 0 else 0
        
        data_object = {
            "id": id,
            "name": args[1],
            "startingTime": starting_time,
            "duration": int(args[0]),
            "data": data
        }
        
        data_json["saved_datas"].append(data_object)

        with open("data.json", "w") as f:
            json.dump(data_json, f, indent=4)

        print(f"Read data has saved successfully! Save ID: {id}")
    
    elif (command == COMMANDS["plot"]["trigger"]): #plot USAGE: -p <save_ID>
        with open("data.json", "r") as f:
            data_json = json.load(f)

        x_axis = []
        y_axis = []

        if (len(data_json["saved_datas"]) > int(args[0])):
            datas = data_json["saved_datas"][int(args[0])]["data"]
            name = data_json["saved_datas"][int(args[0])]["name"]
            for data in datas:
                x_axis.append(data[0]) 
                y_axis.append(data[1])

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

    elif (command == COMMANDS["close"]["trigger"]): #close USAGE: -c
        ser.close()
        break
