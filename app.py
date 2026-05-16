import streamlit as st
import pandas as pd
import os
import uuid
import re

from datetime import datetime
from collections import Counter
usuarios = st.secrets["usuarios"]

# =========================
# CONFIG
# =========================

st.set_page_config(
    layout="wide",
    page_title="IA - Análise Completa"
)

st.title("📊 IA - Análise Completa")

# =========================
# LOGIN
# =========================

if "logado" not in st.session_state:

    st.session_state.logado = False

if not st.session_state.logado:

    st.subheader("🔐 Login")

    usuario = st.text_input(
        "Usuário",
        key="login_usuario"
    )

    senha = st.text_input(
        "Senha",
        type="password",
        key="login_senha"
    )

    if st.button(
        "Entrar",
        key="login_btn"
    ):

        if usuario in usuarios:

            dados_usuario = usuarios[
                usuario
            ]

            senha_correta = (
                dados_usuario["senha"]
            )

            data_expiracao = datetime.strptime(

                dados_usuario["expira"],

                "%Y-%m-%d"

            ).date()

            hoje = (
                datetime.today().date()
            )

            if senha == senha_correta:

                if hoje <= data_expiracao:

                    st.session_state.logado = True

                    st.session_state.usuario = usuario

                    st.rerun()

                else:

                    st.error(
                        "Acesso expirado"
                    )

            else:

                st.error(
                    "Senha incorreta"
                )

        else:

            st.error(
                "Usuário não encontrado"
            )

    st.stop()

# =========================
# VERIFICAÇÃO
# =========================

if not os.path.exists(
    "resultado_modelo.xlsx"
):

    st.error(
        "Arquivo resultado_modelo.xlsx não encontrado"
    )

    st.stop()

# =========================
# LEITURA
# =========================

df = pd.read_excel(
    "resultado_modelo.xlsx"
)


# =========================
# DATA
# =========================

df['Data'] = pd.to_datetime(

    df['Data'],

    dayfirst=True,

    errors='coerce'
)

df['Data_str'] = (

    df['Data']
    .dt.strftime('%d/%m/%Y')
)

# =========================
# HORA
# =========================

df['Hora'] = (

    df['Hora']
    .astype(str)
    .str.slice(0, 5)
)

# =========================
# PLACAR
# =========================

df['Placar'] = (

    df['Placar']
    .astype(str)
    .str.strip()
)

df['Placar'] = (

    df['Placar']
    .replace("-", "🔮")
)

# =========================
# PROBABILIDADE
# =========================

df['Probabilidade (%)'] = (

    df['Probabilidade']
    .astype(float)
    * 100

).round(2)

# =========================
# NORMALIZAR
# =========================

def normalizar_placar(placar):

    placar = (
        str(placar)
        .strip()
        .lower()
    )

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

# =========================
# RESULTADO
# =========================

def resultado_flag(placar):

    if placar == "🔮":

        return "🔮"

    try:

        gols = int(

            placar
            .split('x')[0]
            .strip()
        )

        return (
            "🟢 V"
            if gols > 0
            else "🔴 X"
        )

    except:

        return ""

df['Resultado'] = (

    df['Placar']
    .apply(resultado_flag)
)

# =========================
# ABAS
# =========================

tab1, tab2, tab3, tab4 = st.tabs([

    "⚽ Jogos do Dia",

    "🧠 Análise Manual",

    "⚽ Placares Processados",

    "🏆 Ligas"
])

