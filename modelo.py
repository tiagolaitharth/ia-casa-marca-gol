import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

ARQUIVO = r'C:\Users\Pichau\OneDrive\BASE DE DADOS.xlsx'


def rodar_modelo():
    print("Lendo base...")
    df = pd.read_excel(ARQUIVO, header=9)

    df.columns = [c.strip() for c in df.columns]

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

    # =========================
    # SEPARAÇÃO CORRETA
    # =========================

    df['Placar'] = df['Placar'].astype(str).str.strip()

    df_treino = df[df['Placar'] != "-"].copy()
    df_prever = df[df['Placar'] == "-"].copy()

    # =========================
    # TARGET (SÓ TREINO)
    # =========================

    def extrair_alvo(placar):
        try:
            gols = int(str(placar).split('x')[0].strip())
            return 1 if gols > 0 else 0
        except:
            return 0

    df_treino['ALVO'] = df_treino['Placar'].apply(extrair_alvo)

    # =========================
    # FEATURES (AMBOS)
    # =========================

    def criar_features(df_):
        df_['FORCA_ATAQUE_CASA'] = df_['MÉDIA GOL A FAVOR CASA'] * df_['% Marca Gol Casa']
        df_['FRAGILIDADE_DEFESA_FORA'] = df_['MÉDIA GOLS CONTRA FORA']
        df_['INDICE_GOL_CASA'] = df_['FORCA_ATAQUE_CASA'] - df_['FRAGILIDADE_DEFESA_FORA']
        df_['JOGO_TRAVADO'] = df_['MÉDIA GOLS TOTAL CASA'] + df_['MÉDIA GOLS TOTAL FORA']
        df_['PRESSAO_VISITANTE'] = 1 / df_['ODD FORA']
        return df_

    df_treino = criar_features(df_treino)
    df_prever = criar_features(df_prever)

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
    # PREVISÃO (SÓ FUTURO)
    # =========================

    if len(df_prever) > 0:
        X_prever = df_prever[colunas].fillna(0)
        X_prever_scaled = scaler.transform(X_prever)

        df_prever['Probabilidade'] = modelo.predict_proba(X_prever_scaled)[:, 1]
    else:
        df_prever['Probabilidade'] = []

    # =========================
    # JUNTA RESULTADO FINAL
    # =========================

    df_treino['Probabilidade'] = None

    df_resultado = pd.concat([df_treino, df_prever])

    df_resultado = df_resultado[[
        'Liga',
        'Data',
        'Time Casa',
        'Time Visitante',
        'Placar',
        'Probabilidade'
    ]]

    df_resultado.to_excel("resultado_modelo.xlsx", index=False)

    print("Arquivo gerado com sucesso!")


if __name__ == "__main__":
    rodar_modelo()