"""
SEO Orchestrator
Coordinates multiple agents to provide comprehensive SEO solutions
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from .concept_graph import ConceptGraph
from .agents import SEOStrategist, SchemaArchitect, MetaTagOptimizer, ContentCritic


class SEOOrchestrator:
    """
    Main orchestrator that coordinates all SEO agents.
    Implements the planning layer and multi-step reasoning chain.
    Works with SEOKnowledgeBaseAdapter (wraps main KB) or VectorKnowledgeBase.
    """
    
    def __init__(self,
                 knowledge_base=None,
                 concept_graph: Optional[ConceptGraph] = None,
                 enable_critic: bool = True):
        """
        Initialize the orchestrator with all agents.
        
        Args:
            knowledge_base: Vector knowledge base for retrieval
            concept_graph: Concept graph for reasoning
            enable_critic: Whether to enable content critique
        """
        self.knowledge_base = knowledge_base
        self.concept_graph = concept_graph
        self.enable_critic = enable_critic
        
        # Initialize all agents
        self.strategist = SEOStrategist(knowledge_base, concept_graph)
        self.schema_architect = SchemaArchitect(knowledge_base, concept_graph)
        self.meta_optimizer = MetaTagOptimizer(knowledge_base, concept_graph)
        self.critic = ContentCritic(knowledge_base, concept_graph) if enable_critic else None
        
        # Execution history
        self.history = []
        
        print("🤖 SEO Orchestrator initialized with agents:")
        print(f"   • {self.strategist.name}")
        print(f"   • {self.schema_architect.name}")
        print(f"   • {self.meta_optimizer.name}")
        if self.critic:
            print(f"   • {self.critic.name}")
    
    def execute(self, 
                query: str,
                context: Optional[Dict[str, Any]] = None,
                agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute the full SEO pipeline.
        
        Args:
            query: User query or topic
            context: Additional context (page_type, url, etc.)
            agents: List of agents to run (default: all)
            
        Returns:
            Comprehensive SEO analysis and recommendations
        """
        context = context or {}
        start_time = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"🚀 Executing SEO Pipeline")
        print(f"   Query: {query}")
        print(f"{'='*60}\n")
        
        # Step 1: Strategic Analysis
        print("📊 Step 1: Strategic Analysis...")
        strategy_result = self.strategist.process(query, context)
        
        # Step 2: Schema Generation
        print("📐 Step 2: Schema Architecture...")
        schema_data = context.get('schema_data') or {
            k: v for k, v in {
                'title': context.get('title', query),
                'description': context.get('description', ''),
                'url': context.get('url', ''),
                'author': context.get('author', ''),
                'publisher': context.get('brand', context.get('publisher', '')),
            }.items() if v
        }
        schema_context = {
            'page_type': context.get('page_type', 'Article'),
            'data': schema_data
        }
        schema_result = self.schema_architect.process(query, schema_context)
        
        # Step 3: Meta Tag Optimization
        print("🏷️  Step 3: Meta Tag Optimization...")
        meta_context = {
            'title': context.get('title', query),
            'description': context.get('description', ''),
            'url': context.get('url', ''),
            'brand': context.get('brand', ''),
            'image': context.get('image', ''),
            'og_type': strategy_result['content_strategy'].get('content_type', 'website')
        }
        meta_result = self.meta_optimizer.process(query, meta_context)
        
        # Step 4: Content Critique (if enabled)
        critique_result = None
        if self.critic and context.get('content'):
            print("🔍 Step 4: Content Critique...")
            critique_result = self.critic.process(context['content'], context)
        
        # Compile final result
        execution_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            'query': query,
            'timestamp': start_time.isoformat(),
            'execution_time_seconds': execution_time,
            'strategy': strategy_result,
            'schema': schema_result,
            'meta_tags': meta_result,
            'critique': critique_result,
            'deliverables': self._compile_deliverables(
                strategy_result, schema_result, meta_result
            )
        }
        
        self.history.append(result)
        
        print(f"\n✅ Pipeline complete in {execution_time:.2f}s")
        
        return result
    
    def _compile_deliverables(self, 
                             strategy: Dict,
                             schema: Dict,
                             meta: Dict) -> Dict[str, Any]:
        """Compile all deliverables into actionable outputs"""
        
        return {
            'seo_strategy': {
                'intent': strategy['intent'],
                'target_serp_features': strategy['serp_features'],
                'content_type': strategy['content_strategy']['content_type'],
                'recommended_sections': strategy['content_strategy']['sections'],
                'target_word_count': strategy['content_strategy']['target_length']
            },
            'keyword_clusters': strategy['keyword_clusters'],
            'schema_markup': {
                'primary': schema['primary_schema'],
                'additional_recommended': schema['additional_schemas'],
                'validation': schema['validation']
            },
            'meta_tags': {
                'title': meta['title'],
                'description': meta['description'],
                'html_output': self.meta_optimizer.generate_html_meta_tags(meta['meta_tags'])
            },
            'social_media': meta['social_tags'],
            'knowledge_sources': list(set(
                strategy.get('knowledge_sources', []) +
                [s['metadata'].get('book_title', 'Unknown') 
                 for s in schema.get('knowledge_references', [])]
            ))
        }
    
    def _generate_meta_html(self, meta_tags: List[Dict]) -> str:
        """Generate HTML from meta tags"""
        html_lines = []
        
        for tag in meta_tags:
            if tag.get('type') == 'charset':
                html_lines.append(f'<meta charset="{tag["content"]}">')
            elif tag.get('type') == 'viewport':
                html_lines.append(f'<meta name="viewport" content="{tag["content"]}">')
            elif tag.get('type') == 'title':
                html_lines.append(f'<title>{tag["content"]}</title>')
            elif tag.get('type') == 'canonical':
                html_lines.append(f'<link rel="canonical" href="{tag["content"]}">')
            elif tag.get('type') == 'og':
                html_lines.append(f'<meta property="{tag["property"]}" content="{tag["content"]}">')
            elif tag.get('type') == 'twitter':
                html_lines.append(f'<meta name="{tag["name"]}" content="{tag["content"]}">')
            else:
                html_lines.append(f'<meta name="{tag["name"]}" content="{tag["content"]}">')
        
        return '\n'.join(html_lines)
    
    def quick_meta(self, 
                   title: str,
                   description: str,
                   url: str,
                   **kwargs) -> Dict[str, Any]:
        """
        Quick meta tag generation without full pipeline.
        
        Args:
            title: Page title
            description: Page description
            url: Page URL
            **kwargs: Additional context
            
        Returns:
            Meta tags and recommendations
        """
        context = {
            'title': title,
            'description': description,
            'url': url,
            **kwargs
        }
        
        return self.meta_optimizer.process(title, context)
    
    def quick_schema(self,
                    page_type: str,
                    data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Quick schema generation without full pipeline.
        
        Args:
            page_type: Type of schema (Article, Product, etc.)
            data: Data to populate schema
            
        Returns:
            Generated schema
        """
        context = {
            'page_type': page_type,
            'data': data
        }
        
        return self.schema_architect.process(page_type, context)
    
    def analyze_competitor(self, 
                          competitor_content: str,
                          target_keyword: str) -> Dict[str, Any]:
        """
        Analyze competitor content and suggest improvements.
        
        Args:
            competitor_content: Content to analyze
            target_keyword: Target keyword
            
        Returns:
            Analysis and recommendations
        """
        context = {
            'content': competitor_content,
            'target_keyword': target_keyword
        }
        
        # Run strategist for keyword research
        strategy = self.strategist.process(target_keyword, context)
        
        # Run critic on content
        critique = self.critic.process(competitor_content, context) if self.critic else None
        
        return {
            'keyword_strategy': strategy,
            'content_critique': critique,
            'opportunities': self._identify_opportunities(strategy, critique)
        }
    
    def _identify_opportunities(self, 
                               strategy: Dict,
                               critique: Optional[Dict]) -> List[str]:
        """Identify SEO opportunities based on analysis"""
        opportunities = []
        
        # From strategy
        for cluster in strategy.get('keyword_clusters', []):
            opportunities.append(f"Target keyword cluster: {cluster['name']}")
        
        for feature in strategy.get('serp_features', []):
            opportunities.append(f"Optimize for SERP feature: {feature}")
        
        # From critique
        if critique:
            for rec in critique.get('recommendations', []):
                opportunities.append(f"Fix: {rec}")
        
        return opportunities
    
    def generate_content_brief(self, topic: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a comprehensive content brief.
        
        Args:
            topic: Content topic
            **kwargs: Additional context
            
        Returns:
            Complete content brief
        """
        # Run full pipeline
        result = self.execute(topic, kwargs)
        
        brief = {
            'topic': topic,
            'objective': result['strategy']['intent'],
            'target_audience': kwargs.get('audience', 'General'),
            'content_type': result['deliverables']['seo_strategy']['content_type'],
            'suggested_sections': result['deliverables']['seo_strategy']['recommended_sections'],
            'target_word_count': result['deliverables']['seo_strategy']['target_word_count'],
            'primary_keywords': [k['keywords'][0] for k in result['deliverables']['keyword_clusters'][:2]],
            'secondary_keywords': [k['keywords'][1:] for k in result['deliverables']['keyword_clusters'][:2]],
            'serp_features_to_target': result['deliverables']['seo_strategy']['target_serp_features'],
            'schema_requirements': result['deliverables']['schema_markup']['additional_recommended'],
            'meta_tags': {
                'title': result['deliverables']['meta_tags']['title'],
                'description': result['deliverables']['meta_tags']['description']
            },
            'internal_linking_suggestions': self._suggest_internal_links(topic, result),
            'content_guidelines': {
                'tone': kwargs.get('tone', 'Professional'),
                'style': kwargs.get('style', 'Informative'),
                'expertise_level': kwargs.get('expertise', 'Intermediate')
            }
        }
        
        return brief
    
    def _suggest_internal_links(self, topic: str, result: Dict) -> List[str]:
        """Suggest internal linking opportunities"""
        suggestions = []
        
        # Get related concepts from concept graph
        if self.concept_graph:
            expansion = self.concept_graph.expand_concept(topic, depth=2)
            for related in expansion.get('related', [])[:5]:
                suggestions.append(f"Link to: {related}")
        
        # Add pillar/cluster suggestions
        suggestions.append(f"Pillar page: Ultimate Guide to {topic}")
        suggestions.append(f"Cluster content: {topic} for Beginners")
        suggestions.append(f"Cluster content: Advanced {topic} Techniques")
        
        return suggestions
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            'total_executions': len(self.history),
            'knowledge_base': self.knowledge_base.get_stats() if self.knowledge_base else None,
            'concept_graph': self.concept_graph.get_stats() if self.concept_graph else None,
            'agents': {
                'strategist': self.strategist.name,
                'schema_architect': self.schema_architect.name,
                'meta_optimizer': self.meta_optimizer.name,
                'critic': self.critic.name if self.critic else None
            }
        }


if __name__ == '__main__':
    # Test the orchestrator
    orchestrator = SEOOrchestrator()
    
    result = orchestrator.execute(
        "how to optimize meta tags for SEO",
        context={
            'page_type': 'article',
            'url': 'https://example.com/meta-tags-guide',
            'brand': 'SEO Pro'
        }
    )
    
    print("\n" + "="*60)
    print("RESULT SUMMARY")
    print("="*60)
    print(f"Intent: {result['strategy']['intent']['primary']}")
    print(f"Content Type: {result['strategy']['content_strategy']['content_type']}")
    print(f"Title: {result['deliverables']['meta_tags']['title']}")
    print(f"Description: {result['deliverables']['meta_tags']['description']}")
