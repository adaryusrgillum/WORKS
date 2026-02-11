"""
Lead Capture Module for SEOBOT
Handles smart fill extraction, lead database, and RAG-powered recommendations
"""

import sqlite3
import json
import re
import uuid
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

# Selenium imports (optional - falls back to requests if not available)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Fallback to requests
import requests


class SeleniumScanner:
    """Selenium-based scanner for JavaScript-rendered pages"""

    def __init__(self, headless: bool = True, timeout: int = 15):
        self.headless = headless
        self.timeout = timeout
        self.driver = None

    def _init_driver(self):
        """Initialize Chrome WebDriver"""
        if not SELENIUM_AVAILABLE:
            raise RuntimeError("Selenium not installed. Run: pip install selenium webdriver-manager")

        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # Suppress logging
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(self.timeout)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Chrome: {e}")

    def scan_url(self, url: str) -> Tuple[str, Dict]:
        """
        Scan URL with Selenium, return (html, page_data)
        page_data includes title, description, schema_data, etc.
        """
        if not self.driver:
            self._init_driver()

        page_data = {
            "url": url,
            "title": "",
            "description": "",
            "schema_data": [],
            "og_data": {},
            "links": [],
            "images": [],
            "headings": {"h1": [], "h2": [], "h3": []},
            "load_time": 0,
            "status": "success"
        }

        try:
            start_time = time.time()
            self.driver.get(url)

            # Wait for page to load (wait for body)
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Additional wait for JS rendering
            time.sleep(2)

            page_data["load_time"] = round(time.time() - start_time, 2)

            # Get rendered HTML
            html = self.driver.page_source

            # Extract page data
            page_data["title"] = self.driver.title or ""

            # Get meta description
            try:
                desc_el = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
                page_data["description"] = desc_el.get_attribute("content") or ""
            except:
                pass

            # Get OG data
            og_tags = ["og:title", "og:description", "og:image", "og:url", "og:site_name"]
            for tag in og_tags:
                try:
                    el = self.driver.find_element(By.CSS_SELECTOR, f'meta[property="{tag}"]')
                    page_data["og_data"][tag] = el.get_attribute("content") or ""
                except:
                    pass

            # Get schema.org JSON-LD
            try:
                schema_scripts = self.driver.find_elements(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
                for script in schema_scripts:
                    try:
                        schema_json = json.loads(script.get_attribute("innerHTML"))
                        page_data["schema_data"].append(schema_json)
                    except:
                        pass
            except:
                pass

            # Get headings
            for h_level in ["h1", "h2", "h3"]:
                try:
                    headings = self.driver.find_elements(By.TAG_NAME, h_level)
                    page_data["headings"][h_level] = [h.text.strip() for h in headings if h.text.strip()]
                except:
                    pass

            # Get images (for alt text analysis)
            try:
                images = self.driver.find_elements(By.TAG_NAME, "img")
                page_data["images"] = [
                    {"src": img.get_attribute("src"), "alt": img.get_attribute("alt") or ""}
                    for img in images[:50]  # Limit to first 50
                ]
            except:
                pass

            # Get links
            try:
                links = self.driver.find_elements(By.TAG_NAME, "a")
                page_data["links"] = [
                    {"href": a.get_attribute("href"), "text": a.text.strip()}
                    for a in links[:100]  # Limit to first 100
                ]
            except:
                pass

            return html, page_data

        except Exception as e:
            page_data["status"] = f"error: {str(e)}"
            return "", page_data

    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def scan_url_with_fallback(url: str, use_selenium: bool = True) -> Tuple[str, Dict]:
    """
    Scan URL with Selenium if available, fallback to requests
    Returns (html, page_data)
    """
    page_data = {
        "url": url,
        "title": "",
        "description": "",
        "schema_data": [],
        "og_data": {},
        "scan_method": "unknown",
        "status": "success"
    }

    # Try Selenium first
    if use_selenium and SELENIUM_AVAILABLE:
        try:
            with SeleniumScanner(headless=True, timeout=15) as scanner:
                html, page_data = scanner.scan_url(url)
                page_data["scan_method"] = "selenium"
                if html:
                    return html, page_data
        except Exception as e:
            page_data["selenium_error"] = str(e)

    # Fallback to requests
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        html = response.text

        page_data["scan_method"] = "requests"

        # Extract basic data from HTML
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
        if title_match:
            page_data["title"] = title_match.group(1).strip()

        desc_match = re.search(
            r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
            html, re.I
        )
        if desc_match:
            page_data["description"] = desc_match.group(1).strip()

        # Get schema data
        schema_matches = re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html, re.I | re.DOTALL
        )
        for schema_str in schema_matches:
            try:
                page_data["schema_data"].append(json.loads(schema_str))
            except:
                pass

        return html, page_data

    except Exception as e:
        page_data["status"] = f"error: {str(e)}"
        page_data["scan_method"] = "failed"
        return "", page_data

