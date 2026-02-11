"""
Knowledge Base Module for SEO Bot
Uses ChromaDB + BGE embeddings for semantic search, SQLite for templates
"""

import sqlite3
import json
import warnings
from typing import List, Dict, Any, Optional
from pathlib import Path

# Suppress HuggingFace/tokenizer warnings during load
warnings.filterwarnings("ignore")

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# BGE models use prefixes for best performance
BGE_QUERY_PREFIX = "query: "
BGE_PASSAGE_PREFIX = "passage: "
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
CHROMA_COLLECTION = "seobot_knowledge"


class SEOKnowledgeBase:
    """Vector-based knowledge base with semantic search (ChromaDB + BGE)"""

    def __init__(self, db_path: str = "seo_knowledge.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.chroma_path = Path(db_path).parent / "chroma_db"
        self.chroma_client = None
        self.collection = None
        self.embedder = None

    def connect(self):
        """Connect to SQLite and ChromaDB"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.chroma_path.mkdir(parents=True, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            metadata={"description": "SEOBOT knowledge chunks"},
        )

        return self

    def close(self):
        """Close database connections"""
        if self.conn:
            self.conn.close()

    def _get_embedder(self) -> SentenceTransformer:
        """Lazy load embedding model"""
        if self.embedder is None:
            print("Loading embedding model (BGE-large)...")
            self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        return self.embedder

    def reset_vector_store(self):
        """Clear all chunks (for full rebuild)"""
        self.chroma_client.delete_collection(CHROMA_COLLECTION)
        self.collection = self.chroma_client.create_collection(
            name=CHROMA_COLLECTION,
            metadata={"description": "SEOBOT knowledge chunks"},
        )
        print("Vector store reset.")

    def init_database(self):
        """Initialize SQLite schema (templates only; chunks live in ChromaDB)"""
        self.cursor.executescript("""
            -- Schema templates table
            CREATE TABLE IF NOT EXISTS schema_templates (
                id TEXT PRIMARY KEY,
                schema_type TEXT,
                name TEXT,
                template TEXT,
                description TEXT,
                example TEXT
            );

            -- Meta tag templates
            CREATE TABLE IF NOT EXISTS meta_templates (
                id TEXT PRIMARY KEY,
                tag_type TEXT,
                name TEXT,
                template TEXT,
                description TEXT,
                priority INTEGER
            );

            -- Search history
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                results_count INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()
        return self

    def build_vocabulary(self, chunks: List[Dict[str, Any]]):
        """No-op: embeddings handle semantic representation"""
        pass

    def add_knowledge_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 100,
    ):
        """Add chunks to ChromaDB with BGE embeddings"""
        if not chunks:
            return

        print(f"Embedding {len(chunks)} chunks...")
        model = self._get_embedder()

        ids = []
        documents = []
        metadatas = []

        for c in chunks:
            ids.append(c["chunk_id"])
            documents.append(c["content"])
            metadatas.append({
                "book_id": c.get("book_id", ""),
                "book_title": c.get("book_title", ""),
                "chapter_title": c.get("chapter_title", ""),
                "category": c.get("category", "general"),
                "relevance_score": str(c.get("relevance_score", 0)),
            })

        # BGE passage prefix for documents
        docs_for_embed = [BGE_PASSAGE_PREFIX + d for d in documents]
        embeddings = model.encode(docs_for_embed, show_progress_bar=True)

        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i : i + batch_size],
                embeddings=embeddings[i : i + batch_size].tolist(),
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )

        print("Chunks added to vector store.")

    def search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic search using BGE embeddings"""
        self.cursor.execute(
            "INSERT INTO search_history (query) VALUES (?)",
            (query,),
        )
        self.conn.commit()

        if self.collection.count() == 0:
            return []

        model = self._get_embedder()
        query_embedding = model.encode(
            [BGE_QUERY_PREFIX + query],
            show_progress_bar=False,
        )[0].tolist()

        where = {"category": category} if category else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(limit * 2, self.collection.count()) or limit,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        out = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                dist = results["distances"][0][i] if results["distances"] else 0
                # ChromaDB uses L2 distance; lower = more similar. Convert to similarity-like score
                similarity = 1.0 / (1.0 + dist) if dist is not None else 1.0
                out.append({
                    "id": meta.get("book_id", "") + "_" + str(i),
                    "book_title": meta.get("book_title", ""),
                    "chapter_title": meta.get("chapter_title", ""),
                    "content": doc,
                    "category": meta.get("category", "general"),
                    "relevance_score": int(meta.get("relevance_score", 0)),
                    "similarity": similarity,
                    "combined_score": similarity,
                })

        out.sort(key=lambda x: x["combined_score"], reverse=True)
        out = out[:limit]

        self.cursor.execute(
            "UPDATE search_history SET results_count = ? WHERE id = last_insert_rowid()",
            (len(out),),
        )
        self.conn.commit()

        return out

    def semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Alias for search (both use semantic retrieval now)"""
        return self.search(query, limit=limit)

    def get_categories(self) -> List[str]:
        """Get distinct categories from ChromaDB metadata"""
        if self.collection.count() == 0:
            return []
        # ChromaDB doesn't have GROUP BY; get all and dedupe
        data = self.collection.get(include=["metadatas"])
        cats = set()
        if data and data.get("metadatas"):
            for m in data["metadatas"]:
                c = m.get("category", "general")
                if c:
                    cats.add(c)
        return sorted(cats)

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        stats["total_chunks"] = self.collection.count()
        data = self.collection.get(include=["metadatas"])
        book_ids = set()
        if data and data.get("metadatas"):
            for m in data["metadatas"]:
                bid = m.get("book_id", "")
                if bid:
                    book_ids.add(bid)
        stats["total_books"] = len(book_ids)
        self.cursor.execute("SELECT COUNT(*) FROM search_history")
        stats["total_searches"] = self.cursor.fetchone()[0]
        stats["categories"] = {c: 0 for c in self.get_categories()}
        if data and data.get("metadatas"):
            for m in data["metadatas"]:
                c = m.get("category", "general")
                stats["categories"][c] = stats["categories"].get(c, 0) + 1
        return stats

    def init_schema_templates(self):
        """Initialize schema.org templates (unchanged from original)"""
        templates = [
            {
                "id": "schema_localbusiness",
                "schema_type": "LocalBusiness",
                "name": "Local Business",
                "template": '{\n  "@context": "https://schema.org",\n  "@type": "LocalBusiness",\n  "name": "{{business_name}}",\n  "image": "{{image_url}}",\n  "@id": "{{website_url}}",\n  "url": "{{website_url}}",\n  "telephone": "{{phone}}",\n  "address": {\n    "@type": "PostalAddress",\n    "streetAddress": "{{street}}",\n    "addressLocality": "{{city}}",\n    "addressRegion": "{{state}}",\n    "postalCode": "{{zip}}",\n    "addressCountry": "{{country}}"\n  },\n  "geo": {\n    "@type": "GeoCoordinates",\n    "latitude": {{lat}},\n    "longitude": {{lng}}\n  },\n  "openingHoursSpecification": [\n    {{hours}}\n  ],\n  "priceRange": "{{price_range}}"\n}',
                "description": "Schema for local businesses with physical location",
                "example": "Restaurants, shops, service providers",
            },
            {
                "id": "schema_article",
                "schema_type": "Article",
                "name": "Article/Blog Post",
                "template": '{\n  "@context": "https://schema.org",\n  "@type": "Article",\n  "headline": "{{title}}",\n  "description": "{{description}}",\n  "image": "{{image_url}}",\n  "author": {"@type": "Person", "name": "{{author_name}}"},\n  "publisher": {"@type": "Organization", "name": "{{publisher_name}}", "logo": {"@type": "ImageObject", "url": "{{logo_url}}"}},\n  "datePublished": "{{publish_date}}",\n  "dateModified": "{{modified_date}}"\n}',
                "description": "Schema for articles and blog posts",
                "example": "Blog posts, news articles",
            },
            {
                "id": "schema_product",
                "schema_type": "Product",
                "name": "Product",
                "template": '{\n  "@context": "https://schema.org",\n  "@type": "Product",\n  "name": "{{product_name}}",\n  "image": "{{image_url}}",\n  "description": "{{description}}",\n  "brand": {"@type": "Brand", "name": "{{brand_name}}"},\n  "offers": {"@type": "Offer", "url": "{{product_url}}", "priceCurrency": "{{currency}}", "price": "{{price}}", "availability": "https://schema.org/{{availability}}", "priceValidUntil": "{{valid_until}}"},\n  "aggregateRating": {"@type": "AggregateRating", "ratingValue": "{{rating}}", "reviewCount": "{{review_count}}"}\n}',
                "description": "Schema for e-commerce products",
                "example": "Physical products, digital goods",
            },
            {
                "id": "schema_faq",
                "schema_type": "FAQPage",
                "name": "FAQ Page",
                "template": '{\n  "@context": "https://schema.org",\n  "@type": "FAQPage",\n  "mainEntity": [{{faq_items}}]\n}',
                "description": "Schema for FAQ pages to get rich snippets",
                "example": "FAQ sections, help pages",
            },
            {
                "id": "schema_howto",
                "schema_type": "HowTo",
                "name": "How-To Guide",
                "template": '{\n  "@context": "https://schema.org",\n  "@type": "HowTo",\n  "name": "{{title}}",\n  "description": "{{description}}",\n  "image": "{{image_url}}",\n  "totalTime": "{{duration}}",\n  "step": [{{steps}}]\n}',
                "description": "Schema for how-to guides and tutorials",
                "example": "DIY guides, recipes, tutorials",
            },
            {
                "id": "schema_breadcrumbs",
                "schema_type": "BreadcrumbList",
                "name": "Breadcrumbs",
                "template": '{\n  "@context": "https://schema.org",\n  "@type": "BreadcrumbList",\n  "itemListElement": [{{breadcrumb_items}}]\n}',
                "description": "Schema for breadcrumb navigation",
                "example": "Site navigation breadcrumbs",
            },
        ]
        for t in templates:
            self.cursor.execute(
                "INSERT OR REPLACE INTO schema_templates (id, schema_type, name, template, description, example) VALUES (?, ?, ?, ?, ?, ?)",
                (t["id"], t["schema_type"], t["name"], t["template"], t["description"], t["example"]),
            )
        self.conn.commit()

    def init_meta_templates(self):
        """Initialize meta tag templates (unchanged from original)"""
        templates = [
            {"id": "meta_viewport", "tag_type": "viewport", "name": "Viewport", "template": '<meta name="viewport" content="width=device-width, initial-scale=1.0">', "description": "Essential for mobile-responsive design", "priority": 1},
            {"id": "meta_charset", "tag_type": "charset", "name": "Character Set", "template": '<meta charset="UTF-8">', "description": "Defines character encoding", "priority": 1},
            {"id": "meta_description", "tag_type": "description", "name": "Meta Description", "template": '<meta name="description" content="{{description}}">', "description": "Search result snippet (150-160 chars)", "priority": 1},
            {"id": "meta_keywords", "tag_type": "keywords", "name": "Meta Keywords", "template": '<meta name="keywords" content="{{keywords}}">', "description": "Less important now but still used", "priority": 3},
            {"id": "meta_robots", "tag_type": "robots", "name": "Robots", "template": '<meta name="robots" content="{{directive}}">', "description": "index/follow, noindex, nofollow", "priority": 2},
            {"id": "meta_canonical", "tag_type": "canonical", "name": "Canonical URL", "template": '<link rel="canonical" href="{{canonical_url}}">', "description": "Prevents duplicate content issues", "priority": 1},
            {"id": "meta_author", "tag_type": "author", "name": "Author", "template": '<meta name="author" content="{{author_name}}">', "description": "Content author name", "priority": 3},
            {"id": "og_title", "tag_type": "open_graph", "name": "OG Title", "template": '<meta property="og:title" content="{{title}}">', "description": "Facebook/Open Graph title", "priority": 2},
            {"id": "og_description", "tag_type": "open_graph", "name": "OG Description", "template": '<meta property="og:description" content="{{description}}">', "description": "Facebook/Open Graph description", "priority": 2},
            {"id": "og_image", "tag_type": "open_graph", "name": "OG Image", "template": '<meta property="og:image" content="{{image_url}}">', "description": "Facebook/Open Graph image", "priority": 2},
            {"id": "og_url", "tag_type": "open_graph", "name": "OG URL", "template": '<meta property="og:url" content="{{url}}">', "description": "Facebook/Open Graph canonical URL", "priority": 2},
            {"id": "og_type", "tag_type": "open_graph", "name": "OG Type", "template": '<meta property="og:type" content="{{type}}">', "description": "Content type: website, article, product", "priority": 2},
            {"id": "twitter_card", "tag_type": "twitter", "name": "Twitter Card", "template": '<meta name="twitter:card" content="{{card_type}}">', "description": "summary, summary_large_image, app, player", "priority": 2},
            {"id": "twitter_title", "tag_type": "twitter", "name": "Twitter Title", "template": '<meta name="twitter:title" content="{{title}}">', "description": "Twitter card title", "priority": 2},
            {"id": "twitter_description", "tag_type": "twitter", "name": "Twitter Description", "template": '<meta name="twitter:description" content="{{description}}">', "description": "Twitter card description", "priority": 2},
            {"id": "twitter_image", "tag_type": "twitter", "name": "Twitter Image", "template": '<meta name="twitter:image" content="{{image_url}}">', "description": "Twitter card image", "priority": 2},
        ]
        for t in templates:
            self.cursor.execute(
                "INSERT OR REPLACE INTO meta_templates (id, tag_type, name, template, description, priority) VALUES (?, ?, ?, ?, ?, ?)",
                (t["id"], t["tag_type"], t["name"], t["template"], t["description"], t["priority"]),
            )
        self.conn.commit()

    def get_schema_templates(self, schema_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if schema_type:
            self.cursor.execute("SELECT * FROM schema_templates WHERE schema_type = ?", (schema_type,))
        else:
            self.cursor.execute("SELECT * FROM schema_templates")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_meta_templates(self, tag_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if tag_type:
            self.cursor.execute("SELECT * FROM meta_templates WHERE tag_type = ? ORDER BY priority", (tag_type,))
        else:
            self.cursor.execute("SELECT * FROM meta_templates ORDER BY priority")
        return [dict(row) for row in self.cursor.fetchall()]


if __name__ == "__main__":
    kb = SEOKnowledgeBase().connect().init_database()
    kb.init_schema_templates()
    kb.init_meta_templates()
    print("Database initialized with templates")
    kb.close()
