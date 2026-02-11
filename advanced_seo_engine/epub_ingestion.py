"""
EPUB Ingestion Pipeline
Extracts, chunks, and indexes EPUB content for the knowledge base
"""

import os
import re
import hashlib
from typing import List, Dict, Any, Optional, Generator
from pathlib import Path
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Handle ebooklib import with warnings suppressed
try:
    import ebooklib
    from ebooklib import epub
except Exception as e:
    print(f"Warning: Could not import ebooklib: {e}")
    ebooklib = None
    epub = None

from bs4 import BeautifulSoup


@dataclass
class TextChunk:
    """Represents a chunk of text from a book"""
    id: str
    text: str
    book_title: str
    book_author: str
    chapter_title: str
    chunk_index: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'text': self.text,
            'metadata': {
                'book_title': self.book_title,
                'book_author': self.book_author,
                'chapter_title': self.chapter_title,
                'chunk_index': self.chunk_index,
                **self.metadata
            }
        }


class EPUBIngestionPipeline:
    """
    Pipeline for ingesting EPUB books into the knowledge base.
    Handles extraction, cleaning, chunking, and concept extraction.
    """
    
    def __init__(self, 
                 chunk_size: int = 500,
                 chunk_overlap: int = 50,
                 min_chunk_size: int = 100):
        """
        Initialize the ingestion pipeline.
        
        Args:
            chunk_size: Target size of each chunk in words
            chunk_overlap: Number of words to overlap between chunks
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        # SEO-related keywords for categorization
        self.seo_categories = {
            'meta_tags': ['meta tag', 'title tag', 'meta description', 'viewport', 'canonical'],
            'structured_data': ['schema.org', 'json-ld', 'structured data', 'rich snippet', 'microdata'],
            'technical_seo': ['robots.txt', 'sitemap', 'crawl', 'index', 'redirect', 'canonical'],
            'on_page': ['content optimization', 'keyword density', 'header tag', 'h1', 'h2', 'alt text'],
            'off_page': ['backlink', 'link building', 'domain authority', 'page rank'],
            'local_seo': ['google business', 'local pack', 'citation', 'nap'],
            'analytics': ['google analytics', 'search console', 'tracking', 'conversion'],
            'performance': ['site speed', 'core web vitals', 'lighthouse', 'page speed']
        }
    
    def extract_epub(self, filepath: str) -> Dict[str, Any]:
        """
        Extract content from an EPUB file.
        
        Args:
            filepath: Path to EPUB file
            
        Returns:
            Dictionary with book metadata and chapters
        """
        if ebooklib is None:
            raise ImportError("ebooklib not available. Please install it.")
        
        print(f"📖 Extracting: {Path(filepath).name}")
        
        book = epub.read_epub(filepath)
        
        # Extract metadata
        book_data = {
            'title': self._get_metadata(book, 'title') or Path(filepath).stem,
            'author': self._get_metadata(book, 'creator') or 'Unknown',
            'language': self._get_metadata(book, 'language') or 'en',
            'identifier': self._get_metadata(book, 'identifier') or '',
            'chapters': [],
            'filepath': filepath
        }
        
        # Extract chapters
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                chapter = self._parse_chapter(item)
                if chapter and len(chapter['content']) > self.min_chunk_size:
                    book_data['chapters'].append(chapter)
        
        print(f"   ✓ Extracted {len(book_data['chapters'])} chapters")
        return book_data
    
    def _get_metadata(self, book, name: str) -> Optional[str]:
        """Safely get metadata from EPUB"""
        try:
            data = book.get_metadata('DC', name)
            return data[0][0] if data else None
        except:
            return None
    
    def _parse_chapter(self, item) -> Optional[Dict[str, Any]]:
        """Parse a single chapter/document item"""
        try:
            content = item.get_content().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get title
            title = ''
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
            else:
                title = item.get_name().split('/')[-1].replace('.html', '').replace('.xhtml', '').replace('_', ' ').title()
            
            # Get text content
            text = soup.get_text(separator='\n', strip=True)
            text = self._clean_text(text)
            
            return {
                'id': item.get_id(),
                'name': item.get_name(),
                'title': title,
                'content': text,
                'word_count': len(text.split())
            }
        except Exception as e:
            print(f"   ⚠ Error parsing chapter {item.get_name()}: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', ' ', text)
        return text.strip()
    
    def chunk_text(self, text: str, 
                   book_title: str,
                   book_author: str,
                   chapter_title: str) -> List[TextChunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            book_title: Book title
            book_author: Book author
            chapter_title: Chapter title
            
        Returns:
            List of TextChunk objects
        """
        words = text.split()
        chunks = []
        
        # Calculate chunk boundaries
        start = 0
        chunk_index = 0
        
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            # Skip if too short
            if len(chunk_text) >= self.min_chunk_size:
                # Generate unique ID
                content_hash = hashlib.md5(chunk_text.encode()).hexdigest()[:12]
                chunk_id = f"{self._sanitize_id(book_title)}_{self._sanitize_id(chapter_title)}_{chunk_index}_{content_hash}"
                
                # Determine category
                category = self._categorize_content(chunk_text)
                
                chunk = TextChunk(
                    id=chunk_id,
                    text=chunk_text,
                    book_title=book_title,
                    book_author=book_author,
                    chapter_title=chapter_title,
                    chunk_index=chunk_index,
                    metadata={
                        'word_count': len(chunk_words),
                        'category': category,
                        'start_word': start,
                        'end_word': end
                    }
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # Move to next chunk with overlap
            start += self.chunk_size - self.chunk_overlap
            
            # Prevent infinite loop on small chunks
            if start >= end:
                break
        
        return chunks
    
    def _sanitize_id(self, text: str) -> str:
        """Create a safe ID from text"""
        return re.sub(r'[^\w]', '_', text.lower())[:30]
    
    def _categorize_content(self, text: str) -> str:
        """Categorize content by SEO topic"""
        text_lower = text.lower()
        
        scores = {}
        for category, keywords in self.seo_categories.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        return 'general'
    
    def process_book(self, filepath: str) -> List[TextChunk]:
        """
        Process a single EPUB book into chunks.
        
        Args:
            filepath: Path to EPUB file
            
        Returns:
            List of TextChunk objects
        """
        book_data = self.extract_epub(filepath)
        all_chunks = []
        
        print(f"   Chunking {len(book_data['chapters'])} chapters...")
        
        for chapter in book_data['chapters']:
            chunks = self.chunk_text(
                chapter['content'],
                book_data['title'],
                book_data['author'],
                chapter['title']
            )
            all_chunks.extend(chunks)
        
        print(f"   ✓ Created {len(all_chunks)} chunks")
        return all_chunks
    
    def process_directory(self, directory: str, 
                         pattern: str = "*.epub") -> List[TextChunk]:
        """
        Process all EPUB files in a directory.
        
        Args:
            directory: Directory to search
            pattern: File pattern to match
            
        Returns:
            List of TextChunk objects from all books
        """
        path = Path(directory)
        epub_files = list(path.glob(pattern))
        
        if not epub_files:
            print(f"⚠ No EPUB files found in {directory}")
            return []
        
        print(f"\n📚 Found {len(epub_files)} EPUB file(s)")
        print("="*60)
        
        all_chunks = []
        for epub_file in epub_files:
            try:
                chunks = self.process_book(str(epub_file))
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"   ❌ Error processing {epub_file.name}: {e}")
        
        print("="*60)
        print(f"✅ Total chunks created: {len(all_chunks)}")
        
        return all_chunks
    
    def extract_concepts(self, chunks: List[TextChunk]) -> Dict[str, List[str]]:
        """
        Extract key concepts from chunks for concept graph.
        
        Args:
            chunks: List of TextChunk objects
            
        Returns:
            Dictionary mapping concepts to chunk IDs
        """
        concept_map = {}
        
        for chunk in chunks:
            # Extract potential concepts (capitalized phrases)
            words = chunk.text.split()
            for i, word in enumerate(words):
                if word[0].isupper() and len(word) > 3:
                    # Get phrase (up to 3 words)
                    phrase = word
                    if i + 1 < len(words) and words[i + 1][0].isupper():
                        phrase += ' ' + words[i + 1]
                    
                    if phrase not in concept_map:
                        concept_map[phrase] = []
                    concept_map[phrase].append(chunk.id)
        
        # Filter to concepts that appear multiple times
        return {k: v for k, v in concept_map.items() if len(v) >= 2}
    
    def get_stats(self, chunks: List[TextChunk]) -> Dict[str, Any]:
        """Get statistics about processed chunks"""
        if not chunks:
            return {}
        
        books = set(c.book_title for c in chunks)
        categories = {}
        for c in chunks:
            cat = c.metadata.get('category', 'general')
            categories[cat] = categories.get(cat, 0) + 1
        
        word_counts = [c.metadata.get('word_count', 0) for c in chunks]
        
        return {
            'total_chunks': len(chunks),
            'total_books': len(books),
            'books': list(books),
            'categories': categories,
            'avg_chunk_size': sum(word_counts) / len(word_counts) if word_counts else 0,
            'min_chunk_size': min(word_counts) if word_counts else 0,
            'max_chunk_size': max(word_counts) if word_counts else 0
        }


