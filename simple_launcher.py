#!/usr/bin/env python3
"""
SEOBOT Simple Launcher - Minimal version for testing
"""

import sys
import io
import warnings
warnings.filterwarnings('ignore')

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("="*60)
print("SEOBOT Advanced - Starting up...")
print("="*60)

# Step 1: Basic imports
print("\n📦 Loading basic modules...")
from pathlib import Path
print("   OK pathlib")

import json
print("   OK json")

# Step 2: Check for EPUBs
epub_files = list(Path('.').glob('*.epub'))
print(f"\nFound {len(epub_files)} EPUB file(s):")
for f in epub_files:
    print(f"   - {f.name}")

# Step 3: Load ChromaDB
print("\nConnecting to vector database...")
import chromadb
from chromadb.config import Settings

data_dir = Path("./seobot_data")
data_dir.mkdir(exist_ok=True)

client = chromadb.Client(Settings(
    persist_directory=str(data_dir / "chroma_db"),
    anonymized_telemetry=False
))

collection = client.get_or_create_collection(
    name="seo_knowledge",
    metadata={"hnsw:space": "cosine"}
)

count = collection.count()
print(f"   OK Collection has {count} documents")

# Step 4: Check if we need to ingest
if count == 0 and epub_files:
    print("\nWARNING: Knowledge base is empty!")
    print("   Run setup_advanced.py first to ingest EPUB files:")
    print("   python setup_advanced.py")
    sys.exit(1)

# Step 5: Load embedding model (this takes time)
print("\nLoading embedding model (this may take a minute)...")
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-large-en-v1.5')
print("   OK Model loaded")

# Step 6: Define search function
def search(query, n=5):
    """Search the knowledge base"""
    instruction = "Represent this sentence for searching relevant passages: "
    embedding = model.encode(instruction + query, normalize_embeddings=True).tolist()
    
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n,
        include=['documents', 'metadatas', 'distances']
    )
    
    output = []
    for i in range(len(results['ids'][0])):
        output.append({
            'id': results['ids'][0][i],
            'text': results['documents'][0][i],
            'metadata': results['metadatas'][0][i],
            'similarity': 1 - results['distances'][0][i]
        })
    return output

# Step 7: Interactive mode
print("\n" + "="*60)
print("SEOBOT Ready!")
print("="*60)
print("\nCommands:")
print("  search <query>  - Search knowledge base")
print("  stats           - Show statistics")
print("  quit            - Exit")
print("="*60)

while True:
    try:
        user_input = input("\n🤖> ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break
        
        if user_input.lower() == 'stats':
            print(f"\nStatistics:")
            print(f"   Documents: {collection.count()}")
            continue
        
        if user_input.lower().startswith('search '):
            query = user_input[7:]
        else:
            query = user_input
        
        print(f"\nSearching: '{query}'")
        results = search(query, n=5)
        
        print(f"\nFound {len(results)} results:")
        for i, r in enumerate(results, 1):
            meta = r['metadata'] or {}
            print(f"\n{i}. [{meta.get('category', 'general')}] "
                  f"Score: {r['similarity']:.3f}")
            print(f"   Source: {meta.get('book_title', 'Unknown')}")
            print(f"   {r['text'][:200]}...")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        break
    except Exception as e:
        print(f"Error: {e}")
