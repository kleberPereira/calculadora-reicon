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
TEXT_DARK = "#1d130c"

# --- FUNÇÃO AUXILIAR: IMAGEM PARA BASE64 ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# --- TELA DE LOGIN (ESTILO ULTRA-MINIMALISTA) ---
def login_screen():
    # Injeção de Fontes, Ícones e CSS Global do Login
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1" rel="stylesheet">
        <style>
            /* Reset e Estilo do Login */
            [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; }
            .stApp { background-color: #ffffff; }
            
            .login-wrapper {
                max-width: 480px;
                margin: 0 auto;
                padding: 40px 24px;
                text-align: center;
                font-family: 'Manrope', sans-serif;
            }
            .sailing-icon { color: #fe7f2d; font-size: 48px; margin-bottom: 20px; }
            .login-title { font-size: 36px; font-weight: 800; color: #1d130c; margin-bottom: 8px; letter-spacing: -1px; }
            .login-subtitle { font-size: 14px; color: #9ca3af; font-weight: 500; margin-bottom: 60px; }
            .input-label { font-size: 10px; font-weight: 800; color: #9ca3af; text-transform: uppercase; letter-spacing: 2px; text-align: left; margin-bottom: 12px; display: block; }
            
            /* Customização do Input de Senha Streamlit */
            div[data-testid="stTextInput"] input {
                border: none !important;
                border-bottom: 1px solid #e5e7eb !important;
                border-radius: 0px !important;
                background-color: transparent !important;
                padding: 16px 0px !important;
                font-size: 18px !important;
                color: #1d130c !important;
                font-family: 'Manrope', sans-serif !important;
            }
            div[data-testid="stTextInput"] input:focus {
                border-bottom: 1px solid #fe7f2d !important;
                box-shadow: none !important;
                background-color: #f9fafb !important;
            }
            
            /* Botão de Entrada */
            div.stButton > button {
                width: 100% !important;
                background-color: #fe7f2d !important;
                color: white !important;
                border: none !important;
                border-radius: 12px !important;
                height: 56px !important;
                font-size: 18px !important;
                font-weight: 700 !important;
                margin-top: 40px !important;
                transition: all 0.2s;
            }
            div.stButton > button:active { transform: scale(0.98); }
            
            .footer-text { margin-top: 80px; font-size: 11px; color: #9ca3af; line-height: 1.6; }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
        st.markdown('<span class="material-symbols-outlined sailing-icon">sailing</span>', unsafe_allow_html=True)
        st.markdown('<h1 class="login-title">Grupo Reicon</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Calculadora de Frete</p>', unsafe_allow_html=True)
        
        st.markdown('<span class="input-label">Acesso: Time comercial reicon</span>', unsafe_allow_html=True)
        # O label é vazio para usarmos o nosso próprio span estilizado acima
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
                Sistema de uso exclusivo para colaboradores.<br>
                Criado por Kleber Pereira.
            </div>
            </div>
        """, unsafe_allow_html=True)

# 2. VERIFICAÇÃO DE AUTENTICAÇÃO
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    login_screen()
    st.stop()

# --- INÍCIO DO APP PRINCIPAL (DASHBOARD COMERCIAL) ---

# Injeção de CSS para o Dashboard (Mobile-First)
st.markdown(f"""
    <style>
    .stApp {{ background-color: #f8fafc; font-family: 'Manrope', sans-serif; }}
    
    /* Header Estilizado para Mobile */
    .app-header {{
        display: flex; flex-direction: column; align-items: center;
        padding: 20px 0; border-bottom: 2px solid {REICON_ORANGE};
        margin-bottom: 25px; background-color: white; border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }}
    .logo-main {{ width: 140px; height: auto; margin-bottom: 10px; }}
    .app-title {{ color: {REICON_BLUE}; font-size: 20px; font-weight: 800; margin: 0; }}
    .app-subtitle {{ color: {REICON_ORANGE}; font-size: 11px; font-weight: 600; text-transform: uppercase; margin: 0; }}

    /* Fix para prevenir teclado no Selectbox do celular */
    div[data-baseweb="select"] input {{
        pointer-events: none !important;
        caret-color: transparent !important;
    }}
    
    /* Estilo dos Cards das Colunas */
    div[data-testid="column"] {{
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        margin-bottom: 16px;
    }}
    
    /* Footer de Resultado Final */
    .total-card {{
        background-color: {REICON_BLUE};
        color: white;
        padding: 24px;
        border-radius: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 32px;
        margin-bottom: 16px;
        border-bottom: 6px solid {REICON_ORANGE};
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }}
    .total-val {{ font-size: 32px; font-weight: 800; color: {REICON_ORANGE}; margin: 0; }}
    .wa-icon {{ text-decoration: none; color: white; font-size: 32px; transition: transform 0.2s; }}
    .wa-icon:active {{ transform: scale(0.9); }}
    
    /* Labels do App */
    label {{ font-size: 0.75rem !important; font-weight: 800 !important; color: {REICON_BLUE} !important; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.7; }}
    </style>
""", unsafe_allow_html=True)

# Renderização do Header com Logo
logo_img = get_base64_image("image_aefad8.png")
if logo_img:
    st.markdown(f"""
        <div class="app-header">
            <img src="data:image/png;base64,{logo_img}" class="logo-main">
            <p class="app-title">Calculadora de Fretes</p>
            <p class="app-subtitle">Gestão Comercial Estratégica</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="app-header">
            <p style="font-size:32px; margin:0;">🚢</p>
            <p class="app-title">Grupo Reicon</p>
            <p class="app-subtitle">Gestão Comercial Estratégica</p>
        </div>
    """, unsafe_allow_html=True)

# Carregamento de Dados (Excel)
@st.cache_data
def load_excel_data():
    file_name = "APP - Calcular Fretes Por Praças 2026 - Copia.xlsx"
    try:
        df_raw = pd.read_excel(file_name, sheet_name="BASE_FRETE")
        skip_n = next(i for i, row in df_raw.iterrows() if "ITEM" in row.values) + 1
        return pd.read_excel(file_name, sheet_name="BASE_FRETE", skiprows=skip_n)
    except:
        return None

df_data = load_excel_data()

if df_data is not None:
    # Layout Principal em 3 Colunas (que empilham no celular)
    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        st.markdown("#### 📋 Parâmetros")
        mapa_praças = {
            "Bel-Mcp-Bel": "BLM - MCP", 
            "Bel-Alt-Bel": "BLM - ALT", 
            "Bel-Ita-Bel": "BLM - ITB", 
            "Bel-Sat-Bel": "BLM - STM"
        }
        rota_sel = st.selectbox("Rota de Operação", list(mapa_praças.keys()))
        col_ref = mapa_praças[rota_sel]
        
        item_sel = st.selectbox("Tipo de Carga", df_data['ITEM'].dropna().unique())
        modal_sel = st.selectbox("Modalidade", ["IDA", "VOLTA", "IDA E VOLTA"])
        
        dict_desc = {"0% sem desconto": 0, "5%": 0.05, "7%": 0.07, "10%": 0.1, "15%": 0.15, "20%": 0.2}
        desc_sel = st.selectbox("Desconto Especial", list(dict_desc.keys()))
        val_desc_p = dict_desc[desc_sel]

    # Cálculos de Negócio
    mcp_check = "Mcp" in rota_sel
    icms_val = 0.12 if mcp_check else 0.19
    div_adv = 0.88 if mcp_check else 0.81
    
    try:
        v_bruto_frete = float(df_data.loc[df_data['ITEM'] == item_sel, col_ref].values[0])
    except:
        v_bruto_frete = 0.0
        
    v_frete_desc = v_bruto_frete * (1 - val_desc_p)

    with c2:
        st.markdown("#### ⚖️ Carga e Valores")
        v_carga_input = st.number_input("Valor da Mercadoria (R$)", min_value=0.0, format="%.2f", step=1000.0)
        
        # Fórmula Ad Valorem
        v_ad_valorem = (v_carga_input * 0.002) / div_adv
        if modal_sel == "IDA E VOLTA":
            v_ad_valorem *= 2
            
        st.text_input("Ad Valorem", value=f"R$ {v_ad_valorem:,.2f}", disabled=True)
        st.text_input("Frete c/ Desconto", value=f"R$ {v_frete_desc:,.2f}", disabled=True)

    with c3:
        st.markdown("#### 🛠️ Serviços")
        v_extras_total = 0.0
        with st.expander("Adicionar Serviços Extras"):
            lista_serv = ["ESTIVA REMETENTE", "PESAGEM", "ESTIVA DESTINATÁRIO", "OVAÇÃO", "COLETA", "ENTREGA", "EXPURGO", "ENLONAMENTO", "TRANSBORDO", "OUTROS"]
            for s in lista_serv:
                val_s = st.number_input(s, min_value=0.0, value=0.0, key=f"input_{s}")
                v_extras_total += val_s

    # RESULTADO FINAL
    v_final_frete = v_frete_desc + v_ad_valorem + v_extras_total

    # Gerar Link WhatsApp
    txt_wa = (
        "Olá, segue a cotação solicitada!\n\n"
        "Cotação de Frete\n"
        f"📍 Rota: {rota_sel}\n"
        f"📦 Carga: {item_sel}\n"
        f"💵 Valor: R$ {v_final_frete:,.2f}\n\n"
        "Estamos à disposição e aguardamos sua resposta!"
    )
    url_wa = f"https://wa.me/?text={urllib.parse.quote(txt_wa)}"

    st.markdown(f"""
        <div class="total-card">
            <div>
                <p style="margin:0; font-size:12px; opacity:0.7; font-weight:700; text-transform:uppercase;">Valor Final do Frete</p>
                <p class="total-val">R$ {v_final_frete:,.2f}</p>
            </div>
            <a href="{url_wa}" target="_blank" class="wa-icon" title="Enviar WhatsApp">📩</a>
        </div>
    """, unsafe_allow_html=True)

    # Detalhamento do Cálculo
    with st.expander("📄 Ver Memória de Cálculo"):
        st.markdown(f"""
        - **Frete com Desconto:** R$ {v_frete_desc:,.2f}
        - **Ad Valorem:** R$ {v_ad_valorem:,.2f}
        - **Serviços Adicionais:** R$ {v_extras_total:,.2f}
        <br>
        **Soma Total: R$ {v_final_frete:,.2f}**
        """, unsafe_allow_html=True)
else:
    st.error("Erro ao carregar a base de dados. Verifique o arquivo Excel.")
