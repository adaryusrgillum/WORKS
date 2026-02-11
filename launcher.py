#!/usr/bin/env python3
"""
SEOBOT Launcher - Simple startup script
"""

import sys
import warnings
warnings.filterwarnings('ignore')

# Suppress stderr to avoid Windows console issues
import os
sys.stderr = open(os.devnull, 'w')

from advanced_seo_engine.epub_ingestion import EPUBIngestionPipeline
from advanced_seo_engine.knowledge_base import VectorKnowledgeBase
from advanced_seo_engine.concept_graph import ConceptGraph
from advanced_seo_engine.orchestrator import SEOOrchestrator
from pathlib import Path

def main():
    print("="*60)
    print("🤖 SEOBOT Advanced Launcher")
    print("="*60)
    
    # Setup directories
    data_dir = Path("./seobot_data")
    data_dir.mkdir(exist_ok=True)
    
    # Check for EPUB files
    epub_files = list(Path('.').glob('*.epub'))
    print(f"\n📚 Found {len(epub_files)} EPUB file(s)")
    for f in epub_files:
        print(f"   • {f.name}")
    
    # Initialize knowledge base
    print("\n🔧 Initializing knowledge base...")
    kb = VectorKnowledgeBase(
        persist_directory=str(data_dir / "chroma_db"),
        embedding_model="BAAI/bge-large-en-v1.5"
    )
    
    # Initialize concept graph
    graph_path = data_dir / "concept_graph.json"
    cg = ConceptGraph(str(graph_path))
    
    # Check if we need to ingest
    stats = kb.get_stats()
    if stats['total_documents'] == 0 and epub_files:
        print("\n📥 Ingesting EPUB files...")
        pipeline = EPUBIngestionPipeline(chunk_size=500, chunk_overlap=50)
        
        all_chunks = []
        for epub_file in epub_files:
            try:
                chunks = pipeline.process_book(str(epub_file))
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"   ⚠ Error: {e}")
        
        if all_chunks:
            print(f"\n📤 Adding {len(all_chunks)} chunks to knowledge base...")
            documents = [c.to_dict() for c in all_chunks]
            kb.add_documents(documents)
            
            # Build concept graph
            print("🕸️  Building concept graph...")
            concepts = pipeline.extract_concepts(all_chunks)
            for concept, chunk_ids in list(concepts.items())[:100]:
                cg.add_concept(concept, 'extracted', 'epub')
            cg.save()
    
    # Initialize orchestrator
    print("\n🚀 Starting SEO Orchestrator...")
    orchestrator = SEOOrchestrator(knowledge_base=kb, concept_graph=cg)
    
    # Show stats
    stats = kb.get_stats()
    print("\n📊 Knowledge Base Stats:")
    print(f"   Documents: {stats['total_documents']}")
    print(f"   Sources: {', '.join(stats['sources']) if stats['sources'] else 'None'}")
    print(f"   Categories: {', '.join(stats['categories'])}")
    
    # Interactive loop
    print("\n" + "="*60)
    print("🎯 SEOBOT Advanced Ready!")
    print("="*60)
    print("\nCommands:")
    print("  search <query>    - Search knowledge base")
    print("  analyze <topic>   - Full SEO analysis")
    print("  ask <question>    - Ask SEO question")
    print("  meta              - Generate meta tags")
    print("  schema            - Generate schema")
    print("  quit              - Exit")
    print("="*60)
    
    while True:
        try:
            user_input = input("\n🤖> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ('quit', 'exit', 'q'):
                print("👋 Goodbye!")
                break
            
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if command == 'search':
                if args:
                    print(f"\n🔍 Searching: '{args}'")
                    results = kb.search(args, n_results=5)
                    for i, r in enumerate(results, 1):
                        print(f"\n{i}. [{r['metadata'].get('category', 'general')}] "
                              f"({r['similarity']:.3f})")
                        print(f"   {r['text'][:200]}...")
                else:
                    print("Usage: search <query>")
            
            elif command == 'analyze':
                topic = args or input("Topic: ")
                print(f"\n📊 Analyzing: {topic}")
                result = orchestrator.execute(topic)
                
                print(f"\n🎯 Intent: {result['strategy']['intent']['primary']}")
                print(f"📝 Content Type: {result['strategy']['content_strategy']['content_type']}")
                print(f"🏷️  Title: {result['deliverables']['meta_tags']['title']}")
                print(f"📄 Description: {result['deliverables']['meta_tags']['description']}")
            
            elif command == 'ask':
                question = args or input("Question: ")
                print(f"\n🤔 {question}")
                fusion = kb.semantic_fusion(question, n_results=5)
                print(f"\n💡 Answer based on {len(fusion['sources'])} sources:")
                print(fusion['fused_content'][:800] + "...")
            
            elif command == 'meta':
                title = input("Title: ")
                desc = input("Description: ")
                url = input("URL: ")
                result = orchestrator.quick_meta(title, desc, url)
                print(f"\n🏷️  Generated Meta Tags:")
                print(f"Title: {result['title']}")
                print(f"Description: {result['description']}")
            
            elif command == 'schema':
                print("\nTypes: Article, Product, LocalBusiness, FAQPage, HowTo")
                page_type = input("Schema type: ")
                result = orchestrator.quick_schema(page_type, {})
                import json
                print(f"\n📐 Schema:\n{json.dumps(result['primary_schema'], indent=2)}")
            
            else:
                # Default to search
                results = kb.search(user_input, n_results=3)
                for r in results:
                    print(f"\n• {r['text'][:250]}...")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
