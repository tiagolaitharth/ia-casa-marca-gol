import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(layout="wide")

st.title("📊 IA - Casa Marca Gol")

# =========================
# VERIFICAÇÃO
# =========================

if not os.path.exists("resultado_modelo.xlsx"):
    st.error("Arquivo não encontrado. Rode primeiro o modelo.py")
    st.stop()

df = pd.read_excel("resultado_modelo.xlsx")

# =========================
# TRATAMENTO DE DATA
# =========================

df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
df['Data_str'] = df['Data'].dt.strftime('%d/%m/%Y')

# =========================
# TRATAMENTO
# =========================

df['Placar'] = df['Placar'].astype(str).str.strip()
df['Placar'] = df['Placar'].replace("-", "🔮")

df['Probabilidade (%)'] = (df['Probabilidade'] * 100).round(2)

# =========================
# RESULTADO VISUAL
# =========================

def resultado_flag(placar):
    if placar == "🔮":
        return "🔮"
    try:
        gols = int(placar.split('x')[0].strip())
        return "🟢 V" if gols > 0 else "🔴 X"
    except:
        return ""

df['Resultado'] = df['Placar'].apply(resultado_flag)

# 🔥 FORÇANDO DATA DE HOJE
hoje_str = "23/04/2026"

# =========================
# ABAS
# =========================

tab1, tab2 = st.tabs(["📊 Análise Geral", "🏆 Ligas"])

# =========================
# ABA 1
# =========================

with tab1:

    if "min_prob" not in st.session_state:
        st.session_state.min_prob = 0
    if "max_prob" not in st.session_state:
        st.session_state.max_prob = 100
    if "slider_range" not in st.session_state:
        st.session_state.slider_range = (0, 100)

    if "busca_casa" not in st.session_state:
        st.session_state.busca_casa = ""
    if "busca_visit" not in st.session_state:
        st.session_state.busca_visit = ""
    if "busca_data" not in st.session_state:
        st.session_state.busca_data = ""

    def update_from_slider():
        st.session_state.min_prob = st.session_state.slider_range[0]
        st.session_state.max_prob = st.session_state.slider_range[1]

    def update_from_input():
        st.session_state.slider_range = (
            st.session_state.min_prob,
            st.session_state.max_prob
        )

    def limpar_range():
        st.session_state.slider_range = (0, 100)
        st.session_state.min_prob = 0
        st.session_state.max_prob = 100

    def limpar_filtros():
        st.session_state.busca_casa = ""
        st.session_state.busca_visit = ""
        st.session_state.busca_data = ""

    st.sidebar.header("Filtros")

    st.sidebar.slider(
        "Probabilidade (%)",
        0, 100,
        st.session_state.slider_range,
        key="slider_range",
        on_change=update_from_slider
    )

    st.sidebar.number_input("Min", 0, 100, key="min_prob", on_change=update_from_input)
    st.sidebar.number_input("Max", 0, 100, key="max_prob", on_change=update_from_input)

    st.sidebar.button("🔄 Limpar Range", on_click=limpar_range)

    threshold_min = st.session_state.min_prob
    threshold_max = st.session_state.max_prob

    st.sidebar.subheader("Filtros Avançados")

    todos_times = sorted(set(df['Time Casa']).union(set(df['Time Visitante'])))
    times_sidebar = st.sidebar.multiselect("Times", options=todos_times)

    todas_ligas = sorted(df['Liga'].dropna().unique())
    ligas_sidebar = st.sidebar.multiselect("Ligas", options=todas_ligas)

    placares = sorted(df['Placar'].dropna().unique())
    placar_sidebar = st.sidebar.multiselect("Placar", options=placares)

    df_filtrado = df[
        (df['Probabilidade'] >= threshold_min / 100) &
        (df['Probabilidade'] <= threshold_max / 100)
    ]

    if times_sidebar:
        df_filtrado = df_filtrado[
            df_filtrado['Time Casa'].isin(times_sidebar) |
            df_filtrado['Time Visitante'].isin(times_sidebar)
        ]

    if ligas_sidebar:
        df_filtrado = df_filtrado[df_filtrado['Liga'].isin(ligas_sidebar)]

    if placar_sidebar:
        df_filtrado = df_filtrado[df_filtrado['Placar'].isin(placar_sidebar)]

    st.subheader("🔎 Filtros da tabela")

    c1, c2, c3, c4 = st.columns([1,1,1,1])

    c1.text_input("Time Casa", key="busca_casa")
    c2.text_input("Time Visitante", key="busca_visit")
    c3.text_input("Data (dd/mm/yyyy)", key="busca_data")

    c4.button("🔄 Limpar", on_click=limpar_filtros)

    def aplicar(df_):
        if st.session_state.busca_casa:
            df_ = df_[df_['Time Casa'].str.contains(st.session_state.busca_casa, case=False)]
        if st.session_state.busca_visit:
            df_ = df_[df_['Time Visitante'].str.contains(st.session_state.busca_visit, case=False)]
        if st.session_state.busca_data:
            df_ = df_[df_['Data_str'] == st.session_state.busca_data]
        return df_

    df_filtrado = aplicar(df_filtrado)

    df_passado = df_filtrado[df_filtrado['Placar'] != "🔮"]
    df_0x1 = df_passado[df_passado['Placar'] == "0 x 1"]

    total = len(df_passado)
    erros_0x1 = len(df_0x1)
    taxa_0x1 = (erros_0x1 / total * 100) if total > 0 else 0

    st.markdown("### 📊 Resultado do filtro atual")

    col1, col2, col3 = st.columns(3)
    col1.metric("Jogos no filtro", total)
    col2.metric("0x1", erros_0x1)
    col3.metric("Taxa 0x1", f"{taxa_0x1:.2f}%")

    colunas = ['Liga','Data_str','Time Casa','Time Visitante','Placar','Resultado','Probabilidade (%)']

    st.dataframe(
        df_filtrado[colunas].sort_values(by='Probabilidade (%)', ascending=False),
        use_container_width=True
    )

    # =========================
    # JOGOS DE HOJE (CORRIGIDO)
    # =========================

    st.subheader("📅 Jogos de Hoje")

    df_hoje = df[df['Data_str'] == hoje_str]

    if len(df_hoje) > 0:
        st.dataframe(
            df_hoje[colunas].sort_values(by='Probabilidade (%)', ascending=False),
            use_container_width=True
        )
    else:
        st.warning(f"Nenhum jogo encontrado para hoje ({hoje_str})")