import streamlit as st
import pandas as pd
import os

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
# TRATAMENTO
# =========================

df['Data'] = pd.to_datetime(df['Data'])
df['Data_str'] = df['Data'].dt.strftime('%d/%m/%Y')

df['Placar'] = df['Placar'].astype(str).str.strip()
df['Placar'] = df['Placar'].replace("-", "🔮")

df['Probabilidade (%)'] = (df['Probabilidade'] * 100).round(2)

# =========================
# ESTADO
# =========================

if "min_prob" not in st.session_state:
    st.session_state.min_prob = 70
if "max_prob" not in st.session_state:
    st.session_state.max_prob = 90

if "busca_casa" not in st.session_state:
    st.session_state.busca_casa = ""
if "busca_visit" not in st.session_state:
    st.session_state.busca_visit = ""
if "busca_data" not in st.session_state:
    st.session_state.busca_data = ""

# =========================
# FUNÇÕES
# =========================

def update_from_slider():
    st.session_state.min_prob = st.session_state.slider_range[0]
    st.session_state.max_prob = st.session_state.slider_range[1]

def update_from_input():
    st.session_state.slider_range = (
        st.session_state.min_prob,
        st.session_state.max_prob
    )

def limpar_range():
    st.session_state.min_prob = 70
    st.session_state.max_prob = 90
    st.session_state.slider_range = (70, 90)

def limpar_filtros_tabela():
    st.session_state.busca_casa = ""
    st.session_state.busca_visit = ""
    st.session_state.busca_data = ""

# =========================
# SIDEBAR
# =========================

st.sidebar.header("Filtros")

# Probabilidade
st.sidebar.slider(
    "Probabilidade (%)",
    0, 100,
    (st.session_state.min_prob, st.session_state.max_prob),
    key="slider_range",
    on_change=update_from_slider
)

st.sidebar.number_input("Min", 0, 100, key="min_prob", on_change=update_from_input)
st.sidebar.number_input("Max", 0, 100, key="max_prob", on_change=update_from_input)

st.sidebar.button("🔄 Limpar Range", on_click=limpar_range)

threshold_min = st.session_state.min_prob
threshold_max = st.session_state.max_prob

# TIMES (lista completa)
todos_times = sorted(set(df['Time Casa']).union(set(df['Time Visitante'])))
times_sidebar = st.sidebar.multiselect("Times", options=todos_times)

# LIGAS (lista completa)
if 'Liga' in df.columns:
    todas_ligas = sorted(df['Liga'].dropna().unique())
    ligas_sidebar = st.sidebar.multiselect("Ligas", options=todas_ligas)
else:
    ligas_sidebar = []

# =========================
# FILTRO BASE
# =========================

df_filtrado = df[
    (df['Probabilidade'] >= (threshold_min / 100)) &
    (df['Probabilidade'] <= (threshold_max / 100))
]

# filtro times
if times_sidebar:
    df_filtrado = df_filtrado[
        df_filtrado['Time Casa'].isin(times_sidebar) |
        df_filtrado['Time Visitante'].isin(times_sidebar)
    ]

# filtro ligas
if ligas_sidebar:
    df_filtrado = df_filtrado[
        df_filtrado['Liga'].isin(ligas_sidebar)
    ]

# =========================
# SEPARAÇÃO
# =========================

df_passado = df_filtrado[df_filtrado['Placar'] != "🔮"]
df_futuro = df_filtrado[df_filtrado['Placar'] == "🔮"]

# =========================
# FILTRO TABELA
# =========================

st.subheader("🔎 Filtros da tabela")

c1, c2, c3, c4 = st.columns([1,1,1,1])

busca_casa = c1.text_input("Time Casa", key="busca_casa")
busca_visit = c2.text_input("Time Visitante", key="busca_visit")
busca_data = c3.text_input("Data", key="busca_data")

c4.button("🔄 Limpar", on_click=limpar_filtros_tabela)

def aplicar_filtros(df):
    result = df.copy()

    if busca_casa:
        result = result[
            result['Time Casa'].str.contains(busca_casa, case=False, na=False)
        ]

    if busca_visit:
        result = result[
            result['Time Visitante'].str.contains(busca_visit, case=False, na=False)
        ]

    if busca_data:
        result = result[
            result['Data_str'].str.contains(busca_data, na=False)
        ]

    return result

df_passado = aplicar_filtros(df_passado)
df_futuro = aplicar_filtros(df_futuro)

# =========================
# ERROS
# =========================

df_erros = df_passado[df_passado['Placar'] == "0 x 1"]

total = len(df_passado)
erros = len(df_erros)
acertos = total - erros

taxa = (acertos / total * 100) if total > 0 else 0

# =========================
# MÉTRICAS
# =========================

st.subheader("📊 Resumo")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Jogos", total)
c2.metric("Acertos", acertos)
c3.metric("Erros (0x1)", erros)
c4.metric("Taxa", f"{taxa:.2f}%")

# =========================
# TABELAS
# =========================

colunas = ['Data_str','Time Casa','Time Visitante','Placar','Probabilidade (%)']

st.subheader("📊 Jogos Finalizados")
st.dataframe(df_passado[colunas], width='stretch')

st.subheader("🔮 Jogos Futuros")
st.dataframe(df_futuro[colunas], width='stretch')

# =========================
# ERROS
# =========================

st.subheader("❌ Jogos 0 x 1")

if len(df_erros) > 0:
    st.dataframe(df_erros[colunas], width='stretch')
else:
    st.info("Nenhum 0x1 nesse filtro")

st.write(f"Total 0x1: {len(df_erros)}")