@dataclass
class Lead:
    """Lead data model"""
    id: str
    url: str
    initial_score: float

    # Smart-filled (extracted from page)
    extracted_business_name: str = ""
    extracted_email: str = ""
    extracted_phone: str = ""
    extracted_address: str = ""

    # User-provided (editable)
    business_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    seo_challenge: str = ""

    # Audit data
    full_audit_json: str = ""
    ai_recommendations: str = ""

    # Status
    report_generated: bool = False
    follow_up_status: str = "new"  # new, contacted, converted, lost
    created_at: str = ""
    updated_at: str = ""


class SmartFillExtractor:
    """Extract business info from scanned page data"""

    def __init__(self):
        # Email regex
        self.email_pattern = re.compile(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            re.IGNORECASE
        )
        # Phone regex (US format)
        self.phone_pattern = re.compile(
            r'(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
        )

    def extract_business_info(self, page_data: Dict, html: str) -> Dict[str, str]:
        """Extract all business info from page data and HTML"""
        return {
            "business_name": self.extract_business_name(page_data, html),
            "email": self.extract_email(page_data, html),
            "phone": self.extract_phone(page_data, html),
            "address": self.extract_address(page_data, html),
        }

    def extract_business_name(self, page_data: Dict, html: str) -> str:
        """
        Priority:
        1. Schema.org name
        2. og:site_name
        3. Title before | or -
        4. Domain name
        """
        # 1. Schema.org name
        schema_data = page_data.get("schema_data", [])
        if schema_data:
            for schema in schema_data:
                if isinstance(schema, dict):
                    name = schema.get("name", "")
                    if name:
                        return name

        # 2. og:site_name
        og_match = re.search(
            r'property=["\']og:site_name["\'][^>]*content=["\']([^"\']+)["\']',
            html, re.IGNORECASE
        )
        if not og_match:
            og_match = re.search(
                r'content=["\']([^"\']+)["\'][^>]*property=["\']og:site_name["\']',
                html, re.IGNORECASE
            )
        if og_match:
            return og_match.group(1).strip()

        # 3. Title before separator
        title = page_data.get("title", "")
        if title:
            # Split on common separators
            for sep in [" | ", " - ", " :: ", " – ", " — "]:
                if sep in title:
                    return title.split(sep)[0].strip()
            # Return title if short enough
            if len(title) < 50:
                return title

        # 4. Domain name
        url = page_data.get("url", "")
        if url:
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            # Capitalize and remove TLD
            name = domain.split(".")[0].title()
            return name

        return ""

    def extract_email(self, page_data: Dict, html: str) -> str:
        """
        Priority:
        1. Schema.org email
        2. mailto: links
        3. Footer regex
        4. Full page regex
        """
        # 1. Schema.org email
        schema_data = page_data.get("schema_data", [])
        if schema_data:
            for schema in schema_data:
                if isinstance(schema, dict):
                    email = schema.get("email", "")
                    if email:
                        return email.replace("mailto:", "")

        # 2. mailto: links
        mailto_match = re.search(r'href=["\']mailto:([^"\'?]+)', html, re.IGNORECASE)
        if mailto_match:
            return mailto_match.group(1).strip()

        # 3. Footer regex (look in footer area first)
        footer_match = re.search(r'<footer[^>]*>(.*?)</footer>', html, re.IGNORECASE | re.DOTALL)
        if footer_match:
            footer_html = footer_match.group(1)
            emails = self.email_pattern.findall(footer_html)
            if emails:
                # Filter out common non-business emails
                for email in emails:
                    if not any(x in email.lower() for x in ['example', 'test', 'noreply', 'no-reply']):
                        return email

        # 4. Full page regex
        all_emails = self.email_pattern.findall(html)
        if all_emails:
            for email in all_emails:
                if not any(x in email.lower() for x in ['example', 'test', 'noreply', 'no-reply', '@sentry', '@seo']):
                    return email

        return ""

    def extract_phone(self, page_data: Dict, html: str) -> str:
        """
        Priority:
        1. Schema.org telephone
        2. tel: links
        3. Footer regex
        4. Full page regex
        """
        # 1. Schema.org telephone
        schema_data = page_data.get("schema_data", [])
        if schema_data:
            for schema in schema_data:
                if isinstance(schema, dict):
                    phone = schema.get("telephone", "")
                    if phone:
                        return phone

        # 2. tel: links
        tel_match = re.search(r'href=["\']tel:([^"\']+)', html, re.IGNORECASE)
        if tel_match:
            return tel_match.group(1).strip()

        # 3. Footer regex
        footer_match = re.search(r'<footer[^>]*>(.*?)</footer>', html, re.IGNORECASE | re.DOTALL)
        if footer_match:
            footer_html = footer_match.group(1)
            phones = self.phone_pattern.findall(footer_html)
            if phones:
                return phones[0]

        # 4. Full page regex (be more careful to avoid random numbers)
        # Look for phone near common labels
        phone_labeled = re.search(
            r'(?:phone|tel|call|contact)[:\s]*([+\d\s\(\)-]{10,})',
            html, re.IGNORECASE
        )
        if phone_labeled:
            return phone_labeled.group(1).strip()

        return ""

    def extract_address(self, page_data: Dict, html: str) -> str:
        """
        Priority:
        1. Schema.org address object
        2. <address> HTML tag
        """
        # 1. Schema.org address
        schema_data = page_data.get("schema_data", [])
        if schema_data:
            for schema in schema_data:
                if isinstance(schema, dict):
                    address = schema.get("address", {})
                    if isinstance(address, dict):
                        parts = []
                        if address.get("streetAddress"):
                            parts.append(address["streetAddress"])
                        if address.get("addressLocality"):
                            parts.append(address["addressLocality"])
                        if address.get("addressRegion"):
                            parts.append(address["addressRegion"])
                        if address.get("postalCode"):
                            parts.append(address["postalCode"])
                        if parts:
                            return ", ".join(parts)
                    elif isinstance(address, str):
                        return address

        # 2. <address> tag
        address_match = re.search(r'<address[^>]*>(.*?)</address>', html, re.IGNORECASE | re.DOTALL)
        if address_match:
            # Clean HTML tags
            address_text = re.sub(r'<[^>]+>', ' ', address_match.group(1))
            address_text = ' '.join(address_text.split())
            if len(address_text) < 200:  # Reasonable length
                return address_text.strip()

        return ""


