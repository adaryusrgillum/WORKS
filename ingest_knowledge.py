
import os
import json
import uuid
from pathlib import Path
import sys

# Add advanced_seo_engine to path
sys.path.append(str(Path(__file__).parent / "advanced_seo_engine"))

from advanced_seo_engine.knowledge_base import VectorKnowledgeBase
from advanced_seo_engine.epub_ingestion import EPUBIngestionPipeline

def ingest_txt_files(kb, training_dir):
    print(f"--- Ingesting TXT files from {training_dir} ---")
    for txt_file in training_dir.glob("*.txt"):
        if txt_file.name == "seo_rules_extracted.txt":
            continue # Already in JSON or redundant
        
        print(f"Processing {txt_file.name}...")
        text = txt_file.read_text(encoding="utf-8", errors="ignore")
        
        # Simple chunking by paragraph/lines for TXT
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 100]
        
        docs = []
        for i, p in enumerate(paragraphs):
            docs.append({
                "id": f"txt_{txt_file.stem}_{i}",
                "text": p,
                "metadata": {
                    "source": txt_file.name,
                    "type": "text_extract",
                    "chunk_index": i
                }
            })
        
        if docs:
            kb.add_documents(docs)

def ingest_json_rules(kb, json_path):
    print(f"--- Ingesting JSON rules from {json_path} ---")
    if not json_path.exists():
        print("JSON rules file not found.")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    categories = data.get("categories", {})
    all_docs = []
    
    for cat, rules in categories.items():
        print(f"Processing category: {cat} ({len(rules)} rules)")
        for i, rule in enumerate(rules):
            if len(rule.strip()) < 20:
                continue
                
            all_docs.append({
                "id": f"rule_{cat}_{i}",
                "text": rule,
                "metadata": {
                    "source": "seo_rules_extracted.json",
                    "category": cat,
                    "type": "rule",
                    "rule_index": i
                }
            })
            
            # Add in batches
            if len(all_docs) >= 100:
                kb.add_documents(all_docs)
                all_docs = []
                
    if all_docs:
        kb.add_documents(all_docs)

def ingest_epubs(kb, pipeline, root_dir):
    print(f"--- Ingesting EPUBs from {root_dir} ---")
    epub_files = list(root_dir.glob("*.epub"))
    for epub_file in epub_files:
        print(f"Processing {epub_file.name}...")
        try:
            book_data = pipeline.extract_epub(str(epub_file))
            chunks = pipeline.chunk_content(book_data)
            
            kb_docs = []
            for chunk in chunks:
                kb_docs.append(chunk.to_dict())
            
            if kb_docs:
                kb.add_documents(kb_docs)
        except Exception as e:
            print(f"Error processing {epub_file.name}: {e}")

def main():
    workspace_root = Path(__file__).parent
    training_dir = workspace_root / "seo_training_data"
    json_path = training_dir / "seo_rules_extracted.json"
    
    # Initialize KB
    kb = VectorKnowledgeBase(persist_directory="./chroma_db")
    pipeline = EPUBIngestionPipeline(chunk_size=400, chunk_overlap=50)
    
    # Run ingestion
    ingest_json_rules(kb, json_path)
    ingest_txt_files(kb, training_dir)
    ingest_epubs(kb, pipeline, workspace_root)
    
    print("\n✅ Ingestion complete.")
    print(f"Total documents in KB: {kb.collection.count()}")

if __name__ == "__main__":
    main()
