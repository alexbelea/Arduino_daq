import serial
import time
import csv

# Configure serial port - adjust COM port as needed
ser = serial.Serial('COM3', 115200, timeout=1)
time.sleep(2)  # Wait for Arduino to reset

filename = f"arduino_daq_data_{time.strftime('%Y%m%d_%H%M%S')}.csv"
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    print(f"Waiting for data... (will save to {filename})")
    
    # Wait for start signal
    while True:
        line = ser.readline().decode('utf-8').strip()
        if "START_RECORDING" in line:
            print("Recording started!")
            break
        elif line:  # Write header if received
            writer.writerow(line.split(','))
    
    # Read and save data
    while True:
        line = ser.readline().decode('utf-8').strip()
        if "END_RECORDING" in line:
            print("Recording complete!")
            break
        elif line and ',' in line:  # Only write data lines
            writer.writerow(line.split(','))
            
    # Get summary
    while True:
        line = ser.readline().decode('utf-8').strip()
        if "READY_FOR_NEXT_RECORDING" in line:
            print("Ready for next recording.")
            break
        elif line:
            print(line)

ser.close()
print(f"Data saved to {filename}")