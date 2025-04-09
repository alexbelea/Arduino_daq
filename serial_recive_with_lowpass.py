import serial
import platform
import glob
import time
import csv
import matplotlib.pyplot as plt
import pandas as pd
import os
import re
import numpy as np
from scipy import signal

# the arduino code decides recording length, this is just a timeout which
# must be greater than the time in arduino code
recordingLength = 10 # seconds # Must change both here and in arduino_code.cpp

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

def apply_lowpass_filter(data, cutoff_freq, fs, order=4):
    """
    Apply a low-pass Butterworth filter to the data
    
    Parameters:
    data (numpy.ndarray): The data to filter
    cutoff_freq (float): The cutoff frequency in Hz
    fs (float): The sampling frequency in Hz
    order (int): The filter order (4 pole = 24dB/octave, 6 pole = 36dB/octave)
    
    Returns:
    numpy.ndarray: The filtered data
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff_freq / nyquist
    
    # Design the Butterworth filter
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    
    # Apply the filter using filtfilt for zero-phase filtering (no time delay)
    filtered_data = signal.filtfilt(b, a, data)
    
    return filtered_data

def filter_and_save_data(filename, cutoff_freq=2.0, filter_order=4):
    """
    Load data from CSV, apply a low-pass filter, and save the filtered data
    
    Parameters:
    filename (str): The CSV file containing the data
    cutoff_freq (float): The cutoff frequency in Hz
    filter_order (int): The filter order (4=24dB/octave, 5=30dB/octave, 6=36dB/octave)
    
    Returns:
    str: The filename of the filtered data
    """
    try:
        print(f"Filtering data from {filename}...")
        
        # Read the CSV data
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
        
        # Calculate the sampling frequency from the time data
        # Use the median time difference to handle potential irregularities
        time_diffs = np.diff(df['Time(ms)'])
        median_time_diff = np.median(time_diffs)  # in milliseconds
        fs = 1000.0 / median_time_diff  # Convert to Hz
        print(f"Estimated sampling frequency: {fs:.1f} Hz")
        
        # Filter each analog channel
        analog_channels = ['A0(V)', 'A1(V)', 'A2(V)', 'A3(V)']
        for channel in analog_channels:
            if channel in df.columns:
                df[f"{channel}_filtered"] = apply_lowpass_filter(
                    df[channel].values, cutoff_freq, fs, order=filter_order
                )
        
        # Save the filtered data to a new CSV file
        filtered_filename = f"{os.path.splitext(filename)[0]}_filtered.csv"
        df.to_csv(filtered_filename, index=False)
        print(f"Filtered data saved to {filtered_filename}")
        
        return filtered_filename
        
    except Exception as e:
        print(f"Error filtering data: {e}")
        return filename

def plot_data(filename, show_original=True, show_filtered=True, overlapping_plots=False):
    """
    Plot the DAQ data, showing both original and filtered signals if available
    
    Parameters:
    filename (str): The CSV file to plot
    show_original (bool): Whether to show the original data
    show_filtered (bool): Whether to show the filtered data
    overlapping_plots (bool): If True, overlaps all channels on a single plot; otherwise creates separate subplots
    """
    try:
        # Read the CSV data
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
        
        # Check for filtered columns
        has_filtered = any('_filtered' in col for col in df.columns)
        
        # Identify all analog channels
        analog_channels = [col for col in df.columns if col.startswith('A') and col.endswith('(V)') and not '_filtered' in col]
        
        # Create color cycle for different channels
        colors = ['orange', 'yellow', 'blue', 'purple', 'pink', 'pink', 'pink', 'pink']
        
        if overlapping_plots:
            # Create a single plot with all channels overlapping
            plt.figure(figsize=(14, 8))
            
            # Plot original data
            if show_original:
                for i, channel in enumerate(analog_channels):
                    color = colors[i % len(colors)]
                    plt.plot(df['Time(ms)'], df[channel], label=f'{channel} Original', 
                            linewidth=1.5, alpha=0.4, color=color, linestyle='-')
            
            # Plot filtered data
            if has_filtered and show_filtered:
                for i, channel in enumerate(analog_channels):
                    filtered_channel = f"{channel}_filtered"
                    if filtered_channel in df.columns:
                        color = colors[i % len(colors)]
                        plt.plot(df['Time(ms)'], df[filtered_channel], label=f'{channel} Filtered', 
                                linewidth=2.5, color=color, linestyle='-')
            
            # Set the y-axis range from 0 to 5V
            plt.ylim(0, 5)
            
            # Add labels and title
            plt.xlabel('Time (ms)')
            plt.ylabel('Voltage (V)')
            plt.title('Arduino DAQ - All Channels')
            plt.legend()
            plt.grid(True)
            
        else:
            # Create the plot with individual subplots per channel
            plt.figure(figsize=(12, 10))
            
            # Organize subplots - one subplot per analog channel
            for i, channel in enumerate(analog_channels):
                plt.subplot(len(analog_channels), 1, i+1)
                
                # Plot original data if requested
                if show_original:
                    plt.plot(df['Time(ms)'], df[channel], label=f'{channel} Original', 
                            linewidth=1, alpha=0.7, color='lightgray')
                
                # Plot filtered data if available and requested
                filtered_channel = f"{channel}_filtered"
                if has_filtered and filtered_channel in df.columns and show_filtered:
                    plt.plot(df['Time(ms)'], df[filtered_channel], label=f'{channel} Filtered', 
                            linewidth=2, color='blue')
                
                # Set the y-axis range from 0 to 5V
                plt.ylim(0, 5)
                
                # Add labels
                plt.ylabel('Voltage (V)')
                if i == len(analog_channels) - 1:  # Only add x-label for bottom subplot
                    plt.xlabel('Time (ms)')
                
                plt.title(f'Channel {channel}')
                plt.legend()
                plt.grid(True)
        
        # Add some information about the data range
        min_voltage = min(df[analog_channels].min())
        max_voltage = max(df[analog_channels].max())
        duration = df['Time(ms)'].max() - df['Time(ms)'].min()
        sample_count = len(df)
        sample_rate = sample_count/(duration/1000) if duration > 0 else 0
        
        if has_filtered:
            filtered_channels = [col for col in df.columns if '_filtered' in col]
            min_filtered = min(df[filtered_channels].min())
            max_filtered = max(df[filtered_channels].max())
            filter_info = f"Filtered data range: {min_filtered:.3f} - {max_filtered:.3f} V\n"
        else:
            filter_info = ""
        
        info_text = f"Data summary:\n" \
                    f"Duration: {duration:.1f} ms\n" \
                    f"Samples: {sample_count}\n" \
                    f"Sample rate: {sample_rate:.1f} Hz\n" \
                    f"Raw data range: {min_voltage:.3f} - {max_voltage:.3f} V\n" \
                    f"{filter_info}"
                    
        plt.figtext(0.02, 0.02, info_text, fontsize=10, 
                    bbox=dict(facecolor='white', alpha=0.8))
        
        # Save the plot
        plot_suffix = "_overlapped" if overlapping_plots else "_subplots"
        plot_filename = f"{os.path.splitext(filename)[0]}{plot_suffix}_plot.png"
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

    # Ask for filter settings
    print("\nLow-pass filter settings:")
    cutoff_freq = float(input("Enter cutoff frequency in Hz (recommended: 1.0-2.0 for 0.5Hz signals): ") or "1.5")
    filter_order = int(input("Enter filter order (4=24dB/octave, 5=30dB/octave, 6=36dB/octave): ") or "4")
    
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
                timeout_duration = recordingLength  # timeout to prevent loop #seconds 
                
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
            
            # Apply low-pass filter to the data
            filtered_filename = filter_and_save_data(clean_filename, 
                                                   cutoff_freq=cutoff_freq, 
                                                   filter_order=filter_order)
                
            # Ask if user wants to plot the data
            plot_choice = input("Plot the data? (y/n): ")
            if plot_choice.lower() == 'y':
                plot_style = input("Plot style - separate subplots or overlapping channels? (s/o): ").lower()
                overlapping = plot_style == 'o'
                plot_data(filtered_filename, show_original=True, show_filtered=True, overlapping_plots=overlapping)
                
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

def filter_existing_file():
    """
    Function to filter an existing data file without recording new data
    """
    filename = input("Enter the path to the data file: ")
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return
    
    # Clean the file if needed
    clean_filename = clean_data_file(filename)
    
    # Ask for filter settings
    print("\nLow-pass filter settings:")
    cutoff_freq = float(input("Enter cutoff frequency in Hz (recommended: 1.0-2.0 for 0.5Hz signals): ") or "1.5")
    filter_order = int(input("Enter filter order (4=24dB/octave, 5=30dB/octave, 6=36dB/octave): ") or "4")
    
    # Apply filter
    filtered_filename = filter_and_save_data(clean_filename, 
                                           cutoff_freq=cutoff_freq, 
                                           filter_order=filter_order)
    
    # Plot the results
    plot_choice = input("Plot the filtered data? (y/n): ")
    if plot_choice.lower() == 'y':
        plot_style = input("Plot style - separate subplots or overlapping channels? (s/o): ").lower()
        overlapping = plot_style == 'o'
        plot_data(filtered_filename, show_original=True, show_filtered=True, overlapping_plots=overlapping)

if __name__ == "__main__":
    print("Arduino DAQ with Low-Pass Filter")
    print("--------------------------------")
    print("1. Record new data from Arduino")
    print("2. Filter existing data file")
    
    choice = input("Enter your choice (1/2): ")
    
    if choice == "1":
        main()
    elif choice == "2":
        filter_existing_file()
    else:
        print("Invalid choice")