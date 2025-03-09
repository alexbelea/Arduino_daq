import serial
import platform
import glob
import time
import csv
import matplotlib.pyplot as plt
import pandas as pd
import os
import re

def list_available_ports():
    """Lists all available serial ports based on the operating system"""
    system = platform.system()
    
    if system == 'Windows':
        # Windows-specific port listing
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    elif system == 'Linux':
        # Linux-specific port listing (your original code)
        return glob.glob('/dev/tty[A-Za-z]*')
    elif system == 'Darwin':  # macOS
        # macOS typically uses similar naming to Linux
        return glob.glob('/dev/tty.*') + glob.glob('/dev/cu.*')
    else:
        print(f"Unsupported operating system: {system}")
        return []

def plot_data(filename):
    """Plot the DAQ data"""
    try:
        # Read the CSV data with flexible parsing
        try:
            # Try standard header names
            df = pd.read_csv(filename)
        except:
            # Try with manual column specification
            df = pd.read_csv(filename, names=['Sample', 'Time(ms)', 'A0(V)', 'A1(V)', 'A2(V)', 'A3(V)'])
        
        # Clean the dataframe - remove rows with invalid data
        # Convert all columns to numeric, errors become NaN
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Drop rows with NaN values
        df = df.dropna()
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        
        # Plot each analog channel
        plt.plot(df['Time(ms)'], df['A0(V)'], label='Analog 0', linewidth=2)
        plt.plot(df['Time(ms)'], df['A1(V)'], label='Analog 1', linewidth=2)
        plt.plot(df['Time(ms)'], df['A2(V)'], label='Analog 2', linewidth=2)
        plt.plot(df['Time(ms)'], df['A3(V)'], label='Analog 3', linewidth=2)
        
        # Set the y-axis range from 0 to 5V as requested
        plt.ylim(0, 5)
        
        # Add labels and title
        plt.xlabel('Time (ms)')
        plt.ylabel('Voltage (V)')
        plt.title('Arduino DAQ - 4-Channel Analog Readings')
        plt.legend()
        plt.grid(True)
        
        # Add some information about the data range
        min_voltage = min(df[['A0(V)', 'A1(V)', 'A2(V)', 'A3(V)']].min())
        max_voltage = max(df[['A0(V)', 'A1(V)', 'A2(V)', 'A3(V)']].max())
        duration = df['Time(ms)'].max() - df['Time(ms)'].min()
        sample_count = len(df)
        sample_rate = sample_count/(duration/1000) if duration > 0 else 0
        
        info_text = f"Data summary:\n" \
                    f"Duration: {duration:.1f} ms\n" \
                    f"Samples: {sample_count}\n" \
                    f"Sample rate: {sample_rate:.1f} Hz\n" \
                    f"Min voltage: {min_voltage:.3f} V\n" \
                    f"Max voltage: {max_voltage:.3f} V"
                    
        plt.figtext(0.02, 0.02, info_text, fontsize=10, 
                    bbox=dict(facecolor='white', alpha=0.8))
        
        # Add second X-axis with time in seconds
        ax1 = plt.gca()
        ax2 = ax1.twiny()
        ax2.set_xlim(ax1.get_xlim())
        ax2.set_xticks([df['Time(ms)'].min(), df['Time(ms)'].max()])
        ax2.set_xticklabels([f"{df['Time(ms)'].min()/1000:.2f}s", f"{df['Time(ms)'].max()/1000:.2f}s"])
        ax2.set_xlabel("Time (s)")
        
        # Save the plot
        plot_filename = f"{os.path.splitext(filename)[0]}_plot.png"
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        print(f"Plot saved as {plot_filename}")
        
        # Show the plot
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error plotting data: {e}")

def clean_data_file(filename):
    """Cleans a CSV data file by removing invalid lines"""
    try:
        print(f"Cleaning data file {filename}...")
        
        # Read the file
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        cleaned_lines = []
        header_found = False
        
        # Regular expression to match valid data lines
        # Format: number,number,number,number,number,number
        data_pattern = re.compile(r'^\d+,\d+,\d+\.\d+,\d+\.\d+,\d+\.\d+,\d+\.\d+$')
        
        for line in lines:
            line = line.strip()
            
            # Keep the header line
            if "Sample,Time" in line:
                cleaned_lines.append(line + '\n')
                header_found = True
                continue
            
            # Check if it's a valid data line
            if data_pattern.match(line) or (line.count(',') == 5 and line[0].isdigit()):
                cleaned_lines.append(line + '\n')
        
        # If no header was found, add one
        if not header_found and cleaned_lines:
            cleaned_lines.insert(0, "Sample,Time(ms),A0(V),A1(V),A2(V),A3(V)\n")
        
        # Write the cleaned data back to file
        clean_filename = f"{os.path.splitext(filename)[0]}_clean.csv"
        with open(clean_filename, 'w') as file:
            file.writelines(cleaned_lines)
            
        print(f"Cleaned data saved to {clean_filename}")
        return clean_filename
        
    except Exception as e:
        print(f"Error cleaning data file: {e}")
        return filename

def main():
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

    try:
        # Configure serial port
        ser = serial.Serial(selected_port, 115200, timeout=2)
        print(f"Connected to {selected_port}")
        time.sleep(2)  # Wait for Arduino to reset
        
        # Flush any leftover data
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Wait for Arduino ready signal
        print("Waiting for Arduino to be ready...")
        ready = False
        timeout = time.time() + 10  # 10 second timeout
        
        while not ready and time.time() < timeout:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line == "ARDUINO_DAQ_READY":
                ready = True
                print("Arduino is ready!")
            elif line:
                print(f"Received: {line}")
        
        if not ready:
            print("Arduino did not respond with ready signal, continuing anyway...")
        
        while True:
            # Ask user if they want to start recording
            choice = input("Start recording? (y/n): ")
            if choice.lower() != 'y':
                break
            
            # Create a filename for this recording session
            filename = f"arduino_daq_data_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='') as file:
                # Send start command
                ser.write(b"START\n")
                
                print(f"Recording data to {filename}...")
                recording = True
                data_lines = 0
                
                # Start time for timeout
                start_time = time.time()
                timeout_duration = 15  # seconds
                
                while recording and (time.time() - start_time) < timeout_duration:
                    if ser.in_waiting:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        
                        if "RECORDING_COMPLETE" in line:
                            recording = False
                            print("Recording complete!")
                        elif "SAMPLES_COLLECTED" in line:
                            try:
                                samples = int(line.split(":")[1])
                                print(f"Collected {samples} samples")
                            except:
                                print(f"Received sample info: {line}")
                        elif "END_OF_DATA" in line:
                            print("End of data received")
                        elif line:
                            # Write the line to the file
                            file.write(line + '\n')
                            data_lines += 1
                            
                            # Show progress periodically
                            if data_lines % 100 == 0:
                                print(f"Received {data_lines} data points...", end='\r')
                
                print(f"\nSaved {data_lines} data points to {filename}")
            
            # Try to clean the data file
            clean_filename = clean_data_file(filename)
            
            # Ask if user wants to plot the data
            plot_choice = input("Plot the data? (y/n): ")
            if plot_choice.lower() == 'y':
                plot_data(clean_filename)
                
    except serial.SerialException as e:
        print(f"Error: {e}")
        print("Tips for Linux serial ports:")
        print("1. Make sure you have permission to access serial ports.")
        print("2. You might need to run: sudo usermod -a -G dialout $USER")
        print("3. Then log out and log back in for the changes to take effect.")
        
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
        
    finally:
        # Close the serial port
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    main()