import streamlit as st
import pandas as pd
import os
from datetime import datetime
from collections import Counter
import re
usuarios = st.secrets["usuarios"]


st.set_page_config(layout="wide")

st.title("📊 Sistema IA")

# =========================
# LOGIN
# =========================

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
                    st.session_state.tipo = dados_usuario["tipo"]

                    st.rerun()

                else:
                    st.error("Acesso expirado")

            else:
                st.error("Senha incorreta")

        else:
            st.error("Usuário não encontrado")

    st.stop()

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
df['Hora'] = df['Hora'].astype(str).str.slice(0,5)

df['Placar'] = df['Placar'].astype(str).str.strip()
df['Placar'] = df['Placar'].replace("-", "🔮")

df['Probabilidade (%)'] = (
    df['Probabilidade'] * 100
).round(2)

# =========================
# RESULTADO VISUAL
# =========================

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

df['Resultado'] = df['Placar'].apply(resultado_flag)

# =========================
# ABAS
# =========================

tab1, tab2, tab3 = st.tabs([
    "📊 Análise Geral",
    "🏆 Ligas",
    "⚽ Placares"
])

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

    if "data_inicial" not in st.session_state:
        st.session_state.data_inicial = ""

    if "data_final" not in st.session_state:
        st.session_state.data_final = ""

    def update_from_slider():

        st.session_state.min_prob = (
            st.session_state.slider_range[0]
        )

        st.session_state.max_prob = (
            st.session_state.slider_range[1]
        )

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
        st.session_state.data_inicial = ""
        st.session_state.data_final = ""

    st.sidebar.header("Filtros")

    st.sidebar.slider(
        "Probabilidade (%)",
        0,
        100,
        st.session_state.slider_range,
        key="slider_range",
        on_change=update_from_slider
    )

    st.sidebar.number_input(
        "Min",
        0,
        100,
        key="min_prob",
        on_change=update_from_input
    )

    st.sidebar.number_input(
        "Max",
        0,
        100,
        key="max_prob",
        on_change=update_from_input
    )

    st.sidebar.button(
        "🔄 Limpar Range",
        on_click=limpar_range
    )

    threshold_min = st.session_state.min_prob
    threshold_max = st.session_state.max_prob

    st.sidebar.subheader("Filtros Avançados")

    todos_times = sorted(
        set(df['Time Casa']).union(
            set(df['Time Visitante'])
        )
    )

    times_sidebar = st.sidebar.multiselect(
        "Times",
        options=todos_times
    )

    todas_ligas = sorted(
        df['Liga'].dropna().unique()
    )

    ligas_sidebar = st.sidebar.multiselect(
        "Ligas",
        options=todas_ligas
    )

    placares = sorted(
        df['Placar'].dropna().unique()
    )

    placar_sidebar = st.sidebar.multiselect(
        "Placar",
        options=placares
    )

    # =========================
    # FILTRO BASE
    # =========================

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

        df_filtrado = df_filtrado[
            df_filtrado['Liga'].isin(ligas_sidebar)
        ]

    if placar_sidebar:

        df_filtrado = df_filtrado[
            df_filtrado['Placar'].isin(placar_sidebar)
        ]

    # =========================
    # FILTROS TABELA
    # =========================

    st.subheader("🔎 Filtros da tabela")

    c1, c2, c3, c4, c5 = st.columns([1,1,1,1,1])
    c1.text_input("Time Casa", key="busca_casa")
    c2.text_input("Time Visitante", key="busca_visit")
    c3.text_input(
    "Data Inicial",
    key="data_inicial"
)

    c4.text_input(
    "Data Final",
    key="data_final"
)

    c4.button(
        "🔄 Limpar",
        on_click=limpar_filtros
    )
    def aplicar(df):

        if st.session_state.busca_casa:

            df = df[
                df['Time Casa'].str.lower().str.startswith(
                    st.session_state.busca_casa.lower()
                )
            ]

        if st.session_state.busca_visit:

            df = df[
                df['Time Visitante'].str.lower().str.startswith(
                    st.session_state.busca_visit.lower()
                )
            ]

        if (
            st.session_state.data_inicial and
            st.session_state.data_final
        ):

            try:

                data_ini = pd.to_datetime(
                    st.session_state.data_inicial,
                    dayfirst=True
                )

                data_fim = pd.to_datetime(
                    st.session_state.data_final,
                    dayfirst=True
                )

                df = df[
                    (df['Data'] >= data_ini) &
                    (df['Data'] <= data_fim)
                ]

            except:
                pass

        return df

    
    df_filtrado = aplicar(df_filtrado)

    # =========================
    # MÉTRICAS
    # =========================

    df_passado = df_filtrado[
        df_filtrado['Placar'] != "🔮"
    ]

    df_0x1 = df_passado[
        df_passado['Placar'] == "0 x 1"
    ]

    total = len(df_passado)

    erros_0x1 = len(df_0x1)

    taxa_0x1 = (
        erros_0x1 / total * 100
    ) if total > 0 else 0

    st.markdown("### 📊 Resultado do filtro atual")

    col1, col2, col3 = st.columns(3)

    col1.metric("Jogos no filtro", total)
    col2.metric("0x1", erros_0x1)
    col3.metric("Taxa 0x1", f"{taxa_0x1:.2f}%")

    # =========================
    # PROCESSAR PLACARES
    # =========================

    col_btn_proc1, col_btn_proc2 = st.columns([1,4])

    with col_btn_proc1:

        if st.button("⚽ Processar Placares"):

            placares_processados = df_filtrado[
                df_filtrado['Placar'] != "🔮"
            ]['Placar'].dropna().tolist()

            st.session_state.placares_processados = placares_processados

            st.success("Processados, vá para Placares")

    # =========================
    # TABELA PRINCIPAL
    # =========================

    colunas = [
        'Liga',
        'Data_str',
        'Time Casa',
        'Time Visitante',
        'Placar',
        'Resultado',
        'Probabilidade (%)'
    ]

    st.dataframe(
        df_filtrado[colunas].sort_values(
            by='Probabilidade (%)',
            ascending=False
        ),
        use_container_width=True
    )

    # =========================
    # JOGOS DE HOJE
    # =========================

    df_futuro = df_filtrado[
        df_filtrado['Placar'] == "🔮"
    ]

    st.subheader("📅 Jogos de Hoje")

    if len(df_futuro) > 0:

        st.dataframe(
            df_futuro[[
                'Liga',
                'Data_str',
                'Hora',
                'Time Casa',
                'Time Visitante',
                'Placar',
                'Resultado',
                'Probabilidade (%)'
            ]].sort_values(
                by='Probabilidade (%)',
                ascending=False
            ),
            use_container_width=True
        )

    else:
        st.info("Nenhum jogo futuro")

