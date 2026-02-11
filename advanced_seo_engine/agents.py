"""
SEO Agents - Specialized AI agents for different SEO tasks
Each agent has a specific role and expertise area
"""

import json
import re
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base class for all SEO agents"""
    
    def __init__(self, name: str, knowledge_base=None, concept_graph=None):
        self.name = name
        self.knowledge_base = knowledge_base
        self.concept_graph = concept_graph
        self.memory = []  # Agent's working memory
    
    @abstractmethod
    def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a query and return results"""
        pass
    
    def retrieve_knowledge(self, query: str, n_results: int = 5) -> List[Dict]:
        """Retrieve relevant knowledge from the knowledge base"""
        if self.knowledge_base:
            return self.knowledge_base.search(query, n_results=n_results)
        return []
    
    def expand_concepts(self, concepts: List[str]) -> Dict[str, Any]:
        """Expand concepts using the concept graph"""
        if not self.concept_graph:
            return {}
        
        expansions = {}
        for concept in concepts:
            expansions[concept] = self.concept_graph.expand_concept(concept)
        return expansions
    
    def log(self, message: str):
        """Log agent activity"""
        self.memory.append({'agent': self.name, 'message': message})


class SEOStrategist(BaseAgent):
    """
    SEO Strategist Agent
    Analyzes queries, classifies intent, and develops SEO strategies
    """
    
    # Intent classification patterns
    INTENT_PATTERNS = {
        'informational': ['what is', 'how to', 'why', 'guide', 'tutorial', 'explain'],
        'transactional': ['buy', 'price', 'discount', 'deal', 'purchase', 'order'],
        'navigational': ['login', 'sign in', 'website', 'homepage', 'official'],
        'commercial_investigation': ['best', 'top', 'review', 'compare', 'vs', 'alternative']
    }
    
    SERP_FEATURES = {
        'featured_snippet': ['what is', 'how to', 'why does', 'definition'],
        'people_also_ask': ['how', 'why', 'what', 'when', 'where'],
        'local_pack': ['near me', 'local', 'in city', 'nearby'],
        'shopping': ['buy', 'price', 'cheap', 'deal'],
        'video': ['tutorial', 'how to', 'demo', 'walkthrough']
    }
    
    def __init__(self, knowledge_base=None, concept_graph=None):
        super().__init__("SEO Strategist", knowledge_base, concept_graph)
    
    def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze query and develop SEO strategy
        
        Returns strategy with:
        - Intent classification
        - SERP feature targets
        - Content recommendations
        - Keyword clusters
        """
        self.log(f"Analyzing query: {query}")
        
        # Classify intent
        intent = self._classify_intent(query)
        
        # Identify SERP features
        serp_features = self._identify_serp_features(query)
        
        # Retrieve knowledge
        knowledge = self.retrieve_knowledge(query, n_results=10)
        
        # Generate keyword clusters
        keyword_clusters = self._generate_keyword_clusters(query, knowledge)
        
        # Develop content strategy
        content_strategy = self._develop_content_strategy(intent, serp_features, knowledge)
        
        return {
            'agent': self.name,
            'query': query,
            'intent': intent,
            'serp_features': serp_features,
            'keyword_clusters': keyword_clusters,
            'content_strategy': content_strategy,
            'knowledge_sources': list(set(k['metadata'].get('book_title', 'Unknown') for k in knowledge)),
            'reasoning': self.memory
        }
    
    def _classify_intent(self, query: str) -> Dict[str, Any]:
        """Classify search intent"""
        query_lower = query.lower()
        
        scores = {}
        for intent_type, patterns in self.INTENT_PATTERNS.items():
            score = sum(1 for p in patterns if p in query_lower)
            scores[intent_type] = score
        
        # Get primary intent
        primary_intent = max(scores, key=scores.get)
        
        # Calculate confidence
        total_score = sum(scores.values())
        confidence = scores[primary_intent] / max(total_score, 1)
        
        return {
            'primary': primary_intent,
            'confidence': confidence,
            'all_scores': scores
        }
    
    def _identify_serp_features(self, query: str) -> List[str]:
        """Identify which SERP features to target"""
        query_lower = query.lower()
        features = []
        
        for feature, patterns in self.SERP_FEATURES.items():
            if any(p in query_lower for p in patterns):
                features.append(feature)
        
        return features
    
    def _generate_keyword_clusters(self, query: str, knowledge: List[Dict]) -> List[Dict]:
        """Generate keyword clusters based on knowledge"""
        # Extract terms from knowledge
        all_text = ' '.join([k['text'] for k in knowledge[:5]])
        
        # Simple keyword extraction (can be enhanced with NLP)
        words = re.findall(r'\b[a-z]{5,}\b', all_text.lower())
        from collections import Counter
        
        # Filter out common words
        stop_words = {'about', 'after', 'again', 'against', 'because', 'before',
                     'being', 'between', 'could', 'does', 'doing', 'during',
                     'having', 'into', 'more', 'most', 'other', 'over', 'such',
                     'than', 'that', 'their', 'them', 'then', 'there', 'these',
                     'they', 'this', 'those', 'through', 'under', 'very', 'what',
                     'when', 'where', 'which', 'while', 'with', 'would'}
        
        keywords = [w for w in words if w not in stop_words]
        top_keywords = Counter(keywords).most_common(15)
        
        # Group into clusters
        clusters = [
            {
                'name': f'{query} - Primary',
                'keywords': [query] + [k for k, _ in top_keywords[:5]],
                'intent': 'primary'
            },
            {
                'name': f'{query} - Related',
                'keywords': [k for k, _ in top_keywords[5:10]],
                'intent': 'secondary'
            },
            {
                'name': f'{query} - Long-tail',
                'keywords': [f'how to {query}', f'what is {query}', f'best {query}'],
                'intent': 'long_tail'
            }
        ]
        
        return clusters
    
    def _develop_content_strategy(self, intent: Dict, serp_features: List, 
                                   knowledge: List[Dict]) -> Dict[str, Any]:
        """Develop content strategy based on analysis"""
        
        strategy = {
            'content_type': 'article',
            'format': 'standard',
            'sections': [],
            'target_length': 1500,
            'schema_recommendations': []
        }
        
        # Adjust based on intent
        if intent['primary'] == 'informational':
            strategy['content_type'] = 'guide'
            strategy['format'] = 'how-to' if 'how to' in str(knowledge).lower() else 'explanatory'
            strategy['sections'] = ['Introduction', 'What is', 'How it works', 'Benefits', 'Conclusion']
            strategy['schema_recommendations'] = ['Article', 'FAQPage']
            
        elif intent['primary'] == 'commercial_investigation':
            strategy['content_type'] = 'comparison'
            strategy['format'] = 'listicle'
            strategy['sections'] = ['Introduction', 'Top Options', 'Comparison', 'Recommendations']
            strategy['schema_recommendations'] = ['Article', 'ItemList']
            
        elif intent['primary'] == 'transactional':
            strategy['content_type'] = 'product_page'
            strategy['format'] = 'sales'
            strategy['sections'] = ['Product Info', 'Features', 'Pricing', 'CTA']
            strategy['schema_recommendations'] = ['Product', 'Offer']
        
        # Adjust for SERP features
        if 'featured_snippet' in serp_features:
            strategy['sections'].insert(0, 'Quick Answer')
        
        if 'people_also_ask' in serp_features:
            strategy['sections'].append('FAQ')
            if 'FAQPage' not in strategy['schema_recommendations']:
                strategy['schema_recommendations'].append('FAQPage')
        
        return strategy


class SchemaArchitect(BaseAgent):
    """
    Schema Architect Agent
    Generates valid Schema.org JSON-LD structured data
    """
    
    SCHEMA_TEMPLATES = {
        'Article': {
            '@context': 'https://schema.org',
            '@type': 'Article',
            'headline': '{{title}}',
            'description': '{{description}}',
            'image': '{{image_url}}',
            'author': {
                '@type': 'Person',
                'name': '{{author}}'
            },
            'publisher': {
                '@type': 'Organization',
                'name': '{{publisher}}',
                'logo': {
                    '@type': 'ImageObject',
                    'url': '{{logo_url}}'
                }
            },
            'datePublished': '{{date_published}}',
            'dateModified': '{{date_modified}}'
        },
        'Product': {
            '@context': 'https://schema.org',
            '@type': 'Product',
            'name': '{{product_name}}',
            'image': '{{image_url}}',
            'description': '{{description}}',
            'brand': {
                '@type': 'Brand',
                'name': '{{brand}}'
            },
            'offers': {
                '@type': 'Offer',
                'url': '{{url}}',
                'priceCurrency': '{{currency}}',
                'price': '{{price}}',
                'availability': 'https://schema.org/{{availability}}'
            }
        },
        'LocalBusiness': {
            '@context': 'https://schema.org',
            '@type': 'LocalBusiness',
            'name': '{{business_name}}',
            'image': '{{image_url}}',
            '@id': '{{website_url}}',
            'url': '{{website_url}}',
            'telephone': '{{phone}}',
            'address': {
                '@type': 'PostalAddress',
                'streetAddress': '{{street}}',
                'addressLocality': '{{city}}',
                'addressRegion': '{{state}}',
                'postalCode': '{{zip}}',
                'addressCountry': '{{country}}'
            }
        },
        'FAQPage': {
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            'mainEntity': []
        },
        'HowTo': {
            '@context': 'https://schema.org',
            '@type': 'HowTo',
            'name': '{{title}}',
            'description': '{{description}}',
            'totalTime': '{{duration}}',
            'estimatedCost': {
                '@type': 'MonetaryAmount',
                'currency': '{{currency}}',
                'value': '{{cost}}'
            },
            'step': []
        },
        'BreadcrumbList': {
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': []
        },
        'WebPage': {
            '@context': 'https://schema.org',
            '@type': 'WebPage',
            'name': '{{title}}',
            'description': '{{description}}',
            'url': '{{url}}',
            'breadcrumb': '{{breadcrumb}}'
        },
        'Organization': {
            '@context': 'https://schema.org',
            '@type': 'Organization',
            'name': '{{org_name}}',
            'url': '{{website_url}}',
            'logo': '{{logo_url}}',
            'sameAs': []
        }
    }
    
    def __init__(self, knowledge_base=None, concept_graph=None):
        super().__init__("Schema Architect", knowledge_base, concept_graph)
    
    def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Schema.org structured data
        
        Args:
            query: The content/topic
            context: Contains page_type, data fields, etc.
        """
        self.log(f"Generating schema for: {query}")
        
        page_type = context.get('page_type', 'Article')
        data = context.get('data', {})
        
        # Retrieve schema knowledge
        schema_knowledge = self.retrieve_knowledge(
            f"schema.org {page_type} structured data", 
            n_results=3
        )
        
        # Generate schema
        schema = self._generate_schema(page_type, data)
        
        # Validate schema
        validation = self._validate_schema(schema)
        
        # Suggest additional schemas
        additional_schemas = self._suggest_additional_schemas(page_type, context)
        
        return {
            'agent': self.name,
            'primary_schema': schema,
            'validation': validation,
            'additional_schemas': additional_schemas,
            'knowledge_references': schema_knowledge,
            'reasoning': self.memory
        }
    
    def _generate_schema(self, schema_type: str, data: Dict[str, Any]) -> Dict:
        """Generate a schema with data filled in"""
        if schema_type not in self.SCHEMA_TEMPLATES:
            return {'error': f'Unknown schema type: {schema_type}'}
        
        template = self.SCHEMA_TEMPLATES[schema_type].copy()
        
        # Recursively fill in template values
        return self._fill_template(template, data)
    
    def _fill_template(self, template: Any, data: Dict) -> Any:
        """Recursively fill template placeholders"""
        if isinstance(template, dict):
            return {k: self._fill_template(v, data) for k, v in template.items()}
        elif isinstance(template, list):
            return [self._fill_template(item, data) for item in template]
        elif isinstance(template, str) and template.startswith('{{') and template.endswith('}}'):
            key = template[2:-2]
            return data.get(key, '')
        else:
            return template
    
    def _validate_schema(self, schema: Dict) -> Dict[str, Any]:
        """Validate schema structure"""
        issues = []
        
        # Check required fields
        if '@context' not in schema:
            issues.append("Missing @context")
        if '@type' not in schema:
            issues.append("Missing @type")
        
        # Check for empty values
        def check_empty(obj, path=''):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    check_empty(v, f"{path}.{k}")
            elif isinstance(obj, str) and not obj:
                issues.append(f"Empty value at {path}")
        
        check_empty(schema)
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }
    
    def _suggest_additional_schemas(self, primary_type: str, context: Dict) -> List[str]:
        """Suggest additional schemas to include"""
        suggestions = ['BreadcrumbList']  # Always suggest breadcrumbs
        
        if primary_type == 'Article':
            suggestions.extend(['WebPage', 'Organization'])
        elif primary_type == 'Product':
            suggestions.extend(['WebPage', 'Organization', 'BreadcrumbList'])
        elif primary_type == 'LocalBusiness':
            suggestions.extend(['WebPage'])
        
        return suggestions
    
    def generate_faq_schema(self, faqs: List[Dict[str, str]]) -> Dict:
        """Generate FAQPage schema from list of Q&A"""
        schema = self.SCHEMA_TEMPLATES['FAQPage'].copy()
        
        for faq in faqs:
            schema['mainEntity'].append({
                '@type': 'Question',
                'name': faq['question'],
                'acceptedAnswer': {
                    '@type': 'Answer',
                    'text': faq['answer']
                }
            })
        
        return schema
    
    def generate_breadcrumb_schema(self, items: List[Dict[str, str]]) -> Dict:
        """Generate BreadcrumbList schema"""
        schema = self.SCHEMA_TEMPLATES['BreadcrumbList'].copy()
        
        for i, item in enumerate(items, 1):
            schema['itemListElement'].append({
                '@type': 'ListItem',
                'position': i,
                'name': item['name'],
                'item': item['url']
            })
        
        return schema


