import streamlit as st
st.image("AnalyzeLogo.png", width=150)
st.markdown(
    """
    <div style="text-align: center;">
        <img src="logo.png" width="120">
        <h1>The Upside RX Analyzer</h1>
        <p>AI-powered restructuring insights</p>
    </div>
    """,
    unsafe_allow_html=True
)
st.set_page_config(
    page_title="RX Analyzer",
    page_icon="logo.png"
)
st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)
from openai import OpenAI
import PyPDF2
import os

# --- CONFIG ---
st.set_page_config(
    page_title="RX Analyzer",
    page_icon="📉",
    layout="wide"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
# --- STYLING (dark + red theme) ---
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0a0a0a;
    color: #e6e6e6;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

h1, h2, h3 {
    color: white;
}

.stTextArea textarea {
    background-color: #141414;
    color: white;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 10px;
}

.stButton button {
    background-color: #e50914;
    color: white;
    border-radius: 8px;
    height: 45px;
    width: 100%;
    border: none;
    font-weight: 600;
}

.stButton button:hover {
    background-color: #ff1a1a;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

hr {
    border: 0.5px solid #222;
}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("# Distressed Company Analyzer")
st.markdown("Analyze filings, news, or transcripts for restructuring signals.")

st.markdown("<hr>", unsafe_allow_html=True)

# --- FUNCTIONS ---
def extract_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
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
    - Fulcrum security (if applicable)
    - 3 sharp interview talking points

    Keep it tight and analytical.

    Text:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


# --- LAYOUT ---
left, right = st.columns([2, 1])

with left:
    st.subheader("Input")

    uploaded = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
    text_input = st.text_area("Or paste text", height=200)

with right:
    st.subheader("Run Analysis")
    run = st.button("Analyze")

# --- INPUT HANDLING ---
content = ""

if uploaded:
    if uploaded.type == "application/pdf":
        content = extract_pdf(uploaded)
    else:
        content = uploaded.read().decode("utf-8")

elif text_input.strip():
    content = text_input

# --- OUTPUT ---
if run:
    if content == "":
        st.warning("Add a file or paste text first.")
    else:
        with st.spinner("Processing..."):
            result = analyze_text(content[:15000])

        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Analysis")

        st.markdown(result)