with tab1:

    st.subheader("📅 Jogos do Dia")

    if "analise_jogo" not in st.session_state:

        st.session_state.analise_jogo = None

    busca_time = st.text_input(
        "🔎 Buscar Time",
        key="tab1_busca"
    )

    filtro_oportunidade = st.selectbox(

        "🎯 Filtrar Oportunidades",

        [

            "Todos",

            "🔥 ELITE 0x1",
            "🔥 ELITE 1x0",

            "🚀 TOP 0x1",
            "🚀 TOP 1x0",

            "✅ BOM 0x1",
            "✅ BOM 1x0",

            "⚠️ MÉDIO 0x1",
            "⚠️ MÉDIO 1x0"
        ],

        key="tab1_filtro"
    )

    df_jogos = df[
        df['Placar'] == "🔮"
    ].copy()

    if busca_time:

        df_jogos = df_jogos[

            df_jogos['Time Casa']
            .astype(str)
            .str.lower()
            .str.contains(
                busca_time.lower(),
                na=False
            )

            |

            df_jogos['Time Visitante']
            .astype(str)
            .str.lower()
            .str.contains(
                busca_time.lower(),
                na=False
            )
        ]

    df_jogos = df_jogos.sort_values(

        by='Probabilidade (%)',

        ascending=False
    )

    for _, row in df_jogos.iterrows():

        liga = row['Liga']

        casa = row['Time Casa']

        fora = row['Time Visitante']

        prob = row['Probabilidade (%)']

        hora = row['Hora']

        jogo_id = f"{casa}_{fora}"

        min_range = int(prob)

        max_range = 100

        df_range = df[

            (df['Probabilidade (%)'] >= min_range) &

            (df['Probabilidade (%)'] <= max_range) &

            (df['Placar'] != "🔮")

        ].copy()

        total_jogos = len(df_range)

        total_0x1 = len(

            df_range[
                df_range['Placar'] == "0 x 1"
            ]
        )

        total_1x0 = len(

            df_range[
                df_range['Placar'] == "1 x 0"
            ]
        )

        pct_0x1 = (

            total_0x1 / total_jogos * 100

        ) if total_jogos > 0 else 0

        pct_1x0 = (

            total_1x0 / total_jogos * 100

        ) if total_jogos > 0 else 0

        lay_0x1 = 100 - pct_0x1

        lay_1x0 = 100 - pct_1x0

        status_0x1 = ""

        status_1x0 = ""

        # =========================
        # ELITE GLOBAL
        # =========================

        if lay_0x1 >= 99:

            status_0x1 = "🔥 ELITE 0x1"

        if lay_1x0 >= 99:

            status_1x0 = "🔥 ELITE 1x0"

        # =========================
        # FAIXA 93-100
        # =========================

        if prob >= 93:

            if not status_0x1:

                if lay_0x1 >= 96:

                    status_0x1 = "🚀 TOP 0x1"

                elif lay_0x1 >= 91:

                    status_0x1 = "✅ BOM 0x1"

            if not status_1x0:

                if lay_1x0 >= 96:

                    status_1x0 = "🚀 TOP 1x0"

                elif lay_1x0 >= 91:

                    status_1x0 = "✅ BOM 1x0"

        # =========================
        # FAIXA 90-92.99
        # =========================

        elif prob >= 90:

            if not status_0x1:

                if lay_0x1 >= 98:

                    status_0x1 = "🚀 TOP 0x1"

                elif lay_0x1 >= 95:

                    status_0x1 = "✅ BOM 0x1"

                elif lay_0x1 >= 91:

                    status_0x1 = "⚠️ MÉDIO 0x1"

            if not status_1x0:

                if lay_1x0 >= 98:

                    status_1x0 = "🚀 TOP 1x0"

                elif lay_1x0 >= 95:

                    status_1x0 = "✅ BOM 1x0"

                elif lay_1x0 >= 91:

                    status_1x0 = "⚠️ MÉDIO 1x0"

        # =========================
        # FILTRO
        # =========================

        mostrar = False

        if filtro_oportunidade == "Todos":

            mostrar = True

        elif filtro_oportunidade == status_0x1:

            mostrar = True

        elif filtro_oportunidade == status_1x0:

            mostrar = True

        if not mostrar:

            continue

        # =========================
        # CARD
        # =========================

        with st.container(border=True):

            st.markdown(
                f"### ⚽ {casa} x {fora}"
            )

            st.write(
                f"🏆 {liga}"
            )

            st.write(
                f"🕒 {hora}"
            )

            st.write(
                f"📊 {prob:.2f}%"
            )

            if status_0x1:

                st.success(status_0x1)

            if status_1x0:

                st.success(status_1x0)

            if st.button(

                "🔍 Análise Completa",

                key=jogo_id
            ):

                st.session_state.analise_jogo = jogo_id

            if st.session_state.analise_jogo == jogo_id:

                st.divider()

                st.subheader(
                    "📊 Análise Completa"
                )

                if st.button(

                    "❌ Fechar Análise",

                    key=f"fechar_{jogo_id}"
                ):

                    st.session_state.analise_jogo = None

                    st.rerun()

                st.write(
                    f"📚 {total_jogos} jogos analisados"
                )

                st.write(
                    f"0x1 → {total_0x1} vezes ({pct_0x1:.2f}%)"
                )

                st.write(
                    f"1x0 → {total_1x0} vezes ({pct_1x0:.2f}%)"
                )

                        # =========================
                # PREVISÃO
                # =========================

                def extrair_gols(
                    lista,
                    lado
                ):

                    gols = []

                    for linha in lista:

                        p = normalizar_placar(
                            linha
                        )

                        if p:

                            a, b = map(

                                int,

                                p.split(" x ")
                            )

                            if lado == "casa":

                                gols.append(a)

                            else:

                                gols.append(b)

                    return gols

                lista_casa = df[

                    (df['Time Casa'] == casa) &

                    (df['Placar'] != "🔮")

                ]['Placar'].tolist()

                lista_fora = df[

                    (df['Time Visitante'] == fora) &

                    (df['Placar'] != "🔮")

                ]['Placar'].tolist()

                gols_casa = extrair_gols(
                    lista_casa,
                    "casa"
                )

                gols_fora = extrair_gols(
                    lista_fora,
                    "fora"
                )

                if gols_casa and gols_fora:

                    freq_casa = Counter(
                        gols_casa
                    )

                    freq_fora = Counter(
                        gols_fora
                    )

                    total_casa = sum(
                        freq_casa.values()
                    )

                    total_fora = sum(
                        freq_fora.values()
                    )

                    prob_casa = {

                        g: freq_casa[g] / total_casa

                        for g in freq_casa
                    }

                    prob_fora = {

                        g: freq_fora[g] / total_fora

                        for g in freq_fora
                    }

                    resultados = []

                    for g1 in prob_casa:

                        for g2 in prob_fora:

                            probabilidade = (

                                prob_casa[g1] *

                                prob_fora[g2]
                            )

                            resultados.append(

                                (
                                    f"{g1} x {g2}",
                                    probabilidade
                                )
                            )

                    resultados = sorted(

                        resultados,

                        key=lambda x: x[1],

                        reverse=True
                    )

                    st.markdown(
                        "### ⚽ Previsão de Placares"
                    )

                    for placar, probabilidade in resultados[:10]:

                        st.write(
                            f"{placar} → {probabilidade*100:.2f}%"
                        )

                    st.warning(

                        "⚠️ Esses placares não são garantias de lucro. A previsão representa apenas tendências estatísticas do confronto."
                    )

