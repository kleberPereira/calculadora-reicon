import streamlit as st
import pandas as pd
import urllib.parse
import base64
import os

# 1. Configuração da Página
st.set_page_config(page_title="Reicon Comercial", page_icon="🚢", layout="wide")

REICON_BLUE = "#233d4d"
REICON_ORANGE = "#fe7f2d"

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

# --- CSS LIMPO (Sem comentários para evitar erros de texto na tela) ---
estilo_ui = f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet">
<style>
    .stApp {{ background-color: #fcfcfd; font-family: 'Inter', sans-serif; }}
    
    .header-container {{
        background-color: white; padding: 20px; border-radius: 0 0 24px 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 30px;
        text-align: center; border-bottom: 3px solid {REICON_ORANGE};
    }}
    .logo-img {{ width: 140px; height: auto; margin-bottom: 8px; }}
    .header-title {{ color: {REICON_BLUE}; font-size: 22px; font-weight: 800; margin: 0; letter-spacing: -0.5px; }}
    
    div[data-testid="column"] {{
        background-color: white; padding: 24px; border-radius: 20px;
        border: 1px solid #f1f5f9; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.3s ease;
    }}
    
    label {{ font-size: 0.85rem !important; font-weight: 600 !important; color: {REICON_BLUE} !important; margin-bottom: 8px !important; }}
    
    .footer-container {{
        background-color: {REICON_BLUE}; color: white; padding: 28px; border-radius: 24px;
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 40px; margin-bottom: 20px; border-right: 8px solid {REICON_ORANGE};
    }}
    .total-value {{ font-size: 36px; font-weight: 800; color: {REICON_ORANGE}; margin: 0; }}
    
    .wa-btn {{
        background-color: {REICON_ORANGE}; color: white !important; padding: 12px 24px;
        border-radius: 14px; text-decoration: none; display: flex;
        align-items: center; gap: 8px; font-weight: 600; transition: 0.2s;
    }}

    div[data-baseweb="select"] input {{ pointer-events: none !important; }}
</style>
"""
st.markdown(estilo_ui, unsafe_allow_html=True)

# --- HEADER ---
logo_base64 = get_base64_image("Reicon_full.png")
st.markdown(f"""
    <div class="header-container">
        {f'<img src="data:image/png;base64,{logo_base64}" class="logo-img">' if logo_base64 else '🚢'}
        <p class="header-title">Calculadora de Fretes por Praça</p>
    </div>
""", unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with st.container():
        _, center, _ = st.columns([1, 2, 1])
        with center:
            st.markdown("### 🔐 Acesso Restrito")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            if st.button("Entrar", use_container_width=True):
                if senha == "reicon2026": 
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Senha inválida")
    st.stop()

# --- CARREGAMENTO DE DADOS ---
NOME_ARQUIVO = "APP - Calcular Fretes Por Praças 2026 - Copia.xlsx"

@st.cache_data
def carregar_dados():
    try:
        df_raw = pd.read_excel(NOME_ARQUIVO, sheet_name="BASE_FRETE")
        skip = next(i for i, row in df_raw.iterrows() if "ITEM" in row.values) + 1
        return pd.read_excel(NOME_ARQUIVO, sheet_name="BASE_FRETE", skiprows=skip)
    except: return None

df_frete = carregar_dados()

if df_frete is not None:
    c1, c2, c3 = st.columns([1,1,1])

    with c1:
        st.markdown("##### 📋 Parametros")
        mapa_rota = {"Bel-Mcp-Bel": "BLM - MCP", "Bel-Alt-Bel": "BLM - ALT", "Bel-Ita-Bel": "BLM - ITB", "Bel-Sat-Bel": "BLM - STM"}
        rota_ui = st.selectbox("Rota", list(mapa_rota.keys()))
        col_tecnica = mapa_rota[rota_ui]
        tipo_carga = st.selectbox("Tipo de Carga", df_frete['ITEM'].dropna().unique())
        modalidade = st.selectbox("Modalidade", ["IDA", "VOLTA", "IDA E VOLTA"])
        descontos = {"0% sem desconto": 0, "5%": 0.05, "7%": 0.07, "10%": 0.1, "15%": 0.15, "20%": 0.2}
        perc_desc = descontos[st.selectbox("Desconto", list(descontos.keys()))]

    # Cálculos
    is_mcp = "Mcp" in rota_ui
    divisor_adv = 0.88 if is_mcp else 0.81
    valor_bruto = float(df_frete.loc[df_frete['ITEM'] == tipo_carga, col_tecnica].values[0])
    v_com_desconto = valor_bruto * (1 - perc_desc)

    with c2:
        st.markdown("##### ⚖️ Carga")
        v_carga_user = st.number_input("Valor Mercadoria (R$)", min_value=0.0, format="%.2f")
        calc_adv = (v_carga_user * 0.002) / divisor_adv
        if modalidade == "IDA E VOLTA": calc_adv *= 2
        st.text_input("Ad Valorem", value=f"R$ {calc_adv:,.2f}", disabled=True)
        st.text_input("Frete Líquido", value=f"R$ {v_com_desconto:,.2f}", disabled=True)

    with c3:
        st.markdown("##### 🛠️ Extras")
        total_extras = 0.0
        with st.expander("Expandir Serviços"):
            servicos = ["ESTIVA REMETENTE", "PESAGEM", "ESTIVA DESTINATÁRIO", "OVAÇÃO", "COLETA", "ENTREGA", "EXPURGO", "ENLONAMENTO", "TRANSBORDO", "OUTROS"]
            for serv in servicos:
                val = st.number_input(serv, min_value=0.0, value=0.0, key=f"srv_{serv}")
                total_extras += val

    # Resultado Final
    valor_final = v_com_desconto + calc_adv + total_extras
    msg_wa = f"Olá, segue a cotação solicitada!\n📍 Rota: {rota_ui}\n📦 Carga: {tipo_carga}\n💵 Valor: R$ {valor_final:,.2f}"
    link_wa = f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"

    st.markdown(f"""
        <div class="footer-container">
            <div>
                <p style="margin:0; font-size:14px; opacity:0.8;">VALOR TOTAL DO FRETE FINAL</p>
                <p class="total-value">R$ {valor_final:,.2f}</p>
            </div>
            <div>
                <a href="{link_wa}" target="_blank" class="wa-btn">
                    <span class="material-symbols-outlined">send</span> Enviar
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("📄 Memória de Cálculo"):
        st.write(f"Frete: R$ {v_com_desconto:,.2f} | AdVal: R$ {calc_adv:,.2f} | Extras: R$ {total_extras:,.2f}")
