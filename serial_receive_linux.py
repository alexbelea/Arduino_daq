import serial
import time
import csv
import glob

def list_available_ports():
    """Lists all available serial ports on Linux"""
    return glob.glob('/dev/tty[A-Za-z]*')

# List available ports
available_ports = list_available_ports()
print("Available ports:")
for i, port in enumerate(available_ports):
    print(f"{i}: {port}")

# Let user select port
if available_ports:
    port_index = int(input("Select port by number: "))
    selected_port = available_ports[port_index]
else:
    print("No serial ports found. Make sure Arduino is connected.")
    selected_port = input("Enter port manually (e.g., /dev/ttyACM0): ")

# Configure serial port with selected port
try:
    ser = serial.Serial(selected_port, 115200, timeout=1)
    print(f"Connected to {selected_port}")
    time.sleep(2)  # Wait for Arduino to reset

    filename = f"arduino_daq_data_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        print(f"Waiting for data... (will save to {filename})")
        
        # Wait for start signal
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if "START_RECORDING" in line:
                print("Recording started!")
                break
            elif line and ',' in line:  # Write header if received
                writer.writerow(line.split(','))
                print(f"Received header: {line}")
        
        # Read and save data
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if "END_RECORDING" in line:
                print("Recording complete!")
                break
            elif line and ',' in line:  # Only write data lines
                writer.writerow(line.split(','))
                print(f"Data: {line}", end='\r')
                
        # Get summary
        print("\nSummary:")
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if "READY_FOR_NEXT_RECORDING" in line:
                print("Ready for next recording.")
                choice = input("Start another recording? (y/n): ")
                if choice.lower() == 'y':
                    print("Waiting for next recording...")
                    continue
                else:
                    break
            elif line:
                print(line)

    ser.close()
    print(f"Data saved to {filename}")
    
except serial.SerialException as e:
    print(f"Error: {e}")
    print("Tips for Linux serial ports:")
    print("1. Make sure you have permission to access serial ports.")
    print("2. You might need to run: sudo usermod -a -G dialout $USER")
    print("3. Then log out and log back in for the changes to take effect.")
    print("4. Common Arduino ports on Linux are /dev/ttyACM0 or /dev/ttyUSB0")