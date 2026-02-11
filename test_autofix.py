"""Test auto-fix functionality"""
from seo_knowledge_engine import seo_engine

print("=== SEO AUTO-FIX TEST ===\n")

# Test 1: Short description
print("Test 1: Short Description")
short_desc = "Professional web design services in West Virginia."
print(f"Original: \"{short_desc}\"")
print(f"Length: {len(short_desc)} chars")

is_valid, issues, fixed_desc = seo_engine.validate_meta_description(short_desc)
print(f"Fixed: \"{fixed_desc}\"")
print(f"New Length: {len(fixed_desc)} chars")
print(f"Issues: {issues}")
print()

# Test 2: Short title
print("Test 2: Short Title")
short_title = "Adaryus Portfolio"
print(f"Original: \"{short_title}\"")
print(f"Length: {len(short_title)} chars")

is_valid, issues, fixed_title = seo_engine.validate_meta_title(short_title)
print(f"Fixed: \"{fixed_title}\"")
print(f"New Length: {len(fixed_title)} chars")
print(f"Issues: {issues}")
print()

# Test 3: Generate meta tags with auto-fix
print("Test 3: Generate Meta Tags with Auto-Fix")
page_data = {
    'title': 'Adaryus',
    'description': 'Web design services.',
    'url': 'https://adaryus.com',
    'site_name': 'Adaryus',
    'og_type': 'website'
}

meta_tags = seo_engine.get_complete_meta_tags(page_data)
print(meta_tags[:800] + "...")
