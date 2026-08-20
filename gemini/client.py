"""
Google Gemini API Client (Online Smart Brain)
Used optionally for complex queries when internet and API key are available.
"""

import os
from typing import Dict, Any, Optional

class GeminiAgriClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initializes the Gemini API client safely if API key is provided."""
        if not self.api_key or "your_gemini_api_key" in self.api_key:
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.sdk_type = "google-genai"
        except ImportError:
            try:
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=self.api_key)
                self.client = genai_legacy.GenerativeModel("gemini-1.5-flash")
                self.sdk_type = "google-generativeai"
            except ImportError:
                self.client = None
                self.sdk_type = None

    def is_configured(self) -> bool:
        return bool(self.api_key and "your_gemini_api_key" not in self.api_key)

    def generate(self, user_query: str, rag_context: str) -> Dict[str, Any]:
        """
        Sends the user question + RAG context to Gemini API.
        """
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is not configured or invalid.")

        prompt = (
            "You are AgriVoice, an expert agricultural advisor assisting a farmer. "
            "Provide helpful, concise, practical, and clear advice. "
            "Use the provided local agricultural context to ground your answer.\n\n"
            f"LOCAL AGRICULTURAL CONTEXT:\n{rag_context}\n\n"
            f"FARMER QUESTION:\n{user_query}\n\n"
            "ADVICE:"
        )

        try:
            if hasattr(self, "sdk_type") and self.sdk_type == "google-genai" and self.client:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                answer = response.text
            elif hasattr(self, "sdk_type") and self.sdk_type == "google-generativeai" and self.client:
                response = self.client.generate_content(prompt)
                answer = response.text
            else:
                # Direct REST fallback using requests if SDK not installed yet
                import requests
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                res = requests.post(url, json=payload, timeout=10)
                res.raise_json = res.json()
                answer = res.raise_json["candidates"][0]["content"]["parts"][0]["text"]

            return {
                "answer": answer.strip(),
                "brain": "Google Gemini API (Online Smart Mode)",
                "offline": False
            }
        except Exception as e:
            raise RuntimeError(f"Gemini API request failed: {e}")
