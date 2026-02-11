"""
Setup script for SEOBOT
Initializes the knowledge base from EPUB books
"""

import sys
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed"""
    required = {
        'chromadb': 'chromadb',
        'sentence_transformers': 'sentence-transformers',
        'networkx': 'networkx',
        'ebooklib': 'ebooklib',
        'bs4': 'beautifulsoup4',
        'lxml': 'lxml',
    }
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    if missing:
        print("❌ Missing dependencies:")
        for pkg in missing:
            print(f"   • {pkg}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    return True


def setup_knowledge_base(db_path: str = "seo_knowledge.db", force: bool = False):
    """Initialize the knowledge base from EPUB files"""
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False

    print("="*60)
    print("🤖 SEOBOT Setup")
    print("="*60)
    
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        return False
    print("✅ All dependencies installed")
    
    from epub_parser import EPUBParser
    from knowledge_base import SEOKnowledgeBase
    
    # Check for EPUB files
    epub_files = list(Path('.').glob('*.epub'))
    
    if not epub_files:
        print("\n❌ No EPUB files found in current directory!")
        print("Please place your SEO books (.epub files) in this directory.")
        return False
    
    print(f"\n📚 Found {len(epub_files)} EPUB file(s):")
    for f in epub_files:
        print(f"   • {f.name}")
    
    # Check if database exists
    db_exists = Path(db_path).exists()
    rebuild = force

    if db_exists and not force:
        print(f"\n⚠️  Database already exists: {db_path}")
        response = input("Do you want to rebuild it? (y/N): ").strip().lower()
        if response != 'y':
            print("Using existing database.")
            return True
        rebuild = True

    # Initialize database
    print("\n🔧 Initializing knowledge base...")
    kb = SEOKnowledgeBase(db_path).connect().init_database()

    # Reset vector store on rebuild
    if rebuild:
        kb.reset_vector_store()

    # Parse EPUB files
    print("\n📖 Parsing books...")
    parser = EPUBParser()
    books, knowledge = parser.parse_all_books('.')

    if not knowledge:
        print("\n❌ No knowledge extracted from books!")
        return False

    print(f"\n✅ Extracted {len(knowledge)} knowledge chunks from {len(books)} books")

    # Embed and add to ChromaDB (semantic search)
    kb.add_knowledge_chunks(knowledge)
    
    # Initialize templates
    print("📝 Adding schema templates...")
    kb.init_schema_templates()
    kb.init_meta_templates()
    
    # Show stats
    stats = kb.get_stats()
    print("\n" + "="*60)
    print("📊 Knowledge Base Summary:")
    print("="*60)
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Books: {stats['total_books']}")
    print(f"Categories: {', '.join(stats['categories'].keys())}")
    print("="*60)
    
    kb.close()
    
    print("\n✅ Setup complete! Run 'python seo_bot.py' to start.")
    return True


if __name__ == '__main__':
    force = '--force' in sys.argv or '-f' in sys.argv
    setup_knowledge_base(force=force)
