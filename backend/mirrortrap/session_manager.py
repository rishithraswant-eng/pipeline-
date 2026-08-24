import time
from typing import Dict, Any, Optional

class SessionManager:
    """
    In-Memory Session Manager.
    Stores live session state (command list, ICI history, current profile) keyed by session_id.
    """
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    def create_session(self, session_id: str) -> None:
        self.active_sessions[session_id] = {
            "start_time": time.time(),
            "commands": [],
            "ici_history": [],
            "profile": {
                "expertise_level": "Script Kiddie",
                "expertise_confidence": 0.0,
                "primary_objective": "exploratory",
                "objective_confidence": 0.0,
                "operational_state": "exploratory",
                "engagement_score": 0.0,
                "total_commands": 0,
                "unique_techniques": [],
                "technique_confidences": []
            }
        }
        
    def end_session(self, session_id: str) -> None:
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["end_time"] = time.time()
            
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.active_sessions.get(session_id)
        
    def add_command(self, session_id: str, command: Dict[str, Any]) -> None:
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session["commands"].append(command)
            session["profile"]["total_commands"] += 1
            if "ici_ms" in command:
                session["ici_history"].append(command["ici_ms"])

    def update_profile(self, session_id: str, profile_update: Dict[str, Any]) -> None:
        if session_id in self.active_sessions:
            # We don't overwrite the whole dict, just update fields
            for k, v in profile_update.items():
                self.active_sessions[session_id]["profile"][k] = v
