import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

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

df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
df['Data_str'] = df['Data'].dt.strftime('%d/%m/%Y')

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

hoje = datetime.today().date()

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

    # SIDEBAR
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

    # FILTRO BASE
    df_filtrado = df[
        (df['Probabilidade (%)'] >= threshold_min) &
        (df['Probabilidade (%)'] <= threshold_max)
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

    # FILTROS TABELA
    st.subheader("🔎 Filtros da tabela")

    c1, c2, c3, c4 = st.columns([1,1,1,1])

    c1.text_input("Time Casa", key="busca_casa")
    c2.text_input("Time Visitante", key="busca_visit")
    c3.text_input("Data", key="busca_data")

    c4.button("🔄 Limpar", on_click=limpar_filtros)

    def aplicar(df_):
        if st.session_state.busca_casa:
            df_ = df_[df_['Time Casa'].str.contains(st.session_state.busca_casa, case=False)]
        if st.session_state.busca_visit:
            df_ = df_[df_['Time Visitante'].str.contains(st.session_state.busca_visit, case=False)]
        if st.session_state.busca_data:
            df_ = df_[df_['Data_str'].str.contains(st.session_state.busca_data)]
        return df_

    df_filtrado = aplicar(df_filtrado)

    # MÉTRICAS
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

    # TABELA PRINCIPAL
    colunas = ['Liga','Data_str','Time Casa','Time Visitante','Placar','Resultado','Probabilidade (%)']

    st.dataframe(
        df_filtrado[colunas].sort_values(by='Probabilidade (%)', ascending=False),
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # JOGOS DE HOJE (CORRIGIDO)
    # =========================

    inicio_dia = datetime.combine(hoje, datetime.min.time())
    fim_dia = inicio_dia + timedelta(days=1)

    df_hoje = df[(df['Data'] >= inicio_dia) & (df['Data'] < fim_dia)]

    # Forçar conversão para string e garantir que placares sejam exibidos
    df_hoje['Placar'] = df_hoje['Placar'].astype(str)
    df_hoje['Placar_Display'] = df_hoje['Placar'].apply(
        lambda x: x if x != "🔮" else "⏳ Aguardando"
    )

    # Separar jogos futuros e finalizados
    df_hoje_futuro = df_hoje[df_hoje['Placar'] == "🔮"].copy()
    df_hoje_finalizado = df_hoje[df_hoje['Placar'] != "🔮"].copy()

    st.subheader("📅 Jogos de Hoje")

    # Abas para melhor organização
    tab_hoje_futuro, tab_hoje_finalizado = st.tabs(["🔮 Futuros", "✅ Finalizados"])

    with tab_hoje_futuro:
        if len(df_hoje_futuro) > 0:
            colunas_exibicao = ['Liga', 'Data_str', 'Time Casa', 'Time Visitante', 'Placar_Display', 'Probabilidade (%)']
            st.dataframe(
                df_hoje_futuro[colunas_exibicao].sort_values(by='Probabilidade (%)', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("📭 Nenhum jogo futuro programado para hoje")

    with tab_hoje_finalizado:
        if len(df_hoje_finalizado) > 0:
            # Ordenar por horário (mais recentes primeiro)
            df_hoje_finalizado = df_hoje_finalizado.sort_values(by='Data', ascending=False)
            
            # Adicionar indicador visual de acerto/erro
            df_hoje_finalizado['Acertou?'] = df_hoje_finalizado['Placar'].apply(
                lambda x: "✅ Sim" if int(x.split('x')[0].strip()) > 0 else "❌ Não"
            )
            
            colunas_exibicao = ['Liga', 'Data_str', 'Time Casa', 'Time Visitante', 'Placar', 'Acertou?', 'Probabilidade (%)']
            
            st.dataframe(
                df_hoje_finalizado[colunas_exibicao],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Placar": st.column_config.TextColumn("Placar Final"),
                    "Acertou?": st.column_config.TextColumn("Casa Marcou Gol?"),
                    "Probabilidade (%)": st.column_config.ProgressColumn(
                        "Probabilidade",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    )
                }
            )
            
            # Métrica de acerto do dia
            total_jogos = len(df_hoje_finalizado)
            acertos = len(df_hoje_finalizado[df_hoje_finalizado['Acertou?'] == "✅ Sim"])
            taxa_acerto = (acertos / total_jogos * 100) if total_jogos > 0 else 0
            
            st.success(f"🎯 **Taxa de acerto hoje:** {acertos}/{total_jogos} ({taxa_acerto:.1f}%)")
            
            # Mostrar quais jogos errou
            erros = df_hoje_finalizado[df_hoje_finalizado['Acertou?'] == "❌ Não"]
            if len(erros) > 0:
                with st.expander(f"⚠️ Jogos que deram errado hoje ({len(erros)})"):
                    st.dataframe(
                        erros[['Liga', 'Time Casa', 'Time Visitante', 'Placar', 'Probabilidade (%)']],
                        use_container_width=True,
                        hide_index=True
                    )
        else:
            st.info("📭 Nenhum jogo finalizado hoje ainda")

# =========================
# ABA 2 - LIGAS
# =========================

with tab2:
    st.subheader("🏆 Análise por Liga")
    
    # Selectbox para escolher liga
    ligas_disponiveis = sorted(df['Liga'].dropna().unique())
    liga_selecionada = st.selectbox("Selecione a Liga", ligas_disponiveis)
    
    if liga_selecionada:
        df_liga = df[df['Liga'] == liga_selecionada].copy()
        
        # Separar jogos passados e futuros
        df_liga_passado = df_liga[df_liga['Placar'] != "🔮"]
        df_liga_futuro = df_liga[df_liga['Placar'] == "🔮"]
        
        col1_liga, col2_liga, col3_liga = st.columns(3)
        
        with col1_liga:
            st.metric("Total de Jogos", len(df_liga))
        
        with col2_liga:
            if len(df_liga_passado) > 0:
                acertos_liga = len(df_liga_passado[df_liga_passado['Placar'].apply(
                    lambda x: int(x.split('x')[0].strip()) > 0
                )])
                taxa_liga = (acertos_liga / len(df_liga_passado) * 100)
                st.metric("Taxa de Acerto", f"{taxa_liga:.1f}%")
            else:
                st.metric("Taxa de Acerto", "N/A")
        
        with col3_liga:
            st.metric("Jogos Futuros", len(df_liga_futuro))
        
        # Mostrar próximos jogos da liga
        st.markdown(f"#### 🔮 Próximos Jogos - {liga_selecionada}")
        if len(df_liga_futuro) > 0:
            st.dataframe(
                df_liga_futuro[['Data_str', 'Time Casa', 'Time Visitante', 'Probabilidade (%)']]
                .sort_values(by='Data', ascending=True),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(f"Nenhum jogo futuro para {liga_selecionada}")
        
        # Mostrar histórico de acertos da liga
        st.markdown(f"#### 📊 Histórico - {liga_selecionada}")
        if len(df_liga_passado) > 0:
            df_liga_passado['Casa_Marcou'] = df_liga_passado['Placar'].apply(
                lambda x: "Sim" if int(x.split('x')[0].strip()) > 0 else "Não"
            )
            
            # Tabela de contingência simples
            st.dataframe(
                df_liga_passado[['Data_str', 'Time Casa', 'Time Visitante', 'Placar', 'Casa_Marcou', 'Probabilidade (%)']]
                .sort_values(by='Data', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(f"Nenhum jogo finalizado para {liga_selecionada}")