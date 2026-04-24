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
# TRATAMENTO DE DATA
# =========================

df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
df['Data_str'] = df['Data'].dt.strftime('%d/%m/%Y')

# =========================
# TRATAMENTO GERAL
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
# FILTRO PRINCIPAL
# =========================

colunas = ['Liga','Data_str','Time Casa','Time Visitante','Placar','Resultado','Probabilidade (%)']

st.subheader("📅 Jogos de Hoje")

df_hoje = df[df['Data_str'] == hoje_str]
df_hoje_futuro = df_hoje[df_hoje['Placar'] == "🔮"]

if len(df_hoje_futuro) > 0:
    st.dataframe(
        df_hoje_futuro[colunas].sort_values(by='Probabilidade (%)', ascending=False),
        use_container_width=True
    )
else:
    st.warning(f"Nenhum jogo encontrado para hoje ({hoje_str})")