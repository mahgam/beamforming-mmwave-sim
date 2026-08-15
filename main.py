import numpy as np
import matplotlib.pyplot as plt

from src.array_models import UniformLinearArray
from src.beamformers import BeamformerEngine

def run_simulation():
    np.random.seed(42)
    
    # 1. System Parameters
    NUM_ELEMENTS = 16
    FREQ = 28e9         # 28 GHz
    NUM_SAMPLES = 2000
    SNR_DB = 10         # Target signal SNR (+10 dB)
    INR_DB = 5          # Moderate interferer (+5 dB)
    
    THETA_SOI = 15.0    # Target angle (+15°)
    THETA_INT = -30.0   # Interferer angle (-30°)
    
    # 2. Setup Array and Vectors
    array = UniformLinearArray(num_elements=NUM_ELEMENTS, freq=FREQ)
    a_soi = array.steering_vector(THETA_SOI)
    a_int = array.steering_vector(THETA_INT)
    
    # 3. Synthesize Ideal QPSK Symbols
    bits_soi = np.random.randint(0, 2, (NUM_SAMPLES, 2))
    s_soi_ideal = ((2 * bits_soi[:, 0] - 1) + 1j * (2 * bits_soi[:, 1] - 1)) / np.sqrt(2)
    
    bits_int = np.random.randint(0, 2, (NUM_SAMPLES, 2))
    s_int_ideal = ((2 * bits_int[:, 0] - 1) + 1j * (2 * bits_int[:, 1] - 1)) / np.sqrt(2)
    
    # Scale power based on SNR/INR
    s_soi = s_soi_ideal * np.sqrt(10 ** (SNR_DB / 10))
    s_int = s_int_ideal * np.sqrt(10 ** (INR_DB / 10))
    
    # 4. Synthesize Received Signal Matrix X
    noise = (np.random.randn(NUM_ELEMENTS, NUM_SAMPLES) + 
             1j * np.random.randn(NUM_ELEMENTS, NUM_SAMPLES)) / np.sqrt(2)
    
    X = a_soi @ s_soi.reshape(1, -1) + a_int @ s_int.reshape(1, -1) + noise
    
    # 5. Covariance Estimation & Beamforming
    R_xx = (X @ X.conj().T) / NUM_SAMPLES
    w_das = BeamformerEngine.delay_and_sum(a_soi)
    w_mvdr = BeamformerEngine.mvdr(R_xx, a_soi)
    
    s_hat_das_raw = (w_das.conj().T @ X).flatten()
    s_hat_mvdr_raw = (w_mvdr.conj().T @ X).flatten()
    
    # 6. Equalization
    PILOT_LEN = 100
    s_recovered_das = BeamformerEngine.equalize_signal(s_hat_das_raw, s_soi_ideal[:PILOT_LEN])
    s_recovered_mvdr = BeamformerEngine.equalize_signal(s_hat_mvdr_raw, s_soi_ideal[:PILOT_LEN])
    
    # Calculate BER for MVDR
    bits_detected_I = (s_recovered_mvdr.real > 0).astype(int)
    bits_detected_Q = (s_recovered_mvdr.imag > 0).astype(int)
    bits_detected = np.column_stack((bits_detected_I, bits_detected_Q))
    ber = np.sum(bits_soi != bits_detected) / (NUM_SAMPLES * 2)
    
    print("--- Beamformer Execution Complete ---")
    print(f"Target Angle: {THETA_SOI}° | Interferer Angle: {THETA_INT}°")
    print(f"MVDR Recovered BER: {ber * 100:.2f}%")

    # 7. Visualization
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Subplot 1: Spatial Beampattern
    theta_scan = np.linspace(-90, 90, 361)
    pattern_mvdr = [np.abs(w_mvdr.conj().T @ array.steering_vector(a))[0, 0] ** 2 for a in theta_scan]
    pattern_mvdr_db = 10 * np.log10(np.array(pattern_mvdr) / np.max(pattern_mvdr))
    
    axes[0].plot(theta_scan, pattern_mvdr_db, color="blue", label="MVDR Pattern")
    axes[0].axvline(THETA_SOI, color="green", linestyle=":", label=f"SOI ({THETA_SOI}°)")
    axes[0].axvline(THETA_INT, color="red", linestyle=":", label=f"Interferer ({THETA_INT}°)")
    axes[0].set_title("Spatial Radiation Pattern")
    axes[0].set_xlabel("Angle θ (deg)")
    axes[0].set_ylabel("Gain (dB)")
    axes[0].grid(True, linestyle=":", alpha=0.6)
    axes[0].legend()

    # Subplot 2: Constellation Recovery
    axes[1].scatter(s_recovered_mvdr[:500].real, s_recovered_mvdr[:500].imag, alpha=0.6, color="blue", label="Recovered")
    axes[1].scatter(s_soi_ideal[:4].real, s_soi_ideal[:4].imag, color="red", marker="x", s=80, linewidths=2, label="Ideal")
    axes[1].set_title(f"Equalized Constellation (BER = {ber*100:.2f}%)")
    axes[1].set_xlabel("In-Phase (I)")
    axes[1].set_ylabel("Quadrature (Q)")
    axes[1].grid(True, linestyle=":", alpha=0.6)
    axes[1].legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_simulation()