<div align="center">
    <br/>
    <h1>Intelligo</h1>
    <h3>Translate your favourite Asian web novels to English</h3>
</div>

![Python 3.11+](https://img.shields.io/badge/python-%3E=3.11-blue?logo=python)

# Requirements
* Python 3.11+
* [OpenRouter API key](https://openrouter.ai/keys)

**Supported languages:** Korean

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
## Glossary
By default, Intelligo builds a glossary of terms at `output/term_glossary.json` during translation.
This glossary is automatically fed back into later chapters to keep names and key terms consistent.

You can override the glossary location:
```bash
python main.py --input-dir input --output-dir output --glossary-file ./my_glossary.json
```
## Changing OpenRouter models
You can use whichever AI model you'd like for translation. Change the `model` field in `intelligo/config.toml` to your desired model.

Try to choose a model with a higher context window. A higher context window generally means a better translation as the model has a larger 'memory' than a model with a smaller window.