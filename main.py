import serial
import json
import time
import matplotlib.pyplot as plt

DEFAULT_PORT = 'COM3'
DEFAULT_BAUNDRATE = 115200

with open("config.json", "r") as f:
    CONFIG = json.load(f)
    COMMANDS = CONFIG["commands"]

while(True):
    code = input("> ")
    splited_code = code.split()
    command = splited_code[0]
    args = splited_code[1:]
    
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

    elif (command == COMMANDS["write"]["trigger"]): #write USAGE: -w <message>
        if (len(args) == 0):
            print("Syntax Error. Usage: -w <message>!")
        else:
            ser.write(args[0].encode('utf-8'))
            print("The message's writen successfully!")
    elif (command == COMMANDS["read_save"]["trigger"]): #read save USAGE: -rs <seconds> <name>
        if (len(args) == 0):
            print("Syntax Error. Usage: -rs <seconds>!")
        else:
            data = []
            starting_time = time.time()

            while ((time.time() - starting_time) < int(args[0])):
                receivedData = ser.readline()
                data.append((time.time(), receivedData.decode('utf-8').strip()))
            
            id = data_json["savedDatas"][-1]["id"] + 1 if len(data_json["savedDatas"]) > 0 else 0
            
            data_object = {
                "id": id,
                "name": args[1],
                "startingTime": starting_time,
                "duration": int(args[0]),
                "data": data
            }

            with open("data.json", "r") as f:
                data_json = json.load(f)
            
            data_json["savedDatas"].append(data_object)

            with open("data.json", "w") as f:
                json.dump(data_json, f, indent=4)

            print(f"Read data has saved successfully! Save ID: {id}")
    
    elif (command == COMMANDS["plot"]["trigger"]): #plot USAGE: -p <save_ID>
        if (len(args) > 0):
            with open("data.json", "r") as f:
                data_json = json.load(f)

            x_axis = []
            y_axis = []

            if (len(data_json["savedDatas"]) > int(args[0])):
                datas = data_json["savedDatas"][int(args[0])]["data"]
                name = data_json["savedDatas"][int(args[0])]["name"]
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
        else:
            print("Syntax Error. Usage: -p <save_ID>!")

    elif (command == COMMANDS["help"]["trigger"]):
        print("Help:")
        for command in COMMANDS:
            print(f"{COMMANDS[command]["trigger"]}: {COMMANDS[command]["description"]} Usage: {COMMANDS[command]["usage"]}")

    elif (command == COMMANDS["close"]["trigger"]): #close USAGE: -c
        ser.close()
        break