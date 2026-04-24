import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import os

ARQUIVO = r'C:\Users\Pichau\OneDrive\BASE DE DADOS.xlsx'
ARQUIVO_RESULTADO = "resultado_modelo.xlsx"


def rodar_modelo():
    print("Lendo base...")
    df = pd.read_excel(ARQUIVO, header=9)

    df.columns = [c.strip() for c in df.columns]

    # =========================
    # TRATAMENTO
    # =========================

    colunas_base = [
        'ODD CASA',
        'ODD FORA',
        'MÉDIA CHUTES NO GOL CASA',
        'MÉDIA GOL A FAVOR CASA',
        '% Marca Gol Casa',
        'MÉDIA GOLS CONTRA CASA',
        'MÉDIA GOLS CONTRA FORA',
        'MÉDIA GOLS TOTAL CASA',
        'MÉDIA GOLS TOTAL FORA'
    ]

    def limpar(v):
        try:
            return float(str(v).replace(',', '.'))
        except:
            return 0

    for c in colunas_base:
        df[c] = df[c].apply(limpar)

    df['Placar'] = df['Placar'].astype(str).str.strip()
    df['Data'] = pd.to_datetime(df['Data'])

    # =========================
    # TREINO (SÓ PASSADO)
    # =========================

    hoje = datetime.today().date()
    df_treino = df[df['Data'].dt.date < hoje].copy()

    def extrair_alvo(placar):
        try:
            gols = int(str(placar).split('x')[0].strip())
            return 1 if gols > 0 else 0
        except:
            return 0

    df_treino['ALVO'] = df_treino['Placar'].apply(extrair_alvo)

    # =========================
    # FEATURES
    # =========================

    def criar_features(df_):
        df_['FORCA_ATAQUE_CASA'] = df_['MÉDIA GOL A FAVOR CASA'] * df_['% Marca Gol Casa']
        df_['FRAGILIDADE_DEFESA_FORA'] = df_['MÉDIA GOLS CONTRA FORA']
        df_['INDICE_GOL_CASA'] = df_['FORCA_ATAQUE_CASA'] - df_['FRAGILIDADE_DEFESA_FORA']
        df_['JOGO_TRAVADO'] = df_['MÉDIA GOLS TOTAL CASA'] + df_['MÉDIA GOLS TOTAL FORA']
        df_['PRESSAO_VISITANTE'] = 1 / df_['ODD FORA']
        return df_

    df = criar_features(df)
    df_treino = criar_features(df_treino)

    colunas = colunas_base + [
        'FORCA_ATAQUE_CASA',
        'FRAGILIDADE_DEFESA_FORA',
        'INDICE_GOL_CASA',
        'JOGO_TRAVADO',
        'PRESSAO_VISITANTE'
    ]

    # =========================
    # TREINO
    # =========================

    X = df_treino[colunas].fillna(0)
    y = df_treino['ALVO']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("Treinando modelo...")

    modelo = MLPClassifier(
        hidden_layer_sizes=(20, 10),
        max_iter=1500,
        random_state=42
    )

    modelo.fit(X_scaled, y)

    # =========================
    # PREVISÃO (TODOS)
    # =========================

    X_total = df[colunas].fillna(0)
    X_total_scaled = scaler.transform(X_total)

    df['Probabilidade'] = modelo.predict_proba(X_total_scaled)[:, 1]

    # =========================
    # 🔥 PRESERVAR PROBABILIDADES ANTIGAS
    # =========================

    if os.path.exists(ARQUIVO_RESULTADO):
        df_antigo = pd.read_excel(ARQUIVO_RESULTADO)

        df_antigo['Data'] = pd.to_datetime(df_antigo['Data'])

        # chave única
        df['chave'] = (
            df['Data'].astype(str) +
            df['Time Casa'] +
            df['Time Visitante']
        )

        df_antigo['chave'] = (
            df_antigo['Data'].astype(str) +
            df_antigo['Time Casa'] +
            df_antigo['Time Visitante']
        )

        mapa_prob = dict(zip(df_antigo['chave'], df_antigo['Probabilidade']))

        # mantém a probabilidade antiga se já existir
        df['Probabilidade'] = df.apply(
            lambda row: mapa_prob[row['chave']] if row['chave'] in mapa_prob else row['Probabilidade'],
            axis=1
        )

        df.drop(columns=['chave'], inplace=True)

    # =========================
    # OUTPUT FINAL
    # =========================

    df_resultado = df[[
        'Liga',
        'Data',
        'Time Casa',
        'Time Visitante',
        'Placar',
        'Probabilidade'
    ]]

    df_resultado.to_excel(ARQUIVO_RESULTADO, index=False)

    print("Arquivo atualizado com sucesso!")


if __name__ == "__main__":
    rodar_modelo()