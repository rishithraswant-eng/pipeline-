import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ExpertiseClassifier:
    """
    Phase 3: Heuristic-based expertise classifier.
    In v2.0, this will be replaced by a fine-tuned DistilBERT model.
    """
    def __init__(self):
        # We simulate model loading by setting a flag
        # Dynamic download logic for DistilBERT/BERT is prepared in .gitignore but logic is in heuristics for Phase 3
        self.is_loaded = True
        logger.info("Loaded heuristic expertise classifier.")

    def classify_command(self, raw_command: str) -> Dict[str, Any]:
        """
        Mimics what the trained model will do using keyword scoring across 4 tiers.
        """
        cmd = raw_command.lower()
        score = 0
        
        # Complex operators
        if '|' in cmd: score += 5
        if '$(' in cmd or '`' in cmd: score += 10
        if '>' in cmd or '>>' in cmd: score += 3
        
        # Tool sophistication
        if any(x in cmd for x in ['net ', 'ipconfig', 'dir']):
            score += 0
        if any(x in cmd for x in ['nmap', 'mimikatz']):
            score += 20
        if any(x in cmd for x in ['cobaltstrike', 'powersploit', 'empire']):
            score += 30
            
        # Privilege escalation / encoding
        if 'base64' in cmd or '-enc' in cmd:
            score += 15

        if score < 15:
            level = "Script Kiddie"
            conf = 0.6 + (score / 100.0)
        elif score < 35:
            level = "Intermediate"
            conf = 0.6 + ((score - 15) / 100.0)
        elif score < 60:
            level = "Advanced"
            conf = 0.7 + ((score - 35) / 100.0)
        else:
            level = "APT"
            conf = 0.8 + min((score - 60) / 100.0, 0.19)
            
        return {
            "expertise_level": level,
            "confidence": round(min(conf, 0.99), 2),
            "heuristic_score": score
        }
