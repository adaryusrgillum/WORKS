"""
EPUB Parser Module for SEO Bot
Extracts and processes content from EPUB files for knowledge base
"""

import warnings
warnings.filterwarnings('ignore')

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib


class EPUBParser:
    """Parse EPUB files and extract structured content"""
    
    def __init__(self):
        self.books = []
    
    def parse_epub(self, filepath: str) -> Dict[str, Any]:
        """Parse a single EPUB file and extract all relevant content"""
        book = epub.read_epub(filepath)
        
        book_data = {
            'title': self._get_metadata(book, 'title'),
            'author': self._get_metadata(book, 'creator'),
            'language': self._get_metadata(book, 'language'),
            'identifier': self._get_metadata(book, 'identifier'),
            'chapters': [],
            'filepath': filepath,
            'book_id': hashlib.md5(filepath.encode()).hexdigest()[:12]
        }
        
        # Extract chapters
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                chapter = self._parse_chapter(item)
                if chapter and len(chapter['content']) > 100:
                    book_data['chapters'].append(chapter)
        
        return book_data
    
    def _get_metadata(self, book, name: str) -> str:
        """Safely get metadata from EPUB"""
        try:
            data = book.get_metadata('DC', name)
            return data[0][0] if data else 'Unknown'
        except:
            return 'Unknown'
    
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
                # Try to get from file name
                title = item.get_name().split('/')[-1].replace('.html', '').replace('.xhtml', '').replace('_', ' ').title()
            
            # Get text content
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            text = self._clean_text(text)
            
            return {
                'id': item.get_id(),
                'name': item.get_name(),
                'title': title,
                'content': text,
                'word_count': len(text.split())
            }
        except Exception as e:
            print(f"Error parsing chapter {item.get_name()}: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        return text.strip()
    
    def extract_seo_knowledge(self, book_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract SEO-specific knowledge chunks from book"""
        knowledge_chunks = []
        
        seo_keywords = [
            'meta tag', 'schema.org', 'structured data', 'json-ld', 'rich snippet',
            'open graph', 'twitter card', 'canonical', 'robots.txt', 'sitemap',
            'keyword research', 'backlink', 'domain authority', 'page rank',
            'on-page seo', 'off-page seo', 'technical seo', 'local seo',
            'content optimization', 'title tag', 'meta description', 'header tag',
            'alt text', 'internal linking', 'url structure', 'site speed',
            'mobile optimization', 'core web vitals', 'lighthouse',
            'google search console', 'google analytics', 'ranking factor',
            'search intent', 'semantic search', 'voice search', 'featured snippet'
        ]
        
        for chapter in book_data['chapters']:
            content = chapter['content']
            
            # Split into paragraphs/sections
            paragraphs = [p.strip() for p in content.split('\n') if len(p.strip()) > 50]
            
            for i, para in enumerate(paragraphs):
                para_lower = para.lower()
                
                # Check if paragraph contains SEO-relevant content
                relevance_score = sum(1 for kw in seo_keywords if kw in para_lower)
                
                if relevance_score > 0 or any(kw in para_lower for kw in ['seo', 'search engine', 'google', 'ranking']):
                    chunk = {
                        'book_id': book_data['book_id'],
                        'book_title': book_data['title'],
                        'chapter_title': chapter['title'],
                        'content': para,
                        'chunk_id': f"{book_data['book_id']}_{chapter['id']}_{i}",
                        'relevance_score': relevance_score,
                        'category': self._categorize_content(para_lower)
                    }
                    knowledge_chunks.append(chunk)
        
        return knowledge_chunks
    
    def extract_chunks_for_embedding(
        self,
        book_data: Dict[str, Any],
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Extract 500-word chunks for vector DB embedding.
        Full coverage for semantic search (not keyword-filtered).
        """
        chunks = []
        for chapter in book_data['chapters']:
            text = chapter['content']
            words = text.split()
            start = 0
            idx = 0
            while start < len(words):
                end = min(start + chunk_size, len(words))
                chunk_text = ' '.join(words[start:end])
                if len(chunk_text.strip()) < 50:
                    break
                chunks.append({
                    'chunk_id': f"{book_data['book_id']}_{chapter['id']}_{idx}",
                    'book_id': book_data['book_id'],
                    'book_title': book_data['title'],
                    'chapter_title': chapter['title'],
                    'content': chunk_text,
                    'category': self._categorize_content(chunk_text.lower()),
                    'relevance_score': 0,
                })
                start = end - overlap
                idx += 1
                if start >= len(words):
                    break
        return chunks

    def _categorize_content(self, text: str) -> str:
        """Categorize content by SEO topic"""
        categories = {
            'meta_tags': ['meta tag', 'meta description', 'title tag', 'viewport'],
            'structured_data': ['schema.org', 'structured data', 'json-ld', 'microdata', 'rich snippet'],
            'technical_seo': ['robots.txt', 'sitemap', 'canonical', 'redirect', 'crawl', 'index'],
            'on_page': ['content optimization', 'keyword density', 'header tag', 'h1', 'h2', 'alt text'],
            'off_page': ['backlink', 'link building', 'guest post', 'social signal'],
            'local_seo': ['google business', 'local pack', 'citation', 'nap'],
            'analytics': ['google analytics', 'search console', 'tracking', 'conversion'],
            'performance': ['site speed', 'core web vitals', 'lighthouse', 'page speed']
        }
        
        scores = {}
        for cat, keywords in categories.items():
            scores[cat] = sum(1 for kw in keywords if kw in text)
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'general'
    
    def parse_all_books(self, directory: str = '.') -> List[Dict[str, Any]]:
        """Parse all EPUB files in directory"""
        path = Path(directory)
        epub_files = list(path.glob('*.epub'))
        
        all_books = []
        all_knowledge = []
        
        for epub_file in epub_files:
            print(f"Parsing: {epub_file.name}")
            try:
                book_data = self.parse_epub(str(epub_file))
                all_books.append(book_data)

                # Use 500-word chunks for semantic search (full coverage)
                knowledge = self.extract_chunks_for_embedding(book_data)
                all_knowledge.extend(knowledge)
                
                print(f"  - Extracted {len(knowledge)} knowledge chunks from {len(book_data['chapters'])} chapters")
            except Exception as e:
                print(f"  - Error: {e}")
        
        return all_books, all_knowledge


if __name__ == '__main__':
    parser = EPUBParser()
    books, knowledge = parser.parse_all_books('.')
    
    # Save knowledge to JSON for inspection
    with open('extracted_knowledge.json', 'w', encoding='utf-8') as f:
        json.dump(knowledge[:100], f, indent=2, ensure_ascii=False)
    
    print(f"\nTotal knowledge chunks: {len(knowledge)}")
    print(f"Categories: {set(k['category'] for k in knowledge)}")
