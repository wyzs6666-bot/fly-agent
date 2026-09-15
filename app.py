import subprocess
import streamlit as st

st.title("Fly Agent")
text = st.text_input("输入一句话")
brain = st.selectbox("brain", ["mock", "auto", "real"])

if st.button("运行") and text.strip():
    result = subprocess.run(
        ["fly-agent", "--brain", brain, text],
        capture_output=True,
        text=True
    )
    st.code(result.stdout or result.stderr)