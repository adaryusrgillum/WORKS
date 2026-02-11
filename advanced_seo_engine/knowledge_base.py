"""
Vector Knowledge Base with ChromaDB
Advanced embedding-based retrieval system for EPUB content
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


class VectorKnowledgeBase:
    """
    Advanced vector knowledge base using ChromaDB and sentence transformers.
    Provides semantic search across EPUB books with multi-book fusion.
    """
    
    def __init__(self, 
                 persist_directory: str = "./chroma_db",
                 embedding_model: str = "BAAI/bge-large-en-v1.5",
                 collection_name: str = "seo_knowledge"):
        """
        Initialize the vector knowledge base.
        
        Args:
            persist_directory: Where to store ChromaDB files
            embedding_model: Sentence transformer model for embeddings
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model
        self.collection_name = collection_name
        
        # Initialize embedding model
        print(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Track document sources
        self.sources = {}
        
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text"""
        # BGE models work best with instruction prefix
        instruction = "Represent this sentence for searching relevant passages: "
        embedding = self.embedding_model.encode(
            instruction + text,
            normalize_embeddings=True
        )
        return embedding.tolist()
    
    def add_documents(self, 
                      documents: List[Dict[str, Any]], 
                      batch_size: int = 100) -> None:
        """
        Add documents to the knowledge base.
        
        Args:
            documents: List of dicts with keys: id, text, metadata
            batch_size: Number of documents to process at once
        """
        total = len(documents)
        print(f"Adding {total} documents to knowledge base...")
        
        for i in range(0, total, batch_size):
            batch = documents[i:i + batch_size]
            
            ids = [doc['id'] for doc in batch]
            texts = [doc['text'] for doc in batch]
            metadatas = [doc.get('metadata', {}) for doc in batch]
            
            # Generate embeddings
            embeddings = [self.embed_text(text) for text in texts]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            print(f"  Processed {min(i + batch_size, total)}/{total} documents")
        
        print(f"✅ Added {total} documents to knowledge base")
    
    def search(self, 
               query: str, 
               n_results: int = 10,
               filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of result dicts with text, metadata, and distance
        """
        query_embedding = self.embed_text(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        
        return formatted_results
    
    def multi_book_search(self,
                         query: str,
                         n_results: int = 10,
                         diversity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Search across multiple books with diversity scoring.
        Ensures results come from different sources for broader perspective.
        """
        # Get more results initially for diversity filtering
        initial_results = self.search(query, n_results=n_results * 3)
        
        # Group by book/source
        by_source = {}
        for result in initial_results:
            source = result['metadata'].get('book_title', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(result)
        
        # Select diverse results (round-robin from each source)
        diverse_results = []
        source_indices = {s: 0 for s in by_source}
        
        while len(diverse_results) < n_results and any(
            source_indices[s] < len(by_source[s]) for s in by_source
        ):
            for source in by_source:
                idx = source_indices[source]
                if idx < len(by_source[source]):
                    diverse_results.append(by_source[source][idx])
                    source_indices[source] += 1
                    if len(diverse_results) >= n_results:
                        break
        
        return diverse_results
    
    def semantic_fusion(self,
                       query: str,
                       n_results: int = 5) -> Dict[str, Any]:
        """
        Perform semantic fusion - merge related concepts from multiple sources
        into a unified understanding.
        """
        results = self.multi_book_search(query, n_results=n_results * 2)
        
        if not results:
            return {'fused_content': '', 'sources': [], 'concepts': []}
        
        # Extract key concepts (simple approach - can be enhanced with NER)
        all_text = ' '.join([r['text'] for r in results])
        words = all_text.lower().split()
        
        # Find frequently mentioned terms (simple concept extraction)
        from collections import Counter
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
                     'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has',
                     'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see',
                     'two', 'who', 'boy', 'did', 'she', 'use', 'her', 'way', 'many',
                     'oil', 'sit', 'set', 'run', 'eat', 'far', 'sea', 'eye', 'too',
                     'any', 'try', 'ask', 'end', 'why', 'let', 'put', 'say', 'too',
                     'old', 'tell', 'very', 'when', 'much', 'would', 'there', 'their',
                     'what', 'said', 'each', 'which', 'will', 'about', 'could', 'other',
                     'after', 'first', 'never', 'these', 'think', 'where', 'being',
                     'every', 'great', 'might', 'shall', 'still', 'those', 'while',
                     'this', 'that', 'with', 'have', 'from', 'they', 'been', 'were',
                     'said', 'time', 'than', 'them', 'into', 'just', 'like', 'over',
                     'also', 'back', 'only', 'know', 'take', 'year', 'good', 'some',
                     'come', 'make', 'well', 'look', 'down', 'most', 'long', 'last',
                     'find', 'give', 'does', 'made', 'part', 'such', 'keep', 'call',
                     'came', 'need', 'feel', 'seem', 'turn', 'hand', 'high', 'sure',
                     'upon', 'head', 'help', 'home', 'side', 'move', 'both', 'five',
                     'once', 'same', 'must', 'name', 'left', 'each', 'done', 'open',
                     'case', 'show', 'live', 'play', 'went', 'told', 'seen', 'hear',
                     'talk', 'soon', 'read', 'stop', 'face', 'fact', 'land', 'line',
                     'kind', 'next', 'word', 'is', 'to', 'of', 'a', 'in', 'on', 'at',
                     'by', 'as', 'it', 'or', 'be', 'an', 'if', 'up', 'so', 'no', 'go',
                     'me', 'we', 'do', 'am', 'my', 'us', 'he', 'ha', 'wa'}
        
        concepts = [w for w in words if len(w) > 4 and w not in stop_words]
        top_concepts = [c for c, _ in Counter(concepts).most_common(10)]
        
        # Create fused content summary
        fused_content = '\n\n'.join([
            f"[{r['metadata'].get('book_title', 'Unknown')}] {r['text'][:300]}..."
            for r in results[:n_results]
        ])
        
        return {
            'fused_content': fused_content,
            'sources': list(set(r['metadata'].get('book_title', 'Unknown') for r in results)),
            'concepts': top_concepts,
            'raw_results': results[:n_results]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        count = self.collection.count()
        
        # Get unique sources
        all_meta = self.collection.get(include=['metadatas'])
        sources = set()
        categories = set()
        
        if all_meta['metadatas']:
            for meta in all_meta['metadatas']:
                if meta:
                    sources.add(meta.get('book_title', 'unknown'))
                    categories.add(meta.get('category', 'unknown'))
        
        return {
            'total_documents': count,
            'sources': list(sources),
            'categories': list(categories),
            'embedding_model': self.embedding_model_name,
            'collection_name': self.collection_name
        }
    
    def delete_collection(self):
        """Delete the entire collection"""
        self.client.delete_collection(self.collection_name)
        print(f"Deleted collection: {self.collection_name}")


if __name__ == '__main__':
    # Test the knowledge base
    kb = VectorKnowledgeBase(persist_directory="./test_chroma")
    
    # Add test documents
    test_docs = [
        {
            'id': 'doc1',
            'text': 'SEO meta tags are crucial for search engine optimization. The title tag should be 50-60 characters.',
            'metadata': {'book_title': 'SEO Guide', 'category': 'meta_tags', 'chapter': 'Chapter 1'}
        },
        {
            'id': 'doc2',
            'text': 'Schema.org structured data helps search engines understand your content better.',
            'metadata': {'book_title': 'SEO Guide', 'category': 'structured_data', 'chapter': 'Chapter 2'}
        },
        {
            'id': 'doc3',
            'text': 'Backlinks are still one of the most important ranking factors in SEO.',
            'metadata': {'book_title': 'Advanced SEO', 'category': 'off_page', 'chapter': 'Chapter 5'}
        }
    ]
    
    kb.add_documents(test_docs)
    
    # Test search
    results = kb.search("meta tags optimization", n_results=2)
    print("\nSearch results:")
    for r in results:
        print(f"  {r['similarity']:.3f}: {r['text'][:100]}...")
    
    # Test semantic fusion
    fusion = kb.semantic_fusion("SEO best practices")
    print("\nSemantic fusion sources:", fusion['sources'])
    print("Key concepts:", fusion['concepts'])
