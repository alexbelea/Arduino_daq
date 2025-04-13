import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def apply_lowpass_filter(data, fs):
    """Apply a 4-pole low-pass Butterworth filter with 5Hz cutoff"""
    cutoff_freq = 2.0
    filter_order = 4
   
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
    
    # # Add a note about filtfilt vs filter
    # plt.figtext(0.5, 0.01, 
    #             'Note: The actual implementation uses filtfilt() which applies the filter twice,\n'
    #             'effectively doubling the filter order. This affects the transition steepness and phase response.',
    #             ha='center', fontsize=10, bbox=dict(facecolor='yellow', alpha=0.2))
    
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

def compare_lfilter_vs_filtfilt(fs=500):
    """
    Compare the frequency response of lfilter vs filtfilt application
    
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
    
    # Calculate theoretical frequency response using freqz
    w, h_theory = signal.freqz(b, a, worN=8000)
    
    # Create a test signal with frequencies up to Nyquist
    t = np.linspace(0, 10, int(10 * fs), endpoint=False)  # 10 seconds of data
    
    # Create a frequency sweep signal (chirp)
    # Start at 0.1 Hz and go up to Nyquist frequency
    test_signal = signal.chirp(t, f0=0.1, f1=nyquist, t1=10, method='logarithmic')
    
    # Apply filters
    filtered_lfilter = signal.lfilter(b, a, test_signal)
    filtered_filtfilt = signal.filtfilt(b, a, test_signal)
    
    # Calculate FFTs
    n = len(test_signal)
    freqs = np.fft.rfftfreq(n, d=1/fs)
    
    # Need a window to reduce spectral leakage
    window = np.hanning(n)
    
    # Calculate FFTs with window
    fft_original = np.fft.rfft(test_signal * window)
    fft_lfilter = np.fft.rfft(filtered_lfilter * window)
    fft_filtfilt = np.fft.rfft(filtered_filtfilt * window)
    
    # Convert to dB (with small epsilon to avoid log(0))
    eps = 1e-10
    mag_original = 20 * np.log10(np.abs(fft_original) + eps)
    mag_lfilter = 20 * np.log10(np.abs(fft_lfilter) + eps)
    mag_filtfilt = 20 * np.log10(np.abs(fft_filtfilt) + eps)
    
    # Normalize magnitudes
    mag_original -= np.max(mag_original)
    mag_lfilter -= np.max(mag_original)
    mag_filtfilt -= np.max(mag_original)
    
    # Calculate phase responses
    phase_original = np.unwrap(np.angle(fft_original))
    phase_lfilter = np.unwrap(np.angle(fft_lfilter))
    phase_filtfilt = np.unwrap(np.angle(fft_filtfilt))
    
    # Convert to degrees
    phase_original = phase_original * 180 / np.pi
    phase_lfilter = phase_lfilter * 180 / np.pi
    phase_filtfilt = phase_filtfilt * 180 / np.pi
    
    # Create a new figure for comparison
    plt.figure(figsize=(14, 10))
    
    # Plot magnitude response
    plt.subplot(2, 1, 1)
    plt.semilogx(freqs, mag_original, 'k--', alpha=0.5, label='Original Signal')
    plt.semilogx(freqs, mag_lfilter, 'b-', label='lfilter() (single pass)')
    plt.semilogx(freqs, mag_filtfilt, 'r-', label='filtfilt() (forward & backward)')
    
    # Add theoretical response from freqz
    frequencies = w * fs / (2 * np.pi)
    mag_theory = 20 * np.log10(np.abs(h_theory))
    mag_theory -= np.max(mag_original)  # Normalize
    
    # Square the theoretical magnitude for filtfilt (twice the attenuation in dB)
    mag_theory_squared = 2 * mag_theory
    
    plt.semilogx(frequencies, mag_theory, 'g--', label='Theoretical (freqz)')
    plt.semilogx(frequencies, mag_theory_squared, 'm--', label='Theoretical squared (filtfilt)')
    
    plt.axvline(cutoff_freq, color='red', linestyle='--', alpha=0.7)
    plt.axhline(-3, color='green', linestyle='--', alpha=0.7)
    
    # Highlight the roll-off rates
    decade_start = cutoff_freq * 2
    decade_end = decade_start * 5
    
    # Find indices closest to these frequencies for lfilter
    idx_start_lf = np.argmin(np.abs(freqs - decade_start))
    idx_end_lf = np.argmin(np.abs(freqs - decade_end))
    
    # Measure roll-off rates
    if idx_start_lf < len(mag_lfilter) and idx_end_lf < len(mag_lfilter):
        gain_start_lf = mag_lfilter[idx_start_lf]
        gain_end_lf = mag_lfilter[idx_end_lf]
        
        gain_start_ff = mag_filtfilt[idx_start_lf]
        gain_end_ff = mag_filtfilt[idx_end_lf]
        
        # Calculate actual roll-off rates
        rolloff_rate_lf = (gain_end_lf - gain_start_lf) / np.log10(decade_end / decade_start)
        rolloff_rate_ff = (gain_end_ff - gain_start_ff) / np.log10(decade_end / decade_start)
        
        # Annotate roll-off rates
        plt.annotate(f'{rolloff_rate_lf:.1f} dB/decade', 
                     xy=(decade_start * 2, gain_start_lf - 10),
                     color='blue', fontsize=9)
        
        plt.annotate(f'{rolloff_rate_ff:.1f} dB/decade\n(~2x steeper)', 
                     xy=(decade_start * 2, gain_start_ff - 20),
                     color='red', fontsize=9)
    
    plt.title('Magnitude Response Comparison: lfilter() vs filtfilt()')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB, normalized)')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.xlim([0.1, fs/2])
    plt.ylim([-80, 5])
    plt.legend()
    
    # Plot phase response
    plt.subplot(2, 1, 2)
    plt.semilogx(freqs, phase_original, 'k--', alpha=0.5, label='Original Signal')
    plt.semilogx(freqs, phase_lfilter, 'b-', label='lfilter() (single pass)')
    plt.semilogx(freqs, phase_filtfilt, 'r-', label='filtfilt() (forward & backward)')
    
    # Add theoretical phase from freqz
    phase_theory = np.unwrap(np.angle(h_theory)) * 180 / np.pi
    plt.semilogx(frequencies, phase_theory, 'g--', label='Theoretical (freqz)')
    
    # Add vertical line at cutoff frequency
    plt.axvline(cutoff_freq, color='red', linestyle='--', alpha=0.7)
    
    plt.title('Phase Response Comparison: lfilter() vs filtfilt()')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Phase (degrees)')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.xlim([0.1, fs/2])
    plt.legend()
    
    # Add explanatory text
    plt.figtext(0.5, 0.01, 
                'filtfilt() applies the filter twice (forward and backward),\n'
                'which doubles the magnitude roll-off but produces zero phase distortion.',
                ha='center', fontsize=11, bbox=dict(facecolor='yellow', alpha=0.2))
    
    plt.suptitle(f'Comparison of lfilter() vs filtfilt() on 4-pole Butterworth Filter\n'
                 f'(Cutoff: {cutoff_freq} Hz, Order: {filter_order}, Fs: {fs} Hz)', 
                 fontsize=14)
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.show()
    
    # Print comparison info
    print("\nComparison between lfilter() and filtfilt():")
    print("  - lfilter() applies the filter once, with expected roll-off rate")
    print(f"  - Measured lfilter() roll-off in transition band: {rolloff_rate_lf:.1f} dB/decade")
    print(f"  - Measured filtfilt() roll-off in transition band: {rolloff_rate_ff:.1f} dB/decade")
    print(f"  - Ratio: {rolloff_rate_ff/rolloff_rate_lf:.1f}x steeper with filtfilt()")
    print("  - lfilter() introduces phase distortion")
    print("  - filtfilt() maintains zero phase distortion")

if __name__ == "__main__":
    # You can modify the sampling frequency here
    sampling_frequency = 500  # Hz
    
    # Plot the standard frequency response
    plot_frequency_response(fs=sampling_frequency)
    
    # Plot the comparison between lfilter and filtfilt
    compare_lfilter_vs_filtfilt(fs=sampling_frequency)
    
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