import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import json

st.set_page_config(
    page_title="Arena de Vendas - Lojas",
    page_icon="🏆",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {padding: 1rem 1rem 0 1rem; max-width: 100%;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- CONFIG ----------
DATA_FILE = Path(__file__).parent / "dados_placar.json"
SENHA_ADMIN = "prodentis2026"  # troque essa senha se quiser (e o link que você usa)

STORES = [
    {"id": "pmw", "nome": "🏬 PALMAS · PMW"},
    {"id": "slz", "nome": "🏬 SÃO LUÍS · SLZ"},
    {"id": "itz", "nome": "🏬 IMPERATRIZ · ITZ"},
]

DEFAULTS = {
    "dias": 0,
    "pmw": {"ml": 465000, "mf": 0, "vl": 0, "vf": 0},
    "slz": {"ml": 450000, "mf": 0, "vl": 0, "vf": 0},
    "itz": {"ml": 568000, "mf": 0, "vl": 0, "vf": 0},
}


def carregar_dados():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULTS))


def salvar_dados(d):
    DATA_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def fmt_valor(v):
    # formata sem separador de milhar e com vírgula decimal
    # (é o formato que o parser do arena.html espera)
    return f"{float(v):.2f}".replace(".", ",")


dados = carregar_dados()
is_admin = st.query_params.get("chave") == SENHA_ADMIN

# ---------- PAINEL ADMIN ----------
if is_admin:
    st.title("🔐 Painel Admin — Arena de Vendas")
    st.caption("Só quem tem o link com a chave vê esta parte. Os vendedores acessam a URL normal e veem só o resultado abaixo.")

    with st.form("form_placar"):
        dias = st.number_input(
            "Dias úteis passados no mês", min_value=0, max_value=31, value=int(dados.get("dias", 0))
        )
        cols = st.columns(3)
        novos = {"dias": dias}
        for col, store in zip(cols, STORES):
            with col:
                st.subheader(store["nome"])
                sid = store["id"]
                atual = dados.get(sid, DEFAULTS[sid])
                ml = st.number_input("Meta Loja (R$)", min_value=0.0, value=float(atual.get("ml", 0)), key=f"ml_{sid}")
                mf = st.number_input("Meta Fábrica (R$)", min_value=0.0, value=float(atual.get("mf", 0)), key=f"mf_{sid}")
                vl = st.number_input("Atingido Loja (R$)", min_value=0.0, value=float(atual.get("vl", 0)), key=f"vl_{sid}")
                vf = st.number_input("Atingido Fábrica (R$)", min_value=0.0, value=float(atual.get("vf", 0)), key=f"vf_{sid}")
                novos[sid] = {"ml": ml, "mf": mf, "vl": vl, "vf": vf}

        enviado = st.form_submit_button("💾 Salvar e Publicar")
        if enviado:
            salvar_dados(novos)
            dados = novos
            st.success("Placar atualizado! Já está valendo para todo mundo.")

    st.divider()
    st.caption("Pré-visualização — é isso que os vendedores veem:")

# ---------- MONTA O HTML (mesmo pros dois casos) ----------
html_path = Path(__file__).parent / "arena.html"
html_content = html_path.read_text(encoding="utf-8")

init_lines = ["(function(){"]
init_lines.append(f'  document.getElementById("dias").value = {int(dados.get("dias", 0))};')
for store in STORES:
    sid = store["id"]
    valores = dados.get(sid, DEFAULTS[sid])
    for campo in ["ml", "mf", "vl", "vf"]:
        valor_str = fmt_valor(valores.get(campo, 0))
        init_lines.append(f'  document.getElementById("{campo}_{sid}").value = {json.dumps(valor_str)};')
init_lines.append('  if(typeof atualizar==="function") atualizar();')
init_lines.append("})();")
init_script = "\n".join(init_lines)

# esconde sempre o painel de edição de dentro do HTML (a edição agora é só pelo formulário acima, no modo admin)
html_final = html_content.replace(
    "</body>",
    f"<style>.input-section{{display:none!important;}}</style><script>{init_script}</script></body>",
)

components.html(html_final, height=1500, scrolling=True)
