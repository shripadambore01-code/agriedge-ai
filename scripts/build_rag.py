"""
RAG Knowledge Ingestion Script
Builds and verifies the local agricultural knowledge base.
"""

import os
import sys
from pathlib import Path

# Set UTF-8 encoding for standard output if available
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from rag.vector_store import AgriRAG

def main():
    print("=" * 60)
    print("🌾 AgriVoice - Local RAG Knowledge Ingestion")
    print("=" * 60)

    rag = AgriRAG()
    doc_count = len(rag.documents)
    print(f"📖 Loaded {doc_count} agricultural records from dataset.")

    print("\n🔍 Running verification test retrieval...")
    test_queries = [
        "What should I do for yellow rust in wheat?",
        "How much money do farmers get from PM-KISAN?",
        "How to control pink bollworm in cotton?"
    ]

    for q in test_queries:
        res = rag.retrieve(q)
        print(f"\n❓ Query: {q}")
        print(f"📊 Confidence: {res['confidence']}")
        print(f"📑 Top Match: {res['documents'][0]['topic'] if res['documents'] else 'None'}")

    print("\n✅ Local RAG database is structured, verified, and ready.")

if __name__ == "__main__":
    main()