# =========================
# ABA 2 - LIGAS
# =========================

with tab2:

    st.subheader("🏆 Análise por Ligas")

    df_ligas = df[df['Placar'] != "🔮"].copy()

    resumo = df_ligas.groupby('Liga').agg(
        Jogos=('Liga', 'count'),
        Erros_0x1=('Placar', lambda x: (x == "0 x 1").sum())
    ).reset_index()

    resumo['Taxa_0x1 (%)'] = (
        resumo['Erros_0x1'] / resumo['Jogos'] * 100
    ).round(2)

    resumo = resumo.sort_values(
        by='Jogos',
        ascending=False
    )

    st.dataframe(
        resumo,
        use_container_width=True
    )

    liga_selecionada = st.selectbox(
        "Selecionar Liga",
        options=resumo['Liga']
    )

    df_detalhe = df[
        (df['Liga'] == liga_selecionada) &
        (df['Placar'] != "🔮")
    ].copy()

    colunas_liga = [
        'Data_str',
        'Time Casa',
        'Time Visitante',
        'Placar',
        'Resultado'
    ]

    st.subheader(
        f"📊 Todos os jogos da liga: {liga_selecionada}"
    )

    st.dataframe(
        df_detalhe[colunas_liga].sort_values(
            by='Data_str',
            ascending=False
        ),
        use_container_width=True
    )

    # =========================
    # PROCESSAR PLACARES DA LIGA
    # =========================

    if st.button("⚽ Processar Placares da Liga"):

        placares_processados = df_detalhe[
            'Placar'
        ].dropna().tolist()

        st.session_state.placares_processados = (
            placares_processados
        )

        st.success(
            "Placares da liga processados. Vá para a aba Placares."
        )

    # =========================
    # JOGOS 0X1
    # =========================

    df_0x1 = df_detalhe[
        df_detalhe['Placar'] == "0 x 1"
    ]

    st.subheader("❌ Jogos que terminaram 0 x 1")

    if len(df_0x1) > 0:

        st.dataframe(
            df_0x1[colunas_liga].sort_values(
                by='Data_str',
                ascending=False
            ),
            use_container_width=True
        )

    else:
        st.info("Nenhum jogo 0x1 nessa liga 👍")

# =========================
# ESTATÍSTICAS DOS TIMES
# =========================

    # =========================
