import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env')
import time
import json
import logging
import aiosqlite
import asyncio
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)

class DossierGenerator:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.model = os.environ.get("LLM_MODEL", "gemini-2.5-flash")
        self.fallback_models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
        db_path = os.environ.get("SQLITE_DB_PATH", "/data/phantasm.db")
        if db_path.startswith("/data"):
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            db_path = os.path.join(project_root, "data", "phantasm.db")
        self.db_path = db_path
        self.template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        os.makedirs(self.output_dir, exist_ok=True)

    async def _fetch_session_data(self, session_id: str) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT session_pk, duration_seconds, total_commands FROM sessions WHERE session_id = ?", (session_id,))
            session_row = await cursor.fetchone()
            if not session_row:
                raise ValueError(f"Session {session_id} not found")
            
            session_pk = session_row[0]
            duration = session_row[1] or 0
            total_cmds = session_row[2] or 0
            
            cursor = await db.execute("SELECT expertise_level, primary_objective, operational_state FROM operator_profiles WHERE session_fk = ? ORDER BY profile_pk DESC LIMIT 1", (session_pk,))
            prof_row = await cursor.fetchone()
            
            expertise = prof_row[0] if prof_row and prof_row[0] else "Unknown"
            objective = prof_row[1] if prof_row and prof_row[1] else "Unknown"  
            state = prof_row[2] if prof_row and prof_row[2] else "Unknown"

            return {
                "session_pk": session_pk,
                "session_id": session_id,
                "duration": duration,
                "total_commands": total_cmds,
                "expertise": expertise,
                "objective": objective,
                "state": state,
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }

    def _generate_fallback_narrative(self, data: dict) -> str:
        return (
            f"CERT-In THREAT INTELLIGENCE DOSSIER\n"
            f"Session Identifier: {data.get('session_id')}\n"
            f"Infrastructure: PHANTASM Honeypot Array\n\n"
            f"1. THREAT VECTOR & BEHAVIORAL ASSESSMENT:\n"
            f"During engagement window {data.get('generated_at')}, the threat actor executed an interactive session lasting "
            f"{data.get('duration')} seconds, running {data.get('total_commands')} commands. The operator's expertise level is classified "
            f"as '{data.get('expertise')}' with primary objective '{data.get('objective')}'. Operational state during engagement: '{data.get('state')}'.\n\n"
            f"2. IMPACT & VULNERABILITY SURFACE:\n"
            f"Reconnaissance activities targeted synthetic subnet endpoints. Host interactions triggered dynamic ShadowMesh isolation layer protocols, preventing lateral movement into corporate subnets.\n\n"
            f"3. ACTIONABLE COUNTERMEASURES & REMEDIATION PLAN:\n"
            f"- Immediate Containment: Terminate session {data.get('session_id')} ingress sockets, flush transient honeypot buffers, and rotate ingress IP address bindings.\n"
            f"- Identity & Credential Protection: Revoke and regenerate queried Active Directory kerberos ticket hashes and synthetic user credentials.\n"
            f"- Network & Perimeter Defense: Apply strict NFQueue iptables filtering rules and trigger proactive ShadowMesh topology graph mutations.\n"
            f"- CERT-In Advisory Alignment: Log threat telemetry under TLP:AMBER classification and dispatch IOC payload hashes to central threat intelligence feeds."
        )

    async def _call_llm(self, prompt: str, data: dict) -> str:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            logger.warning("No GEMINI_API_KEY found, using rule-based narrative.")
            return self._generate_fallback_narrative(data)
        
        models_to_try = [os.environ.get("LLM_MODEL", "gemini-2.5-flash")] + self.fallback_models
        models_to_try = list(dict.fromkeys(models_to_try))
        
        system_prompt = (
            "You are a senior CERT-In cyber threat intelligence analyst producing an executive cybersecurity threat dossier. "
            "Analyze the provided PHANTASM honeypot session data and structure your formal report strictly into the following distinct sections:\n\n"
            "1. THREAT VECTOR & BEHAVIORAL ASSESSMENT:\n"
            "Analyze the adversary's tactics, techniques, and procedures (TTPs) based on session duration, command volume, assessed expertise, and operational state.\n\n"
            "2. IMPACT & VULNERABILITY SURFACE:\n"
            "Evaluate potential risks, exposure surface across synthetic subnets, and compromised honeypot assets.\n\n"
            "3. ACTIONABLE COUNTERMEASURES & REMEDIATION PLAN:\n"
            "- Immediate Containment: Subnet isolation, active socket teardown, and honeypot IP address rotation.\n"
            "- Identity & Credential Protection: Revoking and rotating compromised Active Directory synthetic credentials.\n"
            "- Network & Perimeter Defense: Updating NFQueue packet filtering rules and executing dynamic ShadowMesh topology mutations.\n"
            "- CERT-In Advisory Alignment: Incident classification guidelines (TLP:AMBER) and automated IOC sharing guidelines."
        )
        
        try:
            genai.configure(api_key=api_key)
            for model_name in models_to_try:
                logger.info(f"Calling Gemini with model: {model_name}")
                try:
                    model = genai.GenerativeModel(model_name, system_instruction=system_prompt)
                    response = await asyncio.to_thread(model.generate_content, prompt)
                    if response and response.text:
                        return response.text
                except Exception as e:
                    logger.error(f"Gemini API exception with model {model_name}: {e}")
        except Exception as genai_err:
            logger.error(f"Failed to configure Gemini API: {genai_err}")

        logger.info("Falling back to rule-based threat narrative generation.")
        return self._generate_fallback_narrative(data)

    async def generate_dossier(self, session_id: str) -> dict:
        start_t = time.time()
        data = await self._fetch_session_data(session_id)
        
        prompt = (
            f"Analyze this PHANTASM session data and generate a detailed CERT-In threat intelligence report: {json.dumps(data)}\n"
            f"Cover Threat Vector & Behavioral Assessment, Impact & Vulnerability Surface, and Actionable Countermeasures & Remediation Plan."
        )
        narrative = await self._call_llm(prompt, data)
        data["narrative"] = narrative

        # Render PDF with ReportLab
        pdf_path = os.path.join(self.output_dir, f"{session_id}_dossier.pdf")
        json_path = os.path.join(self.output_dir, f"{session_id}_dossier.json")
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(Paragraph(f"PHANTASM Session Dossier: {session_id}", styles['Heading1']))
        story.append(Spacer(1, 12))
        
        # Metadata Table
        metadata = [
            ["Session ID", session_id],
            ["Generated At", data["generated_at"]],
            ["Duration (s)", str(data["duration"])],
            ["Total Commands", str(data["total_commands"])],
            ["Expertise Level", data["expertise"]],
            ["Primary Objective", data["objective"]],
            ["Operational State", data["state"]]
        ]
        t = Table(metadata)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (1, 0), (1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # Classification
        story.append(Paragraph("Classification & Assessment", styles['Heading2']))
        story.append(Paragraph(f"Expertise: {data['expertise']} | Objective: {data['objective']} | State: {data['state']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Narrative
        story.append(Paragraph("Threat Narrative", styles['Heading2']))
        story.append(Paragraph(narrative.replace('\n', '<br/>'), styles['Normal']))
        
        doc.build(story)
        
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)

        data["pdf_path"] = pdf_path
        data["json_path"] = json_path

        # Insert dossier into database
        gen_duration = time.time() - start_t
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO dossiers 
                (session_fk, generated_at, generation_duration_s, generation_method, session_id_ref, dossier_full_json, narrative_text, pdf_path)
                VALUES (?, datetime('now'), ?, 'hybrid_llm', ?, ?, ?, ?)
                """,
                (data["session_pk"], gen_duration, session_id, json.dumps(data), narrative, pdf_path)
            )
            await db.execute(
                "UPDATE sessions SET dossier_generated = 1, dossier_path = ?, dossier_json_path = ? WHERE session_pk = ?",
                (pdf_path, json_path, data["session_pk"])
            )
            await db.commit()

        return data
