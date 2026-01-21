import streamlit as st
import pandas as pd
import urllib.parse

# 1. Configuração da Página
st.set_page_config(page_title="Reicon Comercial", page_icon="🚚", layout="wide")

REICON_BLUE = "#233d4d"
REICON_ORANGE = "#fe7f2d"

# --- ADICIONAR LOGO APÓS st.set_page_config ---

# Script para transformar em PWA (Instalável)
st.markdown("""
    <script>
    // Registro de Service Worker para PWA
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js').then(function(registration) {
          console.log('ServiceWorker registrado com sucesso');
        }, function(err) {
          console.log('Falha no registro do ServiceWorker: ', err);
        });
      });
    }
    </script>
    """, unsafe_allow_html=True)

# Código para adicionar o botão de instalação (opcional, o navegador já sugere)
st.markdown("""
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#233d4d">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    """, unsafe_allow_html=True)

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f8fafc; }}
    .header-container {{
        display: flex; justify-content: space-between; align-items: flex-end;
        padding: 0px 0px 10px 0px; border-bottom: 2px solid {REICON_ORANGE}; margin-bottom: 20px;
    }}
    .header-right {{ text-align: right; line-height: 1.2; }}
    .header-title {{ color: {REICON_BLUE}; font-size: 18px; font-weight: 800; margin: 0; }}
    .header-subtitle {{ color: {REICON_BLUE}; font-size: 11px; font-weight: 400; margin: 0; opacity: 0.7; }}
    div[data-testid="column"] {{
        background-color: #FFFFFF; padding: 15px; border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #eef2f6;
    }}
    label {{ font-size: 0.8rem !important; font-weight: 700 !important; color: {REICON_BLUE} !important; text-transform: uppercase; }}
    .footer-container {{
        background-color: {REICON_BLUE}; color: white; padding: 20px; border-radius: 12px;
        display: flex; justify-content: space-between; align-items: center; margin-top: 20px;
        border-bottom: 6px solid {REICON_ORANGE};
    }}
    .total-value {{ font-size: 32px; font-weight: 800; color: {REICON_ORANGE}; margin: 0; }}
    .icon-link {{ text-decoration: none; color: white; font-size: 24px; margin-left: 15px; transition: 0.3s; }}
    .icon-link:hover {{ color: {REICON_ORANGE}; }}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown(f"""
    <div class="header-container">
        <div style="color: {REICON_BLUE}; font-size: 24px; font-weight: 900;">🚢 REICON</div>
        <div class="header-right">
            <p class="header-title">Calculadora de Fretes por Praça</p>
            <p class="header-subtitle">Gestão Comercial Estratégica</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with st.columns([1,1,1])[1]:
        senha = st.text_input("Acesso Comercial Reicon", type="password", placeholder="Digite a senha")
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

# 4. Layout 4 Colunas
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("#### 📋 Parametrização")
    mapa_rota = {"Bel-Mcp-Bel": "BLM - MCP", "Bel-Alt-Bel": "BLM - ALT", "Bel-Ita-Bel": "BLM - ITB", "Bel-Sat-Bel": "BLM - STM"}
    rota_ui = st.selectbox("Rota de Operação", list(mapa_rota.keys()))
    col_tecnica = mapa_rota[rota_ui]
    tipo_carga = st.selectbox("Tipo de Carga", df_frete['ITEM'].dropna().unique())
    modalidade = st.selectbox("Modalidade", ["IDA", "VOLTA", "IDA E VOLTA"])
    descontos = {"0% sem desconto": 0, "5%": 0.05, "7%": 0.07, "10%": 0.1, "15%": 0.15, "20%": 0.2}
    desc_nome = st.selectbox("Desconto Aplicado", list(descontos.keys()))
    perc_desc = descontos[desc_nome]

# Lógica de Cálculo
is_mcp = "Mcp" in rota_ui
icms_taxa = 0.12 if is_mcp else 0.19
divisor_adv = 0.88 if is_mcp else 0.81
valor_bruto = float(df_frete.loc[df_frete['ITEM'] == tipo_carga, col_tecnica].values[0])
valor_do_desconto = valor_bruto * perc_desc
v_com_desconto = valor_bruto - valor_do_desconto

with c2:
    st.markdown("#### 💵 Valores Frete")
    st.text_input("Frete Bruto (c/ ICMS)", value=f"R$ {valor_bruto:,.2f}", disabled=True)
    st.text_input("ICMS Local", value=f"{icms_taxa*100:.0f}%", disabled=True)
    st.text_input("Valor Líquido Frete", value=f"R$ {v_com_desconto:,.2f}", disabled=True)

with c3:
    st.markdown("#### ⚖️ Dados da Carga")
    v_carga_user = st.number_input("Valor da Mercadoria (R$)", min_value=0.0, step=1000.0, format="%.2f")
    calc_adv = (v_carga_user * 0.002) / divisor_adv
    if modalidade == "IDA E VOLTA": calc_adv *= 2
    st.text_input("Ad Valorem", value=f"R$ {calc_adv:,.2f}", disabled=True)

with c4:
    st.markdown("#### 🛠️ Serviços Extras")
    total_extras = 0.0
    servicos = ["ESTIVA REMETENTE", "PESAGEM", "ESTIVA DESTINATÁRIO", "OVAÇÃO", "COLETA", "ENTREGA", "EXPURGO", "ENLONAMENTO", "TRANSBORDO", "OUTROS"]
    for serv in servicos:
        val = st.number_input(serv, min_value=0.0, value=0.0, step=10.0, key=f"srv_{serv}")
        total_extras += val

# 5. Resultado Final
valor_final = v_com_desconto + calc_adv + total_extras

# --- FORMATAÇÃO DA MENSAGEM WHATSAPP ---
msg_wa = (
    "Olá, segue a cotação solicitada!\n\n"
    "Cotação de Frete\n"
    f"- Rota: {rota_ui}\n"
    f"- Carga: {tipo_carga}\n"
    f"- Valor: R$ {valor_final:,.2f}\n\n"
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
            <a href="{link_wa}" target="_blank" class="icon-link" title="Enviar WhatsApp">📩</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 6. Raciocínio de Cálculo
st.markdown("---")
with st.expander("📄 Raciocínio do Cálculo Detalhado"):
    st.markdown(f"""
    ### Detalhamento da Composição:
    
    * **1. Frete Líquido:**
      - Valor Bruto: R$ {valor_bruto:,.2f}
      - Desconto aplicado ({desc_nome}): - R$ {valor_do_desconto:,.2f}
      - **Subtotal Frete: R$ {v_com_desconto:,.2f}**
    
    * **2. Proteção (Ad Valorem):**
      - Cálculo: (R$ {v_carga_user:,.2f} × 0,2%) / {divisor_adv}
      - Multiplicador Modalidade ({modalidade}): {'x2' if modalidade == 'IDA E VOLTA' else 'x1'}
      - **Subtotal Ad Valorem: R$ {calc_adv:,.2f}**
    
    * **3. Serviços Adicionais:**
      - Somatória de itens manuais: **R$ {total_extras:,.2f}**
    
    ---
    **TOTAL GERAL: R$ {valor_final:,.2f}**

    """)