class MetaTagOptimizer(BaseAgent):
    """
    Meta Tag Optimizer Agent
    Generates optimized meta tags for SEO and social sharing
    """
    
    def __init__(self, knowledge_base=None, concept_graph=None):
        super().__init__("Meta Tag Optimizer", knowledge_base, concept_graph)
    
    def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate optimized meta tags
        
        Args:
            query: The page topic/title
            context: Contains description, url, image, etc.
        """
        self.log(f"Optimizing meta tags for: {query}")
        
        # Retrieve meta tag best practices
        meta_knowledge = self.retrieve_knowledge(
            "meta tags optimization best practices",
            n_results=5
        )
        
        # Generate title
        title = self._optimize_title(query, context)
        
        # Generate description
        description = self._optimize_description(context.get('description', ''), context)
        
        # Generate all meta tags
        meta_tags = self._generate_all_meta_tags(title, description, context)
        
        # Generate social tags
        social_tags = self._generate_social_tags(title, description, context)
        
        return {
            'agent': self.name,
            'title': title,
            'description': description,
            'meta_tags': meta_tags,
            'social_tags': social_tags,
            'best_practices': meta_knowledge,
            'reasoning': self.memory
        }
    
    def _optimize_title(self, query: str, context: Dict) -> str:
        """Optimize title tag (50-60 characters optimal)"""
        base_title = context.get('title', query)
        
        # Add brand if space permits
        brand = context.get('brand', '')
        
        if brand and len(base_title) + len(brand) + 3 <= 60:
            title = f"{base_title} | {brand}"
        else:
            title = base_title[:60]
        
        return title
    
    def _optimize_description(self, desc: str, context: Dict) -> str:
        """Optimize meta description (150-160 characters optimal)"""
        if not desc:
            # Generate from knowledge
            knowledge = self.retrieve_knowledge(context.get('title', ''), n_results=1)
            if knowledge:
                desc = knowledge[0]['text'][:160]
            else:
                desc = f"Learn about {context.get('title', '')}. Comprehensive guide with expert insights."
        
        # Ensure proper length
        if len(desc) > 160:
            desc = desc[:157] + '...'
        
        return desc
    
    def _generate_all_meta_tags(self, title: str, description: str, 
                                 context: Dict) -> List[Dict[str, str]]:
        """Generate complete meta tag set"""
        url = context.get('url', '')
        canonical = context.get('canonical', url)
        
        tags = [
            {'name': 'charset', 'content': 'UTF-8', 'type': 'charset'},
            {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0', 'type': 'viewport'},
            {'name': 'title', 'content': title, 'type': 'title'},
            {'name': 'description', 'content': description, 'type': 'standard'},
            {'name': 'canonical', 'content': canonical, 'type': 'canonical'},
            {'name': 'robots', 'content': 'index, follow', 'type': 'robots'}
        ]
        
        # Add Open Graph tags
        tags.extend([
            {'property': 'og:title', 'content': title, 'type': 'og'},
            {'property': 'og:description', 'content': description, 'type': 'og'},
            {'property': 'og:url', 'content': url, 'type': 'og'},
            {'property': 'og:type', 'content': context.get('og_type', 'website'), 'type': 'og'},
            {'property': 'og:image', 'content': context.get('image', ''), 'type': 'og'}
        ])
        
        # Add Twitter Card tags
        tags.extend([
            {'name': 'twitter:card', 'content': 'summary_large_image', 'type': 'twitter'},
            {'name': 'twitter:title', 'content': title, 'type': 'twitter'},
            {'name': 'twitter:description', 'content': description, 'type': 'twitter'},
            {'name': 'twitter:image', 'content': context.get('image', ''), 'type': 'twitter'}
        ])
        
        return tags
    
    def _generate_social_tags(self, title: str, description: str, 
                              context: Dict) -> Dict[str, Any]:
        """Generate social media specific tags"""
        return {
            'facebook': {
                'og:title': title,
                'og:description': description,
                'og:image': context.get('image', ''),
                'og:url': context.get('url', ''),
                'og:type': context.get('og_type', 'website'),
                'og:site_name': context.get('brand', '')
            },
            'twitter': {
                'twitter:card': 'summary_large_image',
                'twitter:title': title,
                'twitter:description': description,
                'twitter:image': context.get('image', ''),
                'twitter:site': context.get('twitter_handle', '')
            },
            'linkedin': {
                'og:title': title,
                'og:description': description,
                'og:image': context.get('image', '')
            }
        }
    
    def generate_html_meta_tags(self, meta_tags: List[Dict]) -> str:
        """Generate HTML string from meta tags"""
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


class ContentCritic(BaseAgent):
    """
    Content Critic Agent
    Evaluates and critiques SEO content for quality and optimization
    """
    
    def __init__(self, knowledge_base=None, concept_graph=None):
        super().__init__("Content Critic", knowledge_base, concept_graph)
    
    def process(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Critique content for SEO quality
        
        Returns critique with scores and recommendations
        """
        self.log("Critiquing content...")
        
        critique = {
            'overall_score': 0,
            'categories': {},
            'issues': [],
            'recommendations': []
        }
        
        # Check title optimization
        title_score = self._check_title(content, context)
        critique['categories']['title'] = title_score
        
        # Check description
        desc_score = self._check_description(content, context)
        critique['categories']['description'] = desc_score
        
        # Check keyword usage
        keyword_score = self._check_keywords(content, context)
        critique['categories']['keywords'] = keyword_score
        
        # Check structure
        structure_score = self._check_structure(content)
        critique['categories']['structure'] = structure_score
        
        # Calculate overall score
        critique['overall_score'] = sum(
            s['score'] for s in critique['categories'].values()
        ) / len(critique['categories'])
        
        # Generate recommendations
        critique['recommendations'] = self._generate_recommendations(critique)
        
        return critique
    
    def _check_title(self, content: str, context: Dict) -> Dict:
        """Check title optimization"""
        title = context.get('title', '')
        score = 100
        issues = []
        
        if not title:
            score -= 50
            issues.append("Missing title tag")
        elif len(title) < 30:
            score -= 20
            issues.append("Title too short (< 30 chars)")
        elif len(title) > 60:
            score -= 10
            issues.append("Title may be truncated (> 60 chars)")
        
        return {'score': max(0, score), 'issues': issues}
    
    def _check_description(self, content: str, context: Dict) -> Dict:
        """Check meta description"""
        desc = context.get('description', '')
        score = 100
        issues = []
        
        if not desc:
            score -= 30
            issues.append("Missing meta description")
        elif len(desc) < 120:
            score -= 10
            issues.append("Description could be more detailed")
        elif len(desc) > 160:
            score -= 10
            issues.append("Description may be truncated")
        
        return {'score': max(0, score), 'issues': issues}
    
    def _check_keywords(self, content: str, context: Dict) -> Dict:
        """Check keyword usage"""
        score = 100
        issues = []
        
        # Check for keyword in title
        target_keyword = context.get('target_keyword', '')
        if target_keyword and target_keyword.lower() not in content.lower():
            score -= 20
            issues.append(f"Target keyword '{target_keyword}' not found in content")
        
        return {'score': max(0, score), 'issues': issues}
    
    def _check_structure(self, content: str) -> Dict:
        """Check content structure"""
        score = 100
        issues = []
        
        # Check for H1
        if '<h1' not in content.lower():
            score -= 15
            issues.append("Missing H1 heading")
        
        # Check for images with alt text
        img_count = content.lower().count('<img')
        alt_count = content.lower().count('alt=')
        if img_count > alt_count:
            score -= 10
            issues.append("Some images missing alt text")
        
        return {'score': max(0, score), 'issues': issues}
    
    def _generate_recommendations(self, critique: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        for category, data in critique['categories'].items():
            if data['score'] < 80:
                for issue in data['issues']:
                    recommendations.append(f"[{category.upper()}] {issue}")
        
        return recommendations


if __name__ == '__main__':
    # Test agents
    strategist = SEOStrategist()
    result = strategist.process("how to optimize meta tags", {})
    print(f"Intent: {result['intent']}")
    print(f"SERP Features: {result['serp_features']}")
    
    schema_agent = SchemaArchitect()
    schema_result = schema_agent.process("Article", {
        'page_type': 'Article',
        'data': {
            'title': 'SEO Best Practices Guide',
            'description': 'Learn the best SEO practices',
            'author': 'John Doe',
            'date_published': '2024-01-01'
        }
    })
    print(f"\nSchema: {json.dumps(schema_result['primary_schema'], indent=2)}")
