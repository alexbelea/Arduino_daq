import matplotlib.pyplot as plt
import pandas as pd
import sys

def plot_daq_data(filename):
    # Read the CSV data
    # Using names to explicitly set column names, and skip the header row if it exists
    try:
        # Try reading with header
        df = pd.read_csv(filename, names=['Sample', 'Time_ms', 'A0', 'A1', 'A2', 'A3'])
        
        # Check if the first row contains headers
        if df.iloc[0, 0] == 'Sample' or isinstance(df.iloc[0, 0], str):
            df = pd.read_csv(filename, skiprows=1, names=['Sample', 'Time_ms', 'A0', 'A1', 'A2', 'A3'])
    except:
        print(f"Error reading file {filename}. Make sure it's a valid CSV file.")
        return
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Plot each analog channel
    plt.plot(df['Time_ms'], df['A0'], label='Analog 0', linewidth=2)
    plt.plot(df['Time_ms'], df['A1'], label='Analog 1', linewidth=2)
    plt.plot(df['Time_ms'], df['A2'], label='Analog 2', linewidth=2)
    plt.plot(df['Time_ms'], df['A3'], label='Analog 3', linewidth=2)
    
    # Set the y-axis range from 0 to 5V as requested
    plt.ylim(0, 5)
    
    # Add labels and title
    plt.xlabel('Time (ms)')
    plt.ylabel('Voltage (V)')
    plt.title('Arduino DAQ - 4-Channel Analog Readings')
    plt.legend()
    plt.grid(True)
    
    # Add some information about the data range
    min_voltage = min(df[['A0', 'A1', 'A2', 'A3']].min())
    max_voltage = max(df[['A0', 'A1', 'A2', 'A3']].max())
    duration = df['Time_ms'].max() - df['Time_ms'].min()
    sample_count = len(df)
    
    info_text = f"Data summary:\n" \
                f"Duration: {duration:.1f} ms\n" \
                f"Samples: {sample_count}\n" \
                f"Sample rate: {sample_count/(duration/1000):.1f} Hz\n" \
                f"Min voltage: {min_voltage:.3f} V\n" \
                f"Max voltage: {max_voltage:.3f} V"
                
    plt.figtext(0.02, 0.02, info_text, fontsize=10, 
                bbox=dict(facecolor='white', alpha=0.8))
    
    # Add second X-axis with time in seconds
    ax1 = plt.gca()
    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_xticks([df['Time_ms'].min(), df['Time_ms'].max()])
    ax2.set_xticklabels([f"{df['Time_ms'].min()/1000:.2f}s", f"{df['Time_ms'].max()/1000:.2f}s"])
    ax2.set_xlabel("Time (s)")
    
    # Save the plot (optional)
    plt.savefig(f"{filename.split('.')[0]}_plot.png", dpi=300, bbox_inches='tight')
    
    # Show the plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Check if a filename was provided as a command line argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # Ask the user for the filename
        filename = input("Enter the CSV data filename: ")
    
    plot_daq_data(filename)