def ingest_epubs_to_knowledge_base(directory: str = ".",
                                   knowledge_base=None,
                                   concept_graph=None) -> Dict[str, Any]:
    """
    Convenience function to ingest all EPUBs into the knowledge base.
    
    Args:
        directory: Directory containing EPUB files
        knowledge_base: VectorKnowledgeBase instance
        concept_graph: ConceptGraph instance
        
    Returns:
        Statistics about the ingestion
    """
    pipeline = EPUBIngestionPipeline()
    
    # Process all EPUBs
    chunks = pipeline.process_directory(directory)
    
    if not chunks:
        return {'status': 'error', 'message': 'No chunks created'}
    
    stats = pipeline.get_stats(chunks)
    
    # Add to knowledge base
    if knowledge_base:
        print("\n📥 Adding to knowledge base...")
        documents = [c.to_dict() for c in chunks]
        knowledge_base.add_documents(documents)
    
    # Add to concept graph
    if concept_graph:
        print("\n🕸️  Building concept graph...")
        concepts = pipeline.extract_concepts(chunks)
        
        for concept, chunk_ids in concepts.items():
            # Add concept node
            concept_graph.add_concept(
                concept,
                concept_type='extracted',
                source='epub_ingestion'
            )
            
            # Add relationships to chunks (as metadata references)
            for chunk_id in chunk_ids[:5]:  # Limit to avoid too many edges
                concept_graph.add_relationship(
                    concept,
                    f"chunk:{chunk_id}",
                    'appears_in',
                    weight=len(chunk_ids) / 100
                )
        
        concept_graph.save()
    
    return {
        'status': 'success',
        'stats': stats
    }


if __name__ == '__main__':
    # Test the pipeline
    pipeline = EPUBIngestionPipeline(chunk_size=300, chunk_overlap=30)
    
    # Process any EPUBs in current directory
    chunks = pipeline.process_directory('.')
    
    if chunks:
        stats = pipeline.get_stats(chunks)
        print("\n📊 Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Show sample chunk
        print("\n📄 Sample chunk:")
        sample = chunks[0]
        print(f"   Book: {sample.book_title}")
        print(f"   Chapter: {sample.chapter_title}")
        print(f"   Category: {sample.metadata['category']}")
        print(f"   Text: {sample.text[:200]}...")
