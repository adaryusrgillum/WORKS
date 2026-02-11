#!/usr/bin/env python3
"""
SEOBOT - Interactive SEO Assistant
A knowledge-powered bot for SEO recommendations, meta tags, and structured data
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from epub_parser import EPUBParser
from knowledge_base import SEOKnowledgeBase
from seo_engine import SEOEngine

try:
    from advanced_seo_engine import SEOOrchestrator, SEOKnowledgeBaseAdapter
    ADVANCED_ENGINE_AVAILABLE = True
except ImportError:
    ADVANCED_ENGINE_AVAILABLE = False


class SEOBot:
    """Interactive SEO Bot with knowledge base"""
    
    def __init__(self, db_path: str = "seo_knowledge.db"):
        self.db_path = db_path
        self.kb = None
        self.engine = None
        self.orchestrator = None
        self.initialized = False
    
    def initialize(self, force_reload: bool = False):
        """Initialize the bot - parse books and build knowledge base"""
        print("🤖 Initializing SEOBOT...")
        
        # Check if database exists
        db_exists = Path(self.db_path).exists()
        
        self.kb = SEOKnowledgeBase(self.db_path).connect().init_database()
        
        if not db_exists or force_reload:
            if force_reload:
                self.kb.reset_vector_store()
            print("📚 Parsing EPUB books...")
            parser = EPUBParser()
            books, knowledge = parser.parse_all_books('.')

            if not knowledge:
                print("⚠️ No knowledge extracted from books!")
                return False

            print(f"📖 Found {len(books)} books with {len(knowledge)} knowledge chunks")

            # Embed and add to vector store (semantic search)
            self.kb.add_knowledge_chunks(knowledge)
            
            # Initialize templates
            print("📝 Initializing schema templates...")
            self.kb.init_schema_templates()
            self.kb.init_meta_templates()
            
            print("✅ Knowledge base built successfully!")
        else:
            print("📦 Using existing knowledge base")
            # Ensure templates exist
            self.kb.init_schema_templates()
            self.kb.init_meta_templates()
        
        self.engine = SEOEngine(self.kb)

        # Initialize advanced orchestrator if available
        if ADVANCED_ENGINE_AVAILABLE:
            kb_adapter = SEOKnowledgeBaseAdapter(self.kb)
            self.orchestrator = SEOOrchestrator(knowledge_base=kb_adapter, enable_critic=True)

        self.initialized = True
        
        # Print stats
        stats = self.kb.get_stats()
        print(f"\n📊 Knowledge Base Stats:")
        print(f"   • Total chunks: {stats['total_chunks']}")
        print(f"   • Books: {stats['total_books']}")
        print(f"   • Searches performed: {stats['total_searches']}")
        print(f"   • Categories: {', '.join(stats['categories'].keys())}")
        
        return True
    
    def interactive_mode(self):
        """Run interactive CLI mode"""
        if not self.initialized:
            if not self.initialize():
                print("❌ Failed to initialize. Exiting.")
                return
        
        print("\n" + "="*60)
        print("🚀 SEOBOT Interactive Mode")
        print("="*60)
        print("\nCommands:")
        print("  search <query>     - Search knowledge base")
        print("  ask <question>     - Get SEO advice")
        print("  analyze            - Analyze a webpage")
        print("  meta               - Generate meta tags")
        print("  schema             - Generate structured data")
        print("  keywords <topic>   - Get keyword suggestions")
        print("  checklist [type]   - Get SEO checklist")
        if ADVANCED_ENGINE_AVAILABLE:
            print("  strategy <topic>    - Full SEO pipeline (intent, schema, meta)")
            print("  brief <topic>      - Generate content brief")
            print("  critique           - Competitor content critique")
        print("  stats              - Show knowledge base stats")
        print("  help               - Show this help")
        print("  quit               - Exit")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("\n🤖 SEOBOT> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if command in ('quit', 'exit', 'q'):
                    print("👋 Goodbye!")
                    break
                
                elif command == 'help':
                    self._show_help()
                
                elif command == 'search':
                    self._handle_search(args)
                
                elif command == 'ask':
                    self._handle_ask(args)
                
                elif command == 'analyze':
                    self._handle_analyze()
                
                elif command == 'meta':
                    self._handle_meta()
                
                elif command == 'schema':
                    self._handle_schema()
                
                elif command == 'keywords':
                    self._handle_keywords(args)
                
                elif command == 'checklist':
                    self._handle_checklist(args)

                elif command == 'strategy' and ADVANCED_ENGINE_AVAILABLE:
                    self._handle_strategy(args)
                
                elif command == 'brief' and ADVANCED_ENGINE_AVAILABLE:
                    self._handle_brief(args)
                
                elif command == 'critique' and ADVANCED_ENGINE_AVAILABLE:
                    self._handle_critique()
                
                elif command == 'stats':
                    self._handle_stats()
                
                else:
                    # Default to search
                    self._handle_search(user_input)
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _show_help(self):
        """Show help message"""
        print("""
