import streamlit as st
import os
from openai import OpenAI

# --- SET YOUR API KEY ---
client = OpenAI( api_key=os.getenv("Open_API_Key") )

# --- ANALYSIS FUNCTION ---
def analyze_text(text):
    prompt = f"""
    You are a top-tier restructuring investment banker.

    Analyze the following company information and provide:

    1. Key business issues
    2. Liquidity concerns
    3. Signs of distress
    4. Likely restructuring path (out-of-court vs Chapter 11)
    5. Where the fulcrum security likely sits
    6. 3 interview-style talking points

    Be concise but insightful.

    Text:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content

# --- UI ---
st.set_page_config(page_title="RX Analyzer", layout="centered")

st.title("📉 Distressed Company Analyzer")
st.write("Paste company news, earnings transcript, or filings to get restructuring insights.")

user_input = st.text_area("Paste company info here:", height=250)

if st.button("Analyze"):
    if user_input.strip() == "":
        st.warning("Please paste some text first.")
    else:
        with st.spinner("Analyzing..."):
            result = analyze_text(user_input)

        st.subheader("📊 Analysis Output")
        st.write(result)