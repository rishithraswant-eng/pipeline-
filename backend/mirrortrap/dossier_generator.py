import os
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
        self.model = os.environ.get("LLM_MODEL", "gemini-3.6-flash")
        self.fallback_model = "gemini-2.5-flash"
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
            
            session_pk, duration, total_cmds = session_row
            
            cursor = await db.execute("SELECT expertise_level, primary_objective, operational_state FROM operator_profiles WHERE session_fk = ? ORDER BY profile_pk DESC LIMIT 1", (session_pk,))
            prof_row = await cursor.fetchone()
            if prof_row:
                expertise, objective, state = prof_row
            else:
                expertise, objective, state = "Unknown", "Unknown", "Unknown"

            return {
                "session_id": session_id,
                "duration": duration,
                "total_commands": total_cmds,
                "expertise": expertise,
                "objective": objective,
                "state": state,
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }

    async def _call_llm(self, prompt: str) -> str:
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY found, using dummy narrative.")
            return "Dummy narrative due to missing API key."

        genai.configure(api_key=self.api_key)
        system_prompt = "You are a senior CERT-In threat analyst. Write a 400-word formal narrative."
        
        try:
            model = genai.GenerativeModel(self.model, system_instruction=system_prompt)
            response = await asyncio.to_thread(model.generate_content, prompt)
            return response.text
        except Exception as e:
            error_text = str(e).lower()
            if "not found" in error_text or "invalid model" in error_text:
                logger.warning(f"Model {self.model} rejected. Falling back to {self.fallback_model}")
                try:
                    fallback = genai.GenerativeModel(self.fallback_model, system_instruction=system_prompt)
                    response = await asyncio.to_thread(fallback.generate_content, prompt)
                    return response.text
                except Exception as fallback_e:
                    logger.error(f"Gemini fallback error: {fallback_e}")
                    return "Error generating narrative."
            logger.error(f"Gemini API exception: {e}")
            return "Error generating narrative."

    async def generate_dossier(self, session_id: str) -> dict:
        data = await self._fetch_session_data(session_id)
        
        prompt = f"Analyze this PHANTASM session data and produce a 400-word narrative: {json.dumps(data)}"
        narrative = await self._call_llm(prompt)
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
        return data
