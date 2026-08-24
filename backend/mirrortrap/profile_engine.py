import time
import json
import numpy as np
import aiosqlite
import os
from typing import Dict, Any

from .classifier import ExpertiseClassifier
from .attck_mapper import ATTCKMapper
from .stress_detector import StressDetector
from .session_manager import SessionManager

class ProfileEngine:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.classifier = ExpertiseClassifier()
        self.attck_mapper = ATTCKMapper()
        self.stress_detector = StressDetector()
        db_path = os.environ.get("SQLITE_DB_PATH", "/data/phantasm.db")
        if db_path.startswith("/data"):
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            db_path = os.path.join(project_root, "data", "phantasm.db")
        self.db_path = db_path

    async def process_command(self, session_id: str, command_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a new command event, updates the session profile, 
        persists to DB, and returns the updated profile.
        """
        self.session_manager.add_command(session_id, command_event)
        session = self.session_manager.get_session(session_id)
        
        raw_cmd = command_event.get("raw_command", "")
        
        # 1. Classification
        class_res = self.classifier.classify_command(raw_cmd)
        
        # 2. ATT&CK Mapping
        techniques = self.attck_mapper.map_command(raw_cmd)
        for t in techniques:
            if t not in session["profile"]["unique_techniques"]:
                session["profile"]["unique_techniques"].append(t)
            session["profile"]["technique_confidences"].append(class_res["confidence"])
            
        # 3. Stress Detection
        ici_history = session.get("ici_history", [])
        state = self.stress_detector.detect_state(ici_history)
        
        # 4. Engagement Score Calculation
        # (unique_techniques * 15) + (technique_confidence_avg * 30) + (dwell_minutes * 2), capped at 100
        unique_t_count = len(session["profile"]["unique_techniques"])
        conf_avg = float(np.mean(session["profile"]["technique_confidences"])) if session["profile"]["technique_confidences"] else 0.0
        dwell_minutes = (time.time() - session["start_time"]) / 60.0
        
        engagement_score = min(100.0, (unique_t_count * 15) + (conf_avg * 30) + (dwell_minutes * 2))
        
        # Determine objective (simplified for Phase 3 heuristic)
        primary_objective = "exploratory"
        if "T1490" in techniques or "T1486" in techniques:
            primary_objective = "ransomware"
        elif "T1003" in techniques:
            primary_objective = "credential_harvest"
        
        # Build profile update
        profile_update = {
            "expertise_level": class_res["expertise_level"],
            "expertise_confidence": class_res["confidence"],
            "primary_objective": primary_objective,
            "objective_confidence": 0.8,
            "operational_state": state,
            "engagement_score": round(engagement_score, 2)
        }
        self.session_manager.update_profile(session_id, profile_update)
        
        # Format for DB writing
        prof = session["profile"]
        elapsed_s = int(time.time() - session["start_time"])
        
        async with aiosqlite.connect(self.db_path) as db:
            # Get session pk
            cursor = await db.execute("SELECT session_pk FROM sessions WHERE session_id = ?", (session_id,))
            row = await cursor.fetchone()
            if not row:
                raise ValueError(f"Session {session_id} not found in DB")
            session_fk = row[0]
            
            # Write to operator_profiles
            await db.execute('''
                INSERT INTO operator_profiles (
                    session_fk, snapshot_at, session_elapsed_s, command_count_at_snapshot,
                    expertise_level, expertise_confidence, primary_objective, objective_confidence,
                    operational_state, engagement_score_at_snapshot
                ) VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_fk, elapsed_s, prof["total_commands"],
                prof["expertise_level"], prof["expertise_confidence"],
                prof["primary_objective"], prof["objective_confidence"],
                prof["operational_state"], prof["engagement_score"]
            ))
            
            # Update sessions table
            await db.execute('''
                UPDATE sessions 
                SET total_commands = ?, unique_techniques = ?, engagement_score = ?
                WHERE session_pk = ?
            ''', (
                prof["total_commands"], unique_t_count, prof["engagement_score"], session_fk
            ))
            await db.commit()
            
        return prof
