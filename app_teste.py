# =========================
# IMPORTAÇÕES
# =========================

import streamlit as st
from streamlit_js_eval import streamlit_js_eval
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
# ABAS PRINCIPAIS
# =========================

tab1, tab2, tab3, tab4 = st.tabs([
    "⚽ Jogos do Dia",
    "🧠 Análise Manual",
    "⚽ Placares Processados",
    "🏆 Ligas"
])


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
# DETECÇÃO REAL MOBILE
# =========================

largura_tela = streamlit_js_eval(
    js_expressions='window.innerWidth',
    key='LARGURA'
)

mobile = False

if largura_tela:

    mobile = largura_tela < 768


with tab1:

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


with tab2:

    st.subheader("🧠 Central Estatística")

        # =========================
    # FILTROS
    # =========================

    f1, f2, f3, f4 = st.columns(4)

    with f1:

        filtro_casa = st.text_input(
            "🏠 Time Casa"
        )

    with f2:

        filtro_fora = st.text_input(
            "✈️ Time Fora"
        )

    with f3:

        data_inicio = st.date_input(
            "📅 Data Inicial",
            value=df['Data'].min()
        )

    with f4:

        data_final = st.date_input(
            "📅 Data Final",
            value=df['Data'].max()
        )
    



    col1, col2 = st.columns(2)

    with col1:

        min_range = st.number_input(
            "Range mínimo (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1
        )

    with col2:

        max_range = st.number_input(
            "Range máximo (%)",
            min_value=0.0,
            max_value=100.0,
            value=100.0,
            step=0.1
        )

        # =========================
    # FILTRO
    # =========================

    df_lab = df[
        (df['Probabilidade (%)'] >= min_range) &
        (df['Probabilidade (%)'] <= max_range)
    ].copy()

    # =========================
    # FILTRO TIME CASA
    # =========================

    if filtro_casa:

        df_lab = df_lab[

            df_lab['Time Casa']
            .astype(str)
            .str.contains(
                filtro_casa,
                case=False,
                na=False
            )
        ]

    # =========================
    # FILTRO TIME FORA
    # =========================

    if filtro_fora:

        df_lab = df_lab[

            df_lab['Time Visitante']
            .astype(str)
            .str.contains(
                filtro_fora,
                case=False,
                na=False
            )
        ]

    # =========================
    # FILTRO DATA
    # =========================

    df_lab = df_lab[

        (df_lab['Data'].dt.date >= data_inicio) &

        (df_lab['Data'].dt.date <= data_final)
    ]

    # =========================
    # JOGOS FINALIZADOS
    # =========================

    df_finalizados = df_lab[
        df_lab['Placar'] != "🔮"
    ]

    total = len(df_finalizados)

    total_0x1 = len(
        df_finalizados[
            df_finalizados['Placar'] == "0 x 1"
        ]
    )

    taxa_0x1 = (
        total_0x1 / total * 100
    ) if total > 0 else 0
    # =========================
    # MÉTRICAS
    # =========================

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Jogos", total)

    with c2:
        st.metric("0x1", total_0x1)

    with c3:
        st.metric(
            "Taxa 0x1",
            f"{taxa_0x1:.2f}%"
        )

    # =========================
    # PROCESSAR PLACARES
    # =========================

    if st.button("⚽ Processar Placares"):

        placares_processados = (
            df_finalizados['Placar']
            .dropna()
            .tolist()
        )

        st.session_state[
            "placares_processados"
        ] = placares_processados

        st.success("Placares processados")


    if mobile:

        st.dataframe(

            df_lab[[
                'Time Casa',
                'Time Visitante',
                'Probabilidade (%)',
                'Placar'
            ]],

            hide_index=True,
            use_container_width=True
        )

    else:

        st.dataframe(

            df_lab[[
                'Liga',
                'Data_str',
                'Hora',
                'Time Casa',
                'Time Visitante',
                'Placar',
                'Probabilidade (%)'
            ]],

            hide_index=True,
            use_container_width=True
        )


# =========================
# ABA PLACARES PROCESSADOS
# =========================

