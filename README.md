# AI Code Reviewer

Automated GitHub PR review bot powered by Claude AI.

## Status

🚧 In active development — Day 1 setup complete.

## Tech Stack

- Python 3.11+
- FastAPI
- Anthropic Claude API
- PyGithub
- NetworkX

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
cp .env.example .env
# Fill in .env with your keys
uvicorn src.main:app --reload
```

## License

MIT