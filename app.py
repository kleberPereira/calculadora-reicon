import streamlit as st
import pandas as pd
import urllib.parse
import base64

# 1. Configuração da Página
st.set_page_config(page_title="Reicon Comercial", page_icon="🚢", layout="wide")

REICON_BLUE = "#233d4d"
REICON_ORANGE = "#fe7f2d"

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

# --- CSS REFINADO ---
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
    .header-title {{ color: {REICON_BLUE}; font-size: 22px; font-weight: 800; margin: 0; }}
    
    div[data-testid="column"] {{
        background-color: white; padding: 24px; border-radius: 20px;
        border: 1px solid #f1f5f9; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }}
    
    label {{ font-size: 0.85rem !important; font-weight: 600 !important; color: {REICON_BLUE} !important; margin-bottom: 8px !important; }}
    
    .footer-container {{
        background-color: {REICON_BLUE}; color: white; padding: 28px; border-radius: 24px;
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 40px; margin-bottom: 20px; border-right: 8px solid {REICON_ORANGE};
    }}
    .total-value {{ font-size: 36px; font-weight: 800; color: {REICON_ORANGE}; margin: 0; }}
    
    .wa-btn {{
        background-color: #25D366; color: white !important; padding: 12px 20px;
        border-radius: 14px; text-decoration: none; display: flex;
        align-items: center; gap: 10px; font-weight: 600; transition: 0.2s;
    }}

    /* Estilo Memória de Cálculo */
    .memoria-item {{
        display: flex; justify-content: space-between; padding: 8px 0;
        border-bottom: 1px solid #f1f5f9; font-size: 15px; color: #475569;
    }}
    .memoria-label {{ font-weight: 600; color: {REICON_BLUE}; }}
</style>
"""
st.markdown(estilo_ui, unsafe_allow_html=True)

# --- HEADER ---
logo_base64 = get_base64_image("Reicon_full.png")
st.markdown(f'<div class="header-container">{"<img src=\'data:image/png;base64," + logo_base64 + "\' class=\'logo-img\'>" if logo_base64 else "🚢"}<p class="header-title">Calculadora de Fretes por Praça</p></div>', unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, center, _ = st.columns([1, 2, 1])
    with center:
        senha = st.text_input("Acesso Restrito", type="password", placeholder="Digite sua senha")
        if st.button("Entrar", use_container_width=True):
            if senha == "reicon2026": st.session_state.auth = True; st.rerun()
            else: st.error("Senha inválida")
    st.stop()

# --- DADOS ---
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
        st.markdown("##### 📋 Parâmetros")
        mapa_rota = {"Bel-Mcp-Bel": "BLM - MCP", "Bel-Alt-Bel": "BLM - ALT", "Bel-Ita-Bel": "BLM - ITB", "Bel-Sat-Bel": "BLM - STM"}
        rota_ui = st.selectbox("Rota", list(mapa_rota.keys()))
        col_tecnica = mapa_rota[rota_ui]
        tipo_carga = st.selectbox("Tipo de Carga", df_frete['ITEM'].dropna().unique())
        modalidade = st.selectbox("Modalidade", ["IDA", "VOLTA", "IDA E VOLTA"])
        descontos_dict = {"0% sem desconto": 0, "5%": 0.05, "7%": 0.07, "10%": 0.1, "15%": 0.15, "20%": 0.2}
        perc_desc = descontos_dict[st.selectbox("Desconto", list(descontos_dict.keys()))]

    # Cálculos
    is_mcp = "Mcp" in rota_ui
    divisor_adv = 0.88 if is_mcp else 0.81
    valor_bruto = float(df_frete.loc[df_frete['ITEM'] == tipo_carga, col_tecnica].values[0])
    
    # Cálculo do valor do desconto em R$
    valor_desconto_reais = valor_bruto * perc_desc
    v_com_desconto = valor_bruto - valor_desconto_reais

    with c2:
        st.markdown("##### ⚖️ Carga")
        v_carga_user = st.number_input("Valor Mercadoria (R$)", value=None, placeholder="Digite o valor", format="%.2f")
        v_carga_calc = v_carga_user if v_carga_user else 0.0
        calc_adv = (v_carga_calc * 0.002) / divisor_adv
        if modalidade == "IDA E VOLTA": calc_adv *= 2
        st.text_input("Ad Valorem", value=f"R$ {calc_adv:,.2f}", disabled=True)
        st.text_input("Frete Líquido", value=f"R$ {v_com_desconto:,.2f}", disabled=True)

    with c3:
        st.markdown("##### 🛠️ Extras")
        total_extras = 0.0
        with st.expander("Serviços Adicionais"):
            servicos = ["ESTIVA REMETENTE", "PESAGEM", "ESTIVA DESTINATÁRIO", "OVAÇÃO", "COLETA", "ENTREGA", "EXPURGO", "ENLONAMENTO", "TRANSBORDO", "OUTROS"]
            for serv in servicos:
                val = st.number_input(serv, value=None, placeholder="0,00", format="%.2f", key=f"srv_{serv}")
                total_extras += val if val else 0.0

    valor_final = v_com_desconto + calc_adv + total_extras
    
    # Resultado Final
    msg_wa = f"Olá, segue a cotação solicitada!\n📍 Rota: {rota_ui}\n📦 Carga: {tipo_carga}\n💵 Valor: R$ {valor_final:,.2f}"
    link_wa = f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"
    wa_svg = """<svg width="20" height="20" viewBox="0 0 448 512" fill="white" xmlns="http://www.w3.org/2000/svg"><path d="M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-117zm-157 338.7c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3L72 359.2l-4.4-7c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7 .9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2s-9.7 1.4-14.8 6.9c-5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4 2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5-3.9-10.5-6.6z"/></svg>"""

    st.markdown(f"""
        <div class="footer-container">
            <div><p style="margin:0; font-size:14px; opacity:0.8;">VALOR TOTAL FINAL</p><p class="total-value">R$ {valor_final:,.2f}</p></div>
            <div><a href="{link_wa}" target="_blank" class="wa-btn">{wa_svg} Enviar</a></div>
        </div>
    """, unsafe_allow_html=True)

    # --- MEMÓRIA DE CÁLCULO MELHORADA ---
    with st.expander("📄 Memória de Cálculo Detalhada"):
        st.markdown(f"""
            <div class="memoria-item"><span class="memoria-label">Frete Base:</span> <span>R$ {v_com_desconto:,.2f}</span></div>
            <div class="memoria-item"><span class="memoria-label">Advaloren:</span> <span>R$ {calc_adv:,.2f}</span></div>
            <div class="memoria-item"><span class="memoria-label">Extras:</span> <span>R$ {total_extras:,.2f}</span></div>
            <div class="memoria-item" style="color: #e53e3e;"><span class="memoria-label" style="color: #e53e3e;">Desconto concedido:</span> <span>- R$ {valor_desconto_reais:,.2f}</span></div>
            <div class="memoria-item" style="border-bottom: none; font-size: 18px; margin-top: 10px;">
                <span class="memoria-label" style="color: {REICON_ORANGE};">VALOR FINAL:</span> 
                <span style="font-weight: 800; color: {REICON_ORANGE};">R$ {valor_final:,.2f}</span>
            </div>
        """, unsafe_allow_html=True)

