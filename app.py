import streamlit as st
import pandas as pd
import urllib.parse
import os

# 1. Configuração da Página
st.set_page_config(page_title="Reicon Comercial", page_icon="🚢", layout="wide")

# Cores e Variáveis de Estilo
REICON_BLUE = "#233d4d"
REICON_ORANGE = "#fe7f2d"

# --- CSS MATERIAL DESIGN & MOBILE OPTIMIZATION ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    .stApp {{ background-color: #f0f2f5; font-family: 'Roboto', sans-serif; }}
    
    /* Header Equilibrado para Celular */
    .header-container {{
        display: flex; flex-direction: column; align-items: center;
        padding: 15px 0; border-bottom: 3px solid {REICON_ORANGE};
        margin-bottom: 20px; background-color: white; border-radius: 0 0 15px 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    .logo-img {{ width: 80px; margin-bottom: 10px; }}
    .header-title {{ color: {REICON_BLUE}; font-size: 1.3rem; font-weight: 800; margin: 0; text-align: center; }}
    .header-subtitle {{ color: {REICON_ORANGE}; font-size: 0.8rem; font-weight: 400; margin: 0; text-align: center; text-transform: uppercase; letter-spacing: 1px; }}

    /* Cards Estilo Material Design */
    div[data-testid="column"] {{
        background-color: #FFFFFF; padding: 20px; border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
        margin-bottom: 15px;
    }}
    div[data-testid="column"]:hover {{
        box-shadow: 0 10px 20px rgba(0,0,0,0.15), 0 6px 6px rgba(0,0,0,0.10);
    }}
    
    /* Inputs e Labels */
    label {{ font-size: 0.75rem !important; font-weight: 700 !important; color: {REICON_BLUE} !important; opacity: 0.8; }}
    .stSelectbox, .stNumberInput {{ margin-bottom: 5px; }}
    
    /* Correção do Teclado no Celular (Prevenir foco automático indesejado) */
    div[data-baseweb="select"] input {{
        caret-color: transparent !important; /* Esconde o cursor de digitação */
    }}

    /* Footer / Valor Final Flutuante (Material Design) */
    .footer-container {{
        background-color: {REICON_BLUE}; color: white; padding: 20px; border-radius: 15px;
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 10px; border-left: 8px solid {REICON_ORANGE};
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    .total-value {{ font-size: 2rem; font-weight: 800; color: {REICON_ORANGE}; margin: 0; }}
    
    /* Expander Estilizado */
    .stExpander {{ border: none !important; background-color: #f8fafc !important; border-radius: 8px !important; }}
    
    /* Ícone de Envio */
    .icon-link {{ text-decoration: none; font-size: 30px; transition: transform 0.2s; }}
    .icon-link:hover {{ transform: scale(1.1); }}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER COM LOGO ---
# Se o arquivo de imagem estiver na mesma pasta, ele será carregado
logo_path = "image_aefad8.png"
if os.path.exists(logo_path):
    st.markdown(f"""
        <div class="header-container">
            <img src="data:image/png;base64,{urllib.parse.quote(open(logo_path, "rb").read().encode("base64"))}" class="logo-img">
            <p class="header-title">Calculadora de Fretes por Praça</p>
            <p class="header-subtitle">Gestão Comercial Estratégica</p>
        </div>
        """, unsafe_allow_html=True)
else:
    # Fallback caso a imagem não seja encontrada
    st.markdown(f"""
        <div class="header-container">
            <div style="font-size: 40px; margin-bottom: 5px;">🚢</div>
            <p class="header-title">Calculadora de Fretes por Praça</p>
            <p class="header-subtitle">Gestão Comercial Estratégica</p>
        </div>
        """, unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with st.container():
        senha = st.text_input("Acesso Reicon", type="password", placeholder="Digite a senha")
        if st.button("Entrar"):
            if senha == "reicon2026": st.session_state.auth = True; st.rerun()
            else: st.error("Acesso negado")
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

# 4. Interface Principal
c1, c2, c3 = st.columns([1, 1, 1]) # Colunas para desktop, que empilham no mobile

with c1:
    st.markdown("#### 📋 Parametros")
    mapa_rota = {"Bel-Mcp-Bel": "BLM - MCP", "Bel-Alt-Bel": "BLM - ALT", "Bel-Ita-Bel": "BLM - ITB", "Bel-Sat-Bel": "BLM - STM"}
    rota_ui = st.selectbox("Rota de Operação", list(mapa_rota.keys()))
    col_tecnica = mapa_rota[rota_ui]
    
    # Selectbox com label amigável
    tipo_carga = st.selectbox("Tipo de Carga", df_frete['ITEM'].dropna().unique())
    modalidade = st.selectbox("Modalidade", ["IDA", "VOLTA", "IDA E VOLTA"])
    descontos = {"0% sem desconto": 0, "5%": 0.05, "7%": 0.07, "10%": 0.1, "15%": 0.15, "20%": 0.2}
    desc_nome = st.selectbox("Desconto Especial", list(descontos.keys()))
    perc_desc = descontos[desc_nome]

# Cálculos Técnicos
is_mcp = "Mcp" in rota_ui
icms_taxa = 0.12 if is_mcp else 0.19
divisor_adv = 0.88 if is_mcp else 0.81
valor_bruto = float(df_frete.loc[df_frete['ITEM'] == tipo_carga, col_tecnica].values[0])
v_com_desconto = valor_bruto * (1 - perc_desc)

with c2:
    st.markdown("#### 💵 Valores e Carga")
    v_carga_user = st.number_input("Valor da Mercadoria (R$)", min_value=0.0, step=1000.0, format="%.2f")
    calc_adv = (v_carga_user * 0.002) / divisor_adv
    if modalidade == "IDA E VOLTA": calc_adv *= 2
    
    st.text_input("Ad Valorem", value=f"R$ {calc_adv:,.2f}", disabled=True)
    st.text_input("Frete com Desconto", value=f"R$ {v_com_desconto:,.2f}", disabled=True)

with c3:
    st.markdown("#### 🛠️ Serviços")
    # Colocando os serviços extras em um EXPANDER para mobile
    total_extras = 0.0
    with st.expander("Clique para Adicionar Extras"):
        servicos = ["ESTIVA REMETENTE", "PESAGEM", "ESTIVA DESTINATÁRIO", "OVAÇÃO", "COLETA", "ENTREGA", "EXPURGO", "ENLONAMENTO", "TRANSBORDO", "OUTROS"]
        for serv in servicos:
            val = st.number_input(serv, min_value=0.0, value=0.0, step=10.0, key=f"srv_{serv}")
            total_extras += val

# 5. Resultado Final (Mobile View)
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
            <p style="margin:0; font-size:0.8rem; opacity:0.8;">VALOR FINAL</p>
            <p class="total-value">R$ {valor_final:,.2f}</p>
        </div>
        <div>
            <a href="{link_wa}" target="_blank" class="icon-link">📩</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 6. Raciocínio (Recolhido para não poluir)
with st.expander("📄 Ver Detalhamento do Cálculo"):
    st.write(f"**Frete Bruto:** R$ {valor_bruto:,.2f}")
    st.write(f"**Desconto ({desc_nome}):** - R$ {valor_bruto * perc_desc:,.2f}")
    st.write(f"**Ad Valorem:** + R$ {calc_adv:,.2f}")
    st.write(f"**Serviços:** + R$ {total_extras:,.2f}")
