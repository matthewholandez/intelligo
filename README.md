<div align="center">
    <br/>
    <h1>Intelligo</h1>
    <h3>Translate your favourite Asian web novels to English</h3>
</div>

# Installation
First, clone this repository:
```bash
git clone https://github.com/matthewholandez/intelligo
```
Then, install dependencies:
```bash
cd intelligo
pip install -r requirements.txt
```
Then, configure your Gemini API key for translation:
```bash
mv .env.example .env
```
Finally, edit `.env` by replacing `your_key_here` [with your actual API key.](http://console.cloud.google.com/)

# Usage
```bash
python main.py --help
```

Note: Intelligo is currently only compatible with HTML files from certain web novel sites.