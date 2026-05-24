# ⚡ TechDoc AI Agent

> **Automatically generate and update technical documentation from codebases, APIs, pull requests, and deployment changes.**

Developers rarely update documentation, causing outdated APIs and onboarding confusion. TechDoc AI Agent solves this by using Claude claude-sonnet-4-6 to automatically produce accurate, developer-friendly documentation — instantly.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **Code → Docs** | Paste or upload source code → get docstrings, README, architecture overview |
| 🔀 **PR Analyzer** | Point to any GitHub PR URL → get a professional changelog entry |
| 🚀 **Deployment Docs** | Paste deployment diffs → get release notes & migration guides |
| 🌐 **API Documentation** | Paste route code or upload OpenAPI JSON → full API reference |
| 🔄 **Diff-Aware Updates** | Paste old + new code → update only what changed |
| 📦 **Multi-Format Export** | Download as Markdown, styled HTML, or ZIP archive |

### Supported Languages
Python · JavaScript · TypeScript · Java · Go · Rust · C/C++ · Ruby · PHP · C#

### Supported Doc Styles
Google · NumPy/SciPy · reStructuredText (Sphinx) · JSDoc · Javadoc

---

## 🚀 Quick Start

```bash
# 1. Clone / navigate to the project
cd AI_agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API keys
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 4. Run the app
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com)
- (Optional) A [GitHub Personal Access Token](https://github.com/settings/tokens) for PR analysis

### Setup

```bash
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```env
ANTHROPIC_API_KEY=sk-ant-...          # Required
GITHUB_TOKEN=ghp_...                   # Optional — for PR analysis
```

You can also enter API keys directly in the app sidebar.

---

## 💻 Usage

### Tab 1: 📝 Code → Docs

1. Choose **Paste Code** or **Upload Files**
2. Select documentation types: Docstrings, README, API Docs, Architecture
3. Click **⚡ Generate Documentation**
4. Download as Markdown or HTML

**Example input:**
```python
def calculate_compound_interest(principal, rate, n, t):
    return principal * (1 + rate/n) ** (n*t)
```

**Example output (Google style):**
```python
def calculate_compound_interest(principal, rate, n, t):
    """Calculate compound interest over a period.

    Args:
        principal (float): Initial investment amount.
        rate (float): Annual interest rate as a decimal (e.g., 0.05 for 5%).
        n (int): Number of times interest is compounded per year.
        t (int): Number of years.

    Returns:
        float: Final amount after compound interest.

    Example:
        >>> calculate_compound_interest(1000, 0.05, 12, 5)
        1283.36
    """
    return principal * (1 + rate/n) ** (n*t)
```

---

### Tab 2: 🔀 PR Analyzer

1. Paste a GitHub PR URL: `https://github.com/owner/repo/pull/123`
2. Or paste a raw diff
3. Click **📝 Generate Changelog Entry**

Output follows [Keep a Changelog](https://keepachangelog.com) format.

---

### Tab 3: 🚀 Deployment Docs

1. Enter service name, old version, new version
2. Paste deployment diff, commit messages, or config changes
3. Select: Release Notes / Migration Guide / Breaking Changes
4. Click **🚀 Generate Release Docs**

---

### Tab 4: 🌐 API Documentation

1. Paste route handler code (Flask / FastAPI / Express)
2. Or upload an OpenAPI/Swagger `.json` file
3. Click **🌐 Generate API Documentation**

---

## 🏗️ Architecture

```
AI_agent/
├── app.py                    # Streamlit UI (4 tabs)
├── agent/
│   ├── doc_agent.py          # Claude claude-sonnet-4-6 agent (tool use + caching)
│   └── prompts.py            # System prompts for each doc type
├── parsers/
│   ├── code_parser.py        # Python AST + regex multi-language parser
│   ├── pr_parser.py          # Unified diff parser
│   └── api_parser.py         # Route extractor (Flask/FastAPI/Express/OpenAPI)
└── utils/
    ├── github_client.py      # GitHub REST API client
    ├── exporter.py           # Markdown → HTML / ZIP exporter
    └── file_handler.py       # Multi-file upload handler
```

**Data flow:**
```
User Input (code/PR/diff)
      ↓
  Parsers (extract structure)
      ↓
  DocAgent (Claude claude-sonnet-4-6 with prompt caching)
      ↓
  Generated Markdown
      ↓
  Exporter (MD / HTML / ZIP)
      ↓
  User Download
```

---

## ⚙️ Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | Your Anthropic API key |
| `GITHUB_TOKEN` | No | GitHub PAT for PR analysis |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — feel free to use and modify.

---

*Built with ❤️ using [Claude claude-sonnet-4-6](https://anthropic.com) and [Streamlit](https://streamlit.io)*