with tab3:

    st.subheader("⚽ Placares Processados")

    if "placares_processados" not in st.session_state:

        st.info("Nenhum placar processado ainda")

    else:

        lista_placares = (
            st.session_state["placares_processados"]
        )

        placares_validos = []

        for placar in lista_placares:

            try:

                gols_casa = int(
                    placar.split("x")[0].strip()
                )

                gols_fora = int(
                    placar.split("x")[1].strip()
                )

                placares_validos.append(
                    (placar, gols_casa, gols_fora)
                )

            except:
                pass

        # =========================
        # SEPARAÇÃO
        # =========================

        casa = []
        empate = []
        fora = []

        for placar, gc, gf in placares_validos:

            if gc > gf:

                casa.append(placar)

            elif gc == gf:

                empate.append(placar)

            else:

                fora.append(placar)

        # =========================
        # CONTADORES
        # =========================

        total = len(placares_validos)

        total_casa = len(casa)

        total_empate = len(empate)

        total_fora = len(fora)

        pct_casa = (
            total_casa / total * 100
        ) if total > 0 else 0

        pct_empate = (
            total_empate / total * 100
        ) if total > 0 else 0

        pct_fora = (
            total_fora / total * 100
        ) if total > 0 else 0

        # =========================
        # CONTAGEM
        # =========================

        casa_count = Counter(casa)

        empate_count = Counter(empate)

        fora_count = Counter(fora)

        casa_ordenado = sorted(
            casa_count.items(),
            key=lambda x: x[1],
            reverse=True
        )

        empate_ordenado = sorted(
            empate_count.items(),
            key=lambda x: x[1],
            reverse=True
        )

        fora_ordenado = sorted(
            fora_count.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # =========================
        # MÉTRICAS VISUAIS
        # =========================

        c1, c2, c3 = st.columns(3)

        with c1:

            st.success(
                f"""
🏠 CASA

{total_casa} jogos

{pct_casa:.2f}%
"""
            )

        with c2:

            st.info(
                f"""
🤝 EMPATE

{total_empate} jogos

{pct_empate:.2f}%
"""
            )

        with c3:

            st.error(
                f"""
✈️ FORA

{total_fora} jogos

{pct_fora:.2f}%
"""
            )

        # =========================
        # COLUNAS
        # =========================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown("## 🏠 Casa")

            for placar, qtd in casa_ordenado:

                pct = (
                    qtd / total_casa * 100
                ) if total_casa > 0 else 0

                st.write(
                    f"🏠 {placar} → {qtd} ({pct:.2f}%)"
                )

        with col2:

            st.markdown("## 🤝 Empate")

            for placar, qtd in empate_ordenado:

                pct = (
                    qtd / total_empate * 100
                ) if total_empate > 0 else 0

                st.write(
                    f"🤝 {placar} → {qtd} ({pct:.2f}%)"
                )

        with col3:

            st.markdown("## ✈️ Fora")

            for placar, qtd in fora_ordenado:

                pct = (
                    qtd / total_fora * 100
                ) if total_fora > 0 else 0

                st.write(
                    f"✈️ {placar} → {qtd} ({pct:.2f}%)"
                )


# =========================
# ABA LIGAS
# =========================

with tab4:

    st.subheader("🏆 Análise por Liga")

    # =========================
    # SOMENTE FINALIZADOS
    # =========================

    df_ligas = df[
        df['Placar'] != "🔮"
    ].copy()

    # =========================
    # AGRUPAMENTO
    # =========================

    dados_ligas = []

    ligas = sorted(
        df_ligas['Liga'].dropna().unique()
    )

    for liga in ligas:

        df_liga = df_ligas[
            df_ligas['Liga'] == liga
        ]

        total_jogos = len(df_liga)

        total_0x1 = len(
            df_liga[
                df_liga['Placar'] == "0 x 1"
            ]
        )

        pct_0x1 = (
            total_0x1 / total_jogos * 100
        ) if total_jogos > 0 else 0

        dados_ligas.append({

            "Liga": liga,

            "Jogos": total_jogos,

            "0x1": total_0x1,

            "% 0x1": round(pct_0x1, 2)

        })

    # =========================
    # DATAFRAME
    # =========================

    df_ligas_final = pd.DataFrame(
        dados_ligas
    )

    df_ligas_final = df_ligas_final.sort_values(
        by="% 0x1",
        ascending=True
    ).reset_index(drop=True)

    df_ligas_final.index += 1

    st.dataframe(

        df_ligas_final,

        use_container_width=True
    )