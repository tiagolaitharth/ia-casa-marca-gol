# =========================
# IMPORTAÇÕES
# =========================

import streamlit as st
import pandas as pd
import os
import re
import uuid

from datetime import datetime
from collections import Counter


# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================

st.set_page_config(
    layout="wide",
    page_title="IA - Análise Completa"
)

st.title("📊 IA - Análise Completa")


# =========================
# LOGIN
# =========================

# =========================
# USUÁRIO LOCAL TESTE
# =========================

usuarios = {
    "tiago": {
        "senha": "123",
        "expira": "2099-12-31"
    }
}

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:

    st.subheader("🔐 Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        if usuario in usuarios:

            dados_usuario = usuarios[usuario]

            senha_correta = dados_usuario["senha"]

            data_expiracao = datetime.strptime(
                dados_usuario["expira"],
                "%Y-%m-%d"
            ).date()

            hoje = datetime.today().date()

            if senha == senha_correta:

                if hoje <= data_expiracao:

                    st.session_state.logado = True
                    st.session_state.usuario = usuario

                    st.rerun()

                else:
                    st.error("Acesso expirado")

            else:
                st.error("Senha incorreta")

        else:
            st.error("Usuário não encontrado")

    st.stop()


# =========================
# VERIFICAÇÃO DO ARQUIVO
# =========================

if not os.path.exists("resultado_modelo.xlsx"):

    st.error(
        "Arquivo resultado_modelo.xlsx não encontrado"
    )

    st.stop()


# =========================
# LEITURA DA BASE
# =========================

df = pd.read_excel("resultado_modelo.xlsx")


# =========================
# TRATAMENTO DOS DADOS
# =========================

df['Data'] = pd.to_datetime(df['Data'])

df['Data_str'] = (
    df['Data']
    .dt.strftime('%d/%m/%Y')
)

df['Hora'] = (
    df['Hora']
    .astype(str)
    .str.slice(0, 5)
)

df['Placar'] = (
    df['Placar']
    .astype(str)
    .str.strip()
)

df['Placar'] = (
    df['Placar']
    .replace("-", "🔮")
)

df['Probabilidade (%)'] = (
    df['Probabilidade'] * 100
).round(2)


# =========================
# FUNÇÕES GERAIS
# =========================

def normalizar_placar(placar):

    placar = str(placar).strip().lower()

    if not placar:
        return None

    m = re.match(
        r"^\s*(\d+)\D+(\d+)\s*$",
        placar
    )

    if not m:
        return None

    a, b = m.groups()

    return f"{int(a)} x {int(b)}"


def resultado_flag(placar):

    if placar == "🔮":
        return "🔮"

    try:

        gols = int(
            placar.split('x')[0].strip()
        )

        return "🟢 V" if gols > 0 else "🔴 X"

    except:
        return ""


df['Resultado'] = (
    df['Placar']
    .apply(resultado_flag)
)

# =========================
# DETECÇÃO MOBILE
# =========================

mobile_css = """
<style>

/* =========================
MOBILE
========================= */

@media (max-width: 768px) {

    .mobile-card {

        background-color: #111111;

        padding: 18px;

        border-radius: 14px;

        margin-bottom: 18px;

        border: 1px solid #333333;
    }

    .mobile-title {

        font-size: 18px;

        font-weight: bold;

        margin-bottom: 8px;
    }

    .mobile-prob {

        font-size: 16px;

        color: #00ff88;

        margin-bottom: 12px;
    }

    .stButton > button {

        width: 100%;

        border-radius: 10px;

        height: 48px;

        font-size: 16px;
    }
}


/* =========================
DESKTOP
========================= */

.desktop-card {

    background-color: #111111;

    padding: 18px;

    border-radius: 14px;

    margin-bottom: 18px;

    border: 1px solid #333333;
}

.desktop-title {

    font-size: 22px;

    font-weight: bold;

    margin-bottom: 10px;
}

.desktop-prob {

    font-size: 18px;

    color: #00ff88;

    margin-bottom: 14px;
}

</style>
"""

st.markdown(
    mobile_css,
    unsafe_allow_html=True
)

# =========================
# JOGOS FUTUROS
# =========================

df_jogos = df[
    df['Placar'] == "🔮"
].copy()


# =========================
# ORDENA POR PROBABILIDADE
# =========================

df_jogos = df_jogos.sort_values(
    by='Probabilidade (%)',
    ascending=False
)


# =========================
# TÍTULO
# =========================

st.subheader("📅 Jogos do Dia")


# =========================
# LOOP DOS JOGOS
# =========================

for index, row in df_jogos.iterrows():
    liga = row['Liga']

    casa = row['Time Casa']

    fora = row['Time Visitante']

    prob = row['Probabilidade (%)']

    hora = row['Hora']

    jogo_id = str(uuid.uuid4())


    # =========================
    # LINHA RESPONSIVA
    # =========================

    st.markdown(
        f"""
        <div style="
            padding:10px;
            border-bottom:1px solid #222;
            margin-bottom:6px;
        ">

        <div style="
            font-size:16px;
            font-weight:bold;
            margin-bottom:4px;
        ">
            ⚽ {casa} x {fora}
        </div>

        <div style="
            font-size:13px;
            color:#AAAAAA;
            margin-bottom:8px;
        ">
            🏆 {liga} |
            🕒 {hora} |
            📊 {prob:.2f}%
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    analisar = st.button(
        "🔍 Análise Completa",
        key=jogo_id,
        use_container_width=True
    )


    if analisar:

        st.markdown("---")

        st.subheader(
            f"🔍 {casa} x {fora}"
        )

        st.write(
            f"📊 Probabilidade do modelo: {prob:.2f}%"
        )
    

    
    # =========================
# GRID DE CARDS
# =========================

if "contador_coluna" not in st.session_state:
    st.session_state.contador_coluna = 0

if st.session_state.contador_coluna == 0:
    cols = st.columns(3)

coluna_atual = cols[
    st.session_state.contador_coluna
]

st.session_state.contador_coluna += 1

if st.session_state.contador_coluna > 2:
    st.session_state.contador_coluna = 0