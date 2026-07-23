import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="Arena de Vendas - Lojas",
    page_icon="🏆",
    layout="wide",
)

# Remove paddings padrão do Streamlit para o HTML ocupar a tela toda
st.markdown(
    """
    <style>
        .block-container {padding: 0; max-width: 100%;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

html_path = Path(__file__).parent / "arena.html"
html_content = html_path.read_text(encoding="utf-8")

components.html(html_content, height=2200, scrolling=True)
