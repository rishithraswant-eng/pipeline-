from typing import List

class ATTCKMapper:
    """
    Maps raw commands to MITRE ATT&CK technique IDs using exact TRD rules.
    """
    # Dictionary constant mapping TRD rules
    TECHNIQUE_MAP = {
        "nmap": "T1046",       # Network Service Discovery
        "mimikatz": "T1003",   # OS Credential Dumping
        "sekurlsa": "T1003",   # OS Credential Dumping
        "lsadump": "T1003",    # OS Credential Dumping
        "vssadmin": "T1490",   # Inhibit System Recovery
        "shadow": "T1490",     # Inhibit System Recovery
        "backup": "T1490",     # Inhibit System Recovery
        "encrypt": "T1486",    # Data Encrypted for Impact
        "schtasks": "T1053",   # Scheduled Task/Job
        "net use": "T1021",    # Remote Services
        "select": "T1005",     # Data from Local System (SQL query)
        "get-aduser": "T1087", # Account Discovery
        "curl": "T1105",       # Ingress Tool Transfer
        "dir": "T1083",        # File and Directory Discovery
        "ipconfig": "T1016",   # System Network Configuration Discovery
        "net": "T1087",        # Account Discovery
        "ping": "T1018",       # Remote System Discovery
    }

    def __init__(self):
        self.is_loaded = True

    def map_command(self, raw_command: str) -> List[str]:
        cmd = raw_command.lower()
        techniques = set()
        
        for keyword, technique_id in self.TECHNIQUE_MAP.items():
            if keyword in cmd:
                techniques.add(technique_id)
                
        # Default to a generic execution technique if no mapping found
        if not techniques:
            techniques.add("T1059") # Command and Scripting Interpreter
            
        return list(techniques)
