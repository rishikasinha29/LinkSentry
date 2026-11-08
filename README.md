# LinkSentry v2.0

A dark SOC-inspired URL risk analysis dashboard built with Streamlit.

## Features
- URL parsing with common slash/backslash input normalization
- Rule-based indicators for raw IP hosts, long URLs, suspicious keywords, known shorteners, multiple subdomains, `@` symbols, and HTTP
- Low / Medium / High heuristic classification
- Interactive risk gauge and risk distribution donut chart
- Detailed indicator explanations and point contributions
- Session scan history and CSV export

## Run locally

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Important limitations
This is an educational heuristic prototype, not a phishing verdict engine. It does not visit URLs, follow redirects, query reputation databases, inspect page content, or guarantee safety. A low score does not mean a URL is safe.
