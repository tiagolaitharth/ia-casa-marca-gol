# =========================
# JOGOS DE HOJE (SEPARADOS)
# =========================

df_hoje = df[df['Data'].dt.date == hoje]

df_hoje_futuro = df_hoje[df_hoje['Placar'] == "🔮"]

st.subheader("📅 Jogos de Hoje")

st.markdown("#### 🔮 Jogos de Hoje (Futuros)")
if len(df_hoje_futuro) > 0:
    st.dataframe(
        df_hoje_futuro[colunas].sort_values(by='Probabilidade (%)', ascending=False),
        use_container_width=True
    )
else:
    st.info("Nenhum jogo futuro hoje")