with tab2:

    st.subheader("🧠 Análise Manual")

    # =========================
    # FILTROS
    # =========================

    c1, c2 = st.columns(2)

    with c1:

        filtro_casa = st.text_input(
            "🏠 Time Casa",
            key="manual_casa"
        )

    with c2:

        filtro_fora = st.text_input(
            "✈️ Time Fora",
            key="manual_fora"
        )

    # =========================
    # DATAS
    # =========================

    d1, d2 = st.columns(2)

    with d1:

        data_inicio = st.date_input(
            "📅 Data Inicial",
            value=df['Data'].min().date(),
            format="DD/MM/YYYY",
            key="manual_data_inicio"
        )

    with d2:

        data_final = st.date_input(
            "📅 Data Final",
            value=df['Data'].max().date(),
            format="DD/MM/YYYY",
            key="manual_data_final"
        )

    # =========================
    # RANGE
    # =========================

    r1, r2 = st.columns(2)

    with r1:

        min_range = st.number_input(
            "Range mínimo (%)",
            min_value=0,
            max_value=100,
            value=0,
            key="manual_min"
        )

    with r2:

        max_range = st.number_input(
            "Range máximo (%)",
            min_value=0,
            max_value=100,
            value=100,
            key="manual_max"
        )

    # =========================
    # BOTÕES
    # =========================

    b1, b2 = st.columns(2)

    with b1:

        aplicar = st.button(
            "🔍 Aplicar Filtros",
            use_container_width=True,
            key="manual_aplicar"
        )

    with b2:

        limpar = st.button(
            "🧹 Limpar Filtros",
            use_container_width=True,
            key="manual_limpar"
        )
    
    if limpar:

        del st.session_state["manual_min"]

        del st.session_state["manual_max"]

        st.rerun()

    # =========================
    # BASE
    # =========================

    df_manual = df.copy()

    # RANGE

    df_manual = df_manual[

        (df_manual['Probabilidade (%)'] >= min_range) &

        (df_manual['Probabilidade (%)'] <= max_range)
    ]

    # CASA

    if filtro_casa:

        df_manual = df_manual[

            df_manual['Time Casa']
            .astype(str)
            .str.lower()
            .str.contains(
                filtro_casa.lower(),
                na=False
            )
        ]

    # FORA

    if filtro_fora:

        df_manual = df_manual[

            df_manual['Time Visitante']
            .astype(str)
            .str.lower()
            .str.contains(
                filtro_fora.lower(),
                na=False
            )
        ]

    # DATAS

    df_manual = df_manual[

        (df_manual['Data'].dt.date >= data_inicio) &

        (df_manual['Data'].dt.date <= data_final)
    ]

    # =========================
    # MÉTRICAS
    # =========================

    total = len(df_manual)

    total_0x1 = len(

        df_manual[
            df_manual['Placar'] == "0 x 1"
        ]
    )

    total_1x0 = len(

        df_manual[
            df_manual['Placar'] == "1 x 0"
        ]
    )

    pct_0x1 = (

        total_0x1 / total * 100

    ) if total > 0 else 0

    pct_1x0 = (

        total_1x0 / total * 100

    ) if total > 0 else 0

    m1, m2, m3 = st.columns(3)

    with m1:

        st.metric(
        "Jogos",
        total
    )

    with m2:

        st.metric(
        "0x1",
        total_0x1
    )

    with m3:

        st.metric(
        "Taxa 0x1",
        f"{pct_0x1:.2f}%"
    )

    # =========================
    # PROCESSAR PLACARES
    # =========================

    if st.button(

        "⚽ Processar Placares",

        use_container_width=True,

        key="manual_processar"
    ):

        placares_processados = [

            normalizar_placar(p)

            for p in df_manual['Placar']
            .dropna()
            .tolist()

            if normalizar_placar(p)
        ]

        st.session_state[
            "placares_processados"
        ] = placares_processados

        st.success(
            "Placares processados"
        )

    # =========================
    # TABELA
    # =========================

    st.dataframe(

        df_manual[[

            'Liga',
            'Data_str',
            'Hora',
            'Time Casa',
            'Time Visitante',
            'Probabilidade (%)',
            'Placar'
        ]],

        use_container_width=True,
        hide_index=True
    )

