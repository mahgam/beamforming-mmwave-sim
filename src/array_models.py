import numpy as np

class UniformLinearArray:
    """1D Uniform Linear Array (ULA) operating at mmWave frequencies."""
    
    def __init__(self, num_elements=16, freq=28e9, element_spacing_ratio=0.5):
        self.N = num_elements
        self.freq = freq
        self.c = 3e8  # Speed of light (m/s)
        self.wavelength = self.c / self.freq
        self.d = element_spacing_ratio * self.wavelength
        self.element_positions = np.arange(self.N) * self.d

    def steering_vector(self, theta_deg):
        """Computes normalized array steering vector a(theta)."""
        theta_rad = np.radians(theta_deg)
        k = 2 * np.pi / self.wavelength
        phase_shifts = k * self.element_positions * np.sin(theta_rad)
        a = np.exp(-1j * phase_shifts).reshape(-1, 1)
        return a / np.sqrt(self.N)