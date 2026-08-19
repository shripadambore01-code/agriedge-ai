"""
Dual-Brain Decision Router
Directs queries between Local Offline LLM and Google Gemini API based on mode and connectivity.
"""

from typing import Dict, Any
from gemini.connectivity import check_internet_connection
from gemini.client import GeminiAgriClient
from llm.local_llm import LocalAgriLLM

class AgriBrainRouter:
    def __init__(self, local_llm: LocalAgriLLM, gemini_client: GeminiAgriClient, default_mode: str = "auto"):
        self.local_llm = local_llm
        self.gemini_client = gemini_client
        self.mode = default_mode.lower()

    def set_mode(self, mode: str):
        if mode.lower() in ["off", "auto", "on"]:
            self.mode = mode.lower()

    def process_query(self, user_query: str, rag_result: Dict[str, Any], override_mode: str = None) -> Dict[str, Any]:
        """
        Orchestrates RAG context through the optimal brain.
        """
        current_mode = (override_mode or self.mode).lower()
        rag_context = rag_result.get("context", "")
        rag_confidence = rag_result.get("confidence", 0.0)

        # 1. PURE OFFLINE MODE ("off")
        if current_mode == "off":
            result = self.local_llm.generate(user_query, rag_context)
            result["mode"] = "off (Forced Offline)"
            result["internet_available"] = False
            return result

        # Check internet connectivity & Gemini configuration
        has_internet = check_internet_connection()
        gemini_ready = self.gemini_client.is_configured()

        # 2. ONLINE PRIORITY MODE ("on")
        if current_mode == "on":
            if has_internet and gemini_ready:
                try:
                    result = self.gemini_client.generate(user_query, rag_context)
                    result["mode"] = "on (Online Priority)"
                    result["internet_available"] = True
                    return result
                except Exception as e:
                    print(f"?? Gemini API failed ({e}), falling back to Local Offline Brain.")

            # Graceful offline fallback
            result = self.local_llm.generate(user_query, rag_context)
            result["mode"] = "on (Fallback to Local - Offline/Unreachable)"
            result["internet_available"] = has_internet
            return result

        # 3. HYBRID / AUTO MODE ("auto")
        # Heuristic: If RAG confidence is low (< 0.5) or query is long/complex, and online -> consult Gemini
        needs_cloud_boost = (rag_confidence < 0.5) or (len(user_query.split()) > 18)
        
        if needs_cloud_boost and has_internet and gemini_ready:
            try:
                result = self.gemini_client.generate(user_query, rag_context)
                result["mode"] = "auto (Smart Cloud Boost Activated)"
                result["internet_available"] = True
                return result
            except Exception as e:
                print(f"?? Smart Cloud Boost failed ({e}), using Local Offline Brain.")

        # Default standard path is always local offline model
        result = self.local_llm.generate(user_query, rag_context)
        result["mode"] = "auto (Local Reasoning Sufficient)"
        result["internet_available"] = has_internet
        return result
