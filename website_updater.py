"""
SEOBOT Website Updater - Automatically fixes SEO issues using Knowledge Engine
"""

import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup

from seo_knowledge_engine import seo_engine, SEORule


class WebsiteUpdater:
    """
    Automatically updates website files to comply with SEO rules
    Uses the SEOKnowledgeEngine for validation and fixes
    """
    
    def __init__(self, project_path: str, project_data: Dict):
        self.project_path = Path(project_path)
        self.project_data = project_data
        self.backup_dir = None
        self.changes_log = []
        self.stats = {
            "files_processed": 0,
            "fixes_applied": 0,
            "warnings": 0,
            "errors": 0
        }
    
    def create_backup(self) -> Path:
        """Create timestamped backup of project"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_path.parent / f"{self.project_path.name}_backup_{timestamp}"
        
        if self.project_path.exists():
            shutil.copytree(self.project_path, self.backup_dir, ignore=shutil.ignore_patterns(
                'node_modules', '.git', 'dist', 'build', '*.tmp'
            ))
        
        return self.backup_dir
    
    def scan_files(self) -> List[Path]:
        """Find all HTML/TSX/JSX/Vue files to process"""
        files = []
        
        for pattern in ['**/*.html', '**/*.tsx', '**/*.jsx', '**/*.vue']:
            files.extend(self.project_path.glob(pattern))
        
        # Filter out node_modules and dist
        files = [f for f in files if 'node_modules' not in str(f) and 'dist' not in str(f)]
        
        return files
    
    def process_file(self, file_path: Path) -> Dict:
        """Process a single file and apply SEO fixes"""
        result = {
            "file": str(file_path),
            "success": False,
            "fixes": [],
            "warnings": [],
            "errors": []
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Determine page type from filename
            page_name = file_path.stem
            page_data = self._get_page_data(page_name)
            
            # Apply all fixes
            content = self._fix_meta_tags(content, page_data, result)
            content = self._fix_schema_markup(content, page_data, result)
            content = self._fix_open_graph(content, page_data, result)
            content = self._fix_twitter_cards(content, page_data, result)
            content = self._fix_image_alt_text(content, result)
            content = self._fix_headings(content, result)
            content = self._add_performance_optimizations(content, result)
            
            # Write if changed
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                result["success"] = True
                self.stats["files_processed"] += 1
                self.stats["fixes_applied"] += len(result["fixes"])
            
        except Exception as e:
            result["errors"].append(str(e))
            self.stats["errors"] += 1
        
        return result
    
    def _get_page_data(self, page_name: str) -> Dict:
        """Get page-specific data for SEO generation"""
        base_data = self.project_data.copy()
        
        # Customize based on page name
        page_configs = {
            'index': {'title_suffix': '', 'og_type': 'website'},
            'about': {'title_suffix': 'About Us', 'og_type': 'website'},
            'contact': {'title_suffix': 'Contact', 'og_type': 'website'},
            'services': {'title_suffix': 'Services', 'og_type': 'website'},
            'portfolio': {'title_suffix': 'Portfolio', 'og_type': 'website'},
            'blog': {'title_suffix': 'Blog', 'og_type': 'website'},
        }
        
        config = page_configs.get(page_name.lower(), {'title_suffix': page_name.title(), 'og_type': 'website'})
        
        if config['title_suffix']:
            base_data['title'] = f"{base_data['name']} - {config['title_suffix']}"
        else:
            base_data['title'] = f"{base_data['name']} - {base_data['type']}"
        
        base_data['og_type'] = config['og_type']
        base_data['url'] = f"https://{base_data['domain']}/{page_name if page_name != 'index' else ''}"
        
        return base_data
    
    def _fix_meta_tags(self, content: str, page_data: Dict, result: Dict) -> str:
        """Fix meta tags according to SEO rules"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Ensure head exists
        if not soup.head:
            soup.html.insert(0, soup.new_tag('head'))
        
        # Fix title
        title = soup.find('title')
        new_title = page_data['title']
        
        # Validate and fix title length
        is_valid, issues = seo_engine.validate_meta_title(new_title)
        if not is_valid:
            for issue in issues:
                result["warnings"].append(f"Title: {issue}")
            # Auto-fix
            if len(new_title) < 50:
                new_title = f"{new_title} | Professional Services"
            if len(new_title) > 60:
                new_title = new_title[:57] + "..."
        
        if title:
            title.string = new_title
            result["fixes"].append(f"Updated title: {new_title}")
        else:
            title_tag = soup.new_tag('title')
            title_tag.string = new_title
            soup.head.insert(0, title_tag)
            result["fixes"].append(f"Added title: {new_title}")
        
        # Fix meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        new_desc = page_data.get('description', '')
        
        # Validate and fix description
        is_valid, issues = seo_engine.validate_meta_description(new_desc)
        if not is_valid:
            for issue in issues:
                result["warnings"].append(f"Description: {issue}")
            # Auto-fix
            if len(new_desc) < 150:
                new_desc = f"{new_desc} Contact us today to learn more!"
            if len(new_desc) > 160:
                new_desc = new_desc[:157] + "..."
        
        if meta_desc:
            meta_desc['content'] = new_desc
            result["fixes"].append(f"Updated description ({len(new_desc)} chars)")
        else:
            meta_tag = soup.new_tag('meta')
            meta_tag.attrs['name'] = 'description'
            meta_tag.attrs['content'] = new_desc
            soup.head.append(meta_tag)
            result["fixes"].append(f"Added description ({len(new_desc)} chars)")
        
        # Add viewport if missing
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            viewport_tag = soup.new_tag('meta')
            viewport_tag.attrs['name'] = 'viewport'
            viewport_tag.attrs['content'] = 'width=device-width, initial-scale=1.0'
            soup.head.append(viewport_tag)
            result["fixes"].append("Added viewport meta tag")
        
        # Add canonical if missing
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            canonical_tag = soup.new_tag('link')
            canonical_tag.attrs['rel'] = 'canonical'
            canonical_tag.attrs['href'] = page_data['url']
            soup.head.append(canonical_tag)
            result["fixes"].append(f"Added canonical: {page_data['url']}")
        
        # Add robots if missing
        robots = soup.find('meta', attrs={'name': 'robots'})
        if not robots:
            robots_tag = soup.new_tag('meta')
            robots_tag.attrs['name'] = 'robots'
            robots_tag.attrs['content'] = 'index, follow'
            soup.head.append(robots_tag)
            result["fixes"].append("Added robots meta tag")
        
        return str(soup)
    
    def _fix_schema_markup(self, content: str, page_data: Dict, result: Dict) -> str:
        """Add or fix Schema.org JSON-LD markup"""
        soup = BeautifulSoup(content, 'html.parser')
        
        if not soup.head:
            return content
        
        # Check for existing schema
        existing = soup.find('script', attrs={'type': 'application/ld+json'})
        
        # Generate new schema
        schema_html = seo_engine.get_complete_schema(page_data)
        
        if existing:
            existing.replace_with(BeautifulSoup(schema_html, 'html.parser'))
            result["fixes"].append(f"Updated {page_data.get('schema_type', 'WebPage')} schema")
        else:
            soup.head.append(BeautifulSoup(schema_html, 'html.parser'))
            result["fixes"].append(f"Added {page_data.get('schema_type', 'WebPage')} schema markup")
        
        return str(soup)
    
    def _fix_open_graph(self, content: str, page_data: Dict, result: Dict) -> str:
        """Add Open Graph meta tags"""
        soup = BeautifulSoup(content, 'html.parser')
        
        if not soup.head:
            return content
        
        og_tags = {
            'og:type': page_data.get('og_type', 'website'),
            'og:url': page_data['url'],
            'og:title': page_data['title'],
            'og:description': page_data.get('description', ''),
            'og:image': f"{page_data['url']}/og-image.jpg",
            'og:site_name': page_data['name']
        }
        
        added = 0
        for property_name, content_value in og_tags.items():
            existing = soup.find('meta', attrs={'property': property_name})
            if existing:
                existing['content'] = content_value
            else:
                tag = soup.new_tag('meta')
                tag.attrs['property'] = property_name
                tag.attrs['content'] = content_value
                soup.head.append(tag)
                added += 1
        
        if added > 0:
            result["fixes"].append(f"Added {added} Open Graph tags")
        else:
            result["fixes"].append("Updated Open Graph tags")
        
        return str(soup)
    
    def _fix_twitter_cards(self, content: str, page_data: Dict, result: Dict) -> str:
        """Add Twitter Card meta tags"""
        soup = BeautifulSoup(content, 'html.parser')
        
        if not soup.head:
            return content
        
        twitter_tags = {
            'twitter:card': 'summary_large_image',
            'twitter:url': page_data['url'],
            'twitter:title': page_data['title'],
            'twitter:description': page_data.get('description', ''),
            'twitter:image': f"{page_data['url']}/twitter-image.jpg"
        }
        
        added = 0
        for name, content_value in twitter_tags.items():
            existing = soup.find('meta', attrs={'name': name})
            if existing:
                existing['content'] = content_value
            else:
                tag = soup.new_tag('meta')
                tag.attrs['name'] = name
                tag.attrs['content'] = content_value
                soup.head.append(tag)
                added += 1
        
        if added > 0:
            result["fixes"].append(f"Added {added} Twitter Card tags")
        else:
            result["fixes"].append("Updated Twitter Card tags")
        
        return str(soup)
    
    def _fix_image_alt_text(self, content: str, result: Dict) -> str:
        """Add alt text to images missing it"""
        soup = BeautifulSoup(content, 'html.parser')
        
        images_without_alt = soup.find_all('img', alt=False)
        fixed = 0
        
        for img in images_without_alt:
            src = img.get('src', '')
            if src:
                # Generate alt from filename
                filename = Path(src).stem
                alt_text = filename.replace('-', ' ').replace('_', ' ').title()
                img['alt'] = alt_text
                fixed += 1
        
        if fixed > 0:
            result["fixes"].append(f"Added alt text to {fixed} images")
        
        return str(soup)
    
    def _fix_headings(self, content: str, result: Dict) -> str:
        """Fix heading hierarchy issues"""
        soup = BeautifulSoup(content, 'html.parser')
        
        h1s = soup.find_all('h1')
        
        if len(h1s) == 0:
            result["warnings"].append("No H1 tag found - add one with primary keyword")
        elif len(h1s) > 1:
            result["warnings"].append(f"Multiple H1 tags found ({len(h1s)}) - should only have one")
        else:
            result["fixes"].append("H1 tag verified (1 found)")
        
        return str(soup)
    
    def _add_performance_optimizations(self, content: str, result: Dict) -> str:
        """Add performance optimization hints"""
        # Add lazy loading to images
        soup = BeautifulSoup(content, 'html.parser')
        
        images = soup.find_all('img')
        lazy_added = 0
        
        for img in images:
            if not img.get('loading'):
                img['loading'] = 'lazy'
                lazy_added += 1
        
        if lazy_added > 0:
            result["fixes"].append(f"Added lazy loading to {lazy_added} images")
        
        return str(soup)
    
    def generate_htaccess(self) -> str:
        """Generate .htaccess with caching and compression"""
        return """# SEOBOT Generated .htaccess - Performance Optimizations
# Generated: """ + datetime.now().isoformat() + """

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain text/html text/xml text/css
    AddOutputFilterByType DEFLATE application/xml application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript application/json
</IfModule>

# Browser caching
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/webp "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType font/woff2 "access plus 1 year"
    ExpiresDefault "access plus 2 days"
</IfModule>

# Security headers
<IfModule mod_headers.c>
    Header set X-Content-Type-Options "nosniff"
    Header set X-Frame-Options "SAMEORIGIN"
    Header set X-XSS-Protection "1; mode=block"
    Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>

# Redirect HTTP to HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]

# Clean URLs (remove .html extension)
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME}\\.html -f
RewriteRule ^(.*)$ $1.html [NC,L]
"""
    
    def generate_robots_txt(self) -> str:
        """Generate robots.txt"""
        domain = self.project_data.get('domain', 'example.com')
        return f"""# SEOBOT Generated robots.txt
User-agent: *
Allow: /

# Sitemap
Sitemap: https://{domain}/sitemap.xml

# Disallow admin areas
Disallow: /admin/
Disallow: /wp-admin/
Disallow: /private/
"""
    
    def run_full_update(self) -> Dict:
        """Run complete website update"""
        # Create backup
        backup_path = self.create_backup()
        
        # Scan files
        files = self.scan_files()
        
        # Process each file
        results = []
        for file_path in files:
            result = self.process_file(file_path)
            results.append(result)
        
        # Generate .htaccess
        htaccess_path = self.project_path / '.htaccess'
        if not htaccess_path.exists():
            htaccess_path.write_text(self.generate_htaccess())
            self.stats["fixes_applied"] += 1
            results.append({
                "file": ".htaccess",
                "success": True,
                "fixes": ["Created .htaccess with caching rules"],
                "warnings": [],
                "errors": []
            })
        
        # Generate robots.txt
        robots_path = self.project_path / 'robots.txt'
        if not robots_path.exists():
            robots_path.write_text(self.generate_robots_txt())
            self.stats["fixes_applied"] += 1
            results.append({
                "file": "robots.txt",
                "success": True,
                "fixes": ["Created robots.txt"],
                "warnings": [],
                "errors": []
            })
        
        return {
            "backup_path": str(backup_path),
            "stats": self.stats,
            "results": results
        }


if __name__ == "__main__":
    # Test
    print("SEOBOT Website Updater Module Loaded")
    print("Integrates with seo_knowledge_engine for rule-based fixes")
