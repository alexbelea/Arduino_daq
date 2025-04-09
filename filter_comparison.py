import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import os
import tkinter as tk
from tkinter import filedialog

def apply_lowpass_filter(data, cutoff_freq, fs, order=4):
    """
    Apply a low-pass Butterworth filter to the data
    
    Parameters:
    data (numpy.ndarray): The data to filter
    cutoff_freq (float): The cutoff frequency in Hz
    fs (float): The sampling frequency in Hz
    order (int): The filter order
    
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

def load_csv_file(filepath=None):
    """
    Load a CSV file containing time-series data
    
    Parameters:
    filepath (str, optional): Path to the CSV file. If None, opens a file dialog.
    
    Returns:
    pandas.DataFrame: The loaded data
    """
    if filepath is None:
        # Use Tkinter file dialog to select file
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        filepath = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filepath:  # User cancelled
            return None
    
    try:
        # Try standard header names first
        df = pd.read_csv(filepath)
        
        # Check if the file has the expected columns
        if not any(col.startswith('A') and col.endswith('(V)') for col in df.columns):
            # Try with manual column specification
            df = pd.read_csv(filepath, names=['Sample', 'Time(ms)', 'A0(V)', 'A1(V)', 'A2(V)', 'A3(V)'])
        
        # Clean the dataframe - convert all columns to numeric, errors become NaN
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Drop rows with NaN values
        df = df.dropna()
        
        return df
    
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

def compare_filters(df, cutoff_freq1, cutoff_freq2, order1, order2):
    """
    Compare different filter settings on the same dataset
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the data
    cutoff_freq1 (float): First cutoff frequency in Hz
    cutoff_freq2 (float): Second cutoff frequency in Hz
    order1 (int): First filter order
    order2 (int): Second filter order
    """
    # Check if DataFrame is valid
    if df is None or df.empty:
        print("No valid data to process")
        return
    
    # Find the first voltage column
    voltage_cols = [col for col in df.columns if col.startswith('A') and col.endswith('(V)')]
    if not voltage_cols:
        print("No voltage columns found in the CSV file")
        return
    
    voltage_col = voltage_cols[0]
    print(f"Using voltage column: {voltage_col}")
    
    # Get the time column
    time_col = 'Time(ms)' if 'Time(ms)' in df.columns else df.columns[1]
    
    # Calculate the sampling frequency
    time_diffs = np.diff(df[time_col])
    median_time_diff = np.median(time_diffs)  # in milliseconds
    fs = 1000.0 / median_time_diff  # Convert to Hz
    print(f"Estimated sampling frequency: {fs:.1f} Hz")
    
    # Get the raw data
    raw_data = df[voltage_col].values
    time_data = df[time_col].values
    
    # Apply different filters
    filtered_data1 = apply_lowpass_filter(raw_data, cutoff_freq1, fs, order=order1)
    filtered_data2 = apply_lowpass_filter(raw_data, cutoff_freq1, fs, order=order2)
    filtered_data3 = apply_lowpass_filter(raw_data, cutoff_freq2, fs, order=order1)
    filtered_data4 = apply_lowpass_filter(raw_data, cutoff_freq2, fs, order=order2)
    
    # Create a 2x2 subplot figure
    fig, axs = plt.subplots(2, 2, figsize=(15, 10), sharex=True, sharey=True)
    fig.suptitle(f'Low-Pass Filter Comparison - {voltage_col}', fontsize=16)
    
    # Plot the results
    axs[0, 0].plot(time_data, raw_data, 'lightgray', linewidth=1, alpha=0.7, label='Original')
    axs[0, 0].plot(time_data, filtered_data1, 'blue', linewidth=2, label=f'{cutoff_freq1}Hz, Order {order1}')
    axs[0, 0].set_title(f'Cutoff: {cutoff_freq1}Hz, Order: {order1}')
    axs[0, 0].legend()
    axs[0, 0].grid(True)
    
    axs[0, 1].plot(time_data, raw_data, 'lightgray', linewidth=1, alpha=0.7, label='Original')
    axs[0, 1].plot(time_data, filtered_data2, 'green', linewidth=2, label=f'{cutoff_freq1}Hz, Order {order2}')
    axs[0, 1].set_title(f'Cutoff: {cutoff_freq1}Hz, Order: {order2}')
    axs[0, 1].legend()
    axs[0, 1].grid(True)
    
    axs[1, 0].plot(time_data, raw_data, 'lightgray', linewidth=1, alpha=0.7, label='Original')
    axs[1, 0].plot(time_data, filtered_data3, 'red', linewidth=2, label=f'{cutoff_freq2}Hz, Order {order1}')
    axs[1, 0].set_title(f'Cutoff: {cutoff_freq2}Hz, Order: {order1}')
    axs[1, 0].legend()
    axs[1, 0].grid(True)
    
    axs[1, 1].plot(time_data, raw_data, 'lightgray', linewidth=1, alpha=0.7, label='Original')
    axs[1, 1].plot(time_data, filtered_data4, 'purple', linewidth=2, label=f'{cutoff_freq2}Hz, Order {order2}')
    axs[1, 1].set_title(f'Cutoff: {cutoff_freq2}Hz, Order: {order2}')
    axs[1, 1].legend()
    axs[1, 1].grid(True)
    
    # Add common labels
    fig.text(0.5, 0.04, 'Time (ms)', ha='center', fontsize=14)
    fig.text(0.04, 0.5, 'Voltage (V)', va='center', rotation='vertical', fontsize=14)
    
    # Add some data information
    data_info = (
        f"Data summary:\n"
        f"Samples: {len(df)}\n"
        f"Sample rate: {fs:.1f} Hz\n"
        f"Min value: {raw_data.min():.2f}V\n"
        f"Max value: {raw_data.max():.2f}V\n"
    )
    fig.text(0.02, 0.02, data_info, fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
    
    # Save the plot
    input_filename = os.path.basename(filepath) if 'filepath' in locals() else "unknown"
    plot_filename = f"filter_comparison_{input_filename.split('.')[0]}.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved as {plot_filename}")
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)  # Adjust to make room for the suptitle
    plt.show()

if __name__ == "__main__":
    print("Low-Pass Filter Comparison Tool")
    print("-------------------------------")
    
    # Let the user select a CSV file
    print("Please select a CSV file to analyze...")
    df = load_csv_file()
    
    if df is not None:
        # Get filter parameters from user
        print("\nEnter filter parameters:")
        cutoff_freq1 = float(input("First cutoff frequency (Hz): ") or "1.0")
        cutoff_freq2 = float(input("Second cutoff frequency (Hz): ") or "2.0")
        order1 = int(input("First filter order: ") or "2")
        order2 = int(input("Second filter order: ") or "4")
        
        # Compare the filters
        compare_filters(df, cutoff_freq1, cutoff_freq2, order1, order2)
    else:
        print("No CSV file selected or error loading file.")