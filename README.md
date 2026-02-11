# 🤖 SEOBOT - SEO Knowledge Assistant

An intelligent SEO bot powered by your EPUB books. Extracts knowledge from SEO books and provides recommendations for meta tags, schema.org structured data, content briefs, and search optimization.

**Single app** — All features in one CLI: semantic search, multi-agent strategy, schema generation, meta tags, content briefs, competitor critique, and more.

## Features

- 📚 **Knowledge Base** — Extracts and indexes content from EPUB books
- 🔍 **Semantic Search** — ChromaDB + BGE embeddings for meaning-based retrieval
- 🏷️ **Meta Tag Generator** — Complete meta tag sets (SEO + Open Graph + Twitter)
- 📐 **Schema.org Generator** — Structured data (JSON-LD) for rich snippets
- 🔍 **Page Analyzer** — Analyze pages for SEO issues
- 🔑 **Keyword Suggestions** — Keyword ideas based on book knowledge
- ✅ **SEO Checklists** — Page-type specific optimization checklists
- 🚀 **Strategy Pipeline** — Full multi-agent pipeline: intent, keywords, schema, meta
- 📋 **Content Brief** — Comprehensive content brief generation
- 🔎 **Competitor Critique** — Analyze competitor content and identify opportunities

## Quick Start

### 1. Setup (First Time)

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize knowledge base from EPUB books (place .epub files in this directory)
python setup.py
```

### 2. Run Interactive Mode

```bash
python seo_bot.py
```

### 3. Run Web App (Streamlit)

```bash
py -3.13 -m streamlit run streamlit_app.py
# or
py -3.13 run_web.py
```

The web app includes:
- EPUB discovery from the current folder
- Initialize/Rebuild knowledge base from your `.epub` files
- Semantic search and Q&A from book passages
- SEO analysis, meta tag generation, schema generation, keywords, and checklists

### 4. Build Desktop App (Electron)

```bash
npm install
npm run build
```

Build output:
- `dist-electron/SEOBOT 1.0.0.exe` (portable desktop app)

Desktop app behavior:
- Starts local Streamlit backend automatically
- Uses the packaged `.epub` books and Python SEO modules
- Opens as a native window instead of browser tab

### 5. One-Shot Commands

```bash
python seo_bot.py --search "meta tags"
python seo_bot.py --ask "how to optimize title tags"
python seo_bot.py --checklist article
python seo_bot.py --brief "local SEO for restaurants"
python seo_bot.py --strategy "how to optimize meta tags" --url https://yoursite.com/guide --type article
```

## Commands

| Command | Description |
|---------|-------------|
| `search <query>` | Search knowledge base |
| `ask <question>` | Get SEO advice |
| `analyze` | Analyze a webpage |
| `meta` | Generate meta tags |
| `schema` | Generate structured data |
| `keywords <topic>` | Get keyword suggestions |
| `checklist [type]` | Get SEO checklist |
| `strategy <topic>` | Full pipeline: intent, keywords, schema, meta |
| `brief <topic>` | Generate content brief |
| `critique` | Competitor content critique |
| `stats` | Show knowledge base stats |
| `help` | Show help |
| `quit` | Exit |

## Project Structure

```
SEOBOT/
├── seo_bot.py           # Main app (single entry point)
├── setup.py             # Setup/initialization
├── epub_parser.py       # EPUB parsing
├── knowledge_base.py    # ChromaDB + BGE embeddings
├── seo_engine.py        # Recommendation engine
├── advanced_seo_engine/ # Multi-agent layer
│   ├── agents.py        # SEO agents
│   ├── orchestrator.py  # Multi-agent coordination
│   ├── kb_adapter.py    # KB adapter for agents
│   ├── concept_graph.py # Knowledge graph
│   └── epub_ingestion.py
├── requirements.txt
├── seo_knowledge.db     # SQLite (templates)
├── chroma_db/           # Vector store
└── *.epub               # Your SEO books
```

## Schema.org Templates

- **LocalBusiness** — Local businesses
- **Article** — Blog posts and articles
- **Product** — E-commerce products
- **FAQPage** — FAQ sections
- **HowTo** — Tutorials and guides
- **BreadcrumbList** — Navigation breadcrumbs

## Rebuilding Knowledge Base

```bash
python setup.py --force
# or
python seo_bot.py --init
```

## Requirements

- Python 3.8+ (3.10–3.12 recommended)
- See `requirements.txt`

First run downloads the BGE-large embedding model (~1.3GB). All processing is local and offline.

## GitHub Pages Deployment

This repository includes a GitHub Actions workflow that automatically deploys a landing page to GitHub Pages when you push to the `main` branch.

### Setup Instructions

1. Go to your repository **Settings** → **Pages**
2. Under **Build and deployment**, set **Source** to **GitHub Actions**
3. Push to the `main` branch or manually trigger the workflow
4. Your site will be available at `https://<username>.github.io/<repository>/`

The landing page showcases SEOBOT features and provides quick links to the GitHub repository and documentation.

### Manual Deployment

You can also manually trigger the deployment:
- Go to **Actions** tab in your repository
- Select **Deploy to GitHub Pages** workflow
- Click **Run workflow**

## License

MIT
