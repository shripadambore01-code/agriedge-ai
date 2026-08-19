"""
Agricultural Knowledge Base - Local Offline Vector Store & Retriever
Retrieves relevant farming practices, pest management, and crop advisories.
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

class AgriRAG:
    def __init__(self, data_path: str = None, persist_dir: str = None):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.data_path = Path(data_path) if data_path else self.base_dir / "rag" / "data" / "agri_knowledge.json"
        self.persist_dir = Path(persist_dir) if persist_dir else self.base_dir / "chroma_db"
        self.documents: List[Dict[str, Any]] = []
        self._load_local_data()

    def _load_local_data(self):
        """Loads structured JSON agricultural knowledge supporting UTF-8 BOM."""
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8-sig") as f:
                self.documents = json.load(f)
        else:
            self.documents = []

    def _normalize_text(self, text: str) -> str:
        """Removes punctuation and normalizes whitespace."""
        return re.sub(r"[^a-zA-Z0-9\s]", " ", text).lower()

    def retrieve(self, query: str, top_k: int = 2) -> Dict[str, Any]:
        """
        Offline retrieval mechanism.
        Uses keyword-weighted relevance and semantic scoring across farming knowledge items.
        """
        if not self.documents:
            self._load_local_data()
            if not self.documents:
                return {"context": "", "documents": [], "confidence": 0.0}

        clean_query = self._normalize_text(query)
        query_tokens = set(clean_query.split())
        scored_docs = []

        for doc in self.documents:
            score = 0.0
            content_norm = self._normalize_text(doc.get("content", ""))
            topic_norm = self._normalize_text(doc.get("topic", ""))
            crop_norm = self._normalize_text(doc.get("crop", ""))
            question_norm = self._normalize_text(doc.get("question", ""))
            keywords = [self._normalize_text(k) for k in doc.get("keywords", [])]

            # Direct phrase overlap in question or keywords
            for kw in keywords:
                if kw in clean_query or clean_query in kw:
                    score += 5.0

            if any(term in clean_query for term in topic_norm.split()):
                score += 3.0

            # Token matching logic
            for token in query_tokens:
                if len(token) <= 2 or token in ["how", "what", "why", "the", "and", "for"]:
                    continue
                if token in crop_norm:
                    score += 3.0
                if token in topic_norm:
                    score += 2.5
                if token in question_norm:
                    score += 2.0
                if any(token in kw for kw in keywords):
                    score += 2.0
                if token in content_norm:
                    score += 1.0

            if score > 0:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_results = scored_docs[:top_k]

        if not top_results:
            return {
                "context": "No specific local farming record found for this exact query.",
                "documents": [],
                "confidence": 0.1
            }

        context_blocks = []
        for rank, (score, doc) in enumerate(top_results, 1):
            context_blocks.append(
                f"[Agri Reference {rank} - {doc.get('topic')} ({doc.get('crop')}):\n{doc.get('content')}]"
            )

        max_score = top_results[0][0]
        confidence = min(1.0, max_score / 8.0)

        return {
            "context": "\n\n".join(context_blocks),
            "documents": [d[1] for d in top_results],
            "confidence": round(confidence, 2)
        }

if __name__ == "__main__":
    rag = AgriRAG()
    sample_query = "What should I spray for yellow rust on my wheat crop?"
    result = rag.retrieve(sample_query)
    print("Sample RAG Query:", sample_query)
    print("Retrieval Confidence:", result["confidence"])
    print("Context Retrieved:\n", result["context"])
