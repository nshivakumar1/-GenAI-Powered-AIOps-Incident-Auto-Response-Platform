import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger()

class GeminiClient:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. AI Analysis will be mocked.")
            
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')

    def analyze_incident(self, logs: str, context: dict = None) -> dict:
        """
        Analyzes logs and context to determine root cause and severity.
        """
        if not self.api_key:
            return self._mock_response()

        prompt = f"""
        You are an expert Site Reliability Engineer (SRE) AI.
        
        Analyze the following application logs and system context to determine the root cause of the incident.
        
        Context: {json.dumps(context) if context else 'N/A'}
        Logs:
        {logs[:2000]}  # Truncate to avoid token limits if necessary
        
        Return your analysis in strictly VALID JSON format with no markdown formatting. The JSON must have these keys:
        - root_cause: (string) A concise technical explanation.
        - severity: (string) "P1" (Critical), "P2" (High), "P3" (Medium).
        - category: (string) "database", "network", "application", "security".
        - suggested_fix: (string) A specific actionable command or step.
        - auto_remediate: (boolean) true if it can be safely fixed automatically (e.g. restart), false otherwise.
        - remediation_action: (string) One of ["restart_service", "scale_up", "clear_cache", "none"].
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Cleanup markdown code blocks if Gemini returns them
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return self._mock_response(error=str(e))

    def _mock_response(self, error=None) -> dict:
        """Fallback response if API fails or key is missing."""
        return {
            "root_cause": f"Simulated Analysis (Gemini Offline). Error: {error}",
            "severity": "P2",
            "category": "application",
            "suggested_fix": "Check Logs Manually",
            "auto_remediate": False,
            "remediation_action": "none"
        }
