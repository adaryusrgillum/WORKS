"""
SEOBOT SEO Engine - Trained on 5 Books
"""
import re, json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class SEOIssue:
    category: str
    severity: str
    title: str
    description: str
    fix: str
    law_reference: str

class SEOEngine:
    TRAINING_BOOKS = [
        {"title": "AI For SEO Essentials", "author": "Andrew Bus", "year": "2024"},
        {"title": "SEO Marketing Secrets", "author": "Web Services", "year": "2016"},
        {"title": "SEO Practice: Get To The Top of Google", "author": "S M Asif Bin Yousuf", "year": "2024"},
        {"title": "SEO 2024: Mastering Schema", "author": "Vikrom Sharma", "year": "2023"},
        {"title": "Python Automation", "author": "Andy Vickler", "year": "2021"},
    ]

    SEO_LAWS = {
        "meta_tags": {"title_min": 50, "title_max": 70, "desc_min": 150, "desc_max": 160,
            "title_law": "Title 50-70 chars with keyword at start",
            "desc_law": "Description 150-160 chars with CTA",
            "og_required": ["og:title", "og:description", "og:image", "og:url"]},
        "content": {"h1_law": "Exactly one H1 per page", "alt_law": "All images need alt text"},
        "schema": {"json_ld_law": "JSON-LD schema required in head"},
        "technical": {"https_law": "HTTPS mandatory", "canonical_law": "Canonical URLs prevent duplicates"},
        "mobile": {"viewport_law": "Viewport meta required"},
    }

    def __init__(self):
        self.rules_path = Path(__file__).parent / "seo_training_data" / "seo_rules_extracted.txt"

    def analyze_html(self, html: str, url: str = "") -> Dict:
        issues, scores = [], {}
        for name, func in [("meta_tags", self._meta), ("content", self._content), ("schema", self._schema), ("technical", self._tech)]:
            i, s = func(html, url)
            issues.extend(i)
            scores[name] = s
        return {"url": url, "overall_score": round(sum(scores.values())/len(scores), 1), "scores": scores,
            "issues": issues, "critical": len([i for i in issues if i.severity=="critical"]),
            "warning": len([i for i in issues if i.severity=="warning"])}

    def _meta(self, html, url):
        issues, score = [], 100
        t = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
        if t:
            tl = len(t.group(1).strip())
            if tl < 50: issues.append(SEOIssue("Meta", "critical", f"Title short ({tl}c)", "Need 50-70", "Expand title", self.SEO_LAWS["meta_tags"]["title_law"])); score -= 15
        else: issues.append(SEOIssue("Meta", "critical", "No title", "Missing", "Add title", self.SEO_LAWS["meta_tags"]["title_law"])); score -= 25
        if 'name="description"' not in html.lower(): issues.append(SEOIssue("Meta", "critical", "No description", "Missing", "Add meta desc", self.SEO_LAWS["meta_tags"]["desc_law"])); score -= 20
        for og in self.SEO_LAWS["meta_tags"]["og_required"]:
            if f'property="{og}"' not in html.lower(): issues.append(SEOIssue("Meta", "warning", f"No {og}", "Missing OG", f"Add {og}", "OG tags needed")); score -= 3
        return issues, max(0, score)

    def _content(self, html, url):
        issues, score = [], 100
        h1c = len(re.findall(r"<h1[^>]*>", html, re.I))
        if h1c == 0: issues.append(SEOIssue("Content", "critical", "No H1", "Missing", "Add H1", self.SEO_LAWS["content"]["h1_law"])); score -= 20
        elif h1c > 1: issues.append(SEOIssue("Content", "warning", f"{h1c} H1s", "Too many", "Keep 1 H1", self.SEO_LAWS["content"]["h1_law"])); score -= 10
        imgs = re.findall(r"<img[^>]+>", html, re.I)
        noalt = [i for i in imgs if "alt=" not in i.lower() or 'alt=""' in i.lower()]
        if noalt: issues.append(SEOIssue("Content", "warning", f"{len(noalt)} imgs no alt", "Need alt", "Add alt", self.SEO_LAWS["content"]["alt_law"])); score -= min(15, len(noalt)*2)
        return issues, max(0, score)

    def _schema(self, html, url):
        issues, score = [], 100
        if "application/ld+json" not in html.lower(): issues.append(SEOIssue("Schema", "critical", "No JSON-LD", "Missing schema", "Add schema", self.SEO_LAWS["schema"]["json_ld_law"])); score -= 30
        return issues, max(0, score)

    def _tech(self, html, url):
        issues, score = [], 100
        if url and not url.startswith("https://") and "localhost" not in url: issues.append(SEOIssue("Technical", "critical", "No HTTPS", "Insecure", "Add SSL", self.SEO_LAWS["technical"]["https_law"])); score -= 20
        if 'rel="canonical"' not in html.lower(): issues.append(SEOIssue("Technical", "warning", "No canonical", "Missing", "Add canonical", self.SEO_LAWS["technical"]["canonical_law"])); score -= 10
        if '<meta name="viewport"' not in html.lower(): issues.append(SEOIssue("Technical", "critical", "No viewport", "Not mobile", "Add viewport", self.SEO_LAWS["mobile"]["viewport_law"])); score -= 15
        return issues, max(0, score)

    def gen_fix(self, issue, proj):
        fixes = {
            "No title": f"<title>{proj.get('name','')} | {proj.get('type','')}</title>",
            "No description": f'<meta name="description" content="{proj.get("description","")}">',
            "No JSON-LD": self._schema_code(proj),
            "No canonical": f'<link rel="canonical" href="https://{proj.get("domain","")}">',
            "No viewport": '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        }
        return fixes.get(issue.title, f"<!-- {issue.fix} -->")

    def _schema_code(self, p):
        s = {"@context": "https://schema.org", "@type": p.get("schema_type", "Organization"),
            "name": p.get("name", ""), "url": f"https://{p.get('domain','')}", "description": p.get("description", "")}
        return '<script type="application/ld+json">\n' + json.dumps(s, indent=2) + '\n</script>'

    def get_recs(self, result):
        recs = [{"priority": 1 if i.severity=="critical" else 2, "category": i.category, "title": i.title,
            "fix": i.fix, "law": i.law_reference, "severity": i.severity} for i in result["issues"]]
        return sorted(recs, key=lambda x: x["priority"])

_engine = None
def get_engine():
    global _engine
    if not _engine: _engine = SEOEngine()
    return _engine
