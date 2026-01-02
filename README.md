# Xe-Bot: Research Paper Animation Generator

A powerful tool that fetches research papers, extracts introductions, segments them by topic, and generates engaging Manim animations for visual learning.

## 🚀 Features

- **Fetch & Extract**: Automatically retrieve research papers from arXiv and extract introductions
- **Segment & Classify**: Break introductions into 4-7 logical segments with topic classification
- **Animate**: Generate professional Manim animations for each segment (visual diagrams, not text walls!)
- **Agentic Flow**: Multi-agent architecture for robust processing pipeline
- **Database Storage**: Persist results in Neon PostgreSQL
- **Video Gallery**: Browse all generated animations with search and filter
- **MCP Server**: Expose animations as an API for AI assistants
- **React Frontend**: Modern, responsive UI with Tailwind CSS

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend)
- Manim Community Edition
- FFmpeg (for video rendering)
- OpenRouter API key
- Neon PostgreSQL database (optional)

## 🛠️ Installation

### Backend Setup

1. **Clone and setup:**
```bash
cd xe-bot
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Linux/Mac
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install Manim (if not already installed):**
```bash
pip install manim
```

4. **Configure environment:**
```bash
copy .env.example .env
# Edit .env with your credentials
```

### Frontend Setup

```bash
cd frontend
npm install
```

## 🚀 Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
python server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access the app at: http://localhost:3000

### Using Docker

```bash
docker-compose up -d
```

## 🔌 MCP Server (API for AI Assistants)

Xe-Bot includes an MCP server that exposes animation generation as tools:

```bash
# Install MCP
pip install mcp

# Run MCP server
python mcp_server.py
```

### Available MCP Tools:
- `search_arxiv` - Search arXiv papers
- `generate_animation` - Generate animations for a paper
- `get_paper_info` - Get paper details
- `list_animations` - List all generated videos
- `get_animation_code` - Get Manim code for a topic

### Claude Desktop Integration

Add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "xe-bot": {
      "command": "python",
      "args": ["path/to/xe-bot/mcp_server.py"],
      "env": {
        "OPENROUTER_API_KEY": "your-key"
      }
    }
  }
}
```

## ⚙️ Configuration

Edit `.env` file with your credentials:

```env
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional (for database persistence)
NEON_DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Animation settings
ANIMATION_OUTPUT_DIR=./output/animations
ANIMATION_QUALITY=medium_quality
```

## 🎯 Usage

### Process an arXiv Paper
```bash
python main.py --arxiv 2301.00234
```

### Generate Code Only (No Video Rendering)
```bash
python main.py --arxiv 2301.00234 --no-render
```

### Animate Custom Text
```bash
python main.py --text "Your research content here" --title "My Animation"
```

### Initialize Database
```bash
python main.py --init-db
```

### Run Demo
```bash
python main.py --demo
```

## 📁 Project Structure

```
xe-bot/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── src/
│   ├── config.py          # Configuration management
│   ├── database/          # Neon PostgreSQL models
│   │   ├── __init__.py
│   │   └── models.py
│   ├── llm/               # OpenRouter integration
│   │   ├── __init__.py
│   │   └── openrouter_client.py
│   ├── extraction/        # Paper fetching & text extraction
│   │   ├── __init__.py
│   │   └── paper_fetcher.py
│   ├── animation/         # Manim animation generation
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   └── templates.py
│   └── agents/            # Agentic workflow
│       ├── __init__.py
│       └── orchestrator.py
├── output/                # Generated animations
└── cache/                 # Cached papers
```

## 🤖 Agentic Architecture

The system uses 4 specialized agents:

1. **Fetcher Agent**: Retrieves papers from arXiv
2. **Extractor Agent**: Uses LLM to extract introduction sections
3. **Segmenter Agent**: Breaks intro into topic-labeled segments
4. **Animator Agent**: Generates Manim code and renders animations