# ESTATÍSTICAS DOS TIMES
# =========================

    vitorias_casa = {}
    derrotas_casa = {}

    vitorias_fora = {}
    derrotas_fora = {}

    empates_casa = {}
    empates_fora = {}

    for _, row in df_detalhe.iterrows():

        try:

            casa = row['Time Casa']
            fora = row['Time Visitante']

            gols_casa = int(
                row['Placar'].split('x')[0].strip()
            )

            gols_fora = int(
                row['Placar'].split('x')[1].strip()
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

# =========================
# ABA 3 - PLACARES
# =========================

with tab3:

    st.subheader("⚽ Análise de Placares")

    if "placares_processados" not in st.session_state:

        st.info("Processe os placares na aba principal")

    else:

        placares = st.session_state.placares_processados

        def normalizar(linha):

            linha = str(linha).strip().lower()

            if not linha:
                return None

            m = re.match(r"^\s*(\d+)\D+(\d+)\s*$", linha)

            if not m:
                return None

            a, b = m.groups()

            return f"{int(a)} x {int(b)}"

        def classificar(placar):

            a, b = map(int, placar.split(" x "))

            if a > b:
                return "casa"

            elif a == b:
                return "empate"

            else:
                return "fora"

        placares_validos = []
        invalidos = 0

        for l in placares:

            p = normalizar(l)

            if p:
                placares_validos.append(p)

            else:
                invalidos += 1

        if not placares_validos:

            st.warning("Nenhum placar válido encontrado.")

        else:

            freq = Counter(placares_validos)

            total = sum(freq.values())

            casa = []
            empate = []
            fora = []

            for placar, qtd in freq.items():

                perc = (qtd / total) * 100

                tipo = classificar(placar)

                item = (placar, qtd, perc)

                if tipo == "casa":
                    casa.append(item)

                elif tipo == "empate":
                    empate.append(item)

                else:
                    fora.append(item)

            total_casa = sum(q for _, q, _ in casa)
            total_empate = sum(q for _, q, _ in empate)
            total_fora = sum(q for _, q, _ in fora)

            casa = sorted(casa, key=lambda x: x[1], reverse=True)
            empate = sorted(empate, key=lambda x: x[1], reverse=True)
            fora = sorted(fora, key=lambda x: x[1], reverse=True)

            st.subheader("📌 Resumo geral")

            col_r1, col_r2, col_r3 = st.columns(3)

            with col_r1:
                st.metric(
                    "🏠 Casa",
                    f"{total_casa}",
                    f"{(total_casa/total)*100:.2f}%"
                )

            with col_r2:
                st.metric(
                    "🤝 Empate",
                    f"{total_empate}",
                    f"{(total_empate/total)*100:.2f}%"
                )

            with col_r3:
                st.metric(
                    "🚗 Fora",
                    f"{total_fora}",
                    f"{(total_fora/total)*100:.2f}%"
                )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.subheader("🏠 Casa")

                for p, q, pc in casa:
                    st.write(f"{p} → {q} ({pc:.2f}%)")

            with col2:

                st.subheader("🤝 Empate")

                for p, q, pc in empate:
                    st.write(f"{p} → {q} ({pc:.2f}%)")

            with col3:

                st.subheader("🚗 Fora")

                for p, q, pc in fora:
                    st.write(f"{p} → {q} ({pc:.2f}%)")

            st.success(
                f"Total válido: {total} | Inválidos: {invalidos}"
            )

    # =========================
    # PREVISÃO MANUAL
    # =========================

    st.divider()

    st.header("2) Previsão (Casa x Fora)")

    if "lista_casa" not in st.session_state:
        st.session_state.lista_casa = ""

    if "lista_fora" not in st.session_state:
        st.session_state.lista_fora = ""

    col_btn3, col_btn4 = st.columns(2)

    with col_btn3:
        gerar = st.button("Gerar previsão")

    with col_btn4:

        if st.button("Limpar previsão"):

            st.session_state.lista_casa = ""
            st.session_state.lista_fora = ""

            st.rerun()

    lista_casa = st.text_area(
        "Lista CASA:",
        height=150,
        key="lista_casa"
    )

    lista_fora = st.text_area(
        "Lista FORA:",
        height=150,
        key="lista_fora"
    )

    if gerar:

        def extrair_gols(lista):

            gols = []

            for linha in lista.splitlines():

                p = normalizar(linha)

                if p:

                    a, b = map(int, p.split(" x "))

                    gols.append(a)

            return gols

        gols_casa = extrair_gols(lista_casa)
        gols_fora = extrair_gols(lista_fora)

        if not gols_casa or not gols_fora:

            st.warning("Preencha as duas listas corretamente.")

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

            st.subheader("📊 Top placares previstos")

            for placar, prob in resultados[:15]:

                st.write(
                    f"{placar} → {prob*100:.2f}%"
                )