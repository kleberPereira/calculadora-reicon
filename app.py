import streamlit as st
import pandas as pd
import urllib.parse
import base64
from io import BytesIO

# 1. Configuração da Página
st.set_page_config(page_title="Reicon Comercial", page_icon="🚢", layout="wide")

REICON_BLUE = "#233d4d"
REICON_ORANGE = "#fe7f2d"

# Função para converter imagem local para base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# --- CSS GLOBAL E TELA DE LOGIN ---
st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&display=swap" rel="stylesheet">
    <style>
    /* Reset Geral */
    .stApp {{ background-color: #ffffff; font-family: 'Manrope', sans-serif; }}
    
    /* Esconder Header do Streamlit na Login */
    header {{visibility: hidden;}}
    
    /* Container Central de Login */
    .login-wrapper {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        max-width: 400px;
        margin: 0 auto;
        padding: 40px 20px;
        text-align: center;
    }}
    
    .logo-discreta {{
        width: 80px;
        height: auto;
        margin-bottom: 20px;
        opacity: 0.9;
    }}
    
    .title-reicon {{
        font-size: 28px;
        font-weight: 800;
        color: {REICON_BLUE};
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }}
    
    .subtitle-reicon {{
        font-size: 14px;
        color: #94a3b8;
        font-weight: 500;
        margin-bottom: 40px;
    }}

    /* Estilização dos Inputs Streamlit para parecer Material Minimal */
    div[data-testid="stTextInput"] label {{
        display: none; /* Esconde label padrão */
    }}
    
    div[data-testid="stTextInput"] input {{
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        color: {REICON_BLUE} !important;
        height: 50px !important;
    }}
    
    div[data-testid="stTextInput"] input:focus {{
        border-color: {REICON_ORANGE} !important;
        box-shadow: 0 0 0 1px {REICON_ORANGE} !important;
    }}

    /* Botão Entrar */
    div.stButton > button {{
        width: 100% !important;
        background-color: {REICON_ORANGE} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        height: 50px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        margin-top: 20px !important;
        transition: all 0.2s ease;
    }}
    
    div.stButton > button:hover {{
        background-color: #e67329 !important;
        transform: translateY(-1px);
    }}

    /* Link Esqueci Senha */
    .forgot-pass {{
        margin-top: 20px;
        font-size: 13px;
        color: #64748b;
        text-decoration: none;
        font-weight: 500;
    }}
    .forgot-pass:hover {{ color: {REICON_ORANGE}; }}

    /* Rodapé */
    .login-footer {{
        margin-top: 60px;
        font-size: 11px;
        color: #cbd5e1;
        line-height: 1.6;
        max-width: 300px;
    }}

    /* Ajustes Dashboard */
    .header-container {{
        display: flex; flex-direction: column; align-items: center;
        padding: 15px 0; border-bottom: 2px solid {REICON_ORANGE};
        margin-bottom: 25px; background-color: white;
    }}
    .logo-dash {{ width: 100px; margin-bottom: 5px; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Lógica de Autenticação (TELA DE LOGIN)
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    # Interface de Login
    logo_base64 = get_base64_image("Reicon_full.png")
    
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    
    if logo_base64:
        st.markdown(f'<img src="data:image/png;base64,{logo_base64}" class="logo-discreta">', unsafe_allow_html=True)
    
    st.markdown(f'<div class="title-reicon">Grupo Reicon</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle-reicon">Calculadora de Frete</div>', unsafe_allow_html=True)
    
    # Input de Senha (O Streamlit já possui o ícone do olho nativo para campos "password")
    senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
    
    if st.button("Entrar"):
        if senha == "reicon2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta")
            
    # Link Esqueci Senha
    st.markdown(f'<a href="https://wa.me/5591982257816" target="_blank" class="forgot-pass">Esqueci minha senha</a>', unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
        <div class="login-footer">
            © 2026 Grupo Reicon Logística. Todos os direitos reservados.<br>
            Sistema de uso exclusivo para colaboradores.<br>
            Criado por Kleber Pereira.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. DASHBOARD (APÓS LOGIN) ---
# Se chegou aqui, está autenticado

# Header do Dashboard
logo_dash = get_base64_image("Reicon_full.png")
st.markdown(f"""
    <div class="header-container">
        {f'<img src="data:image/png;base64,{logo_dash}" class="logo-dash">' if logo_dash else ''}
        <div class="header-right">
            <p style="color:{REICON_BLUE}; font-size:18px; font-weight:800; margin:0;">Calculadora de Fretes por Praça</p>
            <p style="color:{REICON_BLUE}; font-size:11px; font-weight:400; margin:0; opacity:0.7;">Gestão Comercial Estratégica</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Processamento de Dados
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
    # Layout Dashboard
    c1, c2, c3 = st.columns([1,1,1])

    with c1:
        st.markdown("#### 📋 Parametros")
        mapa_rota = {"Bel-Mcp-Bel": "BLM - MCP", "Bel-Alt-Bel": "BLM - ALT", "Bel-Ita-Bel": "BLM - ITB", "Bel-Sat-Bel": "BLM - STM"}
        rota_ui = st.selectbox("Rota de Operação", list(mapa_rota.keys()))
        col_tecnica = mapa_rota[rota_ui]
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

    # Resultado Final
    valor_final = v_com_desconto + calc_adv + total_extras
    msg_wa = f"Olá, segue a cotação solicitada!\n\nCotação de Frete\n📍 Rota: {rota_ui}\n📦 Carga: {tipo_carga}\n💵 Valor: R$ {valor_final:,.2f}\n\nAguardamos sua resposta!"
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

    with st.expander("📄 Ver Detalhamento do Cálculo"):
        st.markdown(f"- **Frete:** R$ {v_com_desconto:,.2f}\n- **Ad Valorem:** R$ {calc_adv:,.2f}\n- **Extras:** R$ {total_extras:,.2f}\n---\n**TOTAL: R$ {valor_final:,.2f}**")
