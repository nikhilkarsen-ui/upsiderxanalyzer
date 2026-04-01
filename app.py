import streamlit as st
from openai import OpenAI
import PyPDF2

# --- CONFIG ---
st.set_page_config(page_title="RX Analyzer", page_icon="📉", layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- SIDEBAR ---
st.sidebar.image("AnalyzeLogo.png", width=120)
st.sidebar.title("RX Analyzer")

page = st.sidebar.radio("Navigate", [
    "Analyzer",
    "About"
])

# --- STYLING ---
st.markdown("""
<style>
body {
    background-color: #0a0a0a;
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
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text


def analyze_text(text):
    prompt = f"""
    You are a restructuring investment banker.

    Analyze the company information below and return:

    - Key issues
    - Liquidity concerns
    - Signs of distress
    - Likely restructuring path
    - Fulcrum security
    - 3 sharp interview talking points

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
        if content == "":
            st.warning("Add input first.")
        else:
            with st.spinner("Analyzing..."):
                result = analyze_text(content[:15000])

            st.markdown("---")
            st.markdown("## 📊 Analysis Output")
            st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)

# =========================
# PAGE: ABOUT
# =========================
elif page == "About":

    st.image("AnalyzeLogo.png", width=100)

    st.markdown("""
    # About RX Analyzer

    RX Analyzer is an AI-powered tool designed to simulate how restructuring professionals think.

    ### What it does:
    - Breaks down distressed companies
    - Identifies liquidity risks
    - Suggests restructuring paths
    - Helps you prep for interviews

    ### Built by:
    Nikhil Senthil  
    Finance + Business Analytics @ Indiana University

    ### Vision:
    Build the go-to platform for restructuring interview prep.
    """)