import streamlit as st
import pandas as pd
import urllib.parse
import base64
from io import BytesIO

# 1. Configuração da Página
st.set_page_config(page_title="Reicon Comercial", page_icon="🚢", layout="wide")

REICON_BLUE = "#233d4d"
REICON_ORANGE = "#fe7f2d"

# Função para converter imagem local para base64 (Header)
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- CSS MOBILE & MATERIAL DESIGN ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #f8fafc; }}
    
    /* HEADER ESTILIZADO */
    .header-container {{
        display: flex; flex-direction: column; align-items: center;
        padding: 10px 0; border-bottom: 3px solid {REICON_ORANGE};
        margin-bottom: 25px; background-color: white;
    }}
    .logo-img {{ width: 120px; height: auto; margin-bottom: 5px; }}
    .header-right {{ text-align: center; }}
    .header-title {{ color: {REICON_BLUE}; font-size: 18px; font-weight: 800; margin: 0; }}
    .header-subtitle {{ color: {REICON_BLUE}; font-size: 11px; font-weight: 400; margin: 0; opacity: 0.7; }}

    /* FIX DO TECLADO NO CELULAR (BLOQUEIO DE INPUT EM SELECTBOX) */
    div[data-baseweb="select"] input {{
        readonly: readonly;
        pointer-events: none !important;
    }}
    
    /* CARDS E COLUNAS */
    div[data-testid="column"] {{
        background-color: #FFFFFF; padding: 15px; border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #eef2f6;
        margin-bottom: 15px;
    }}
    
    /* ESPAÇAMENTO ENTRE VALOR FINAL E DETALHES */
    .footer-container {{
        background-color: {REICON_BLUE}; color: white; padding: 20px; border-radius: 12px;
        display: flex; justify-content: space-between; align-items: center; 
        margin-top: 25px; margin-bottom: 30px; /* Espaço aumentado aqui */
        border-bottom: 6px solid {REICON_ORANGE};
    }}
    
    .total-value {{ font-size: 32px; font-weight: 800; color: {REICON_ORANGE}; margin: 0; }}
    .icon-link {{ text-decoration: none; color: white; font-size: 28px; transition: 0.3s; }}
    
    /* LABELS */
    label {{ font-size: 0.8rem !important; font-weight: 700 !important; color: {REICON_BLUE} !important; text-transform: uppercase; }}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER COM LOGO ---
try:
    logo_base64 = get_base64_image("Reicon_full.png")
    st.markdown(f"""
        <div class="header-container">
            <img src="data:image/png;base64,{logo_base64}" class="logo-img">
            <div class="header-right">
                <p class="header-title">Calculadora de Fretes por Praça</p>
                <p class="header-subtitle">Gestão Comercial Estratégica</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
except:
    st.warning("Logo 'image_aefad8.png' não encontrada. Usando header em texto.")

# 2. Login
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with st.columns([1,2,1])[1]:
        senha = st.text_input("Acesso Comercial Reicon", type="password")
        if st.button("Entrar"):
            if senha == "reicon2026": st.session_state.auth = True; st.rerun()
            else: st.error("Senha inválida")
    st.stop()

# 3. Dados
NOME_ARQUIVO = "APP - Calcular Fretes Por Praças 2026 - Copia.xlsx"

@st.cache_data
def carregar_dados():
    try:
        df_raw = pd.read_excel(NOME_ARQUIVO, sheet_name="BASE_FRETE")
        skip = next(i for i, row in df_raw.iterrows() if "ITEM" in row.values) + 1
        return pd.read_excel(NOME_ARQUIVO, sheet_name="BASE_FRETE", skiprows=skip)
    except: return None

df_frete = carregar_dados()

# 4. Layout
c1, c2, c3 = st.columns([1,1,1])

with c1:
    st.markdown("#### 📋 Parametros")
    mapa_rota = {"Bel-Mcp-Bel": "BLM - MCP", "Bel-Alt-Bel": "BLM - ALT", "Bel-Ita-Bel": "BLM - ITB", "Bel-Sat-Bel": "BLM - STM"}
    rota_ui = st.selectbox("Rota de Operação", list(mapa_rota.keys()))
    col_tecnica = mapa_rota[rota_ui]
    
    # O hack de CSS acima impede o teclado nesta lista
    tipo_carga = st.selectbox("Tipo de Carga", df_frete['ITEM'].dropna().unique())
    modalidade = st.selectbox("Modalidade", ["IDA", "VOLTA", "IDA E VOLTA"])
    descontos = {"0% sem desconto": 0, "5%": 0.05, "7%": 0.07, "10%": 0.1, "15%": 0.15, "20%": 0.2}
    perc_desc = descontos[st.selectbox("Desconto Aplicado", list(descontos.keys()))]

# Cálculos
is_mcp = "Mcp" in rota_ui
icms_taxa = 0.12 if is_mcp else 0.19
divisor_adv = 0.88 if is_mcp else 0.81
valor_bruto = float(df_frete.loc[df_frete['ITEM'] == tipo_carga, col_tecnica].values[0])
v_com_desconto = valor_bruto * (1 - perc_desc)

with c2:
    st.markdown("#### ⚖️ Dados Carga")
    v_carga_user = st.number_input("Valor Mercadoria (R$)", min_value=0.0, format="%.2f")
    calc_adv = (v_carga_user * 0.002) / divisor_adv
    if modalidade == "IDA E VOLTA": calc_adv *= 2
    st.text_input("Ad Valorem", value=f"R$ {calc_adv:,.2f}", disabled=True)
    st.text_input("Frete Líquido", value=f"R$ {v_com_desconto:,.2f}", disabled=True)

with c3:
    st.markdown("#### 🛠️ Extras")
    total_extras = 0.0
    with st.expander("Expandir Serviços"):
        servicos = ["ESTIVA REMETENTE", "PESAGEM", "ESTIVA DESTINATÁRIO", "OVAÇÃO", "COLETA", "ENTREGA", "EXPURGO", "ENLONAMENTO", "TRANSBORDO", "OUTROS"]
        for serv in servicos:
            val = st.number_input(serv, min_value=0.0, value=0.0, key=f"srv_{serv}")
            total_extras += val

# 5. Resultado Final
valor_final = v_com_desconto + calc_adv + total_extras

msg_wa = (
    "Olá, segue a cotação solicitada!\n\n"
    "Cotação de Frete\n"
    f"📍 Rota: {rota_ui}\n"
    f"📦 Carga: {tipo_carga}\n"
    f"💵 Valor: R$ {valor_final:,.2f}\n\n"
    "Estamos à disposição e aguardamos sua resposta!"
)
link_wa = f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"

st.markdown(f"""
    <div class="footer-container">
        <div>
            <p style="margin:0; font-size:14px; opacity:0.8;">VALOR TOTAL DO FRETE FINAL</p>
            <p class="total-value">R$ {valor_final:,.2f}</p>
        </div>
        <div>
            <a href="{link_wa}" target="_blank" class="icon-link">📩</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 6. Raciocínio (Com margem superior garantida pelo CSS)
with st.expander("📄 Ver Detalhamento do Cálculo"):
    st.markdown(f"""
    - **Frete:** R$ {v_com_desconto:,.2f}
    - **Ad Valorem:** R$ {calc_adv:,.2f}
    - **Extras:** R$ {total_extras:,.2f}
    ---
    **TOTAL: R$ {valor_final:,.2f}**
    """)


