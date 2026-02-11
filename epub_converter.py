"""
EPUB to TXT Converter + SEO Rules Extractor
Converts SEO books to text and extracts actionable SEO rules
"""

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os
import re
import json
from datetime import datetime
from pathlib import Path

def epub_to_text(epub_path):
    """Convert EPUB file to plain text"""
    book = epub.read_epub(epub_path)
    chapters = []

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'lxml')
            text = soup.get_text(separator='\n', strip=True)
            if text.strip():
                chapters.append(text)

    return '\n\n'.join(chapters)

def extract_seo_rules(text):
    """Extract actionable SEO rules from text"""
    rules = {
        "meta_tags": [],
        "technical": [],
        "content": [],
        "schema": [],
        "performance": [],
        "keywords": [],
        "links": [],
        "mobile": [],
        "ai_seo": []
    }

    # Patterns to find rules and recommendations
    rule_patterns = [
        r'(?:should|must|always|never|ensure|make sure|important|critical|essential)[\s:]+([^.!?]{20,150}[.!?])',
        r'(?:best practice|tip|rule|guideline)[\s:]+([^.!?]{20,150}[.!?])',
        r'(?:\d+\.\s*)([A-Z][^.!?]{20,150}[.!?])',
    ]

    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower()

        # Meta tag rules
        if any(kw in line_lower for kw in ['meta tag', 'title tag', 'meta description', 'og:', 'open graph']):
            if len(line) > 30 and len(line) < 500:
                rules["meta_tags"].append(line.strip())

        # Technical SEO
        if any(kw in line_lower for kw in ['page speed', 'load time', 'https', 'ssl', 'sitemap', 'robots.txt', 'canonical', '301 redirect']):
            if len(line) > 30 and len(line) < 500:
                rules["technical"].append(line.strip())

        # Content rules
        if any(kw in line_lower for kw in ['content quality', 'keyword density', 'heading', 'h1', 'h2', 'alt text', 'image optimization']):
            if len(line) > 30 and len(line) < 500:
                rules["content"].append(line.strip())

        # Schema/Structured Data
        if any(kw in line_lower for kw in ['schema', 'structured data', 'json-ld', 'rich snippet', 'markup']):
            if len(line) > 30 and len(line) < 500:
                rules["schema"].append(line.strip())

        # Performance
        if any(kw in line_lower for kw in ['core web vitals', 'lcp', 'fid', 'cls', 'performance', 'caching', 'minify', 'compress']):
            if len(line) > 30 and len(line) < 500:
                rules["performance"].append(line.strip())

        # Keywords
        if any(kw in line_lower for kw in ['keyword research', 'long-tail', 'search intent', 'keyword placement']):
            if len(line) > 30 and len(line) < 500:
                rules["keywords"].append(line.strip())

        # Links
        if any(kw in line_lower for kw in ['backlink', 'internal link', 'anchor text', 'link building', 'external link']):
            if len(line) > 30 and len(line) < 500:
                rules["links"].append(line.strip())

        # Mobile
        if any(kw in line_lower for kw in ['mobile-first', 'responsive', 'mobile friendly', 'viewport']):
            if len(line) > 30 and len(line) < 500:
                rules["mobile"].append(line.strip())

        # AI SEO
        if any(kw in line_lower for kw in ['ai', 'chatgpt', 'machine learning', 'natural language', 'semantic']):
            if len(line) > 30 and len(line) < 500:
                rules["ai_seo"].append(line.strip())

    # Deduplicate but keep all findings (no artificial cap)
    for category in rules:
        rules[category] = list(set(rules[category]))

    return rules

def main():
    epub_dir = Path(__file__).parent.resolve()
    output_dir = epub_dir / "seo_training_data"
    output_dir.mkdir(exist_ok=True)

    # Find all EPUB files in directory
    epub_files = list(epub_dir.glob("*.epub"))
    print(f"Found {len(epub_files)} EPUB files in {epub_dir}")

    all_rules = {
        "meta_tags": [],
        "technical": [],
        "content": [],
        "schema": [],
        "performance": [],
        "keywords": [],
        "links": [],
        "mobile": [],
        "ai_seo": []
    }

    for epub_path in epub_files:
        if not epub_path.exists():
            print(f"Skipping {epub_path.name} - not found")
            continue

        print(f"Converting: {epub_path.name}")

        try:
            # Convert to text
            text = epub_to_text(str(epub_path))

            # Save text file
            txt_name = epub_path.stem[:50] + ".txt"
            txt_path = output_dir / txt_name
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"  Saved: {txt_name}")

            # Extract rules
            rules = extract_seo_rules(text)
            for category in all_rules:
                all_rules[category].extend(rules[category])

        except Exception as e:
            print(f"  Error: {e}")

    # Deduplicate all rules
    for category in all_rules:
        all_rules[category] = list(set(all_rules[category]))

    # Save combined rules (TXT)
    rules_path = output_dir / "seo_rules_extracted.txt"
    with open(rules_path, 'w', encoding='utf-8') as f:
        f.write("# SEO RULES EXTRACTED FROM 5 BOOKS\n")
        f.write("# Use these rules to train SEOBOT's analysis engine\n\n")

        for category, rules_list in all_rules.items():
            f.write(f"\n## {category.upper().replace('_', ' ')}\n")
            f.write("-" * 50 + "\n")
            for i, rule in enumerate(rules_list, 1):
                f.write(f"{i}. {rule}\n")

    # Save JSON for structured loading
    json_path = output_dir / "seo_rules_extracted.json"
    json_payload = {
        "generated_at": datetime.now().isoformat(),
        "source_epubs": [p.name for p in epub_files],
        "total_rules": sum(len(r) for r in all_rules.values()),
        "categories": {k: sorted(v) for k, v in all_rules.items()}
    }
    with open(json_path, 'w', encoding='utf-8') as jf:
        json.dump(json_payload, jf, ensure_ascii=False, indent=2)

    print(f"\nRules saved to: {rules_path}")
    print(f"JSON saved to:  {json_path}")
    print(f"Total rules extracted: {json_payload['total_rules']}")

    return all_rules

if __name__ == "__main__":
    main()
