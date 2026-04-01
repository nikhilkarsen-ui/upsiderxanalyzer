import streamlit as st
from openai import OpenAI
import pdfplumber

# --- CONFIG (MUST BE FIRST) ---
st.set_page_config(page_title="RX Analyzer", page_icon="📉", layout="wide")

# --- LOAD API KEY ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- SIDEBAR ---
st.sidebar.image("AnalyzeLogo.png", width=120)
st.sidebar.title("RX Analyzer")

page = st.sidebar.radio("Navigate", ["Analyzer", "About"])

# --- STYLING ---
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0a0a0a;
    color: #e6e6e6;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

.card {
    background-color: #141414;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #222;
}

.stButton button {
    background-color: #e50914;
    color: white;
    border-radius: 10px;
    height: 45px;
    width: 100%;
    border: none;
    font-weight: 600;
}

.stButton button:hover {
    background-color: #ff1a1a;
}
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---

def extract_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text.strip()


def compute_distress_score(text):
    text = text.lower()
    score = 0

    if "liquidity" in text: score += 15
    if "going concern" in text: score += 25
    if "restructuring" in text: score += 20
    if "bankruptcy" in text: score += 30
    if "default" in text: score += 25
    if "debt" in text: score += 10
    if "covenant" in text: score += 15
    if "decline" in text or "down" in text: score += 10

    return min(score, 100)


def extract_signals(text):
    signals = []
    t = text.lower()

    if "liquidity" in t:
        signals.append("Liquidity pressure")
    if "debt" in t:
        signals.append("Highly leveraged")
    if "restructuring" in t:
        signals.append("Active restructuring")
    if "covenant" in t:
        signals.append("Covenant stress")
    if "bankruptcy" in t:
        signals.append("Bankruptcy risk")

    return signals


def analyze_text(text, mode):
    if mode == "Creditor Advisory":
        extra = "Focus heavily on creditor recoveries and downside protection."
    elif mode == "Investment View":
        extra = "Focus on where distressed investors can generate returns."
    else:
        extra = ""

    prompt = f"""
    You are a top-tier restructuring investment banker.

    {extra}

    Analyze the company and return STRICTLY in this format:

    ## Situation Overview
    (2-3 sentences)

    ## Distress Drivers
    - bullet points

    ## Liquidity Analysis
    - runway
    - near-term risks

    ## Capital Structure
    - where stress sits
    - likely fulcrum security

    ## Recommended Action
    - what creditors should do
    - what equity holders should expect

    ## Restructuring Path
    - Out-of-court vs Chapter 11
    - why

    ## Investment Insight
    - where the opportunity is

    ## Interview Talking Points
    - 3 sharp bullets

    Be decisive. No fluff.

    Text:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


# =========================
# PAGE: ANALYZER
# =========================
if page == "Analyzer":

    st.image("AnalyzeLogo.png", width=80)

    st.markdown("""
    # The Upside RX Analyzer
    ### AI-powered restructuring insights
    """)

    st.markdown("---")

    mode = st.selectbox("Analysis Mode", [
        "Standard Analysis",
        "Creditor Advisory",
        "Investment View"
    ])

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📥 Input")

        uploaded = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
        text_input = st.text_area("Or paste text", height=200)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("⚡ Run Analysis")
        run = st.button("Analyze")
        st.markdown('</div>', unsafe_allow_html=True)

    content = ""

    if uploaded:
        if uploaded.type == "application/pdf":
            content = extract_pdf(uploaded)
        else:
            content = uploaded.read().decode("utf-8")

    elif text_input.strip():
        content = text_input

    if run:
        if not content.strip():
            st.warning("Add input first.")
        else:
            score = compute_distress_score(content)
            signals = extract_signals(content)

            colA, colB = st.columns(2)

            with colA:
                st.metric("Distress Score", f"{score}/100")

            with colB:
                st.metric("Risk Level", "High" if score > 60 else "Moderate")

            if signals:
                st.markdown("### 🚨 Key Signals")
                for s in signals:
                    st.write(f"- {s}")

            with st.spinner("Analyzing..."):
                result = analyze_text(content[:15000], mode)

            st.markdown("---")
            st.markdown("## 📊 Analysis Output")
            st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)

            st.caption("Generated using custom restructuring analysis framework")

# =========================
# PAGE: ABOUT
# =========================
elif page == "About":

    st.image("AnalyzeLogo.png", width=100)

    st.markdown("""
    # About RX Analyzer

    RX Analyzer is an AI-powered platform designed to simulate how restructuring professionals think.

    ### What it does:
    - Identifies distress signals
    - Analyzes liquidity risks
    - Suggests restructuring paths
    - Provides interview-ready insights

    ### Built by:
    Nikhil Senthil  
    Finance + Business Analytics @ Indiana University

    ### Vision:
    Build the go-to platform for restructuring recruiting.
    """)