📖 SEOBOT Commands:

  search <query>        Search the knowledge base for SEO information
                        Example: search meta tags

  ask <question>        Ask an SEO question
                        Example: ask how to optimize title tags

  analyze               Analyze a webpage for SEO issues

  meta                  Generate meta tags for a page

  schema                Generate Schema.org structured data

  keywords <topic>      Get keyword suggestions for a topic
                        Example: keywords local seo

  checklist [type]      Get SEO checklist (article, product, business)
                        Example: checklist article

  strategy <topic>      Full SEO pipeline: intent, keywords, schema, meta
                        Example: strategy how to optimize meta tags

  brief <topic>         Generate comprehensive content brief
                        Example: brief local SEO for restaurants

  critique              Analyze competitor content and suggest improvements

  stats                 Show knowledge base statistics

  help                  Show this help message

  quit                  Exit SEOBOT
        """)
    
    def _handle_search(self, query: str):
        """Handle search command"""
        if not query:
            query = input("Enter search query: ")
        
        print(f"\n🔍 Searching for: '{query}'")
        results = self.kb.search(query, limit=5)
        
        if not results:
            print("No results found.")
            return
        
        print(f"\n📚 Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. [{result['category']}] {result['book_title']}")
            print(f"     Chapter: {result['chapter_title']}")
            print(f"     Content: {result['content'][:200]}...")
            print(f"     Relevance: {result['similarity']:.2f}")
            print()
    
    def _handle_ask(self, question: str):
        """Handle ask command"""
        if not question:
            question = input("What's your SEO question? ")
        
        print(f"\n🤔 Question: {question}")
        print("\n💡 Based on my knowledge:\n")
        
        # Search for relevant information
        results = self.kb.search(question, limit=5)
        
        if not results:
            print("I don't have specific information about that. Try searching for related terms.")
            return
        
        # Group by category
        by_category = {}
        for r in results:
            cat = r['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(r)
        
        for category, items in by_category.items():
            print(f"📌 {category.replace('_', ' ').title()}:")
            for item in items[:2]:
                print(f"   • {item['content'][:250]}...")
                print(f"     (from: {item['book_title']})")
            print()
    
    def _handle_analyze(self):
        """Handle analyze command"""
        print("\n🔍 Page Analysis")
        print("-" * 40)
        
        url = input("Page URL: ").strip()
        title = input("Page title (optional): ").strip()
        description = input("Meta description (optional): ").strip()
        page_type = input("Page type (article/product/business/general): ").strip() or "general"
        
        print("\n📊 Analyzing...\n")
        
        analysis = self.engine.analyze_page(url, title, description, page_type=page_type)
        
        print(f"SEO Score: {analysis['score']}/100")
        print()
        
        if analysis['issues']:
            print("⚠️  Issues Found:")
            for issue in analysis['issues']:
                icon = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}[issue['severity']]
                print(f"   {icon} {issue['message']}")
            print()
        
        if analysis['recommendations']:
            print("💡 Recommendations:")
            for rec in analysis['recommendations']:
                print(f"   • [{rec['priority'].upper()}] {rec['action']}")
            print()
        
        # Show recommended meta tags
        print("📋 Recommended Meta Tags:")
        required = [t for t in analysis['meta_tags'] if t['priority'] == 'required']
        for tag in required[:5]:
            print(f"   {tag['html']}")
        print()
        
        # Show structured data suggestions
        if analysis['structured_data']:
            print("📊 Suggested Structured Data:")
            for schema in analysis['structured_data']:
                print(f"   • {schema['name']} ({schema['type']})")
    
    def _handle_meta(self):
        """Handle meta tag generation"""
        print("\n🏷️  Meta Tag Generator")
        print("-" * 40)
        
        data = {
            'title': input("Page title: ").strip(),
            'description': input("Meta description: ").strip(),
            'url': input("Page URL: ").strip(),
            'image_url': input("OG Image URL: ").strip() or 'https://example.com/image.jpg',
            'type': input("Page type (website/article/product): ").strip() or 'website'
        }
        
        print("\n" + "="*60)
        print("Generated Meta Tags:")
        print("="*60 + "\n")
        
        meta_tags = self.engine.generate_meta_tag_set(data)
        print(meta_tags)
        
        print("\n" + "="*60)
    
    def _handle_schema(self):
        """Handle schema generation"""
        print("\n📐 Structured Data Generator")
        print("-" * 40)
        
        print("\nAvailable schema types:")
        templates = self.kb.get_schema_templates()
        for i, t in enumerate(templates, 1):
            print(f"  {i}. {t['name']} ({t['schema_type']})")
        
        choice = input("\nSelect schema type (number or name): ").strip()
        
        # Find selected template
        try:
            idx = int(choice) - 1
            template = templates[idx]
        except (ValueError, IndexError):
            template = next((t for t in templates if t['schema_type'].lower() == choice.lower()), None)
        
        if not template:
            print("❌ Invalid selection")
            return
        
        print(f"\n📖 {template['name']}")
        print(f"Description: {template['description']}")
        print(f"Example use: {template['example']}")
        print("\nFill in the template (press Enter to skip optional fields):\n")
        
        # Extract placeholders from template
        import re
        placeholders = re.findall(r'\{\{(\w+)\}\}', template['template'])
        
        data = {}
        for ph in placeholders:
            if ph not in data:
                value = input(f"  {ph}: ").strip()
                if value:
                    data[ph] = value
        
        # Generate schema
        schema_json = self.engine.generate_schema_json(template['schema_type'], data)
        
        print("\n" + "="*60)
        print("Generated Schema.org JSON-LD:")
        print("="*60 + "\n")
        print("<script type=\"application/ld+json\">")
        print(schema_json)
        print("</script>")
        print("\n" + "="*60)
    
    def _handle_keywords(self, topic: str):
        """Handle keyword suggestions"""
        if not topic:
            topic = input("Enter topic: ")
        
        print(f"\n🔑 Keyword Suggestions for '{topic}':\n")
        
        keywords = self.engine.get_keyword_suggestions(topic, limit=10)
        
        if not keywords:
            print("No suggestions found. Try a different topic.")
            return
        
        for i, kw in enumerate(keywords, 1):
            print(f"  {i}. {kw['keyword']}")
            print(f"     Frequency: {kw['frequency']} mentions")
            if kw['contexts']:
                print(f"     Context: {kw['contexts'][0][:100]}...")
            print()
    
    def _handle_checklist(self, page_type: str):
        """Handle checklist command"""
        if not page_type:
            page_type = input("Page type (article/product/business/general): ").strip() or "general"
        
        print(f"\n✅ SEO Checklist for {page_type.title()} Pages:\n")
        
        checklist = self.engine.get_seo_checklist(page_type)
        
        # Group by category
        by_category = {}
        for item in checklist:
            cat = item['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item)
        
        for category, items in by_category.items():
            print(f"📁 {category.replace('_', ' ').title()}:")
            for item in items:
                priority_icon = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢',
                    'info': '⚪'
                }.get(item['priority'], '⚪')
                print(f"   {priority_icon} {item['item']}")
            print()

    def _handle_strategy(self, topic: str, url: str = "", page_type: str = ""):
        """Handle strategy command - full SEO pipeline via orchestrator"""
        if not topic:
            topic = input("Enter topic for SEO strategy: ").strip()

        if not self.orchestrator:
            print("❌ Advanced engine not available. Run: pip install networkx")
            return

        print(f"\n🚀 Running full SEO pipeline for: {topic}\n")

        if not url:
            url = input("Page URL (or Enter to skip): ").strip() or "https://example.com"
        if not page_type:
            page_type = input("Page type (article/product/business): ").strip() or "article"

        # Map to schema types
        schema_type = {"article": "Article", "product": "Product", "business": "LocalBusiness"}.get(
            page_type.lower(), "Article"
        )

        context = {
            "page_type": schema_type,
            "url": url,
            "title": topic,
            "description": "",
        }

        result = self.orchestrator.execute(topic, context=context)
        d = result["deliverables"]

        print("\n" + "=" * 60)
        print("📋 SEO STRATEGY SUMMARY")
        print("=" * 60)
        print(f"\n🎯 Intent: {d['seo_strategy']['intent']['primary']}")
        print(f"📄 Content type: {d['seo_strategy']['content_type']}")
        print(f"📐 Target sections: {', '.join(d['seo_strategy']['recommended_sections'])}")
        print(f"📊 Word count target: {d['seo_strategy']['target_word_count']}")

        print("\n🔑 Keyword clusters:")
        for i, cluster in enumerate(d["keyword_clusters"][:3], 1):
            print(f"   {i}. {cluster['name']}: {', '.join(cluster['keywords'][:5])}")

        print(f"\n🏷️  Title: {d['meta_tags']['title']}")
        print(f"📝 Description: {d['meta_tags']['description'][:100]}...")

        print("\n📐 Schema types: " + ", ".join(d["schema_markup"]["additional_recommended"]))
        print("\n" + "=" * 60)

    def _handle_brief(self, topic: str):
        """Handle brief command - generate content brief"""
        if not topic:
            topic = input("Enter topic for content brief: ").strip()

        if not self.orchestrator:
            print("❌ Advanced engine not available. Run: pip install networkx")
            return

        print(f"\n📋 Generating content brief for: {topic}\n")
        brief = self.orchestrator.generate_content_brief(topic)

        print("\n" + "=" * 60)
        print("CONTENT BRIEF")
        print("=" * 60)
        print(f"\n📌 Topic: {brief['topic']}")
        print(f"🎯 Objective: {brief['objective'].get('primary', 'N/A')}")
        print(f"📄 Content Type: {brief['content_type']}")
        print(f"📊 Target Word Count: {brief['target_word_count']} words")
        print(f"\n📑 Suggested Sections:")
        for s in brief.get('suggested_sections', []):
            print(f"   • {s}")
        print(f"\n🔑 Primary Keywords: {brief.get('primary_keywords', [])}")
        print(f"\n🏷️ Meta Title: {brief['meta_tags'].get('title', '')}")
        print(f"📝 Meta Description: {brief['meta_tags'].get('description', '')[:100]}...")
        if brief.get('internal_linking_suggestions'):
            print(f"\n🔗 Internal Linking:")
            for link in brief['internal_linking_suggestions'][:5]:
                print(f"   • {link}")
        print("\n" + "=" * 60)

    def _handle_critique(self):
        """Handle critique command - competitor content analysis"""
        if not self.orchestrator:
            print("❌ Advanced engine not available. Run: pip install networkx")
            return

        print("\n🔍 Competitor Content Critique")
        print("-" * 40)
        keyword = input("Target keyword: ").strip()
        print("Paste competitor content (end with empty line or Ctrl+Z):")
        lines = []
        try:
            while True:
                line = input()
                if line == "" and lines:
                    break
                lines.append(line)
        except EOFError:
            pass
        content = "\n".join(lines).strip()

        if not keyword or not content:
            print("❌ Keyword and content are required.")
            return

        print("\n📊 Analyzing...\n")
        result = self.orchestrator.analyze_competitor(content, keyword)

        print("=" * 60)
        print("CRITIQUE & OPPORTUNITIES")
        print("=" * 60)
        for opt in result.get('opportunities', []):
            print(f"   • {opt}")
        print("\n" + "=" * 60)

    def _handle_stats(self):
        """Handle stats command"""
        stats = self.kb.get_stats()
        
        print("\n📊 Knowledge Base Statistics:")
        print("-" * 40)
        print(f"Total Knowledge Chunks: {stats['total_chunks']}")
        print(f"Books in Database: {stats['total_books']}")
        print(f"Total Searches: {stats['total_searches']}")
        print(f"\nCategories:")
        for cat, count in stats['categories'].items():
            print(f"  • {cat}: {count} chunks")
    
    def close(self):
        """Close the bot"""
        if self.kb:
            self.kb.close()


def main():
    parser = argparse.ArgumentParser(description='SEOBOT - SEO Knowledge Assistant')
    parser.add_argument('--init', action='store_true', help='Force re-initialize knowledge base')
    parser.add_argument('--search', type=str, help='Search for a query and exit')
    parser.add_argument('--ask', type=str, help='Ask a question and exit')
    parser.add_argument('--checklist', type=str, help='Get checklist for page type and exit')
    parser.add_argument('--strategy', type=str, help='Full SEO pipeline for a topic and exit')
    parser.add_argument('--brief', type=str, help='Generate content brief for a topic and exit')
    parser.add_argument('--url', type=str, help='Page URL (for --strategy)')
    parser.add_argument('--type', dest='page_type', type=str, help='Page type (for --strategy)')
    parser.add_argument('--db', type=str, default='seo_knowledge.db', help='Database path')
    
    args = parser.parse_args()
    
    bot = SEOBot(db_path=args.db)
    
    try:
        if args.search:
            bot.initialize(force_reload=args.init)
            bot._handle_search(args.search)
        elif args.ask:
            bot.initialize(force_reload=args.init)
            bot._handle_ask(args.ask)
        elif args.checklist:
            bot.initialize(force_reload=args.init)
            bot._handle_checklist(args.checklist)
        elif args.strategy:
            bot.initialize(force_reload=args.init)
            bot._handle_strategy(args.strategy, url=args.url or "", page_type=args.page_type or "")
        elif args.brief:
            bot.initialize(force_reload=args.init)
            bot._handle_brief(args.brief)
        else:
            bot.initialize(force_reload=args.init)
            bot.interactive_mode()
    finally:
        bot.close()


if __name__ == '__main__':
    main()
