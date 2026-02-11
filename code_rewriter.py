"""
SEOBOT Code Rewriter - Automatically fixes SEO issues in website files
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class SEOCodeRewriter:
    """Rewrites website code to fix SEO issues based on the 3 SEO Laws"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.changes_made = []
        self.backup_created = False
        
    def create_backup(self) -> str:
        """Create a backup of the original files"""
        backup_dir = self.project_path / f".seobot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(exist_ok=True)
        
        # Backup HTML, TSX, JSX files
        for ext in ['*.html', '*.tsx', '*.jsx', '*.vue']:
            for file in self.project_path.rglob(ext):
                if 'node_modules' not in str(file) and 'dist' not in str(file):
                    relative = file.relative_to(self.project_path)
                    backup_file = backup_dir / relative
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    backup_file.write_text(file.read_text(encoding='utf-8'), encoding='utf-8')
        
        self.backup_created = True
        return str(backup_dir)
    
    def fix_meta_tags(self, content: str, page_data: Dict) -> Tuple[str, List[str]]:
        """Fix meta tags according to SEO Laws (50-60 char titles, 150-160 char descriptions)"""
        changes = []
        
        # Extract or create title
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        new_title = page_data.get('title', '')
        
        # Ensure title is 50-60 chars
        if len(new_title) < 50:
            new_title = f"{new_title} | {page_data.get('site_name', 'Adaryus')}"
        if len(new_title) > 60:
            new_title = new_title[:57] + "..."
            
        if title_match:
            old_title = title_match.group(1)
            if old_title != new_title:
                content = content.replace(f'<title>{old_title}</title>', f'<title>{new_title}</title>')
                changes.append(f"Title: '{old_title}' → '{new_title}' ({len(new_title)} chars)")
        else:
            # Insert title after <head>
            content = re.sub(r'(<head[^>]*>)', r'\1\n    <title>' + new_title + '</title>', content, flags=re.IGNORECASE)
            changes.append(f"Added title: '{new_title}' ({len(new_title)} chars)")
        
        # Fix or add meta description
        desc = page_data.get('description', '')
        # Ensure description is 150-160 chars with CTA
        if len(desc) < 150:
            cta = " Learn more and get started today!"
            desc = desc[:150-len(cta)] + cta
        if len(desc) > 160:
            desc = desc[:157] + "..."
            
        desc_pattern = r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\'][^>]*>'
        desc_match = re.search(desc_pattern, content, re.IGNORECASE)
        
        if desc_match:
            old_desc = desc_match.group(1)
            if old_desc != desc:
                content = re.sub(desc_pattern, f'<meta name="description" content="{desc}">', content, flags=re.IGNORECASE)
                changes.append(f"Description updated ({len(desc)} chars)")
        else:
            # Add meta description after title
            content = re.sub(r'(</title>)', r'\1\n    <meta name="description" content="' + desc + '">', content, flags=re.IGNORECASE)
            changes.append(f"Added description ({len(desc)} chars)")
        
        # Add viewport if missing
        if not re.search(r'<meta[^>]*viewport', content, re.IGNORECASE):
            content = re.sub(r'(</title>)', r'\1\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">', content, flags=re.IGNORECASE)
            changes.append("Added viewport meta tag")
        
        # Add canonical if missing
        canonical_url = page_data.get('canonical', '')
        if canonical_url and not re.search(r'<link[^>]*canonical', content, re.IGNORECASE):
            content = re.sub(r'(</title>)', r'\1\n    <link rel="canonical" href="' + canonical_url + '">', content, flags=re.IGNORECASE)
            changes.append(f"Added canonical: {canonical_url}")
        
        # Add robots if missing
        if not re.search(r'<meta[^>]*robots', content, re.IGNORECASE):
            content = re.sub(r'(</title>)', r'\1\n    <meta name="robots" content="index, follow">', content, flags=re.IGNORECASE)
            changes.append("Added robots meta tag")
        
        return content, changes
    
    def fix_open_graph(self, content: str, page_data: Dict) -> Tuple[str, List[str]]:
        """Add/fix Open Graph tags"""
        changes = []
        
        og_tags = {
            'og:type': 'website',
            'og:url': page_data.get('url', ''),
            'og:title': page_data.get('title', ''),
            'og:description': page_data.get('description', ''),
            'og:image': page_data.get('image', f"{page_data.get('url', '')}/og-image.jpg")
        }
        
        for property_name, content_value in og_tags.items():
            pattern = rf'<meta[^>]*property=["\']{property_name}["\'][^>]*>'
            tag = f'<meta property="{property_name}" content="{content_value}">'
            
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(pattern, tag, content, flags=re.IGNORECASE)
            else:
                # Add before </head>
                content = re.sub(r'(</head>)', f'    {tag}\n\1', content, flags=re.IGNORECASE)
                changes.append(f"Added {property_name}")
        
        return content, changes
    
    def fix_twitter_cards(self, content: str, page_data: Dict) -> Tuple[str, List[str]]:
        """Add/fix Twitter Card tags"""
        changes = []
        
        twitter_tags = {
            'twitter:card': 'summary_large_image',
            'twitter:url': page_data.get('url', ''),
            'twitter:title': page_data.get('title', ''),
            'twitter:description': page_data.get('description', ''),
            'twitter:image': page_data.get('image', f"{page_data.get('url', '')}/twitter-image.jpg")
        }
        
        for name, content_value in twitter_tags.items():
            pattern = rf'<meta[^>]*name=["\']{name}["\'][^>]*>'
            tag = f'<meta name="{name}" content="{content_value}">'
            
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(pattern, tag, content, flags=re.IGNORECASE)
            else:
                content = re.sub(r'(</head>)', f'    {tag}\n\1', content, flags=re.IGNORECASE)
                changes.append(f"Added {name}")
        
        return content, changes
    
    def generate_schema_markup(self, page_data: Dict) -> str:
        """Generate Schema.org JSON-LD markup"""
        schema_type = page_data.get('schema_type', 'WebPage')
        
        schema = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "name": page_data.get('title', ''),
            "description": page_data.get('description', ''),
            "url": page_data.get('url', '')
        }
        
        if schema_type == 'Organization':
            schema.update({
                "logo": f"{page_data.get('url', '')}/logo.png",
                "sameAs": page_data.get('social_links', []),
                "contactPoint": {
                    "@type": "ContactPoint",
                    "contactType": "customer service"
                }
            })
        
        elif schema_type == 'Person':
            schema.update({
                "jobTitle": page_data.get('job_title', 'Web Designer'),
                "sameAs": page_data.get('social_links', [])
            })
        
        elif schema_type == 'Article':
            schema.update({
                "author": {
                    "@type": "Person",
                    "name": page_data.get('author', 'Adaryus')
                },
                "datePublished": page_data.get('date_published', datetime.now().isoformat()),
                "dateModified": page_data.get('date_modified', datetime.now().isoformat()),
                "image": page_data.get('image', '')
            })
        
        elif schema_type == 'LocalBusiness':
            schema.update({
                "address": {
                    "@type": "PostalAddress",
                    "addressRegion": "WV",
                    "addressCountry": "US"
                },
                "geo": {
                    "@type": "GeoCoordinates",
                    "latitude": "",
                    "longitude": ""
                },
                "openingHours": ["Mo-Fr 09:00-17:00"],
                "priceRange": "$$"
            })
        
        return json.dumps(schema, indent=2)
    
    def fix_schema_markup(self, content: str, page_data: Dict) -> Tuple[str, List[str]]:
        """Add/fix Schema.org markup"""
        changes = []
        
        schema_json = self.generate_schema_markup(page_data)
        schema_script = f'<script type="application/ld+json">\n{schema_json}\n</script>'
        
        # Check if schema already exists
        if re.search(r'<script[^>]*type=["\']application/ld+json["\']', content, re.IGNORECASE):
            # Replace existing
            content = re.sub(
                r'<script[^>]*type=["\']application/ld+json["\'][^>]*>.*?</script>',
                schema_script,
                content,
                flags=re.IGNORECASE | re.DOTALL
            )
            changes.append(f"Updated {page_data.get('schema_type', 'WebPage')} schema")
        else:
            # Add new
            content = re.sub(r'(</head>)', f'    {schema_script}\n\1', content, flags=re.IGNORECASE)
            changes.append(f"Added {page_data.get('schema_type', 'WebPage')} schema markup")
        
        return content, changes
    
    def fix_image_alt_text(self, content: str) -> Tuple[str, List[str]]:
        """Add alt text to images missing it"""
        changes = []
        
        # Find images without alt
        img_pattern = r'<img([^>]*)(?<!alt=)([^>]*)>'
        
        def add_alt(match):
            attrs = match.group(1) + match.group(2)
            # Try to extract filename for alt text
            src_match = re.search(r'src=["\']([^"\']*)["\']', attrs)
            if src_match:
                filename = Path(src_match.group(1)).stem
                alt_text = filename.replace('-', ' ').replace('_', ' ').title()
            else:
                alt_text = "Image"
            
            changes.append(f"Added alt='{alt_text}' to image")
            return f'<img{attrs} alt="{alt_text}">'
        
        content = re.sub(img_pattern, add_alt, content, flags=re.IGNORECASE)
        
        return content, changes
    
    def add_webgl_optimizations(self, content: str) -> Tuple[str, List[str]]:
        """Add WebGL performance optimizations"""
        changes = []
        
        # Add lazy loading for WebGL canvas
        if '<canvas' in content and 'loading="lazy"' not in content:
            content = re.sub(
                r'(<canvas[^>]*)(>)',
                r'\1 loading="lazy"\2',
                content,
                flags=re.IGNORECASE
            )
            changes.append("Added lazy loading to canvas elements")
        
        # Add performance hints
        if 'will-change' not in content:
            content = re.sub(
                r'(<canvas[^>]*)(style=["\'])',
                r'\1style="will-change: transform; ',
                content,
                flags=re.IGNORECASE
            )
            changes.append("Added will-change CSS hint for GPU acceleration")
        
        return content, changes
    
    def add_browser_caching_headers(self, htaccess_path: Path) -> List[str]:
        """Generate .htaccess rules for browser caching"""
        changes = []
        
        htaccess_content = """
# SEOBOT: Browser Caching for Performance
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/webp "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/pdf "access plus 1 month"
    ExpiresByType text/javascript "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType application/x-javascript "access plus 1 month"
    ExpiresByType application/x-shockwave-flash "access plus 1 month"
    ExpiresByType image/x-icon "access plus 1 year"
    ExpiresDefault "access plus 2 days"
</IfModule>

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>
"""
        
        htaccess_file = htaccess_path / ".htaccess"
        if htaccess_file.exists():
            existing = htaccess_file.read_text()
            if "SEOBOT" not in existing:
                htaccess_file.write_text(existing + htaccess_content)
                changes.append("Updated .htaccess with caching rules")
        else:
            htaccess_file.write_text(htaccess_content)
            changes.append("Created .htaccess with caching rules")
        
        return changes
    
    def rewrite_file(self, file_path: Path, page_data: Dict) -> Dict:
        """Rewrite a single file with all SEO fixes"""
        result = {
            'file': str(file_path),
            'success': False,
            'changes': [],
            'error': None
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            all_changes = []
            
            # Apply all fixes
            content, changes = self.fix_meta_tags(content, page_data)
            all_changes.extend(changes)
            
            content, changes = self.fix_open_graph(content, page_data)
            all_changes.extend(changes)
            
            content, changes = self.fix_twitter_cards(content, page_data)
            all_changes.extend(changes)
            
            content, changes = self.fix_schema_markup(content, page_data)
            all_changes.extend(changes)
            
            content, changes = self.fix_image_alt_text(content)
            all_changes.extend(changes)
            
            content, changes = self.add_webgl_optimizations(content)
            all_changes.extend(changes)
            
            # Write back
            file_path.write_text(content, encoding='utf-8')
            
            result['success'] = True
            result['changes'] = all_changes
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def scan_and_rewrite_project(self, project_data: Dict) -> List[Dict]:
        """Scan entire project and rewrite all files"""
        results = []
        
        # Create backup first
        backup_path = self.create_backup()
        
        # Find all HTML/TSX/JSX files
        for ext in ['*.html', '*.tsx', '*.jsx', '*.vue']:
            for file in self.project_path.rglob(ext):
                if 'node_modules' in str(file) or 'dist' in str(file) or '.seobot' in str(file):
                    continue
                
                # Determine page data based on filename
                page_name = file.stem
                page_data = {
                    'title': f"{project_data['name']} - {page_name.title()}",
                    'description': project_data['description'],
                    'site_name': project_data['name'],
                    'url': f"https://{project_data['domain']}/{page_name}",
                    'canonical': f"https://{project_data['domain']}/{page_name}",
                    'schema_type': project_data.get('schema_type', 'WebPage'),
                    'social_links': project_data.get('social_links', [])
                }
                
                result = self.rewrite_file(file, page_data)
                results.append(result)
        
        # Add .htaccess for caching
        htaccess_changes = self.add_browser_caching_headers(self.project_path)
        if htaccess_changes:
            results.append({
                'file': '.htaccess',
                'success': True,
                'changes': htaccess_changes,
                'error': None
            })
        
        return results


# Utility functions for the Streamlit app
def generate_webgl_optimizer() -> str:
    """Generate WebGL optimization code"""
    return """// SEOBOT: WebGL Performance Optimizations
// Add this to your WebGL initialization code

class WebGLOptimizer {
    constructor(canvas) {
        this.canvas = canvas;
        this.setupLazyLoading();
        this.setupPerformanceHints();
    }
    
    setupLazyLoading() {
        // Use Intersection Observer for lazy loading
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.initWebGL();
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(this.canvas);
    }
    
    setupPerformanceHints() {
        // Enable GPU acceleration hints
        this.canvas.style.willChange = 'transform';
        
        // Reduce pixel ratio on mobile for performance
        const isMobile = window.matchMedia('(pointer: coarse)').matches;
        this.pixelRatio = isMobile ? Math.min(window.devicePixelRatio, 1.5) : window.devicePixelRatio;
    }
    
    // Compress textures before uploading to GPU
    async compressTexture(image) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Resize large textures
        const maxSize = 2048;
        let width = image.width;
        let height = image.height;
        
        if (width > maxSize || height > maxSize) {
            const ratio = Math.min(maxSize / width, maxSize / height);
            width *= ratio;
            height *= ratio;
        }
        
        canvas.width = width;
        canvas.height = height;
        ctx.drawImage(image, 0, 0, width, height);
        
        return canvas;
    }
}

// Usage: const optimizer = new WebGLOptimizer(document.getElementById('webgl-canvas'));"""


def generate_service_worker() -> str:
    """Generate service worker for caching"""
    return """// SEOBOT: Service Worker for Browser Caching
const CACHE_NAME = 'seobot-cache-v1';
const urlsToCache = [
    '/',
    '/styles.css',
    '/script.js',
    '/og-image.jpg'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached or fetch new
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});
"""


def generate_lazy_loading_css() -> str:
    """Generate CSS for lazy loading animations"""
    return """/* SEOBOT: Lazy Loading & Performance CSS */

/* Smooth fade-in for lazy-loaded images */
img[loading="lazy"] {
    opacity: 0;
    transition: opacity 0.3s ease-in;
}

img[loading="lazy"].loaded {
    opacity: 1;
}

/* WebGL canvas optimizations */
canvas {
    will-change: transform;
    contain: layout style paint;
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Mobile optimizations */
@media (pointer: coarse) {
    canvas {
        /* Reduce complexity on touch devices */
        image-rendering: optimizeSpeed;
    }
}
"""


if __name__ == "__main__":
    # Test the rewriter
    print("SEOBOT Code Rewriter Module Loaded")
    print("Use in Streamlit app for full functionality")