### System Architecture Diagram

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                              XE-BOT ARCHITECTURE                                  ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║     ┌─────────────────────────────────────────────────────────────────────────┐   ║
║     │                         📱 USER INTERFACES                              │   ║
║     │      ┌──────────┐         ┌──────────┐         ┌──────────┐            │   ║
║     │      │  🌐 Web  │         │  💻 CLI  │         │  🤖 MCP  │            │   ║
║     │      │   App    │         │   Tool   │         │  Server  │            │   ║
║     │      └────┬─────┘         └────┬─────┘         └────┬─────┘            │   ║
║     └───────────┼────────────────────┼────────────────────┼──────────────────┘   ║
║                 └────────────────────┼────────────────────┘                      ║
║                                      ▼                                           ║
║     ┌─────────────────────────────────────────────────────────────────────────┐   ║
║     │                      ⚙️ BACKEND (FastAPI)                               │   ║
║     │  ┌───────────────────────────────────────────────────────────────────┐ │   ║
║     │  │                  🧠 MULTI-AGENT PIPELINE                          │ │   ║
║     │  │                                                                   │ │   ║
║     │  │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐           │ │   ║
║     │  │  │   📥    │   │   📄    │   │   ✂️    │   │   🎬    │           │ │   ║
║     │  │  │ FETCHER │──▶│EXTRACTOR│──▶│SEGMENTER│──▶│ANIMATOR │           │ │   ║
║     │  │  │  Agent  │   │  Agent  │   │  Agent  │   │  Agent  │           │ │   ║
║     │  │  └─────────┘   └─────────┘   └─────────┘   └─────────┘           │ │   ║
║     │  │       │              │             │             │               │ │   ║
║     │  └───────┼──────────────┼─────────────┼─────────────┼───────────────┘ │   ║
║     └──────────┼──────────────┼─────────────┼─────────────┼─────────────────┘   ║
║                │              │             │             │                      ║
║                ▼              ▼             ▼             ▼                      ║
║     ┌──────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐    ║
║     │   📚 arXiv   │  │  🤖 LLM     │  │  🤖 LLM     │  │  🎥 Manim        │    ║
║     │     API      │  │  OpenRouter │  │  OpenRouter │  │  + FFmpeg        │    ║
║     └──────────────┘  └─────────────┘  └─────────────┘  └────────┬─────────┘    ║
║                                                                   │             ║
║                              ┌────────────────────────────────────┘             ║
║                              ▼                                                  ║
║     ┌─────────────────────────────────────────────────────────────────────────┐ ║
║     │                         💾 DATA LAYER                                   │ ║
║     │    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐            │ ║
║     │    │  🗄️ Neon    │    │  📁 Cache    │    │  🎥 Output   │            │ ║
║     │    │  PostgreSQL  │    │   Storage    │    │   Videos     │            │ ║
║     │    └──────────────┘    └──────────────┘    └──────────────┘            │ ║
║     └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

### Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW PIPELINE                                  │
└──────────────────────────────────────────────────────────────────────────────────┘

  INPUT                         PROCESSING                              OUTPUT
  ─────                         ──────────                              ──────

┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────────────┐
│  arXiv  │     │  Paper  │     │  Intro  │     │ Segment │     │   Animation     │
│ Paper ID│────▶│   PDF   │────▶│  Text   │────▶│  JSON   │────▶│    Videos       │
│         │     │         │     │         │     │         │     │                 │
│2301.00234     │ + Meta  │     │500-2000 │     │ 4-7     │     │ • segment_1.mp4 │
└─────────┘     │  data   │     │ words   │     │ chunks  │     │ • segment_2.mp4 │
                └─────────┘     └─────────┘     └─────────┘     │ • full.mp4      │
                                                                └─────────────────┘
                     │               │               │
                     ▼               ▼               ▼
              ┌─────────────────────────────────────────────────┐
              │              NEON POSTGRESQL                    │
              │  ┌─────────┐  ┌─────────┐  ┌─────────────────┐  │
              │  │ papers  │  │segments │  │   animations    │  │
              │  └─────────┘  └─────────┘  └─────────────────┘  │
              └─────────────────────────────────────────────────┘
```

### Component Architecture

```
xe-bot/
│
├── 📱 FRONTEND (React + Tailwind)
│   ├── Paper Search Interface
│   ├── Video Gallery & Player
│   └── Settings Panel
│
├── ⚙️ BACKEND (Python FastAPI)
│   │
│   ├── 🎯 Orchestrator (agents/orchestrator.py)
│   │   └── Controls pipeline execution
│   │
│   ├── 🤖 AGENTS
│   │   ├── 📥 Fetcher Agent ──────▶ arXiv API
│   │   ├── 📄 Extractor Agent ────▶ OpenRouter LLM
│   │   ├── ✂️ Segmenter Agent ────▶ OpenRouter LLM
│   │   └── 🎬 Animator Agent ─────▶ OpenRouter LLM + Manim
│   │
│   └── 📦 SERVICES
│       ├── Config Manager
│       ├── Database Models
│       └── File Manager
│
├── 🔌 MCP SERVER
│   └── AI Assistant Integration (Claude, etc.)
│
└── 💾 STORAGE
    ├── Neon PostgreSQL (papers, segments, metadata)
    ├── Cache Directory (downloaded papers)
    └── Output Directory (rendered videos)
```

## 🎬 Animation Types

- **Segment Animations**: Individual animations for each segment
- **Full Animation**: Combined animation covering entire introduction
- **Templates**: Pre-built templates for common visualizations

## 📝 Example Output

```
🤖 Xe-Bot: Research Paper Animation Pipeline
============================================

Stage 1/4: Fetching Paper
✓ Found: Attention Is All You Need...

Stage 2/4: Extracting Introduction
✓ Extracted introduction (523 words)

Stage 3/4: Segmenting Introduction
✓ Created 4 segments
   1. Background [background]
   2. Problem Statement [problem_statement]
   3. Proposed Approach [approach]
   4. Contributions [contributions]

Stage 4/4: Generating Animations
✓ Generated 5/5 animations

✓ Pipeline Complete!
```

## 🔧 Troubleshooting

### Manim not rendering
- Ensure FFmpeg is installed and in PATH
- Try `manim --version` to verify installation

### OpenRouter API errors
- Verify your API key is correct
- Check your API credits/quota

### Database connection issues
- Verify your Neon connection string
- Ensure SSL mode is enabled

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.
