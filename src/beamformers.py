import numpy as np
import scipy.linalg as la

class BeamformerEngine:
    """Spatial Filtering and Equalization Algorithms."""
    
    @staticmethod
    def delay_and_sum(steering_vector):
        """Conventional Phase-Shift Beamformer."""
        return steering_vector / np.vdot(steering_vector, steering_vector)

    @staticmethod
    def mvdr(covariance_matrix, steering_vector, diagonal_loading=1e-3):
        """Minimum Variance Distortionless Response (Capon) Beamformer."""
        N = covariance_matrix.shape[0]
        R = covariance_matrix + diagonal_loading * np.eye(N)
        R_inv = la.inv(R)
        
        num = R_inv @ steering_vector
        den = np.vdot(steering_vector, num)
        return num / den

    @staticmethod
    def equalize_signal(s_hat, s_ref_pilots):
        """Scalar MMSE equalizer for phase and gain alignment."""
        N_pilots = len(s_ref_pilots)
        g = np.vdot(s_hat[:N_pilots], s_ref_pilots) / np.vdot(s_hat[:N_pilots], s_hat[:N_pilots])
        return s_hat * g