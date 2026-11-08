import csv
import io
import ipaddress
import re
from datetime import datetime
from html import escape
from urllib.parse import urlparse, urlunparse

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="LinkSentry",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- Theme --------------------
# Base colors come from .streamlit/config.toml; this CSS only adds the custom pieces.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700;800&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
:root{--bg:#070b15;--surface:#0d1422;--surface2:#111d2e;--line:#1e3a49;--text:#eaf7ff;--muted:#8298aa;--cyan:#53e8f4;--low:#42e6a4;--medium:#ffbd59;--high:#ff405d}
.stApp{background:radial-gradient(ellipse at 50% -15%,rgba(25,185,208,.12),transparent 42%),linear-gradient(rgba(83,232,244,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(83,232,244,.025) 1px,transparent 1px),var(--bg);background-size:auto,46px 46px,46px 46px,auto;color:var(--text)}
.stApp,.stApp p,.stApp li,.stApp label,.stApp input,.stApp button,.stApp h1,.stApp h2,.stApp h3{font-family:'Inter',sans-serif}
header[data-testid="stHeader"]{background:rgba(7,11,21,.82)} footer{visibility:hidden}
.block-container{max-width:1380px;padding-top:1.3rem;padding-bottom:2.5rem}
section[data-testid="stSidebar"]{background:rgba(8,14,26,.98);border-right:1px solid #183141}
.stApp :focus-visible{outline:2px solid var(--cyan);outline-offset:2px}
.brand{font:700 1.25rem 'Orbitron',sans-serif;color:#eafaff;letter-spacing:.3px}.brand-mark{color:var(--cyan);text-shadow:0 0 18px #53e8f477}
.side-note{color:var(--muted);font-size:.8rem;line-height:1.5}.side-row{display:flex;align-items:center;gap:.55rem;font-size:.86rem;padding:.28rem 0;color:#c8d8e4}.side-row span.n{margin-left:auto;font-family:'JetBrains Mono',monospace;color:#eaf7ff}
.dot{width:.55rem;height:.55rem;border-radius:50%;background:var(--c,var(--muted));box-shadow:0 0 10px var(--c,var(--muted));flex:none}.d-high{--c:var(--high)}.d-medium{--c:var(--medium)}.d-low{--c:var(--low)}
.hero{text-align:center;padding:.35rem 0 1.15rem;margin-bottom:1.2rem;border-bottom:1px solid #1a3948}.hero:after{content:'';display:block;width:190px;height:2px;margin:1rem auto -1.2rem;background:var(--cyan);box-shadow:0 0 14px var(--cyan)}
.hero-kicker{font:.7rem 'JetBrains Mono',monospace;color:var(--cyan);letter-spacing:2.4px}.hero h1{font:700 clamp(1.55rem,3vw,2.45rem) 'Orbitron',sans-serif;color:#eafaff;margin:.55rem 0 .35rem}.hero h1 span{color:var(--cyan)}.hero p{color:#7fa9ba;font:.78rem 'JetBrains Mono',monospace;letter-spacing:1.2px;margin:0}
.page-title{font-size:1.4rem;font-weight:700;letter-spacing:-.02em;margin:.2rem 0 .25rem}.page-sub{color:var(--muted);font-size:.9rem;line-height:1.55;margin-bottom:1.1rem}.section-kicker{color:#4fcbd8;font:.68rem 'JetBrains Mono',monospace;letter-spacing:1.8px;margin:.4rem 0}
.panel{background:linear-gradient(145deg,rgba(15,25,41,.97),rgba(9,15,27,.97));border:1px solid #1d3b4a;border-radius:13px;padding:1rem 1.1rem;box-shadow:0 10px 32px #0002}.panel-title{font:600 .88rem 'Orbitron',sans-serif;color:var(--cyan);letter-spacing:.5px;padding-bottom:.7rem;margin-bottom:.8rem;border-bottom:1px solid #1b3544}
div[data-testid="stForm"]{background:rgba(12,20,34,.94);border:1px solid #214858;border-radius:12px;padding:1rem 1.1rem .45rem;box-shadow:0 8px 30px #0003}
div[data-testid="stTextInput"] input{height:3.05rem;background:#070d18;color:#b9f6ff;border:1px solid #3ab9c8;border-radius:7px;font:600 .9rem 'JetBrains Mono',monospace}
div[data-testid="stTextInput"] input:focus{border-color:var(--cyan);box-shadow:0 0 0 1px var(--cyan),0 0 18px #53e8f41f}
div[data-testid="stFormSubmitButton"] button{width:100%;min-height:3.05rem;background:#102b39;color:var(--cyan);border:1px solid #3cc8d8;border-radius:7px;font:700 .82rem 'Orbitron',sans-serif;letter-spacing:.7px}
div[data-testid="stFormSubmitButton"] button:hover{background:#164353;color:#eaffff;border-color:#8af7ff}
.stButton>button,.stDownloadButton>button{border:1px solid #285064;background:#101d2d;color:#c6e8ef;border-radius:8px}.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--cyan);color:var(--cyan);background:#142b3a}
.verdict{display:flex;align-items:center;gap:1.2rem;background:linear-gradient(120deg,#0e1727,#0a111f);border:1px solid #1e3e4e;border-radius:13px;padding:1.25rem;min-height:190px}
.v-ring-wrap{min-width:130px;text-align:center;border-right:1px solid #1b3544;padding-right:1.15rem}.score-ring{width:108px;height:108px;margin:0 auto .65rem;border-radius:50%;display:grid;place-items:center;background:conic-gradient(var(--c) calc(var(--score)*1%),#1d2939 0);position:relative;box-shadow:0 0 24px color-mix(in srgb,var(--c) 20%,transparent)}.score-ring:before{content:'';position:absolute;inset:9px;border-radius:50%;background:#0b1321;border:1px solid #20394b}.score-ring strong{position:relative;z-index:1;font:700 1.45rem 'Orbitron',sans-serif;color:#f3fbff}.ring-caption{color:#73899e;font:600 .62rem 'Orbitron',sans-serif;letter-spacing:1px}
.v-content{flex:1;min-width:0}.v-label{font:700 clamp(1.1rem,2.3vw,1.85rem) 'Orbitron',sans-serif;letter-spacing:.2px;color:var(--c);line-height:1.3}.v-host{background:#050a13;border-left:3px solid var(--cyan);border-radius:4px;padding:.7rem .8rem;color:#d7e8f2;font:.8rem 'JetBrains Mono',monospace;overflow-wrap:anywhere;margin:.7rem 0}.verdict p{color:#9fb2c2;font-size:.83rem;line-height:1.5;margin:.35rem 0}.v-score{color:#8197aa;font-size:.73rem;margin-top:.5rem}.v-high{--c:var(--high)}.v-medium{--c:var(--medium)}.v-low{--c:var(--low)}
.anatomy{background:#080f1b;border:1px solid #1a3545;border-radius:9px;padding:.9rem 1rem}.url{font:.88rem/1.9 'JetBrains Mono',monospace;overflow-wrap:anywhere}.url .dim{color:#64788a}.url .sub{color:#9cb5c4}.url .domain{color:#e8faff;font-weight:600}.url .flag{border-radius:3px;padding:.05em .25em;margin:0 -.05em}.url .flag-high{background:#ff405d29;color:#ff9aa9;box-shadow:0 0 0 1px #ff405d66}.url .flag-med{background:#ffbd5924;color:#ffd18b;box-shadow:0 0 0 1px #ffbd5959}.url .flag-low{background:#42e6a41f;color:#7ef0c1;box-shadow:0 0 0 1px #42e6a44d}.anatomy-note{color:var(--muted);font-size:.77rem;margin-top:.65rem}
.finding{border:1px solid #1b3545;border-left:3px solid var(--c);border-radius:7px;background:#0b1422;padding:.68rem .75rem;margin:.45rem 0}.f-high{--c:var(--high)}.f-medium{--c:var(--medium)}.f-low{--c:var(--low)}.f-top{display:flex;justify-content:space-between;gap:1rem;align-items:center}.f-title{color:#e5f2fa;font-weight:600;font-size:.82rem}.f-sev{color:var(--c);font:.63rem 'JetBrains Mono',monospace;margin-left:.5rem;text-transform:uppercase}.f-pts{color:var(--c);font:600 .78rem 'JetBrains Mono',monospace}.f-detail{color:#8ea4b5;font-size:.76rem;line-height:1.5;margin-top:.3rem}.empty{color:var(--muted);border:1px dashed #2b4b5b;border-radius:9px;padding:.9rem}.telemetry-card{background:#080f1b;border:1px solid #1b3545;border-radius:8px;padding:.7rem .8rem;min-height:80px}.telemetry-label{color:#788da2;font:600 .62rem 'JetBrains Mono',monospace;letter-spacing:.5px}.telemetry-value{color:#63e8a2;font:700 1.1rem 'Orbitron',sans-serif;margin-top:.35rem}.telemetry-sub{color:#8298aa;font-size:.68rem;margin-top:.15rem}
div[data-testid="stDataFrame"]{border:1px solid #1c3b4b;border-radius:9px}hr{border-color:#1b3545}
</style>
""", unsafe_allow_html=True)


def render(markup):
    """Render HTML without markdown treating indented lines as code blocks."""
    st.markdown(re.sub(r"\n\s*", "", markup).strip(), unsafe_allow_html=True)


# -------------------- Detection logic --------------------
KEYWORDS = ["login", "verify", "update", "account", "password", "banking",
            "secure", "confirm", "wallet", "signin", "payment"]
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "shorturl.at", "is.gd",
              "cutt.ly", "ow.ly", "buff.ly", "tiny.cc"}
TWO_PART_SUFFIXES = {"co.uk", "org.uk", "com.au", "co.in", "org.in", "net.in",
                     "gov.in", "ac.in", "co.jp", "com.br"}
KEYWORD_RE = re.compile("|".join(KEYWORDS), re.I)


def is_ip(host):
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def analyze_url(raw):
    raw = (raw or "").strip()
    if not raw:
        return {"valid": False, "error": "Enter a URL to analyze."}

    # Repair common copy/paste mistakes such as https:\\example.com or https:/example.com.
    normalized = raw.replace("\\", "/")
    if re.match(r"^https?:/+", normalized, re.I):
        scheme, rest = normalized.split(":", 1)
        candidate = scheme.lower() + "://" + rest.lstrip("/")
    elif re.match(r"^https?://", normalized, re.I):
        candidate = normalized
    else:
        candidate = "http://" + normalized.lstrip("/")

    try:
        parsed = urlparse(candidate)
        host = parsed.hostname or ""
        _ = parsed.port
        if not host or ("." not in host and not is_ip(host)):
            return {"valid": False, "error": "Enter a valid hostname, such as https://example.com."}
    except ValueError:
        return {"valid": False, "error": "The URL format or port appears invalid."}

    score, findings = 0, []

    def add(points, key, title, severity, detail):
        nonlocal score
        score += points
        findings.append({"points": points, "key": key, "title": title,
                         "severity": severity, "detail": detail})

    if is_ip(host):
        add(25, "ip", "IP address used as host", "High",
            "The destination is specified as a raw IP address instead of a conventional domain.")
    if len(candidate) > 75:
        add(10, "long", "Unusually long URL", "Low",
            "Long URLs can contain extensive parameters or make the destination harder to inspect.")
    matches = [word for word in KEYWORDS if word in candidate.lower()]
    if matches:
        add(15, "keywords", "Suspicious keyword(s)", "Medium",
            "Keyword matches: " + ", ".join(matches[:6]) + ". These words are not malicious by themselves.")
    if host.lower() in SHORTENERS:
        add(20, "shortener", "URL shortener detected", "Medium",
            "The visible link does not reveal the final destination without resolving the redirect.")
    if not is_ip(host) and len(host.split(".")) > 3:
        add(15, "subdomains", "Multiple subdomains", "Medium",
            "The hostname contains more than three dot-separated labels.")
    if "@" in candidate:
        add(20, "at", "At-sign in URL", "High",
            "An @ symbol can be used to make the apparent destination confusing.")
    if parsed.scheme.lower() == "http":
        add(5, "http", "Unencrypted HTTP", "Low",
            "The URL uses HTTP rather than HTTPS; this is a transport-security concern, not proof of phishing.")

    score = min(score, 100)
    risk = "HIGH" if score >= 50 else "MEDIUM" if score >= 25 else "LOW"

    # Pieces used only for the link breakdown display.
    userinfo, _, hostport = parsed.netloc.rpartition("@")
    port = f":{parsed.port}" if parsed.port else ""
    parts = {
        "scheme": parsed.scheme.lower(),
        "userinfo": userinfo,
        "host": hostport[:-len(port)] if port else hostport,
        "port": port,
        "rest": urlunparse(("", "", parsed.path, parsed.params, parsed.query, parsed.fragment)),
    }
    return {"valid": True, "url": raw, "normalized": candidate, "host": host,
            "scheme": parsed.scheme.upper(), "score": score, "risk": risk,
            "findings": findings, "parts": parts}


def add_to_history(url, result):
    st.session_state.history.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url, "risk": result["risk"], "score": result["score"],
        "findings": "; ".join(f["title"] for f in result["findings"]) or "No configured indicators"
    })
    st.session_state.history = st.session_state.history[:150]


def make_csv(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["timestamp", "url", "risk", "score", "findings"])
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


# -------------------- Display helpers --------------------
def split_host(host):
    """Split a hostname into (subdomains, registrable domain). Approximate, no public-suffix list."""
    labels = host.split(".")
    keep = 3 if len(labels) >= 3 and ".".join(labels[-2:]).lower() in TWO_PART_SUFFIXES else 2
    if len(labels) <= keep:
        return "", host
    return ".".join(labels[:-keep]) + ".", ".".join(labels[-keep:])


def with_keywords(text):
    out, last = [], 0
    for m in KEYWORD_RE.finditer(text):
        out.append(escape(text[last:m.start()]))
        out.append(f'<span class="flag flag-med">{escape(m.group())}</span>')
        last = m.end()
    out.append(escape(text[last:]))
    return "".join(out)


def anatomy_html(r):
    p, hit = r["parts"], {f["key"] for f in r["findings"]}
    out = [f'<span class="{"flag flag-low" if "http" in hit else "dim"}">{escape(p["scheme"])}</span>'
           '<span class="dim">://</span>']
    if p["userinfo"]:
        out.append(f'<span class="flag flag-high">{escape(p["userinfo"])}@</span>')
    sub, dom = ("", p["host"]) if "ip" in hit else split_host(p["host"])
    if sub:
        cls = "sub flag flag-med" if "subdomains" in hit else "sub"
        out.append(f'<span class="{cls}">{with_keywords(sub)}</span>')
    dom_cls = "domain" + (" flag flag-high" if "ip" in hit else " flag flag-med" if "shortener" in hit else "")
    out.append(f'<span class="{dom_cls}">{with_keywords(dom)}</span>')
    tail = p["port"] + p["rest"]
    if tail:
        out.append(f'<span class="dim">{with_keywords(tail)}</span>')
    note = "The domain is brightest. Highlighted parts matched a risk indicator."
    if r["normalized"] != r["url"]:
        note += " Your input was repaired before analysis."
    return (f'<div class="anatomy"><div class="url">{"".join(out)}</div>'
            f'<div class="anatomy-note">{note}</div></div>')


VERDICTS = {
    "HIGH": ("High risk", "Don’t open this link until you’ve verified it independently."),
    "MEDIUM": ("Medium risk", "Some characteristics look suspicious. Check the destination before you continue."),
    "LOW": ("Low risk", "Few indicators matched. That doesn’t mean the link is safe."),
}


def verdict_html(r):
    advice = VERDICTS[r["risk"]][1]
    title = {"HIGH": "HIGH-RISK INDICATORS DETECTED", "MEDIUM": "SUSPICIOUS PATTERNS FOUND", "LOW": "LOW INDICATOR COUNT"}[r["risk"]]
    return (f'<div class="verdict v-{r["risk"].lower()}">'
            f'<div class="v-ring-wrap"><div class="score-ring" style="--score:{r["score"]};"><strong>{r["score"]}</strong></div>'
            '<div class="ring-caption">HEURISTIC SCORE / 100</div></div>'
            f'<div class="v-content"><div class="v-label">{title}</div>'
            f'<div class="v-host"><b style="color:#53e8f4">TARGET:</b> {escape(r["normalized"])}</div>'
            f'<p>{advice}</p><div class="v-score">Risk band: <strong>{r["risk"]}</strong> · Explainable rule-based assessment</div></div></div>')

def findings_html(findings):
    if not findings:
        return '<div class="empty">No indicators matched. That doesn’t prove the link is safe.</div>'
    rows = []
    for f in sorted(findings, key=lambda x: -x["points"]):
        rows.append(
            f'<div class="finding f-{f["severity"].lower()}"><div class="f-top">'
            f'<span class="f-title">{escape(f["title"])}<span class="f-sev">{f["severity"]} severity</span></span>'
            f'<span class="f-pts">+{f["points"]}</span></div>'
            f'<div class="f-detail">{escape(f["detail"])}</div></div>')
    return "".join(rows)


def show_table(df, **kwargs):
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kwargs)
    except Exception:  # older Streamlit versions
        st.dataframe(df, use_container_width=True, hide_index=True, **kwargs)


def show_chart(fig):
    try:
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    except Exception:  # older Streamlit versions
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def risk_donut(counts):
    values = [counts["LOW"], counts["MEDIUM"], counts["HIGH"]]
    fig = go.Figure(data=[go.Pie(
        labels=["Low", "Medium", "High"], values=values, hole=.72, sort=False,
        marker=dict(colors=["#6fcf9f", "#e9b44c", "#f06a5f"], line=dict(color="#10151c", width=3)),
        textinfo="none", hovertemplate="%{label}: %{value}<extra></extra>")])
    fig.update_layout(
        height=240, margin=dict(t=8, b=8, l=8, r=8), showlegend=True,
        legend=dict(orientation="h", y=-.06, x=.5, xanchor="center", font=dict(color="#aab6c6", size=12)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=f"<b>{sum(values)}</b><br><span style='font-size:11px'>scans</span>",
                          x=.5, y=.5, showarrow=False, font=dict(size=24, color="#e8edf4"))])
    return fig


def lexical_telemetry(r):
    value, host = r["normalized"], r["host"]
    from collections import Counter
    import math
    counts = Counter(value)
    entropy = -sum((n / len(value)) * math.log2(n / len(value)) for n in counts.values()) if value else 0.0
    query = r.get("parts", {}).get("rest", "")
    query_count = len([item for item in query.split("?", 1)[-1].split("&") if item]) if "?" in query else 0
    subdomains = max(0, len(host.split(".")) - 2) if not is_ip(host) else "N/A"
    metrics = [("CHARACTER ENTROPY", f"{entropy:.2f}", "Shannon entropy"),
               ("URL LENGTH", str(len(value)), "Characters"),
               ("SUBDOMAINS", str(subdomains), "Approximate label count"),
               ("SPECIAL CHARACTERS", str(sum(not ch.isalnum() for ch in value)), "Non-alphanumeric"),
               ("QUERY PARAMETERS", str(query_count), "Parsed parameters"),
               ("PROTOCOL", r["scheme"], "URL scheme")]
    cards = [f'<div class="telemetry-card"><div class="telemetry-label">{label}</div><div class="telemetry-value">{escape(val)}</div><div class="telemetry-sub">{sub}</div></div>' for label, val, sub in metrics]
    return '<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.55rem">' + ''.join(cards) + '</div>'


# -------------------- State --------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

history = st.session_state.history
counts = {level: sum(row["risk"] == level for row in history) for level in ["LOW", "MEDIUM", "HIGH"]}

SAMPLES = [
    ("Raw IP with @", "http://bank-example.com@185.220.101.4/login"),
    ("Shortened link", "https://bit.ly/3xYzAbC"),
    ("Stacked subdomains", "https://secure-login.account.example.com/verify?token=1&next=payment"),
    ("Clean link", "https://github.com/streamlit/streamlit"),
]


def use_sample(url):
    st.session_state.url_input = url
    st.session_state.run_scan = True


# -------------------- Sidebar --------------------
with st.sidebar:
    render('<div class="brand"><span class="brand-mark">⬡</span> LinkSentry</div><div class="side-note">THREAT INTELLIGENCE WORKSPACE</div>')
    st.write("")
    page = st.radio("WORKSPACE", ["Scan", "History"], label_visibility="visible")
    st.write("")
    render(f"""
    <div class="side-note" style="margin-bottom:.35rem">This session</div>
    <div class="side-row"><span class="dot d-high"></span>High<span class="n">{counts["HIGH"]}</span></div>
    <div class="side-row"><span class="dot d-medium"></span>Medium<span class="n">{counts["MEDIUM"]}</span></div>
    <div class="side-row"><span class="dot d-low"></span>Low<span class="n">{counts["LOW"]}</span></div>
    """)
    st.write("")
    render("""<div class="side-note">● LOCAL ANALYSIS ACTIVE<br>○ REPUTATION FEEDS OFFLINE<br><br>Submitted links are parsed locally and are never opened.</div>""")

render("""<div class="hero"><div class="hero-kicker">LINKSENTRY / SECURITY ANALYTICS PLATFORM</div>
<h1>Advanced <span>Phishing Threat Intelligence</span></h1>
<p>URL STRUCTURE ANALYSIS · LEXICAL TELEMETRY · EXPLAINABLE THREAT SCORING</p></div>""")

# -------------------- Scan --------------------
if page == "Scan":
    render("""
    <div class="section-kicker">THREAT ANALYSIS / URL INSPECTION</div>
    <div class="page-title">Inspect a suspicious URL</div>
    <div class="page-sub">Analyze URL structure and surface configured risk indicators. The submitted link is never visited.</div>
    """)

    with st.form("scan_form"):
        c_input, c_btn = st.columns([5, 1])
        with c_input:
            url = st.text_input("URL to analyze", key="url_input",
                                placeholder="https://example.com/login", label_visibility="collapsed")
        with c_btn:
            submitted = st.form_submit_button("INITIATE SCAN  →")

    if submitted or st.session_state.pop("run_scan", False):
        result = analyze_url(st.session_state.get("url_input", ""))
        if result["valid"]:
            st.session_state.last_result = result
            add_to_history(st.session_state.url_input, result)
            history = st.session_state.history
        else:
            st.error(result["error"])

    render('<div class="muted-s">Try an example</div>')
    for col, (label, sample) in zip(st.columns(len(SAMPLES)), SAMPLES):
        col.button(label, key=f"sample_{label}", on_click=use_sample, args=(sample,))

    r = st.session_state.last_result
    if r and r.get("valid"):
        st.write("")
        render(verdict_html(r))
        st.write("")
        matrix_col, telemetry_col = st.columns([1, 1.3], gap="large")
        with matrix_col:
            render('<div class="panel"><div class="panel-title">🚨 THREAT MATRIX LOG</div>' + findings_html(r["findings"]) + '</div>')
        with telemetry_col:
            render('<div class="panel"><div class="panel-title">▥ LEXICAL TELEMETRY</div>' + lexical_telemetry(r) + '</div>')
        st.write("")
        render('<div class="panel"><div class="panel-title">⌕ URL ANATOMY / LINK BREAKDOWN</div>' + anatomy_html(r) + '</div>')
        st.caption("The score is a transparent heuristic indicator, not a calibrated probability of phishing.")

    st.write("")
    with st.expander("How scoring works"):
        rules = pd.DataFrame([
            ("IP address as host", 25, "High", "Host is a raw IP address"),
            ("At-sign in URL", 20, "High", "URL contains @"),
            ("URL shortener", 20, "Medium", "Host is a known shortener, such as bit.ly or tinyurl.com"),
            ("Suspicious keyword", 15, "Medium", "URL contains: " + ", ".join(KEYWORDS)),
            ("Multiple subdomains", 15, "Medium", "Hostname has more than three labels"),
            ("Long URL", 10, "Low", "More than 75 characters"),
            ("Unencrypted HTTP", 5, "Low", "Scheme is http"),
        ], columns=["Indicator", "Points", "Severity", "Triggers when"])
        show_table(rules)
        st.caption("Scores are capped at 100. 25 to 49 is Medium risk; 50 and above is High risk.")

# -------------------- History --------------------
else:
    render("""
    <div class="section-kicker">SECURITY OPERATIONS / ACTIVITY LOG</div>
    <div class="page-title">Scan history</div>
    <div class="page-sub">Review previous URL inspections from this browser session.</div>
    """)
    if not history:
        st.info("No scans yet. Open Scan and check your first link.")
    else:
        levels = st.multiselect("Show risk levels", ["HIGH", "MEDIUM", "LOW"], default=["HIGH", "MEDIUM", "LOW"])
        table_col, chart_col = st.columns([2.2, 1], gap="large")
        with table_col:
            df = pd.DataFrame(history)
            df = df[df["risk"].isin(levels)]
            df.insert(0, "time", df["timestamp"].str[11:])
            show_table(
                df[["time", "url", "risk", "score", "findings"]],
                column_config={
                    "time": st.column_config.TextColumn("Time", width="small"),
                    "url": st.column_config.TextColumn("URL"),
                    "risk": st.column_config.TextColumn("Risk", width="small"),
                    "score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%d"),
                    "findings": st.column_config.TextColumn("Indicators"),
                })
            b1, b2, _ = st.columns([1.3, 1.1, 1])
            with b1:
                st.download_button("Download CSV", data=make_csv(history),
                                   file_name="linksentry_scan_history.csv", mime="text/csv")
            with b2:
                if st.button("Clear history"):
                    st.session_state.history = []
                    st.session_state.last_result = None
                    st.rerun()
        with chart_col:
            render('<div class="box-title">Risk mix</div>')
            show_chart(risk_donut(counts))

st.write("")
st.caption("Educational prototype using static heuristics. It does not follow redirects, inspect page content, "
           "or query reputation feeds. Telemetry is descriptive; a low score is not proof that a link is safe.")