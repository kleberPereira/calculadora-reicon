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
    except:
        return None

# --- CSS LIMPO E CENTRALIZADO ---
style_css = f"""
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
    .stApp {{ background-color: #ffffff; font-family: 'Manrope', sans-serif; }}
    header {{visibility: hidden;}}
    
    /* Centralização Total da Tela de Login */
    .login-wrapper {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        max-width: 350px;
        margin: 0 auto;
        padding-top: 50px;
        text-align: center;
    }}
    
    .logo-discreta {{ width: 100px; height: auto; margin-bottom: 15px; }}
    .title-reicon {{ font-size: 26px; font-weight: 800; color: {REICON_BLUE}; margin: 0; }}
    .subtitle-reicon {{ font-size: 14px; color: #94a3b8; font-weight: 500; margin-bottom: 40px; }}

    /* Alinhamento dos inputs e botões */
    div[data-testid="stTextInput"], div.stButton {{
        width: 100% !important;
        margin: 0 auto !important;
    }}

    /* Estilo Único do Campo de Senha */
    div[data-testid="stTextInput"] label {{ display: none; }}
    div[data-testid="stTextInput"] input {{
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0 16px !important;
        font-size: 16px !important;
        color: {REICON_BLUE} !important;
        height: 55px !important; /* Altura fixa */
        width: 100% !important;
    }}
    div[data-testid="stTextInput"] input:focus {{ border-color: {REICON_ORANGE} !important; box-shadow: none !important; }}

    /* Botão Entrar Idêntico ao Input */
    div.stButton > button {{
        width: 100% !important;
        background-color: {REICON_ORANGE} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        height: 55px !important; /* Mesma altura do input */
        font-size: 16px !important;
        font-weight: 700 !important;
        margin-top: 15px !important;
        transition: 0.2s ease;
    }}
    
    .forgot-pass {{ margin-top: 20px; font-size: 13px; color: #64748b; text-decoration: none; font-weight: 500; display: block; }}
    .login-footer {{ margin-top: 50px; font-size: 10px; color: #cbd5e1; line-height: 1.6; text-align: center; }}
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)

# 2. Lógica de Autenticação
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    logo_base64 = get_base64_image("Reicon_full.png")
    
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    if logo_base64:
        st.markdown(f'<img src="data:image/png;base64,{logo_base64}" class="logo-discreta">', unsafe_allow_html=True)
    
    st.markdown(f'<div class="title-reicon">Grupo Reicon</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle-reicon">Calculadora de Frete</div>', unsafe_allow_html=True)
    
    # Input de senha limpo
    senha = st.text_input("", type="password", placeholder="Digite sua senha")
    
    if st.button("Entrar"):
        if senha == "reicon2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta")
            
    st.markdown(f'<a href="https://wa.me/5591982257816" target="_blank" class="forgot-pass">Esqueci minha senha</a>', unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="login-footer">
            © 2026 Grupo Reicon Logística. Todos os direitos reservados.<br>
            Sistema de uso exclusivo para colaboradores.<br>
            Criado por Kleber Pereira.
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. DASHBOARD (MANTIDO DO BACKUP) ---
# Se a senha estiver correta, o código abaixo carrega normalmente
st.markdown(f"""
    <div style="text-align:center; padding: 20px; border-bottom: 2px solid {REICON_ORANGE}; margin-bottom: 25px;">
        <p style="color:{REICON_BLUE}; font-size:20px; font-weight:800; margin:0;">Calculadora de Fretes Reicon</p>
    </div>
""", unsafe_allow_html=True)

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
        st.markdown("#### 📋 Parametros")
        mapa_rota = {"Bel-Mcp-Bel": "BLM - MCP", "Bel-Alt-Bel": "BLM - ALT", "Bel-Ita-Bel": "BLM - ITB", "Bel-Sat-Bel": "BLM - STM"}
        rota_ui = st.selectbox("Rota de Operação", list(mapa_rota.keys()))
        col_tecnica = mapa_rota[rota_ui]
        tipo_carga = st.selectbox("Tipo de Carga", df_frete['ITEM'].dropna().unique())
        modalidade = st.selectbox("Modalidade", ["IDA", "VOLTA", "IDA E VOLTA"])
        perc_desc = 0 # Adicione sua lógica de desconto aqui se necessário

    valor_bruto = float(df_frete.loc[df_frete['ITEM'] == tipo_carga, col_tecnica].values[0])
    v_com_desconto = valor_bruto * (1 - perc_desc)

    with c2:
        st.markdown("#### ⚖️ Dados Carga")
        v_carga_user = st.number_input("Valor Mercadoria (R$)", min_value=0.0, format="%.2f")
        st.text_input("Frete Líquido", value=f"R$ {v_com_desconto:,.2f}", disabled=True)

    with c3:
        st.markdown("#### 🛠️ Extras")
        total_extras = 0.0
        with st.expander("Expandir Serviços"):
            servicos = ["ESTIVA REMETENTE", "PESAGEM", "ESTIVA DESTINATÁRIO", "OVAÇÃO", "COLETA", "ENTREGA", "EXPURGO", "ENLONAMENTO", "TRANSBORDO", "OUTROS"]
            for serv in servicos:
                val = st.number_input(serv, min_value=0.0, value=0.0, key=f"srv_{serv}")
                total_extras += val

    valor_final = v_com_desconto + total_extras
    st.markdown(f"""
        <div style="background-color:{REICON_BLUE}; color:white; padding:20px; border-radius:12px; display:flex; justify-content:space-between; align-items:center; margin-top:25px; border-bottom:6px solid {REICON_ORANGE};">
            <div>
                <p style="margin:0; font-size:14px; opacity:0.8;">VALOR TOTAL FINAL</p>
                <p style="font-size:32px; font-weight:800; color:{REICON_ORANGE}; margin:0;">R$ {valor_final:,.2f}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
