import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def apply_lowpass_filter(data, fs):
    """Apply a 4-pole low-pass Butterworth filter with 5Hz cutoff"""
    cutoff_freq = 2.0
    filter_order = 8
   
    nyquist = 0.5 * fs
    normal_cutoff = cutoff_freq / nyquist
   
    b, a = signal.butter(filter_order, normal_cutoff, btype='low', analog=False)
    filtered_data = signal.filtfilt(b, a, data)
   
    return filtered_data

def plot_frequency_response(fs=500):
    """
    Plot the frequency response of the filter
    
    Parameters:
    fs : float
        Sampling frequency in Hz
    """
    # Calculate filter coefficients
    cutoff_freq = 2.0
    filter_order = 4
   
    nyquist = 0.5 * fs
    normal_cutoff = cutoff_freq / nyquist
   
    b, a = signal.butter(filter_order, normal_cutoff, btype='low', analog=False)
    
    # Calculate frequency response
    w, h = signal.freqz(b, a, worN=8000)
    
    # Convert frequency to Hz
    frequencies = w * fs / (2 * np.pi)
    
    # Create a new figure with two subplots
    plt.figure(figsize=(12, 8))
    
    # First subplot: Magnitude response
    plt.subplot(2, 1, 1)
    plt.semilogx(frequencies, 20 * np.log10(abs(h)), 'b')
    plt.axvline(cutoff_freq, color='red', linestyle='--', alpha=0.7)
    plt.axhline(-3, color='green', linestyle='--', alpha=0.7)
    
    # Highlight the roll-off rate
    decade_start = cutoff_freq * 2
    decade_end = decade_start * 5
    
    # Find the response at these points
    idx_start = np.argmin(np.abs(frequencies - decade_start))
    idx_end = np.argmin(np.abs(frequencies - decade_end))
    
    gain_start = 20 * np.log10(abs(h[idx_start]))
    gain_end = 20 * np.log10(abs(h[idx_end]))
    
    # Calculate actual roll-off rate
    rolloff_rate = (gain_end - gain_start) / np.log10(decade_end / decade_start)
    
    plt.plot([decade_start, decade_end], [gain_start, gain_end], 'r-', linewidth=2)
    plt.text(decade_start * 1.5, (gain_start + gain_end) / 2, 
             f'{rolloff_rate:.1f} dB/decade\n(expected: -80 dB/decade)',
             verticalalignment='center')
    
    plt.title('Magnitude Response')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.xlim([0.1, fs/2])
    plt.ylim([-100, 5])
    
    # Add a note about filtfilt vs filter
    plt.figtext(0.5, 0.01, 
                'Note: The actual implementation uses filtfilt() which applies the filter twice,\n'
                'effectively doubling the filter order. This affects the transition steepness and phase response.',
                ha='center', fontsize=10, bbox=dict(facecolor='yellow', alpha=0.2))
    
    # Annotate the -3dB cutoff point
    cutoff_idx = np.argmin(np.abs(frequencies - cutoff_freq))
    cutoff_gain = 20 * np.log10(abs(h[cutoff_idx]))
    plt.annotate(f'Cutoff: {cutoff_freq} Hz ({cutoff_gain:.1f} dB)', 
                 xy=(cutoff_freq, cutoff_gain),
                 xytext=(cutoff_freq * 0.7, cutoff_gain - 10),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=6))
    
    # Second subplot: Phase response
    plt.subplot(2, 1, 2)
    plt.semilogx(frequencies, np.unwrap(np.angle(h)) * 180 / np.pi, 'g')
    plt.axvline(cutoff_freq, color='red', linestyle='--', alpha=0.7)
    plt.title('Phase Response')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Phase (degrees)')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.xlim([0.1, fs/2])
    
    # Add text about filtfilt and phase
    plt.text(0.2, -160, 
             "filtfilt() provides zero phase distortion\n"
             "by applying the filter forward and backward",
             fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
    
    # Add a legend for both plots
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    
    # Add overall title
    plt.suptitle(f'Frequency Response of 4-pole Butterworth Low-Pass Filter\n'
                 f'(Cutoff: {cutoff_freq} Hz, Order: {filter_order}, Fs: {fs} Hz)', 
                 fontsize=14)
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.show()
    
    # Print some numerical data
    print(f"Filter Specifications:")
    print(f"  - Type: Butterworth low-pass")
    print(f"  - Order: {filter_order} (poles)")
    print(f"  - Cutoff frequency: {cutoff_freq} Hz")
    print(f"  - Sampling frequency: {fs} Hz")
    print(f"  - Normalized cutoff: {normal_cutoff:.6f}")
    print(f"  - Theoretical roll-off: {-20*filter_order} dB/decade")
    print(f"  - Measured roll-off (in transition band): {rolloff_rate:.1f} dB/decade")
    
    # Additional info about filtfilt vs filter
    print("\nNote on filtfilt():")
    print("  - The scipy.signal.filtfilt() function applies the filter twice (forward and backward)")
    print("  - This effectively doubles the filter order in terms of magnitude response")
    print("  - It provides zero phase distortion (unlike regular filtering)")
    print("  - The roll-off rate can appear steeper than expected due to this double application")

if __name__ == "__main__":
    # You can modify the sampling frequency here
    sampling_frequency = 500  # Hz
    plot_frequency_response(fs=sampling_frequency)
    
    # Optionally: Show how different sampling frequencies affect the filter
    print("\n\nDemonstrating effect of different sampling frequencies:")
    for test_fs in [100, 500, 1000]:
        cutoff = 2.0
        nyquist = 0.5 * test_fs
        normal_cutoff = cutoff / nyquist
        print(f"For sampling frequency = {test_fs} Hz:")
        print(f"  - Nyquist frequency = {nyquist} Hz")
        print(f"  - Normalized cutoff = {normal_cutoff:.6f}")
        if normal_cutoff >= 1:
            print("  - WARNING: Normalized cutoff >= 1.0, filter will not work correctly!")
        print("")