with tab3:

    st.subheader("⚽ Placares Processados")

    if "placares_processados" not in st.session_state:

        st.info(
            "Nenhum placar processado"
        )

    else:

        lista_placares = (

            st.session_state[
                "placares_processados"
            ]
        )

        # =========================
        # NORMALIZA
        # =========================

        placares_validos = [

            normalizar_placar(p)

            for p in lista_placares

            if normalizar_placar(p)
        ]

        # =========================
        # SEPARAÇÃO
        # =========================

        casa = []
        empate = []
        fora = []

        for placar in placares_validos:

            try:

                gols_casa = int(

                    placar
                    .split("x")[0]
                    .strip()
                )

                gols_fora = int(

                    placar
                    .split("x")[1]
                    .strip()
                )

                if gols_casa > gols_fora:

                    casa.append(
                        placar
                    )

                elif gols_casa == gols_fora:

                    empate.append(
                        placar
                    )

                else:

                    fora.append(
                        placar
                    )

            except:
                pass

        # =========================
        # CONTAGEM
        # =========================

        total = len(
            placares_validos
        )

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
        # MÉTRICAS
        # =========================

        m1, m2, m3 = st.columns(3)

        with m1:

            st.success(

                f"""
🏠 CASA

{total_casa} jogos

{pct_casa:.2f}%
"""
            )

        with m2:

            st.info(

                f"""
🤝 EMPATE

{total_empate} jogos

{pct_empate:.2f}%
"""
            )

        with m3:

            st.error(

                f"""
✈️ FORA

{total_fora} jogos

{pct_fora:.2f}%
"""
            )

        # =========================
        # COUNTER
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
        # TABELAS
        # =========================

        c1, c2, c3 = st.columns(3)

        with c1:

            st.markdown(
                "## 🏠 Casa"
            )

            for placar, qtd in casa_ordenado:

                pct = (

                    qtd / total_casa * 100

                ) if total_casa > 0 else 0

                st.write(
                    f"{placar} → "
                    f"{qtd} "
                    f"({pct:.2f}%)"
                )

        with c2:

            st.markdown(
                "## 🤝 Empate"
            )

            for placar, qtd in empate_ordenado:

                pct = (

                    qtd / total_empate * 100

                ) if total_empate > 0 else 0

                st.write(
                    f"{placar} → "
                    f"{qtd} "
                    f"({pct:.2f}%)"
                )

        with c3:

            st.markdown(
                "## ✈️ Fora"
            )

            for placar, qtd in fora_ordenado:

                pct = (

                    qtd / total_fora * 100

                ) if total_fora > 0 else 0

                st.write(
                    f"{placar} → "
                    f"{qtd} "
                    f"({pct:.2f}%)"
                )

    # =========================
    # PREVISÃO MANUAL
    # =========================

    st.divider()

    st.header("📊 Previsão Manual")

    lista_casa = st.text_area(
        "Lista CASA:",
        height=150,
        key="placar_lista_casa"
    )

    lista_fora = st.text_area(
        "Lista FORA:",
        height=150,
        key="placar_lista_fora"
    )

    gerar = st.button(
        "Gerar previsão",
        key="placar_previsao"
    )

    if gerar:

        def extrair_gols(lista):

            gols = []

            for linha in lista.splitlines():

                p = normalizar_placar(linha)

                if p:

                    a, b = map(int, p.split(" x "))

                    gols.append(a)

            return gols

        gols_casa = extrair_gols(lista_casa)
        gols_fora = extrair_gols(lista_fora)

        if not gols_casa or not gols_fora:

            st.warning(
                "Preencha as duas listas corretamente."
            )

        else:

            freq_casa = Counter(gols_casa)
            freq_fora = Counter(gols_fora)

            total_casa = sum(freq_casa.values())
            total_fora = sum(freq_fora.values())

            prob_casa = {
                g: freq_casa[g] / total_casa
                for g in freq_casa
            }

            prob_fora = {
                g: freq_fora[g] / total_fora
                for g in freq_fora
            }

            resultados = []

            for g1 in prob_casa:

                for g2 in prob_fora:

                    prob = prob_casa[g1] * prob_fora[g2]

                    resultados.append(
                        (f"{g1} x {g2}", prob)
                    )

            resultados = sorted(

                resultados,

                key=lambda x: x[1],

                reverse=True
            )

            st.subheader(
                "📊 Top placares previstos"
            )

            for placar, prob in resultados[:15]:

                st.write(
                    f"{placar} → {prob*100:.2f}%"
                )

            st.warning(
                "⚠️ Esses placares não são garantias de lucro. A previsão representa apenas tendências estatísticas do confronto."
            )

