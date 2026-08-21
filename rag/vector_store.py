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

EMBEDDED_KNOWLEDGE = [
    {
        "id": "wheat_yellow_rust",
        "topic": "Wheat Disease",
        "crop": "Wheat",
        "question": "How do I identify and manage Yellow Rust in wheat crops?",
        "content": "Yellow Rust (Puccinia striiformis) in wheat appears as yellowish-orange powdery stripes or pustules on the upper leaves. In severe cases, it spreads to the leaf sheath and ears. Management: Spray Propiconazole 25% EC @ 1 ml/liter of water or Tebuconazole 25.9% EC @ 1 ml/liter at the first appearance of symptoms. Avoid excessive nitrogen fertilizer and ensure balanced NPK with irrigation.",
        "keywords": ["wheat", "yellow rust", "fungus", "propiconazole", "leaves", "disease"]
    },
    {
        "id": "rice_blast",
        "topic": "Rice Disease",
        "crop": "Rice / Paddy",
        "question": "What are the symptoms and treatment for Rice Blast disease?",
        "content": "Rice Blast (Magnaporthe oryzae) produces spindle-shaped / diamond-shaped lesions with brown borders and grey/white centers on leaves, leaf collars, nodes, and panicles (neck blast). Management: Seed treatment with Tricyclazole 75% WP @ 2g/kg seed. Foliar spray of Tricyclazole 75% WP @ 0.6g/liter or Isoprothiolane 40% EC @ 1.5 ml/liter when lesions appear on 2-5% of leaves.",
        "keywords": ["rice", "paddy", "blast", "tricyclazole", "leaf blast", "neck blast"]
    },
    {
        "id": "cotton_pink_bollworm",
        "topic": "Cotton Pest",
        "crop": "Cotton",
        "question": "How to control Pink Bollworm infestation in cotton?",
        "content": "Pink Bollworm (Pectinophora gossypiella) damages squares, flowers, and bolls, causing rosette flowers and premature boll opening. Control: Install Pheromone traps @ 5-8 traps/acre for monitoring. If trap catches exceed 8 moths/day for 3 consecutive days, spray Profenofos 50% EC @ 2 ml/liter or Emamectin Benzoate 5% SG @ 0.4 g/liter. Release Trichogramma parasitoids early in the season.",
        "keywords": ["cotton", "pink bollworm", "pest", "pheromone traps", "profenofos", "emamectin"]
    },
    {
        "id": "tomato_early_blight",
        "topic": "Tomato Disease",
        "crop": "Tomato",
        "question": "How do I treat Early Blight on tomato plants?",
        "content": "Early Blight (Alternaria solani) causes dark brown circular spots with concentric rings (target board pattern) on older lower leaves. Management: Spray Mancozeb 75% WP @ 2.5 g/liter or Chlorothalonil 75% WP @ 2 g/liter at 10-14 day intervals. Avoid overhead sprinkler irrigation and remove affected lower leaves.",
        "keywords": ["tomato", "early blight", "alternaria", "mancozeb", "concentric rings", "leaf spot"]
    },
    {
        "id": "soil_nitrogen_deficiency",
        "topic": "Soil & Nutrients",
        "crop": "General Crops",
        "question": "What are signs of Nitrogen deficiency in crops and how to fix it?",
        "content": "Nitrogen deficiency causes general yellowing (chlorosis) of older lower leaves starting from the leaf tip towards the base (V-shaped pattern in corn/maize), stunted plant growth, and thin stalks. Treatment: Apply Urea (46% N) as top-dressing or spray 1-2% Urea foliar solution for quick recovery. Incorporate green manure crops like dhaincha or sunn hemp.",
        "keywords": ["nitrogen", "deficiency", "chlorosis", "yellow leaves", "urea", "fertilizer", "soil"]
    },
    {
        "id": "drip_irrigation_guidance",
        "topic": "Irrigation",
        "crop": "General / Vegetables / Fruits",
        "question": "What are the advantages and maintenance tips for drip irrigation?",
        "content": "Drip irrigation saves 40-70% water and increases fertilizer efficiency via fertigation. Maintenance: Flush lateral lines every 15 days by opening end caps. Acid wash lines using 0.5-1% Hydrochloric acid or Phosphoric acid if emitters get clogged due to hard water/calcium deposits. Backwash screen and disc filters weekly.",
        "keywords": ["irrigation", "drip", "water saving", "fertigation", "clogging", "maintenance"]
    },
    {
        "id": "pm_kisan_scheme",
        "topic": "Government Scheme",
        "crop": "All Farmers",
        "question": "What is the PM-KISAN scheme and how do farmers benefit?",
        "content": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) provides financial assistance of Rs. 6,000 per year in three equal 4-monthly installments of Rs. 2,000 directly into bank accounts of landholding farmer families via DBT. Registration requires Aadhaar, land ownership records (7/12 extract / RoR), and active bank account linked to Aadhaar with e-KYC completed.",
        "keywords": ["pm kisan", "scheme", "subsidy", "6000", "government", "financial aid", "ekyc"]
    },
    {
        "id": "pm_fby_crop_insurance",
        "topic": "Government Scheme",
        "crop": "All Crops",
        "question": "How does PMFBY (Crop Insurance Scheme) protect farmers?",
        "content": "Pradhan Mantri Fasal Bima Yojana (PMFBY) covers crop losses caused by non-preventable natural risks (drought, flood, pests, storms). Farmer premium share: 2% for Kharif crops, 1.5% for Rabi food/oilseed crops, and 5% for annual commercial/horticultural crops. Claim notification for localized calamities must be submitted within 72 hours via the Crop Insurance App or toll-free helpline 14447.",
        "keywords": ["pmfby", "crop insurance", "drought", "flood", "claim", "premium", "loss compensation"]
    }
]

class AgriRAG:
    def __init__(self, data_path: str = None, persist_dir: str = None):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.data_path = Path(data_path) if data_path else self.base_dir / "rag" / "data" / "agri_knowledge.json"
        self.persist_dir = Path(persist_dir) if persist_dir else self.base_dir / "chroma_db"
        self.documents: List[Dict[str, Any]] = []
        self._load_local_data()

    def _load_local_data(self):
        """Loads structured JSON agricultural knowledge or falls back to embedded records."""
        try:
            if self.data_path.exists():
                with open(self.data_path, "r", encoding="utf-8-sig") as f:
                    self.documents = json.load(f)
            else:
                self.documents = EMBEDDED_KNOWLEDGE
        except Exception:
            self.documents = EMBEDDED_KNOWLEDGE


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
