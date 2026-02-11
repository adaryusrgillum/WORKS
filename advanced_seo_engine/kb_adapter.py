"""
Adapter to make the main SEOKnowledgeBase compatible with advanced agents.
Agents expect: search(query, n_results=N) -> [{text, metadata: {book_title, ...}}]
Main KB returns: search(query, limit=N) -> [{content, book_title, chapter_title, category, ...}]
"""

from typing import List, Dict, Any, Optional


class SEOKnowledgeBaseAdapter:
    """
    Wraps SEOKnowledgeBase to provide the interface expected by
    SEOStrategist, SchemaArchitect, MetaTagOptimizer, ContentCritic.
    """

    def __init__(self, seo_kb):
        """
        Args:
            seo_kb: SEOKnowledgeBase instance (from knowledge_base.py)
        """
        self._kb = seo_kb

    def search(
        self,
        query: str,
        n_results: int = 5,
        limit: Optional[int] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search and return results in agent-expected format.
        """
        limit = limit or n_results
        results = self._kb.search(query, limit=limit, category=category)

        return [
            {
                "id": r.get("id", ""),
                "text": r.get("content", ""),
                "metadata": {
                    "book_title": r.get("book_title", "Unknown"),
                    "chapter_title": r.get("chapter_title", ""),
                    "category": r.get("category", "general"),
                },
                "similarity": r.get("similarity", 0),
            }
            for r in results
        ]