class RAGReportGenerator:
    """Generate AI-powered recommendations using book knowledge"""

    def __init__(self):
        self.kb = None
        self._kb_available = None

    def _ensure_kb(self):
        """Lazy load knowledge base"""
        if self._kb_available is None:
            try:
                from knowledge_base import SEOKnowledgeBase
                self.kb = SEOKnowledgeBase().connect()
                self._kb_available = self.kb.collection.count() > 0
            except Exception as e:
                print(f"Knowledge base not available: {e}")
                self._kb_available = False
        return self._kb_available

    def generate_recommendations(self, audit: Dict, page_data: Dict) -> Dict:
        """Generate AI-powered recommendations with book citations"""
        recommendations = []

        issues = audit.get("issues", [])

        for issue in issues:
            rec = {
                "issue": issue.title if hasattr(issue, 'title') else issue.get("title", ""),
                "severity": issue.severity if hasattr(issue, 'severity') else issue.get("severity", "warning"),
                "category": issue.category if hasattr(issue, 'category') else issue.get("category", ""),
                "description": issue.description if hasattr(issue, 'description') else issue.get("description", ""),
                "fix": issue.fix if hasattr(issue, 'fix') else issue.get("fix", ""),
                "law_reference": issue.law_reference if hasattr(issue, 'law_reference') else issue.get("law_reference", ""),
                "book_citations": [],
                "ai_recommendation": "",
                "code_fix": ""
            }

            # Query book knowledge for this issue
            book_results = self._query_book_knowledge(f"{rec['issue']} {rec['description']}")
            rec["book_citations"] = book_results

            # Generate AI recommendation based on book knowledge
            if book_results:
                rec["ai_recommendation"] = self._synthesize_recommendation(rec, book_results)
            else:
                rec["ai_recommendation"] = f"Based on SEO best practices: {rec['fix']}"

            # Generate code fix
            rec["code_fix"] = self._generate_code_fix(issue, page_data)

            recommendations.append(rec)

        return {
            "recommendations": recommendations,
            "total_issues": len(recommendations),
            "critical_count": len([r for r in recommendations if r["severity"] == "critical"]),
            "book_citations_count": sum(len(r["book_citations"]) for r in recommendations),
            "generated_at": datetime.now().isoformat()
        }

    def _query_book_knowledge(self, issue_text: str) -> List[Dict]:
        """Query the book knowledge base for relevant passages"""
        if not self._ensure_kb():
            return []

        try:
            results = self.kb.search(issue_text, limit=3)
            return [
                {
                    "book_title": r.get("book_title", "SEO Book"),
                    "chapter": r.get("chapter_title", ""),
                    "content": r.get("content", "")[:300] + "..." if len(r.get("content", "")) > 300 else r.get("content", ""),
                    "relevance": round(r.get("similarity", 0) * 100, 1)
                }
                for r in results
            ]
        except Exception as e:
            print(f"RAG query error: {e}")
            return []

    def _synthesize_recommendation(self, issue: Dict, book_results: List[Dict]) -> str:
        """Synthesize a recommendation from book knowledge"""
        if not book_results:
            return issue.get("fix", "")

        # Build recommendation from best book result
        best = book_results[0]
        book_ref = f"[{best['book_title']}]"

        # Extract key insight from content
        content = best.get("content", "")

        # Simple synthesis: combine issue fix with book insight
        rec = f"{issue.get('fix', '')} According to {book_ref}: "

        # Get first meaningful sentence from book content
        sentences = content.split(".")
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 30 and len(sent) < 200:
                rec += sent + "."
                break

        return rec

    def _generate_code_fix(self, issue, page_data: Dict) -> str:
        """Generate a code snippet to fix the issue"""
        title = issue.title if hasattr(issue, 'title') else issue.get("title", "")

        # Use the SEO engine's fix generator if available
        try:
            from seo_engine import get_engine
            engine = get_engine()
            proj = {
                "name": page_data.get("title", "Business"),
                "domain": urlparse(page_data.get("url", "")).netloc,
                "description": page_data.get("description", ""),
                "schema_type": "Organization"
            }
            return engine.gen_fix(issue, proj)
        except:
            # Fallback to simple code templates
            fixes = {
                "No title": '<title>Your Business Name | Primary Service | Location</title>',
                "Title short": '<title>Your Business Name | Primary Service | Location</title>',
                "No description": '<meta name="description" content="Your compelling description here (150-160 characters with a call to action)">',
                "No JSON-LD": '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Your Business",
  "url": "https://yourdomain.com"
}
</script>''',
                "No canonical": '<link rel="canonical" href="https://yourdomain.com/page">',
                "No viewport": '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                "No H1": '<h1>Your Primary Page Heading with Keywords</h1>',
            }

            for key, code in fixes.items():
                if key.lower() in title.lower():
                    return code

            return f"<!-- Fix needed: {title} -->"


class LeadDatabase:
    """SQLite database for lead storage"""

    def __init__(self, db_path: str = "leads.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to database and ensure schema exists"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        return self

    def _init_schema(self):
        """Create tables if they don't exist"""
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                initial_score REAL,

                extracted_business_name TEXT,
                extracted_email TEXT,
                extracted_phone TEXT,
                extracted_address TEXT,

                business_name TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                seo_challenge TEXT,

                full_audit_json TEXT,
                ai_recommendations TEXT,

                report_generated INTEGER DEFAULT 0,
                follow_up_status TEXT DEFAULT 'new',
                created_at TEXT,
                updated_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(contact_email);
            CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at);
            CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(follow_up_status);
        """)
        self.conn.commit()

    def save_lead(self, lead_dict: Dict) -> str:
        """Save a lead to database, returns lead ID"""
        cursor = self.conn.cursor()

        # Generate ID if not present
        if "id" not in lead_dict or not lead_dict["id"]:
            lead_dict["id"] = str(uuid.uuid4())[:8]

        # Set timestamps
        now = datetime.now().isoformat()
        lead_dict["created_at"] = lead_dict.get("created_at") or now
        lead_dict["updated_at"] = now

        # Convert booleans to integers
        if "report_generated" in lead_dict:
            lead_dict["report_generated"] = 1 if lead_dict["report_generated"] else 0

        # Build query
        columns = list(lead_dict.keys())
        placeholders = ["?" for _ in columns]
        values = [lead_dict[c] for c in columns]

        cursor.execute(
            f"INSERT OR REPLACE INTO leads ({', '.join(columns)}) VALUES ({', '.join(placeholders)})",
            values
        )
        self.conn.commit()

        return lead_dict["id"]

    def get_lead(self, lead_id: str) -> Optional[Dict]:
        """Get a lead by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            d["report_generated"] = bool(d.get("report_generated", 0))
            return d
        return None

    def get_all_leads(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get all leads, optionally filtered by status"""
        cursor = self.conn.cursor()
        if status:
            cursor.execute(
                "SELECT * FROM leads WHERE follow_up_status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM leads ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
        return [dict(row) for row in cursor.fetchall()]

    def update_status(self, lead_id: str, status: str):
        """Update lead follow-up status"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE leads SET follow_up_status = ?, updated_at = ? WHERE id = ?",
            (status, datetime.now().isoformat(), lead_id)
        )
        self.conn.commit()

    def export_to_csv(self, filepath: str):
        """Export all leads to CSV"""
        leads = self.get_all_leads(limit=10000)
        if not leads:
            return

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=leads[0].keys())
            writer.writeheader()
            writer.writerows(leads)

    def get_stats(self) -> Dict:
        """Get lead statistics"""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM leads")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT follow_up_status, COUNT(*) FROM leads GROUP BY follow_up_status")
        by_status = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT AVG(initial_score) FROM leads")
        avg_score = cursor.fetchone()[0] or 0

        return {
            "total_leads": total,
            "by_status": by_status,
            "average_score": round(avg_score, 1)
        }

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Challenge options for dropdown
SEO_CHALLENGES = [
    "Not ranking on Google",
    "Low website traffic",
    "Poor local search visibility",
    "Website is slow",
    "Competitors outranking me",
    "Don't know where to start",
    "Other"
]


def create_lead_from_scan(url: str, score: float, extracted_info: Dict) -> Lead:
    """Factory function to create a Lead from scan results"""
    return Lead(
        id=str(uuid.uuid4())[:8],
        url=url,
        initial_score=score,
        extracted_business_name=extracted_info.get("business_name", ""),
        extracted_email=extracted_info.get("email", ""),
        extracted_phone=extracted_info.get("phone", ""),
        extracted_address=extracted_info.get("address", ""),
        business_name=extracted_info.get("business_name", ""),
        contact_email=extracted_info.get("email", ""),
        contact_phone=extracted_info.get("phone", ""),
        created_at=datetime.now().isoformat()
    )
