import numpy as np
from typing import List

class StressDetector:
    """
    ICI Stress State Machine based on TRD Phase 3 thresholds.
    """
    def __init__(self):
        pass

    def detect_state(self, ici_history: List[int]) -> str:
        """
        Takes a list of Inter-Command Intervals (in ms) and returns the state string.
        Uses exact thresholds from TRD section 9 for Phase 3.
        """
        if len(ici_history) < 20:
            return "exploratory" # Need at least 20 commands before state changes

        window = ici_history[-20:]
        mean_ici = float(np.mean(window))
        std_dev = float(np.std(window))

        if mean_ici < 500:
            return "automated"
        elif std_dev > 3000:
            return "disoriented"
        elif mean_ici < 2000 and std_dev > 800:
            return "stressed"
        elif 2000 <= mean_ici <= 8000 and std_dev < 1000:
            return "methodical"
        else:
            return "exploratory"
