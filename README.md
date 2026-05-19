# AI Code Reviewer

> Automated GitHub Pull Request review bot powered by Claude AI and built on classical data structures.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

AI Code Reviewer automatically analyzes GitHub Pull Requests and posts intelligent code review comments using Claude AI. The system combines static analysis (AST), dependency graph theory, and a smart prioritization engine to deliver high-quality reviews while minimizing API costs.

## Features

- **Webhook-based PR processing** — receives GitHub events in real time
- **AST analysis** — extracts functions, classes, imports, and cyclomatic complexity
- **Dependency graph** — builds project-wide import graph with cycle detection
- **Priority queue** — ranks files by complexity, dependencies, and change size
- **Smart caching** — SHA256-based cache prevents redundant API calls
- **AI-powered reviews** — uses Claude for nuanced code feedback (Day 8+)

## Architecture

GitHub PR → Webhook → FastAPI
↓
[1] Fetch PR files (GitHub API)
↓
[2] Parse AST (Tree)
↓
[3] Build dependency graph (Graph + BFS/DFS)
↓
[4] Priority queue (Min-Heap)
↓
[5] Cache filter (Hash Map)
↓
[6] Claude AI review
↓
[7] Post inline comments to PR

## Data Structures & Algorithms

| Component | Data Structure | Algorithm | Complexity |
|-----------|----------------|-----------|------------|
| AST Analyzer | Tree | DFS traversal | O(n) |
| Dependency Graph | Directed Graph | BFS/DFS, Tarjan's cycle detection | O(V+E) |
| Prioritizer | Min-Heap | heappush/heappop | O(log n) |
| Cache | Hash Map | SHA256 hashing | O(1) avg |

## Tech Stack

- **Python 3.12** — core language
- **FastAPI** — web framework for webhooks
- **NetworkX** — graph operations
- **PyGithub** — GitHub API client
- **Anthropic SDK** — Claude AI integration
- **Graphviz** — graph visualization
- **pytest + pytest-cov** — testing

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/ai-code-reviewer.git
cd ai-code-reviewer

python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows
source venv/bin/activate         # Linux/Mac

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Create a `.env` file with:
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=your-secret
CLAUDE_MODEL=claude-haiku-4-5-20251001
LOG_LEVEL=INFO
PORT=8000
## Usage

### Local development

```bash
uvicorn src.main:app --reload
ngrok http 8000   # expose to GitHub
```

Add the ngrok URL as a webhook in your GitHub repository settings.

### Demo modules (no GitHub needed)

```bash
python -m src.try_parser         # AST analyzer demo
python -m src.try_graph          # Dependency graph demo
python -m src.try_priority       # Priority queue + cache demo
python -m src.try_orchestrator   # Full pipeline demo
```

## Testing

```bash
pytest                           # All tests with coverage
pytest tests/test_ast_analyzer.py -v
```

Coverage report: `htmlcov/index.html`

## Project Structure

ai-code-reviewer/
├── src/
│   ├── main.py                  # FastAPI app + webhook
│   ├── orchestrator.py          # Pipeline coordinator
│   ├── parsers/
│   │   └── ast_analyzer.py      # Tree-based code analysis
│   ├── graph/
│   │   └── dependency_graph.py  # Graph builder + cycle detection
│   ├── priority/
│   │   └── prioritizer.py       # Min-heap priority queue
│   ├── cache/
│   │   └── review_cache.py      # Hash-based cache
│   └── reviewer/                # AI integration (Day 8+)
├── tests/                       # pytest unit + integration tests
├── docs/                        # Reports and diagrams
└── requirements.txt

## Roadmap

- [x] Day 1: Project setup, FastAPI skeleton
- [x] Day 2: GitHub webhook with signature verification
- [x] Day 3: AST analyzer with cyclomatic complexity
- [x] Day 4: Dependency graph with cycle detection
- [x] Day 5: Priority queue and persistent cache
- [x] Day 6: Pipeline orchestrator
- [x] Day 7: Test coverage and documentation
- [x] Day 8: Claude AI integration
- [x] Day 9: GitHub comment posting
- [x] Day 10: End-to-end testing
- [x] Day 11: Polish and edge cases
- [x] Day 12: Production deployment
- [x] Day 13: Final documentation
- [x] Day 14: Presentation

## Author

Qurban — Computer Engineering student at Qarabağ Universiteti

## License

MIT