with tab4:

    st.subheader("🏆 Ligas")

    df_ligas = df[
        df['Placar'] != "🔮"
    ].copy()

    resumo = []

    ligas = sorted(
        df_ligas['Liga']
        .dropna()
        .unique()
    )

    for liga in ligas:

        df_liga = df_ligas[
            df_ligas['Liga'] == liga
        ]

        total = len(df_liga)

        total_0x1 = len(

            df_liga[
                df_liga['Placar'] == "0 x 1"
            ]
        )

        pct_0x1 = (

            total_0x1 / total * 100

        ) if total > 0 else 0

        resumo.append({

            "Liga": liga,

            "Jogos": total,

            "0x1": total_0x1,

            "% 0x1": round(
                pct_0x1,
                2
            )
        })

    df_resumo = pd.DataFrame(
        resumo
    )

    df_resumo = df_resumo.sort_values(
        by="% 0x1",
        ascending=True
    )

    st.dataframe(

        df_resumo,

        use_container_width=True,
        hide_index=True
    )

    st.divider()

    liga_escolhida = st.selectbox(

        "Selecionar Liga",

        ligas,

        key="liga_select"
    )

    df_liga = df_ligas[

        df_ligas['Liga'] == liga_escolhida
    ]

    st.subheader(
        f"📊 Jogos da Liga: {liga_escolhida}"
    )

    st.dataframe(

        df_liga[[

            'Data_str',
            'Hora',
            'Time Casa',
            'Time Visitante',
            'Placar',
            'Probabilidade (%)'
        ]],

        use_container_width=True,
        hide_index=True
    )

    # =========================
    # PROCESSAR PLACARES
    # =========================

    if st.button(

        "⚽ Processar Placares da Liga",

        key="liga_processar"
    ):

        placares_processados = [

            normalizar_placar(p)

            for p in df_liga['Placar']
            .dropna()
            .tolist()

            if normalizar_placar(p)
        ]

        st.session_state[
            "placares_processados"
        ] = placares_processados

        st.success(
            "Placares processados"
        )

    # =========================
    # ESTATÍSTICAS DOS TIMES
    # =========================

    vitorias_casa = {}
    derrotas_casa = {}

    vitorias_fora = {}
    derrotas_fora = {}

    empates_casa = {}
    empates_fora = {}

    for _, row in df_liga.iterrows():

        try:

            casa = row['Time Casa']

            fora = row['Time Visitante']

            gols_casa = int(

                row['Placar']
                .split('x')[0]
                .strip()
            )

            gols_fora = int(

                row['Placar']
                .split('x')[1]
                .strip()
            )

            # VITÓRIA CASA

            if gols_casa > gols_fora:

                vitorias_casa[casa] = (

                    vitorias_casa.get(casa, 0) + 1
                )

                derrotas_fora[fora] = (

                    derrotas_fora.get(fora, 0) + 1
                )

            # VITÓRIA FORA

            elif gols_casa < gols_fora:

                vitorias_fora[fora] = (

                    vitorias_fora.get(fora, 0) + 1
                )

                derrotas_casa[casa] = (

                    derrotas_casa.get(casa, 0) + 1
                )

            # EMPATE

            else:

                empates_casa[casa] = (

                    empates_casa.get(casa, 0) + 1
                )

                empates_fora[fora] = (

                    empates_fora.get(fora, 0) + 1
                )

        except:
            pass

    top_vitorias_casa = sorted(

        vitorias_casa.items(),

        key=lambda x: x[1],

        reverse=True
    )

    top_derrotas_casa = sorted(

        derrotas_casa.items(),

        key=lambda x: x[1],

        reverse=True
    )

    top_empates_casa = sorted(

        empates_casa.items(),

        key=lambda x: x[1],

        reverse=True
    )

    top_vitorias_fora = sorted(

        vitorias_fora.items(),

        key=lambda x: x[1],

        reverse=True
    )

    top_derrotas_fora = sorted(

        derrotas_fora.items(),

        key=lambda x: x[1],

        reverse=True
    )

    top_empates_fora = sorted(

        empates_fora.items(),

        key=lambda x: x[1],

        reverse=True
    )

    st.divider()

    st.subheader("📈 Estatísticas dos Times")

    c1, c2 = st.columns(2)

    with c1:

        st.markdown("## 🏠 CASA")

        st.markdown("### ✅ Mais Vitórias")

        for time, qtd in top_vitorias_casa:

            st.write(f"{time} → {qtd}")

        st.markdown("### ❌ Mais Derrotas")

        for time, qtd in top_derrotas_casa:

            st.write(f"{time} → {qtd}")

        st.markdown("### 🤝 Mais Empates")

        for time, qtd in top_empates_casa:

            st.write(f"{time} → {qtd}")

    with c2:

        st.markdown("## 🚗 FORA")

        st.markdown("### ✅ Mais Vitórias")

        for time, qtd in top_vitorias_fora:

            st.write(f"{time} → {qtd}")

        st.markdown("### ❌ Mais Derrotas")

        for time, qtd in top_derrotas_fora:

            st.write(f"{time} → {qtd}")

        st.markdown("### 🤝 Mais Empates")

        for time, qtd in top_empates_fora:

            st.write(f"{time} → {qtd}")


        