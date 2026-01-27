import streamlit as st
import pandas as pd
import urllib.parse
import base64
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Reicon Comercial", 
    page_icon="🚢", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Cores da Identidade Visual
REICON_BLUE = "#233d4d"
REICON_ORANGE = "#fe7f2d"

# --- FUNÇÃO AUXILIAR: IMAGEM PARA BASE64 ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# --- TELA DE LOGIN (DESIGN REFINADO) ---
def login_screen():
    logo_login = get_base64_image("Reicon_full.png")
    
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&display=swap" rel="stylesheet">
        <style>
            [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; }
            .stApp { background-color: #ffffff; }
            
            .login-wrapper {
                max-width: 380px; /* Reduzido para alinhar melhor com o botão */
                margin: 0 auto;
                padding: 60px 24px;
                text-align: center;
                font-family: 'Manrope', sans-serif;
            }
            .logo-login { width: 180px; margin-bottom: 30px; }
            .login-title { font-size: 24px; font-weight: 800; color: #1d130c; margin-bottom: 4px; text-align: center; }
            .login-subtitle { font-size: 13px; color: #9ca3af; font-weight: 500; margin-bottom: 50px; text-align: center; }
            .input-label { font-size: 10px; font-weight: 800; color: #9ca3af; text-transform: uppercase; letter-spacing: 1.5px; text-align: center; margin-bottom: 15px; display: block; }
            
            /* Customização do Input de Senha */
            div[data-testid="stTextInput"] input {
                border: none !important;
                border-bottom: 1px solid #e5e7eb !important;
                border-radius: 0px !important;
                background-color: transparent !important;
                padding: 16px 12px !important; /* Adicionado espaço à esquerda (12px) */
                font-size: 16px !important;
                color: #1d130c !important;
                transition: all 0.3s;
            }
            div[data-testid="stTextInput"] input:focus {
                border-bottom: 1px solid #fe7f2d !important;
                background-color: #f9fafb !important;
                box-shadow: none !important;
            }
            
            /* Botão de Entrada Ajustado */
            div.stButton > button {
                width: 100% !important;
                background-color: #fe7f2d !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                height: 54px !important;
                font-size: 16px !important;
                font-weight: 700 !important;
                margin-top: 30px !important;
            }
            .footer-text { margin-top: 60px; font-size: 10px; color: #cbd5e1; line-height: 1.5; }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
        
        # Logo Reicon em vez do barco
        if logo_login:
            st.markdown(f'<img src="data:image/png;base64,{logo_login}" class="logo-login">', unsafe_allow_html=True)
        
        st.markdown('<h1 class="login-title">Grupo Reicon</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Calculadora de Frete</p>', unsafe_allow_html=True)
        
        st.markdown('<span class="input-label">Acesso: Time comercial reicon</span>', unsafe_allow_html=True)
        senha = st.text_input("", type="password", placeholder="Digite sua senha", key="user_senha")
        
        if st.button("Entrar"):
            if senha == "reicon2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Senha inválida")
        
        st.markdown("""
            <div class="footer-text">
                © 2026 Grupo Reicon Logística. Todos os direitos reservados.<br>
                Sistema de uso exclusivo para colaboradores. - Criado por Kleber Pereira.
            </div>
            </div>
        """, unsafe_allow_html=True)

# 2. VERIFICAÇÃO DE AUTENTICAÇÃO
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    login_screen()
    st.stop()

# --- DASHBOARD COMERCIAL (MANTIDO DO BACKUP) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #f8fafc; font-family: 'Manrope', sans-serif; }}
    .app-header {{
        display: flex; flex-direction: column; align-items: center;
        padding: 20px 0; border-bottom: 2px solid {REICON_ORANGE};
        margin-bottom: 25px; background-color: white; border-radius: 0 0 20px 20px;
    }}
    .logo-main {{ width: 140px; height: auto; margin-bottom: 10px; }}
    .app-title {{ color: {REICON_BLUE}; font-size: 20px; font-weight: 800; margin: 0; }}
    div[data-baseweb="select"] input {{ pointer-events: none !important; caret-color: transparent !important; }}
    div[data-testid="column"] {{ background-color: white; padding: 20px; border-radius: 16px; border: 1px solid #f1f5f9; margin-bottom: 16px; }}
    .total-card {{ background-color: {REICON_BLUE}; color: white; padding: 24px; border-radius: 20px; display: flex; justify-content: space-between; align-items: center; margin-top: 32px; border-bottom: 6px solid {REICON_ORANGE}; }}
    .total-val {{ font-size: 32px; font-weight: 800; color: {REICON_ORANGE}; margin: 0; }}
    </style>
""", unsafe_allow_html=True)

logo_main = get_base64_image("image_aefad8.png") # Logo do header principal
st.markdown(f"""
    <div class="app-header">
        <img src="data:image/png;base64,{logo_main}" class="logo-main">
        <p class="app-title">Calculadora de Fretes</p>
    </div>
""", unsafe_allow_html=True)

@st.cache_data
def load_excel_data():
    file_name = "APP - Calcular Fretes Por Praças 2026 - Copia.xlsx"
    try:
        df_raw = pd.read_excel(file_name, sheet_name="BASE_FRETE")
        skip_n = next(i for i, row in df_raw.iterrows() if "ITEM" in row.values) + 1
        return pd.read_excel(file_name, sheet_name="BASE_FRETE", skiprows=skip_n)
    except: return None

df_data = load_excel_data()

if df_data is not None:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown("#### 📋 Parâmetros")
        mapa_praças = {"Bel-Mcp-Bel": "BLM - MCP", "Bel-Alt-Bel": "BLM - ALT", "Bel-Ita-Bel": "BLM - ITB", "Bel-Sat-Bel": "BLM - STM"}
        rota_sel = st.selectbox("Rota de Operação", list(mapa_praças.keys()))
        col_ref = mapa_praças[rota_sel]
        item_sel = st.selectbox("Tipo de Carga", df_data['ITEM'].dropna().unique())
        modal_sel = st.selectbox("Modalidade", ["IDA", "VOLTA", "IDA E VOLTA"])
        dict_desc = {"0% sem desconto": 0, "5%": 0.05, "7%": 0.07, "10%": 0.1, "15%": 0.15, "20%": 0.2}
        val_desc_p = dict_desc[st.selectbox("Desconto Especial", list(dict_desc.keys()))]

    # Lógica de cálculo (IDÊNTICA AO BACKUP)
    mcp_check = "Mcp" in rota_sel
    div_adv = 0.88 if mcp_check else 0.81
    v_bruto_frete = float(df_data.loc[df_data['ITEM'] == item_sel, col_ref].values[0])
    v_frete_desc = v_bruto_frete * (1 - val_desc_p)

    with c2:
        st.markdown("#### ⚖️ Carga e Valores")
        v_carga_input = st.number_input("Valor da Mercadoria (R$)", min_value=0.0, format="%.2f", step=1000.0)
        v_ad_valorem = (v_carga_input * 0.002) / div_adv
        if modal_sel == "IDA E VOLTA": v_ad_valorem *= 2
        st.text_input("Ad Valorem", value=f"R$ {v_ad_valorem:,.2f}", disabled=True)
        st.text_input("Frete c/ Desconto", value=f"R$ {v_frete_desc:,.2f}", disabled=True)

    with c3:
        st.markdown("#### 🛠️ Serviços")
        v_extras_total = 0.0
        with st.expander("Expandir Serviços Extras"):
            for s in ["ESTIVA REMETENTE", "PESAGEM", "ESTIVA DESTINATÁRIO", "OVAÇÃO", "COLETA", "ENTREGA", "EXPURGO", "ENLONAMENTO", "TRANSBORDO", "OUTROS"]:
                val_s = st.number_input(s, min_value=0.0, value=0.0, key=f"input_{s}")
                v_extras_total += val_s

    v_final_frete = v_frete_desc + v_ad_valorem + v_extras_total
    url_wa = f"https://wa.me/?text={urllib.parse.quote(f'Cotação Reicon: R$ {v_final_frete:,.2f}')}"

    st.markdown(f"""
        <div class="total-card">
            <div>
                <p style="margin:0; font-size:12px; opacity:0.7; font-weight:700;">VALOR TOTAL DO FRETE FINAL</p>
                <p class="total-val">R$ {v_final_frete:,.2f}</p>
            </div>
            <a href="{url_wa}" target="_blank" style="text-decoration:none; font-size:30px;">📩</a>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("📄 Ver Memória de Cálculo"):
        st.write(f"Frete: R$ {v_frete_desc:,.2f} | AdVal: R$ {v_ad_valorem:,.2f} | Extras: R$ {v_extras_total:,.2f}")
