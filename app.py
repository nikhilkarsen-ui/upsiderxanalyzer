import streamlit as st
from openai import OpenAI
import pdfplumber
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import yfinance as yf

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Upside RX Platform", layout="wide")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# =========================
# STYLING
# =========================
st.markdown("""
<style>
body {background:#0b0f14;color:#e6e6e6;}
.block-container {padding:2rem 3rem;}
.card {background:#121821;border:1px solid #1f2a37;padding:15px;border-radius:10px;}
.stButton button {background:#e50914;color:white;border-radius:6px;}
</style>
""", unsafe_allow_html=True)

# =========================
# DATA FUNCTIONS
# =========================

def get_market_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        financials = stock.financials

        return {
            "price": info.get("currentPrice", 0),
            "market_cap": info.get("marketCap", 0),
            "revenue": financials.loc["Total Revenue"].iloc[0] if "Total Revenue" in financials.index else 0,
            "net_income": financials.loc["Net Income"].iloc[0] if "Net Income" in financials.index else 0
        }
    except:
        return None

def get_sec_filing(ticker):
    try:
        url = f"https://data.sec.gov/submissions/CIK{yf.Ticker(ticker).info['cik_str']:010}.json"
        headers = {"User-Agent": "NikhilSenthil (nikhil@email.com)"}
        data = requests.get(url, headers=headers).json()

        filings = data["filings"]["recent"]
        form = filings["form"][0]
        accession = filings["accessionNumber"][0].replace("-", "")
        cik = str(data["cik"]).zfill(10)

        filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{accession}-index.html"
        return filing_url
    except:
        return None

def scrape_sec_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")
        return " ".join([p.get_text() for p in soup.find_all("p")])[:15000]
    except:
        return ""

# =========================
# SCORING
# =========================

def compute_scores(text, data):
    t = text.lower()

    ai = 50
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":f"Score distress 0-100:\n{text[:3000]}"}]
        )
        ai = int(''.join(filter(str.isdigit, r.choices[0].message.content)))
    except:
        pass

    signals = sum(v for k,v in {
        "bankruptcy":40,"default":30,"restructuring":25,"debt":10
    }.items() if k in t)

    structural = 0
    if "decline" in t: structural += 20
    if "loss" in t: structural += 20

    financial = 0
    if data:
        if data["net_income"] < 0: financial += 20

    total = int(0.4*ai + 0.2*signals + 0.2*structural + 0.2*financial)

    return ai, signals, structural, financial, total

# =========================
# MODELING
# =========================

def estimate_ev(data):
    if not data:
        return 500
    ev = data["market_cap"]
    if data["net_income"] < 0:
        ev *= 0.7
    return int(ev/1_000_000)

def cap_structure():
    return {"Secured":400,"Unsecured":300,"Sub":200}

def waterfall(ev, struct):
    remain=ev
    rec={}
    for k,v in struct.items():
        if remain>=v:
            rec[k]=100
            remain-=v
        elif remain>0:
            rec[k]=int(remain/v*100)
            remain=0
        else:
            rec[k]=0
    return rec

def scenarios(ev):
    return {"Bear":int(ev*0.6),"Base":ev,"Bull":int(ev*1.4)}

# =========================
# UI HEADER
# =========================
st.title("Upside RX Platform")
st.caption("Distressed Investing System")

# =========================
# INPUT
# =========================
ticker = st.text_input("Ticker (e.g. WBA)")
file = st.file_uploader("Upload PDF")
text = st.text_area("Paste text")

run = st.button("Run Analysis")

# =========================
# PROCESS
# =========================
content = ""

data = get_market_data(ticker) if ticker else None

if ticker:
    filing_url = get_sec_filing(ticker)
    if filing_url:
        content = scrape_sec_text(filing_url)

elif file:
    content = pdfplumber.open(file).pages[0].extract_text()

elif text:
    content = text

# =========================
# OUTPUT
# =========================
if run and content:

    ai,sig,struct,fin,score = compute_scores(content, data)

    st.subheader("Risk Dashboard")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("AI", ai)
    c2.metric("Signals", sig)
    c3.metric("Structure", struct)
    c4.metric("Financial", fin)
    c5.metric("Composite", score)

    st.progress(score/100)

    if data:
        st.subheader("Market Data")
        c1,c2,c3 = st.columns(3)
        c1.metric("Price", f"${data['price']}")
        c2.metric("Market Cap", f"${data['market_cap']:,}")
        c3.metric("Revenue", f"${data['revenue']:,}")

        hist = yf.Ticker(ticker).history(period="6mo")
        st.line_chart(hist["Close"])

    ev = estimate_ev(data)
    struct = cap_structure()
    rec = waterfall(ev, struct)

    st.subheader("Recovery Waterfall")
    df = pd.DataFrame({"Layer":rec.keys(),"Recovery":rec.values()})
    st.dataframe(df)
    st.bar_chart(df.set_index("Layer"))

    layer = st.selectbox("Security", list(struct.keys()))
    price = st.slider("Entry Price",10,100,60)

    scen = scenarios(ev)
    returns = {k:rec[layer]-price for k in scen}

    st.subheader("Trade Analysis")
    st.write(returns)

    expected = int(0.3*returns["Bear"]+0.5*returns["Base"]+0.2*returns["Bull"])
    st.metric("Expected Return", expected)

    if "portfolio" not in st.session_state:
        st.session_state.portfolio = []

    if st.button("Add Trade"):
        st.session_state.portfolio.append({
            "time":datetime.datetime.now(),
            "return":expected
        })

    if st.session_state.portfolio:
        st.subheader("Portfolio")
        pf = pd.DataFrame(st.session_state.portfolio)
        st.line_chart(pf.set_index("time"))
        st.metric("Avg Return", int(pf["return"].mean()))