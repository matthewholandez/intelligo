<div align="center">
    <br/>
    <h1>Intelligo</h1>
    <h3>Translate your favourite Asian web novels to English</h3>
</div>

![Python 3.11+](https://img.shields.io/badge/python-%3E=3.11-blue?logo=python)

# Installation
```bash
git clone https://github.com/matthewholandez/intelligo
cd intelligo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mv .env.example .env
```
Edit `.env` by replacing `your_key_here` [with your actual OpenRouter API key.](https://openrouter.ai/keys)

# Usage
```bash
python main.py --help
```

Note: Intelligo is currently only compatible with HTML files from certain web novel sites.
