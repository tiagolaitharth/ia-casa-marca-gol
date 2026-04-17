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

    # TARGET
    def extrair_alvo(placar):
        try:
            gols = int(str(placar).split('x')[0].strip())
            return 1 if gols > 0 else 0
        except:
            return 0

    df['ALVO'] = df['Placar'].apply(extrair_alvo)

    # FEATURES
    df['FORCA_ATAQUE_CASA'] = df['MÉDIA GOL A FAVOR CASA'] * df['% Marca Gol Casa']
    df['FRAGILIDADE_DEFESA_FORA'] = df['MÉDIA GOLS CONTRA FORA']
    df['INDICE_GOL_CASA'] = df['FORCA_ATAQUE_CASA'] - df['FRAGILIDADE_DEFESA_FORA']
    df['JOGO_TRAVADO'] = df['MÉDIA GOLS TOTAL CASA'] + df['MÉDIA GOLS TOTAL FORA']
    df['PRESSAO_VISITANTE'] = 1 / df['ODD FORA']

    colunas = colunas_base + [
        'FORCA_ATAQUE_CASA',
        'FRAGILIDADE_DEFESA_FORA',
        'INDICE_GOL_CASA',
        'JOGO_TRAVADO',
        'PRESSAO_VISITANTE'
    ]

    X = df[colunas].fillna(0)
    y = df['ALVO']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("Treinando modelo...")

    modelo = MLPClassifier(
        hidden_layer_sizes=(20, 10),
        max_iter=1500,
        random_state=42
    )

    modelo.fit(X_scaled, y)

    # RESULTADO
    df_resultado = df.copy()
    df_resultado['Probabilidade'] = modelo.predict_proba(X_scaled)[:, 1]

    # 🔥 AGORA INCLUI LIGA
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