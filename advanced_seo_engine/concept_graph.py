"""
Concept Graph Layer
Builds and maintains a knowledge graph of SEO concepts, entities, and relationships
"""

import json
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict
import networkx as nx
from pathlib import Path


class ConceptGraph:
    """
    Knowledge graph for SEO concepts and entities.
    Enables cross-book reasoning and concept expansion.
    """
    
    # SEO-specific entity types
    ENTITY_TYPES = {
        'seo_concept': ['keyword', 'backlink', 'ranking', 'crawl', 'index', 'sitemap'],
        'schema_type': ['Article', 'Product', 'LocalBusiness', 'FAQPage', 'HowTo', 'BreadcrumbList'],
        'meta_tag': ['title', 'description', 'viewport', 'canonical', 'robots', 'og:title'],
        'technical_term': ['canonical', 'redirect', 'robots.txt', 'hreflang', 'amp'],
        'tool': ['Google Search Console', 'Google Analytics', 'Screaming Frog', 'Ahrefs', 'SEMrush'],
        'metric': ['CTR', 'bounce rate', 'dwell time', 'domain authority', 'page authority']
    }
    
    # Relationship types
    RELATIONSHIPS = {
        'is_a_type_of': 'hierarchical',
        'is_related_to': 'associative',
        'is_used_for': 'functional',
        'improves': 'causal_positive',
        'reduces': 'causal_negative',
        'requires': 'dependency',
        'is_part_of': 'compositional',
        'contradicts': 'opposition',
        'causes': 'causal',
        'belongs_to': 'categorical'
    }
    
    def __init__(self, graph_path: Optional[str] = None):
        """Initialize the concept graph"""
        self.graph = nx.DiGraph()
        self.graph_path = graph_path or "./concept_graph.json"
        
        # Load existing graph if available
        if Path(self.graph_path).exists():
            self.load()
    
    def add_concept(self, 
                   concept: str, 
                   concept_type: str = 'general',
                   source: Optional[str] = None,
                   metadata: Optional[Dict] = None) -> None:
        """
        Add a concept node to the graph.
        
        Args:
            concept: The concept name
            concept_type: Type of concept (seo_concept, schema_type, etc.)
            source: Source book or document
            metadata: Additional metadata
        """
        if concept not in self.graph:
            self.graph.add_node(
                concept,
                type=concept_type,
                sources=[source] if source else [],
                metadata=metadata or {},
                mention_count=1
            )
        else:
            # Update existing node
            node = self.graph.nodes[concept]
            node['mention_count'] = node.get('mention_count', 0) + 1
            if source and source not in node['sources']:
                node['sources'].append(source)
    
    def add_relationship(self,
                        source: str,
                        target: str,
                        relationship: str,
                        weight: float = 1.0,
                        evidence: Optional[str] = None) -> None:
        """
        Add a relationship edge between two concepts.
        
        Args:
            source: Source concept
            target: Target concept
            relationship: Type of relationship
            weight: Relationship strength (0-1)
            evidence: Supporting text/evidence
        """
        # Ensure nodes exist
        if source not in self.graph:
            self.add_concept(source)
        if target not in self.graph:
            self.add_concept(target)
        
        # Add or update edge
        if self.graph.has_edge(source, target):
            # Update existing edge
            edge = self.graph[source][target]
            edge['weight'] = max(edge['weight'], weight)
            edge['mention_count'] = edge.get('mention_count', 0) + 1
            if evidence and evidence not in edge.get('evidence', []):
                if 'evidence' not in edge:
                    edge['evidence'] = []
                edge['evidence'].append(evidence)
        else:
            # Create new edge
            self.graph.add_edge(
                source, target,
                relationship=relationship,
                weight=weight,
                mention_count=1,
                evidence=[evidence] if evidence else []
            )
    
    def extract_concepts_from_text(self, 
                                   text: str, 
                                   source: str,
                                   min_length: int = 4) -> List[str]:
        """
        Extract potential concepts from text.
        Simple implementation - can be enhanced with NER.
        """
        concepts = []
        
        # Look for defined terms (capitalized phrases)
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(pattern, text)
        
        for match in matches:
            if len(match) >= min_length:
                concepts.append(match)
        
        # Look for SEO-specific terms
        text_lower = text.lower()
        for category, terms in self.ENTITY_TYPES.items():
            for term in terms:
                if term.lower() in text_lower:
                    concepts.append(term)
        
        return list(set(concepts))
    
    def expand_concept(self, 
                      concept: str, 
                      depth: int = 2) -> Dict[str, Any]:
        """
        Expand a concept by traversing the graph.
        
        Args:
            concept: Starting concept
            depth: How many hops to traverse
            
        Returns:
            Dictionary with related concepts and paths
        """
        if concept not in self.graph:
            return {'concept': concept, 'related': [], 'paths': []}
        
        related = set()
        paths = []
        
        # BFS traversal
        visited = {concept}
        queue = [(concept, 0, [concept])]
        
        while queue:
            current, current_depth, path = queue.pop(0)
            
            if current_depth >= depth:
                continue
            
            # Get neighbors
            for neighbor in self.graph.successors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    related.add(neighbor)
                    new_path = path + [neighbor]
                    paths.append(new_path)
                    queue.append((neighbor, current_depth + 1, new_path))
            
            for neighbor in self.graph.predecessors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    related.add(neighbor)
                    new_path = path + [neighbor]
                    paths.append(new_path)
                    queue.append((neighbor, current_depth + 1, new_path))
        
        return {
            'concept': concept,
            'related': list(related),
            'paths': paths,
            'entity_type': self.graph.nodes[concept].get('type', 'unknown')
        }
    
    def find_paths(self, 
                  source: str, 
                  target: str,
                  max_length: int = 4) -> List[List[str]]:
        """
        Find paths between two concepts.
        
        Args:
            source: Starting concept
            target: Target concept
            max_length: Maximum path length
            
        Returns:
            List of paths (each path is a list of concepts)
        """
        if source not in self.graph or target not in self.graph:
            return []
        
        try:
            paths = list(nx.all_simple_paths(
                self.graph, source, target, cutoff=max_length
            ))
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def get_centrality_scores(self) -> Dict[str, float]:
        """Get centrality scores for all concepts"""
        if len(self.graph) == 0:
            return {}
        
        return nx.degree_centrality(self.graph)
    
    def get_communities(self) -> List[List[str]]:
        """Find concept communities using Louvain algorithm"""
        if len(self.graph) == 0:
            return []
        
        # Convert to undirected for community detection
        undirected = self.graph.to_undirected()
        
        try:
            from community import community_louvain
            partition = community_louvain.best_partition(undirected)
            
            # Group by community
            communities = defaultdict(list)
            for node, comm_id in partition.items():
                communities[comm_id].append(node)
            
            return list(communities.values())
        except ImportError:
            # Fallback: return connected components
            return [list(c) for c in nx.connected_components(undirected)]
    
    def suggest_related_concepts(self, 
                                 concepts: List[str],
                                 n_suggestions: int = 5) -> List[Dict[str, Any]]:
        """
        Suggest related concepts based on input concepts.
        
        Args:
            concepts: List of input concepts
            n_suggestions: Number of suggestions to return
            
        Returns:
            List of suggested concepts with relevance scores
        """
        scores = defaultdict(float)
        
        for concept in concepts:
            if concept in self.graph:
                # Get neighbors
                for neighbor in self.graph.successors(concept):
                    edge_weight = self.graph[concept][neighbor].get('weight', 1)
                    scores[neighbor] += edge_weight
                
                for neighbor in self.graph.predecessors(concept):
                    edge_weight = self.graph[neighbor][concept].get('weight', 1)
                    scores[neighbor] += edge_weight
        
        # Remove input concepts from suggestions
        for concept in concepts:
            scores.pop(concept, None)
        
        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'concept': c, 'relevance_score': s}
            for c, s in sorted_scores[:n_suggestions]
        ]
    
    def save(self):
        """Save graph to disk"""
        data = {
            'nodes': [
                {'id': n, **self.graph.nodes[n]}
                for n in self.graph.nodes()
            ],
            'edges': [
                {
                    'source': u,
                    'target': v,
                    **self.graph[u][v]
                }
                for u, v in self.graph.edges()
            ]
        }
        
        with open(self.graph_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved graph to {self.graph_path}")
    
    def load(self):
        """Load graph from disk"""
        with open(self.graph_path, 'r') as f:
            data = json.load(f)
        
        self.graph = nx.DiGraph()
        
        # Add nodes
        for node_data in data.get('nodes', []):
            node_id = node_data.pop('id')
            self.graph.add_node(node_id, **node_data)
        
        # Add edges
        for edge_data in data.get('edges', []):
            source = edge_data.pop('source')
            target = edge_data.pop('target')
            self.graph.add_edge(source, target, **edge_data)
        
        print(f"Loaded graph from {self.graph_path} "
              f"({len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges)")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return {
            'num_nodes': len(self.graph.nodes),
            'num_edges': len(self.graph.edges),
            'density': nx.density(self.graph),
            'is_connected': nx.is_weakly_connected(self.graph) if len(self.graph) > 0 else False,
            'top_concepts': sorted(
                [(n, d['mention_count']) for n, d in self.graph.nodes(data=True) 
                 if 'mention_count' in d],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }


if __name__ == '__main__':
    # Test the concept graph
    cg = ConceptGraph()
    
    # Add some concepts
    cg.add_concept('SEO', 'seo_concept', 'SEO Book 1')
    cg.add_concept('Meta Tags', 'meta_tag', 'SEO Book 1')
    cg.add_concept('Title Tag', 'meta_tag', 'SEO Book 1')
    cg.add_concept('Schema.org', 'schema_type', 'SEO Book 2')
    cg.add_concept('Article Schema', 'schema_type', 'SEO Book 2')
    
    # Add relationships
    cg.add_relationship('Title Tag', 'Meta Tags', 'is_a_type_of', 1.0)
    cg.add_relationship('Meta Tags', 'SEO', 'is_part_of', 0.9)
    cg.add_relationship('Article Schema', 'Schema.org', 'is_a_type_of', 1.0)
    cg.add_relationship('Schema.org', 'SEO', 'improves', 0.8)
    
    # Test expansion
    expansion = cg.expand_concept('SEO', depth=2)
    print(f"Concepts related to SEO: {expansion['related']}")
    
    # Test path finding
    paths = cg.find_paths('Title Tag', 'SEO')
    print(f"Paths from Title Tag to SEO: {paths}")
    
    # Test suggestions
    suggestions = cg.suggest_related_concepts(['Meta Tags'])
    print(f"Suggestions for Meta Tags: {suggestions}")
    
    # Save and load
    cg.save()
